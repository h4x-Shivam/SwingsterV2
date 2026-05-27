"""
fetch_all.py — Async OHLCV fetcher using aiohttp + Yahoo Finance chart API.

This module:
  1. Reads data/symbols.csv and filters to VALID_SERIES, appends .NS suffix.
  2. Hits the Yahoo Finance v8 chart endpoint for each ticker concurrently.
  3. Parses the JSON response into (symbol, date, O, H, L, C, volume) rows.
  4. Writes everything to SQLite via db_writer.write_ohlcv().

Two modes:
  --mode full   → downloads 1 year of daily data (first-time bootstrap)
  --mode delta  → downloads last 5 days (nightly refresh, INSERT OR REPLACE)

Usage:
    python -m fetcher.fetch_all --mode full
    python -m fetcher.fetch_all --mode delta
"""

import argparse
import asyncio
import csv
import logging
import sys
import time
from datetime import datetime, timezone

import aiohttp

from config import (
    DB_PATH,
    FETCH_DELTA_PERIOD,
    FETCH_INTERVAL,
    FETCH_PERIOD,
    MIN_PRICE,
    RETRY_ATTEMPTS,
    RETRY_DELAY,
    SEMAPHORE_LIMIT,
    SYMBOLS_CSV,
    USER_AGENT,
    VALID_SERIES,
    YAHOO_CHART_URL,
    YAHOO_SUFFIX,
)
from fetcher.db_writer import init_db, write_ohlcv

# ---------------------------------------------------------------------------
# Windows asyncio fix
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fetcher")


# ---------------------------------------------------------------------------
# Symbol loading
# ---------------------------------------------------------------------------

def load_symbols() -> list[str]:
    """
    Read symbols.csv, keep rows where SERIES is in VALID_SERIES,
    and return a list of Yahoo Finance tickers (e.g. 'RELIANCE.NS').
    """
    tickers: list[str] = []
    with open(SYMBOLS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            series = row.get("SERIES", "").strip()
            symbol = row.get("SYMBOL", "").strip()
            if series in VALID_SERIES and symbol:
                tickers.append(symbol + YAHOO_SUFFIX)
    # Always ensure ^NSEI is included for benchmark data
    tickers.append("^NSEI")
    log.info("Loaded %d tickers from symbols.csv (filtered to %s) + ^NSEI", len(tickers), VALID_SERIES)
    return tickers


# ---------------------------------------------------------------------------
# Single-ticker fetch + parse
# ---------------------------------------------------------------------------

def _parse_chart_json(ticker: str, data: dict) -> list[tuple[str, str, float, float, float, float, int]]:
    """
    Parse Yahoo Finance v8 chart JSON into a list of OHLCV row tuples.

    Each tuple is (symbol, date_str, open, high, low, close, volume).
    Rows with close < MIN_PRICE are silently dropped.
    Returns an empty list if the JSON structure is unexpected.
    """
    try:
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]

        opens = quote["open"]
        highs = quote["high"]
        lows = quote["low"]
        closes = quote["close"]
        volumes = quote["volume"]
    except (KeyError, IndexError, TypeError):
        return []

    # Strip the .NS suffix for storage
    symbol = ticker.replace(YAHOO_SUFFIX, "")
    rows: list[tuple[str, str, float, float, float, float, int]] = []

    for i, ts in enumerate(timestamps):
        o = opens[i]
        h = highs[i]
        l = lows[i]   # noqa: E741
        c = closes[i]
        v = volumes[i]

        # Skip rows with None values (market holidays / missing data)
        if any(val is None for val in (o, h, l, c, v)):
            continue

        # Min price filter
        if c < MIN_PRICE:
            continue

        date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        rows.append((symbol, date_str, float(o), float(h), float(l), float(c), int(v)))

    return rows


