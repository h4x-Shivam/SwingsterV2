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
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional

from config import (
    NUM_AGENTS,
    WORKER_COUNT,
    SCAN_MODES,
    DEFAULT_SCAN_MODE,
    MIN_CANDIDATE_SCORE,
    MAX_CANDIDATES,
)
from fetcher.db_writer import (
    read_ohlcv,
    read_ohlcv_batch,
    get_eligible_symbols,
    get_prefilter_counts,
)

from scanner.models import Candle, ScanResult, rows_to_candles
from scanner.trend import analyze_trend
from scanner.volume import analyze_volume
from scanner.patterns.registry import get_patterns, PATTERN_REGISTRY, get_pattern_config
from scanner.patterns.pivots   import find_swing_pivots
from scanner.rs_rank import compute_rs
from scanner.risk_reward import compute_risk_reward


from log import get_logger

logger = get_logger(__name__)

class RejectedRRError(Exception):
    pass

# No global cache needed, handled per-worker


# ---------------------------------------------------------------------------
# Single-symbol scan
# ---------------------------------------------------------------------------

def scan_symbol(
    symbol: str,
    conn=None,
    nifty_candles: Optional[list[Candle]] = None,
    mode: str = DEFAULT_SCAN_MODE,
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

    # Filter by minimum candle requirement (from each pattern's config)
    active_patterns = [
        p for p in active_patterns
        if len(candles) >= p.config.min_candles
    ]
    
    if not active_patterns:
        return None

    trend = analyze_trend(candles)
    
    # Filter by Stage 2 minimum score (from each pattern's config)
    active_patterns = [
        p for p in active_patterns
        if trend.stage2_score >= p.config.stage2_min_score
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

    # Pivot lookback — use the widest window needed across active patterns
    max_lookback = max(p.config.pivot_lookback for p in active_patterns)
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
    Uses pre-fetched OHLCV data provided by the parent process.
    """
    batch, mode, batch_data, nifty_candles = args
    
    results = []
    rejected_rr = []
    scanned_count = 0
    for symbol in batch:
        try:
            rows = batch_data.get(symbol, [])
            res = scan_symbol(symbol, conn=None, nifty_candles=nifty_candles, mode=mode, preloaded_rows=rows)
            if res is not None:
                results.append(res)
        except RejectedRRError:
            rejected_rr.append(symbol)
        except Exception as e:
            print(f"[WARN] {symbol}: {e}", file=sys.stderr)
        finally:
            scanned_count += 1
    return results, scanned_count, rejected_rr


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
    logger.info("Scan Engine starting")
    logger.info("CPU cores: %d | Workers: %d | Eligible: %d | Batch size: ~%d",
                cpu_cores, actual_workers, len(eligible_symbols), batch_size)
    logger.info("Data source: Remote PostgreSQL (Sequential)")

    # Pre-fetch Nifty candles
    nifty_candles = rows_to_candles(nifty_rows) if nifty_rows else []

    # Fetch ALL data in the parent process
    t_fetch_start = time.perf_counter()
    logger.info("Fetching OHLCV data for eligible symbols from PostgreSQL...")
    all_batch_data = read_ohlcv_batch(eligible_symbols)
    logger.info("Data fetch complete in %.1fs", time.perf_counter() - t_fetch_start)

    # 2.6 Batch splitting strategy using round-robin slice
    batches = [eligible_symbols[i::actual_workers] for i in range(actual_workers)]
    batches = [b for b in batches if b]  # Avoid empty batches

    # Pack (batch, mode, batch_data_subset, nifty_candles) tuple for each worker
    worker_args = []
    for batch in batches:
        # Extract only the data needed for this batch to minimize pickling size
        subset_data = {sym: all_batch_data.get(sym, []) for sym in batch}
        worker_args.append((batch, mode, subset_data, nifty_candles))

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
                        logger.warning("Progress callback error: %s", cb_err)
                logger.info("Progress: %d/%d | %d %s candidates found",
                            total_scanned, total_eligible, len(results), mode)
    except KeyboardInterrupt:
        logger.warning("Scan interrupted by user.")
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

    logger.info(
        "Scan complete | mode: %s | Scanned: %d | Patterns found: %d | "
        "Candidates: %d | Time: %.1fs",
        mode, total_eligible, count_pattern, len(results), elapsed,
    )

    return results, prefilter["total"], count_pattern, rejected_rr_list

