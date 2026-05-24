## 1. Project Configuration

- [x] 1.1 Rewrite `config.py` — replace NSE/curl_cffi constants with Yahoo Finance URL, fetch periods, semaphore limit, retry settings, symbol filters, scanner weights, and all project paths
- [x] 1.2 Update `requirements.txt` — replace `curl_cffi` with `aiohttp`, add `numpy`, `pandas`, `anthropic`, `streamlit`
- [x] 1.3 Update `.gitignore` — add `data/ohlcv.db`, `data/results.json`, `.env`

## 2. SQLite Persistence Layer (db_writer.py)

- [x] 2.1 Implement `get_connection()` — opens SQLite DB with WAL journal mode
- [x] 2.2 Implement `init_db()` — creates `ohlcv` table with `(symbol, date)` primary key and symbol index (IF NOT EXISTS)
- [x] 2.3 Implement `write_ohlcv()` — batch upsert using `INSERT OR REPLACE` for (symbol, date, O, H, L, C, volume) tuples
- [x] 2.4 Implement `read_ohlcv()` — returns all rows for a symbol ordered by date ascending
- [x] 2.5 Implement `get_all_symbols()` — returns sorted list of distinct symbols
- [x] 2.6 Implement `get_row_count()` and `get_latest_date()` helpers

## 3. Async OHLCV Fetcher (fetch_all.py)

- [x] 3.1 Add `asyncio.WindowsSelectorEventLoopPolicy()` for Windows compatibility
- [x] 3.2 Implement `load_symbols()` — reads `symbols.csv`, filters to EQ/BE series, appends `.NS` suffix
- [x] 3.3 Implement `_parse_chart_json()` — parses Yahoo Finance v8 JSON response into OHLCV row tuples, applies min price filter, skips None values
- [x] 3.4 Implement `fetch_one()` — downloads single ticker with retry + exponential backoff on 429 and timeout errors
- [x] 3.5 Implement `fetch_all()` — orchestrates concurrent fetch for all tickers using `asyncio.Semaphore(40)` and `aiohttp.ClientSession` with `TCPConnector(ssl=False)`
- [x] 3.6 Implement CLI with `--mode full` (1y) and `--mode delta` (5d) via argparse

## 4. Integration & Verification

- [x] 4.1 Verify all modules import cleanly (`config`, `fetcher.db_writer`, `fetcher.fetch_all`)
- [x] 4.2 Verify `load_symbols()` correctly filters and returns 2,337 tickers
- [x] 4.3 Verify `python -m fetcher.fetch_all --mode full` runs end-to-end (pending full network run)
