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
    MIN_SIGNAL_SCORE,
    TOP_N_CANDIDATES,
    STAGE2_MIN_SCORE,
    WORKER_COUNT,
    SCAN_MODES,
    SCAN_MODE,
)
from fetcher.db_writer import (
    read_ohlcv,
    get_eligible_symbols,
    get_prefilter_counts,
    get_connection,
)

from scanner.models import Candle, ScanResult, rows_to_candles
from scanner.trend import analyze_trend
from scanner.volume import analyze_volume
from scanner.patterns import detect_patterns
from scanner.rs_rank import compute_rs
from scanner.risk_reward import compute_risk_reward
from scanner.scoring import compute_composite_score


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache: Nifty 50 candles (loaded once per scan_all run)
# ---------------------------------------------------------------------------
_nifty_candles: Optional[list[Candle]] = None


def _load_nifty_candles() -> list[Candle]:
    """Load ^NSEI OHLCV data for RS rank comparison."""
    global _nifty_candles
    if _nifty_candles is None:
        rows = read_ohlcv("^NSEI")
        _nifty_candles = rows_to_candles(rows) if rows else []
    return _nifty_candles


# ---------------------------------------------------------------------------
# Single-symbol scan
# ---------------------------------------------------------------------------

def scan_symbol(
    symbol: str,
    conn: Optional[sqlite3.Connection] = None,
    nifty_candles: Optional[list[Candle]] = None,
    mode: str = "ALL",
) -> Optional[ScanResult]:
    """
    Run the full analysis pipeline for a single symbol.

    Returns ``None`` at any stage that fails its gate condition:
      • No data / too few candles
      • Stage 2 score < 60
      • Illiquid (avg volume < 50k)
      • No chart pattern detected
    """
    # 1. Read OHLCV from DB
    rows = read_ohlcv(symbol, conn=conn)
    if not rows:
        return None

    # 2. Convert to Candles
    candles = rows_to_candles(rows)
    if len(candles) < 30:
        return None

    # 3. Stage 2 trend filter — skip if score < 60
    trend = analyze_trend(candles)
    if trend.stage2_score < STAGE2_MIN_SCORE:
        return None

    # 4. Volume analysis — skip if illiquid
    vol = analyze_volume(candles)
    if vol.is_illiquid:
        return None

    # 5. Pattern detection — skip if None
    signal = detect_patterns(candles, mode=mode)
    if signal is None:
        return None

    # 6. RS rank vs Nifty 50
    nifty = nifty_candles if nifty_candles is not None else _load_nifty_candles()
    rs = compute_rs(candles, nifty)

    # 7. Risk-reward — anchored to the pattern's buy_point
    rr = compute_risk_reward(candles, buy_point=signal.buy_point)

    # Gate: reject setups where risk-reward is invalid
    #   (stop_loss above entry, or no upside after accounting for entry)
    if rr.stop_loss >= signal.buy_point or rr.ratio <= 0:
        return None

    # 8. Composite score
    composite = compute_composite_score(
        signal_strength=signal.strength,
        volume_score=vol.volume_score,
        rr_score=rr.score,
        stage2_score=trend.stage2_score,
        rs_score=rs.rs_score,
        is_stage2=trend.is_stage2,
    )

    return ScanResult(
        symbol=symbol,
        pattern=signal.name,
        signal_strength=signal.strength,
        volume_score=vol.volume_score,
        rr_score=rr.score,
        stage2_score=trend.stage2_score,
        rs_score=rs.rs_score,
        composite_score=composite,
        buy_point=signal.buy_point,
        stop_loss=rr.stop_loss,
        target=rr.target,
        rr_ratio=rr.ratio,
        current_price=candles[-1].close,
        distance_from_buy_pct=signal.distance_from_buy_pct,
        scan_mode=mode,
    )


# ---------------------------------------------------------------------------
# Top-level Batch Scan Process Worker
# ---------------------------------------------------------------------------

def _scan_batch(args: tuple) -> tuple[list[ScanResult], int]:
    """
    Worker entry point for processing a batch of symbols.
    Opens its own SQLite connection, pre-loads nifty candles, and scans symbols.
    """
    batch, mode = args
    conn = get_connection()
    try:
        nifty_rows = read_ohlcv("^NSEI", conn=conn)
        nifty_candles = rows_to_candles(nifty_rows) if nifty_rows else []
        
        results = []
        scanned_count = 0
        for symbol in batch:
            try:
                res = scan_symbol(symbol, conn=conn, nifty_candles=nifty_candles, mode=mode)
                if res is not None:
                    results.append(res)
            except Exception as e:
                print(f"[WARN] {symbol}: {e}", file=sys.stderr)
            finally:
                scanned_count += 1
        return results, scanned_count
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Batch scan
# ---------------------------------------------------------------------------

def scan_all(mode: str = SCAN_MODE) -> list[ScanResult]:
    """
    Scan every eligible symbol in the database using a process pool.

    Returns the top ``TOP_N_CANDIDATES`` results sorted by composite
    score descending, filtered by ``MIN_SIGNAL_SCORE``.
    """
    global _nifty_candles
    _nifty_candles = None  # reset cache for fresh data each run

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
        return []

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
    total_eligible = len(eligible_symbols)
    total_scanned = 0
    executor = None

    try:
        with ProcessPoolExecutor(max_workers=actual_workers) as executor_obj:
            executor = executor_obj
            futures = {executor.submit(_scan_batch, args): args for args in worker_args}
            
            for future in as_completed(futures):
                batch_results, batch_count = future.result()
                results.extend(batch_results)
                total_scanned += batch_count
                # 3.6 Update progress log inside scan_all() to include active mode
                print(f"Progress: {total_scanned}/{total_eligible} | {len(results)} {mode} candidates found")
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        if executor is not None:
            executor.shutdown(wait=False, cancel_futures=True)
        raise

    count_pattern = len(results)

    # Filter by MIN_SIGNAL_SCORE
    results = [r for r in results if r.composite_score >= MIN_SIGNAL_SCORE]

    # Sort descending by composite score, then ascending by symbol to guarantee deterministic order
    results.sort(key=lambda r: (-r.composite_score, r.symbol))

    # Cap at TOP_N_CANDIDATES
    results = results[:TOP_N_CANDIDATES]

    elapsed = time.perf_counter() - t0

    # 3.7 Add final summary log after all futures complete (ASCII safe)
    print(f"\nScan complete - mode: {mode} | "
          f"{total_eligible} scanned | "
          f"{count_pattern} matches -> "
          f"top {len(results)} sent to judge")
    sys.stdout.flush()

    logger.info(
        "Scan complete | Scanned: %d | Patterns found: %d | "
        "Candidates (score>=%d): %d | Time: %.1fs",
        total_eligible,
        count_pattern,
        MIN_SIGNAL_SCORE,
        len(results),
        elapsed,
    )

    return results

