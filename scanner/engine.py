"""
engine.py — Scan engine orchestrator for SwingsterV2.

Multi-stage funnel pipeline per symbol:
  OHLCV → Candles → Stage 2 filter → Liquidity filter → Pattern detection
  → RS Rank → Risk/Reward → Composite Scoring → ScanResult

Batch scanning via ThreadPoolExecutor with NUM_AGENTS workers.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from config import (
    NUM_AGENTS,
    MIN_SIGNAL_SCORE,
    TOP_N_CANDIDATES,
    STAGE2_MIN_SCORE,
)
from fetcher.db_writer import read_ohlcv, get_all_symbols

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

def scan_symbol(symbol: str) -> Optional[ScanResult]:
    """
    Run the full analysis pipeline for a single symbol.

    Returns ``None`` at any stage that fails its gate condition:
      • No data / too few candles
      • Stage 2 score < 60
      • Illiquid (avg volume < 50k)
      • No chart pattern detected
    """
    # 1. Read OHLCV from DB
    rows = read_ohlcv(symbol)
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
    signal = detect_patterns(candles)
    if signal is None:
        return None

    # 6. RS rank vs Nifty 50
    nifty = _load_nifty_candles()
    rs = compute_rs(candles, nifty)

    # 7. Risk-reward
    rr = compute_risk_reward(candles)

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
    )


# ---------------------------------------------------------------------------
# Batch scan
# ---------------------------------------------------------------------------

def scan_all() -> list[ScanResult]:
    """
    Scan every symbol in the database using a thread pool.

    Returns the top ``TOP_N_CANDIDATES`` results sorted by composite
    score descending, filtered by ``MIN_SIGNAL_SCORE``.
    """
    global _nifty_candles
    _nifty_candles = None  # reset cache for fresh data each run

    symbols = get_all_symbols()
    total = len(symbols)
    logger.info("Starting scan of %d symbols with %d workers", total, NUM_AGENTS)

    t0 = time.perf_counter()

    results: list[ScanResult] = []
    errors = 0
    count_stage2 = 0
    count_liquid = 0
    count_pattern = 0
    processed = 0

    def _scan_one(sym: str) -> Optional[ScanResult]:
        """Wrapper with per-symbol error handling."""
        try:
            return scan_symbol(sym)
        except Exception:
            logger.warning("Error scanning %s", sym, exc_info=True)
            return None

    with ThreadPoolExecutor(max_workers=NUM_AGENTS) as executor:
        futures = {executor.submit(_scan_one, sym): sym for sym in symbols}

        for future in as_completed(futures):
            processed += 1

            # Progress logging every 100 symbols
            if processed % 100 == 0:
                elapsed = time.perf_counter() - t0
                logger.info(
                    "Progress: %d/%d (%.1fs elapsed)", processed, total, elapsed
                )

            result = future.result()
            if result is not None:
                results.append(result)

    # Funnel counts — for accurate counts we re-scan the results
    # (the per-symbol scan already did the filtering, so results
    #  are the ones that passed ALL gates)
    count_pattern = len(results)

    # Filter by MIN_SIGNAL_SCORE
    results = [r for r in results if r.composite_score >= MIN_SIGNAL_SCORE]

    # Sort descending by composite score
    results.sort(key=lambda r: r.composite_score, reverse=True)

    # Cap at TOP_N_CANDIDATES
    results = results[:TOP_N_CANDIDATES]

    elapsed = time.perf_counter() - t0

    logger.info(
        "Scan complete | Scanned: %d | Patterns found: %d | "
        "Candidates (score>=%d): %d | Time: %.1fs",
        total,
        count_pattern,
        MIN_SIGNAL_SCORE,
        len(results),
        elapsed,
    )

    return results
