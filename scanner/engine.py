"""
engine.py — Scan engine orchestrator for SwingsterV2.

Multi-stage funnel pipeline per symbol:
  OHLCV → Candles → Stage 2 filter → Liquidity filter → Pattern detection
  → RS Rank → Risk/Reward → Composite Scoring → ScanResult

Batch scanning via ThreadPoolExecutor with NUM_AGENTS workers.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional

from config import (
    NUM_AGENTS,
    STAGE2_MIN_SCORE,
    WORKER_COUNT,
    SCAN_MODES,
    SCAN_MODE,
    MIN_CANDIDATE_SCORE,
    MAX_CANDIDATES,
)
from fetcher.db_writer import (
    read_ohlcv,
    read_ohlcv_batch,
    get_eligible_symbols,
    get_prefilter_counts,
    get_connection,
)

from scanner.models import Candle, ScanResult, rows_to_candles
from scanner.trend import analyze_trend
from scanner.volume import analyze_volume
from scanner.patterns.registry import get_patterns, PATTERN_REGISTRY, get_pattern_config
from scanner.patterns.pivots   import find_swing_pivots
from scanner.rs_rank import compute_rs
from scanner.risk_reward import compute_risk_reward


logger = logging.getLogger(__name__)

class RejectedRRError(Exception):
    pass

# No global cache needed, handled per-worker


# ---------------------------------------------------------------------------
# Single-symbol scan
# ---------------------------------------------------------------------------

def scan_symbol(
    symbol: str,
    conn: Optional[sqlite3.Connection] = None,
    nifty_candles: Optional[list[Candle]] = None,
    mode: str = "ALL",
    preloaded_rows: Optional[list[tuple]] = None,
) -> Optional[ScanResult]:
    """
    Run the full analysis pipeline for a single symbol.

    Returns ``None`` at any stage that fails its gate condition:
      • No data / too few candles
      • Stage 2 score < 60
      • Illiquid (avg volume < 50k)
      • No chart pattern detected
    """
    # 1. Read OHLCV from DB or use preloaded
    if preloaded_rows is not None:
        rows = preloaded_rows
    else:
        rows = read_ohlcv(symbol, conn=conn)
        
    if not rows:
        return None

    # 2. Convert to Candles
    candles = rows_to_candles(rows)

    # get active patterns for this mode
    active_patterns = get_patterns(mode)

    MIN_CANDLES = {
        "VCP": 60,
        "FLAG_POLE": 60,
        "CUP_HANDLE": 100,
        "BREAKOUT": 75
    }
    active_patterns = [
        p for p in active_patterns
        if len(candles) >= MIN_CANDLES.get(p.config.name, 60)
    ]
    
    if not active_patterns:
        return None

    trend = analyze_trend(candles)
    
    STAGE2_MIN_SCORE_DICT = {
        "VCP": 0,
        "FLAG_POLE": 55,
        "CUP_HANDLE": 45,
        "BREAKOUT": 60
    }
    active_patterns = [
        p for p in active_patterns
        if trend.stage2_score >= STAGE2_MIN_SCORE_DICT.get(p.config.name, 60)
    ]
    
    if not active_patterns:
        return None

    # 4. Volume analysis — skip if illiquid
    vol = analyze_volume(candles)
    if vol.is_illiquid:
        return None

    # per-pattern filtering — use each pattern's own config
    # for ALL mode: use the strictest min_signal_score across patterns
    min_score = min(p.config.min_signal_score for p in active_patterns)

    PIVOT_LOOKBACK = {
        "VCP": 120,
        "FLAG_POLE": 60,
        "CUP_HANDLE": 252,
        "BREAKOUT": 75
    }
    max_lookback = max(PIVOT_LOOKBACK.get(p.config.name, 120) for p in active_patterns)
    pivots = find_swing_pivots(candles, lookback=max_lookback)

    # run detectors — only for active patterns
    best_signal = None
    matched_pattern = None
    for pattern in active_patterns:
        sig = pattern.detect(candles, pivots)
        if sig and (best_signal is None or sig.strength > best_signal.strength):
            best_signal = sig
            matched_pattern = pattern

    if best_signal is None or best_signal.strength < min_score:
        return None

    # 6. RS rank vs Nifty 50
    rs = compute_rs(candles, nifty_candles if nifty_candles else [])

    # 7. Risk-reward — anchored to the pattern's config
    rr = compute_risk_reward(candles, matched_pattern.config.rr_hard_minimum, best_signal)

    # Gate: reject setups where risk-reward is invalid
    if rr.ratio <= 0:
        raise RejectedRRError(symbol)

    # 8. Composite score
    composite = matched_pattern.score(
        signal_strength=best_signal.strength,
        volume_score=vol.volume_score,
        rr_score=rr.score,
        stage2_score=trend.stage2_score,
        rs_score=rs.rs_score,
    )

    return ScanResult(
        symbol=symbol,
        pattern=best_signal.name,
        signal_strength=best_signal.strength,
        volume_score=vol.volume_score,
        rr_score=rr.score,
        stage2_score=trend.stage2_score,
        rs_score=rs.rs_score,
        composite_score=composite,
        buy_point=best_signal.buy_point,
        stop_loss=rr.stop_loss,
        target=rr.target,
        rr_ratio=rr.ratio,
        current_price=candles[-1].close,
        distance_from_buy_pct=best_signal.distance_from_buy_pct,
        scan_mode=mode,
    )


# ---------------------------------------------------------------------------
# Top-level Batch Scan Process Worker
# ---------------------------------------------------------------------------

def _scan_batch(args: tuple) -> tuple[list[ScanResult], int, list[str]]:
    """
    Worker entry point for processing a batch of symbols.
    Opens its own SQLite connection, pre-loads nifty candles, and scans symbols.
    """
    batch, mode = args
    conn = get_connection()
    try:
        nifty_rows = read_ohlcv("^NSEI", conn=conn)
        nifty_candles = rows_to_candles(nifty_rows) if nifty_rows else []
        
        # Batch fetch all data for this worker's symbols
        batch_data = read_ohlcv_batch(batch, conn=conn)
        
        results = []
        rejected_rr = []
        scanned_count = 0
        for symbol in batch:
            try:
                rows = batch_data.get(symbol, [])
                res = scan_symbol(symbol, conn=conn, nifty_candles=nifty_candles, mode=mode, preloaded_rows=rows)
                if res is not None:
                    results.append(res)
            except RejectedRRError:
                rejected_rr.append(symbol)
            except Exception as e:
                print(f"[WARN] {symbol}: {e}", file=sys.stderr)
            finally:
                scanned_count += 1
        return results, scanned_count, rejected_rr
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Batch scan
# ---------------------------------------------------------------------------

def scan_all(
    mode: str = SCAN_MODE,
    progress_callback=None,
    limit: Optional[int] = None,
) -> tuple[list[ScanResult], int, int, list[str]]:
    """
    Scan every eligible symbol in the database using a process pool.

    Returns the top ``TOP_N_CANDIDATES`` results sorted by composite
    score descending, filtered by ``MIN_SIGNAL_SCORE``.
    """
    # reset cache removed

    # mode validation
    if mode not in SCAN_MODES:
        raise ValueError(
            f"Invalid mode '{mode}'. Must be one of: {SCAN_MODES}"
        )

    # 1.9 Verify ^NSEI is present in ohlcv.db
    nifty_rows = read_ohlcv("^NSEI")
    if not nifty_rows:
        raise RuntimeError(
            "^NSEI not found in ohlcv.db. Add it to symbols.csv and re-run "
            "--mode full to fetch benchmark data."
        )

    # SQLite pre-filtering
    prefilter = get_prefilter_counts()
    eligible_symbols = get_eligible_symbols()

    if limit is not None and limit > 0:
        eligible_symbols = eligible_symbols[:limit]

    # Log pre-filter summary
    skipped = prefilter["total"] - prefilter["eligible"]
    logger.info(
        "Pre-filter: %d total -> %d eligible "
        "(%d removed - %d illiquid, %d stale, %d penny, %d insufficient history)",
        prefilter["total"],
        prefilter["eligible"],
        skipped,
        prefilter["illiquid"],
        prefilter["stale"],
        prefilter["penny"],
        prefilter["short"]
    )

    if not eligible_symbols:
        logger.info("No eligible symbols to scan after pre-filtering.")
        return [], prefilter["total"], 0, []

    # Configure worker counts based on WORKER_COUNT and symbol count
    actual_workers = min(WORKER_COUNT, len(eligible_symbols))
    batch_size = (len(eligible_symbols) + actual_workers - 1) // actual_workers
    cpu_cores = os.cpu_count() or 1

    # 3.3 Startup diagnostic log
    print("\n" + "-" * 49)
    print("-- SwingsterV2 Scan Engine ----------------------")
    print(f"CPU cores available  : {cpu_cores}")
    print(f"Workers to be used   : {actual_workers}")
    print(f"Eligible symbols     : {len(eligible_symbols)}")
    print(f"Batch size per worker: ~{batch_size}")
    print(f"Estimated scan time  : ~8s")
    print("-" * 49 + "\n")
    sys.stdout.flush()

    # 2.6 Batch splitting strategy using round-robin slice
    batches = [eligible_symbols[i::actual_workers] for i in range(actual_workers)]
    batches = [b for b in batches if b]  # Avoid empty batches

    # Pack (batch, mode) tuple for each worker
    worker_args = [(batch, mode) for batch in batches]

    t0 = time.perf_counter()
    results: list[ScanResult] = []
    rejected_rr_list: list[str] = []
    total_eligible = len(eligible_symbols)
    total_scanned = 0
    executor = None

    try:
        with ProcessPoolExecutor(max_workers=actual_workers) as executor_obj:
            executor = executor_obj
            futures = {executor.submit(_scan_batch, args): args for args in worker_args}
            
            for future in as_completed(futures):
                batch_results, batch_count, batch_rejected = future.result()
                results.extend(batch_results)
                rejected_rr_list.extend(batch_rejected)
                total_scanned += batch_count
                # Call callback if provided
                if progress_callback is not None:
                    try:
                        progress_callback(total_scanned, total_eligible, results)
                    except Exception as cb_err:
                        print(f"[WARN] Progress callback error: {cb_err}", file=sys.stderr)
                # 3.6 Update progress log inside scan_all() to include active mode
                print(f"Progress: {total_scanned}/{total_eligible} | {len(results)} {mode} candidates found")
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        if executor is not None:
            executor.shutdown(wait=False, cancel_futures=True)
        raise

    count_pattern = len(results)

    if mode == "ALL":
        min_score = MIN_CANDIDATE_SCORE
        max_pool  = MAX_CANDIDATES
    else:
        cfg = get_pattern_config(mode)
        min_score = cfg.min_candidate_score
        max_pool  = cfg.max_candidates

    # Filter by min_candidate_score
    results = [r for r in results if r.composite_score >= min_score]

    # Sort descending by composite score, then ascending by symbol to guarantee deterministic order
    results.sort(key=lambda r: (-r.composite_score, r.symbol))

    # Cap at max_pool
    results = results[:max_pool]

    elapsed = time.perf_counter() - t0

    # 3.7 Add final summary log after all futures complete (ASCII safe)
    print(f"\nScan complete - mode: {mode} | "
          f"{total_eligible} scanned | "
          f"{count_pattern} matches -> "
          f"top {len(results)} sent to judge")
    sys.stdout.flush()

    logger.info(
        "Scan complete | Scanned: %d | Patterns found: %d | "
        "Candidates: %d | Time: %.1fs",
        total_eligible,
        count_pattern,
        len(results),
        elapsed,
    )

    return results, prefilter["total"], count_pattern, rejected_rr_list

