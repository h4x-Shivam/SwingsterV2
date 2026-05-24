## Why

SwingsterV2's screener pipeline requires 1 year of daily OHLCV data for all 2,300+ NSE equities. Phase 1 populated `data/symbols.csv` with the ticker master list. Now we need a high-performance fetcher that downloads historical price data from Yahoo Finance and persists it to a local SQLite database — the foundation for the pattern detection scanner.

## What Changes

- **New module `fetcher/fetch_all.py`**: Async aiohttp fetcher hitting the Yahoo Finance v8 chart API directly (no yfinance, no curl_cffi). Supports `--mode full` (1y bootstrap) and `--mode delta` (5d nightly refresh). Uses `asyncio.Semaphore(40)` for concurrency, retry with exponential backoff, and Windows-compatible event loop policy.
- **New module `fetcher/db_writer.py`**: SQLite persistence layer using Python's built-in `sqlite3`. Single `ohlcv` table with `(symbol, date)` primary key. WAL journal mode for concurrent read safety. `INSERT OR REPLACE` for idempotent upserts.
- **Rewritten `config.py`**: Replaced old NSE/curl_cffi constants with the full project configuration — Yahoo Finance URL, fetch periods, semaphore limits, retry settings, symbol filters, scanner weights, and all paths.
- **Updated `requirements.txt`**: Replaced `curl_cffi` with `aiohttp`, added `numpy`, `pandas`, `anthropic`, `streamlit` for the full pipeline.
- **Updated `.gitignore`**: Added `data/ohlcv.db`, `data/results.json`, `.env`.

## Capabilities

### New Capabilities
- `ohlcv-async-fetch`: Async concurrent fetching of daily OHLCV data from Yahoo Finance v8 chart API for all NSE tickers, with retry logic and rate-limit handling.
- `ohlcv-sqlite-storage`: SQLite-based storage for OHLCV data with WAL mode, upsert semantics, and read helpers for downstream consumers (scanner threads).

### Modified Capabilities
_(none — openspec/specs/ is empty, no existing specs to modify)_

## Impact

- **New files**: `fetcher/fetch_all.py`, `fetcher/db_writer.py`
- **Rewritten files**: `config.py`, `requirements.txt`
- **Modified files**: `.gitignore`
- **New runtime artifact**: `data/ohlcv.db` (SQLite database, ~50-100MB when populated)
- **External dependency**: Requires network access to `query1.finance.yahoo.com`
- **Library dependency**: `aiohttp>=3.9.0` (replaces `curl_cffi`)
