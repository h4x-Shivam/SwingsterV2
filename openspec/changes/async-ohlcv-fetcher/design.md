## Context

SwingsterV2 is a multi-agent NSE stock screener. Phase 1 delivered `data/symbols.csv` with 2,364 NSE equity tickers. Phase 2 needs to fetch 1 year of daily OHLCV data for all tickers and store it locally so the scanner pipeline (Phase 3) can run pattern detection without repeated network calls.

The Yahoo Finance v8 chart API provides free, unauthenticated OHLCV data via JSON. NSE's own historical data APIs require complex authentication. Yahoo Finance is the standard choice for Indian market retail tools.

## Goals / Non-Goals

**Goals:**
- Download daily OHLCV data for ~2,300 NSE tickers from Yahoo Finance in under 5 minutes.
- Store data in a local SQLite database optimized for per-symbol reads by scanner threads.
- Support two modes: full bootstrap (1 year) and delta refresh (5 days) for nightly updates.
- Handle failures gracefully — skip broken tickers, never crash the whole run.
- Run on Windows without event loop issues.

**Non-Goals:**
- Real-time or intraday data — daily candles only.
- Historical data beyond 1 year — not needed for swing patterns.
- Using yfinance, curl_cffi, or requests — aiohttp only, for async performance.
- Building a REST API around the data — it's consumed directly by scanner threads.

## Decisions

### 1. HTTP client: aiohttp (not yfinance, not requests)
**Rationale:** We need to fetch ~2,300 tickers concurrently. `aiohttp` with `asyncio.Semaphore(40)` saturates the network without thread overhead. `yfinance` is synchronous and adds unnecessary abstraction. `requests` would require thread pools.
**Alternatives considered:**
- `yfinance` — synchronous, 10x slower for 2,300 tickers, frequent breaking changes.
- `httpx` async — viable but `aiohttp` has better Windows support and is more battle-tested for high concurrency.

### 2. Data source: Yahoo Finance v8 chart API
**Rationale:** The endpoint `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}` returns JSON with timestamps + OHLCV arrays. It's unauthenticated, free, and has been stable for years. NSE tickers use the `.NS` suffix (e.g., `RELIANCE.NS`).
**Alternatives considered:**
- NSE APIs directly — require complex cookie/session handling, rate limits are aggressive, and historical data endpoints are poorly documented.
- Alpha Vantage — free tier limited to 25 requests/day, unusable for 2,300 tickers.

### 3. Storage: SQLite with WAL mode
**Rationale:** A single `ohlcv.db` file keeps deployment simple (no database server). WAL journal mode allows the 5 scanner threads to read concurrently while the fetcher writes. The `(symbol, date)` primary key enables `INSERT OR REPLACE` for idempotent delta fetches.
**Alternatives considered:**
- CSV files per symbol — 2,300 files, slow directory listing, no query capability.
- PostgreSQL — overkill for a single-user desktop tool.

### 4. Concurrency: asyncio.Semaphore(40)
**Rationale:** Windows TCP stack handles ~40 concurrent connections reliably. Higher values cause `ConnectionResetError` on some networks. The semaphore caps in-flight requests without dropping throughput.

### 5. Windows compatibility: WindowsSelectorEventLoopPolicy
**Rationale:** Python's default `ProactorEventLoop` on Windows has known issues with `aiohttp` and SSL. Setting `WindowsSelectorEventLoopPolicy()` at module level avoids `RuntimeError` on Windows. Also using `TCPConnector(ssl=False)` since Yahoo Finance's data API doesn't require strict SSL validation.

### 6. Retry strategy: Exponential backoff, 3 attempts
**Rationale:** Yahoo Finance occasionally returns 429 (rate limit) or times out under load. Exponential backoff (2s, 4s, 8s) absorbs transient failures. After 3 attempts, the ticker is skipped and logged — never crashes the batch.

## Risks / Trade-offs

- **Yahoo Finance may change the v8 API** → Mitigation: The endpoint has been stable since 2020. If it breaks, we only need to update the URL/parsing in `fetch_all.py`. The SQLite schema is API-agnostic.
- **Rate limiting at scale** → Mitigation: Semaphore capped at 40, exponential backoff on 429. Typical full fetch completes in 3-5 minutes.
- **SSL=False is less secure** → Mitigation: We're reading public market data, not sending credentials. The trade-off is acceptable for Windows compatibility.
- **SQLite write contention** → Mitigation: Only the fetcher writes. Scanner threads only read. WAL mode handles this correctly.
- **Large database size** → Mitigation: ~2,300 symbols × 250 trading days × ~50 bytes/row ≈ 30MB. Well within SQLite's comfort zone.