async def fetch_one(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    ticker: str,
    period: str,
) -> list[tuple[str, str, float, float, float, float, int]]:
    """
    Download OHLCV data for a single ticker with retry + exponential backoff.

    Returns parsed row tuples, or an empty list on failure (logged, never crashes).
    """
    url = YAHOO_CHART_URL.format(ticker=ticker)
    params = {"interval": FETCH_INTERVAL, "range": period}

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            async with semaphore:
                async with session.get(url, params=params) as resp:
                    if resp.status == 429:
                        # Rate-limited — back off and retry
                        wait = RETRY_DELAY * (2 ** (attempt - 1))
                        log.warning("%s  429 rate-limited, retrying in %ds (attempt %d/%d)",
                                    ticker, wait, attempt, RETRY_ATTEMPTS)
                        await asyncio.sleep(wait)
                        continue

                    if resp.status != 200:
                        log.warning("%s  HTTP %d (attempt %d/%d)",
                                    ticker, resp.status, attempt, RETRY_ATTEMPTS)
                        await asyncio.sleep(RETRY_DELAY * attempt)
                        continue

                    data = await resp.json()
                    rows = _parse_chart_json(ticker, data)
                    return rows

        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            wait = RETRY_DELAY * (2 ** (attempt - 1))
            log.warning("%s  %s, retrying in %ds (attempt %d/%d)",
                        ticker, type(exc).__name__, wait, attempt, RETRY_ATTEMPTS)
            await asyncio.sleep(wait)

    log.error("%s  FAILED after %d attempts — skipping", ticker, RETRY_ATTEMPTS)
    return []


# ---------------------------------------------------------------------------
# Batch fetch orchestrator
# ---------------------------------------------------------------------------

async def fetch_all(tickers: list[str], period: str) -> int:
    """
    Fetch OHLCV data for all tickers concurrently and write to SQLite.

    Uses asyncio.Semaphore to cap concurrency at SEMAPHORE_LIMIT.
    Returns the total number of OHLCV rows written.
    """
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    connector = aiohttp.TCPConnector(ssl=False)
    headers = {"User-Agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=30)

    total_rows = 0
    success_count = 0
    fail_count = 0

    async with aiohttp.ClientSession(connector=connector, headers=headers, timeout=timeout) as session:
        tasks = [fetch_one(session, semaphore, t, period) for t in tickers]

        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            rows = await coro
            if rows:
                written = write_ohlcv(rows)
                total_rows += written
                success_count += 1
            else:
                fail_count += 1

            # Progress log every 100 tickers
            if i % 100 == 0 or i == len(tickers):
                log.info("Progress: %d/%d tickers processed  (%d rows so far)",
                         i, len(tickers), total_rows)

    log.info("Fetch complete — %d success, %d failed, %d total rows written",
             success_count, fail_count, total_rows)
    return total_rows


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse CLI args and run the async fetcher."""
    parser = argparse.ArgumentParser(description="SwingsterV2 OHLCV Fetcher")
    parser.add_argument(
        "--mode",
        choices=["full", "delta"],
        default="full",
        help="'full' = 1 year of data (bootstrap), 'delta' = last 5 days (refresh)",
    )
    args = parser.parse_args()

    period = FETCH_PERIOD if args.mode == "full" else FETCH_DELTA_PERIOD

    print("=" * 60)
    print("  SwingsterV2 — OHLCV Fetcher")
    print("=" * 60)
    print(f"  Mode:       {args.mode}")
    print(f"  Period:     {period}")
    print(f"  Interval:   {FETCH_INTERVAL}")
    print(f"  Concurrency: {SEMAPHORE_LIMIT}")
    print(f"  Database:   {DB_PATH}")
    print("=" * 60)

    # Ensure DB + table exist
    init_db()

    # Load tickers
    tickers = load_symbols()
    if not tickers:
        log.error("No tickers loaded — check %s", SYMBOLS_CSV)
        sys.exit(1)

    # Run the async fetch
    t0 = time.perf_counter()
    total = asyncio.run(fetch_all(tickers, period))
    elapsed = time.perf_counter() - t0

    print()
    print(f"  Done! {total:,} rows written in {elapsed:.1f}s")
    print(f"  Database: {DB_PATH}")


if __name__ == "__main__":
    main()
