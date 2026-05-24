## ADDED Requirements

### Requirement: Load and filter symbols from CSV
The system SHALL read `data/symbols.csv`, filter rows to only those with SERIES in `{"EQ", "BE"}`, and append the `.NS` suffix to produce Yahoo Finance-compatible ticker strings.

#### Scenario: Valid symbols.csv with mixed series
- **WHEN** `data/symbols.csv` contains rows with SERIES values EQ, BE, BZ, and others
- **THEN** the system SHALL return only tickers where SERIES is EQ or BE, each with `.NS` appended (e.g., `RELIANCE.NS`)

#### Scenario: Empty or missing symbols.csv
- **WHEN** `data/symbols.csv` does not exist or contains no data rows
- **THEN** the system SHALL log an error and exit without attempting any network requests

### Requirement: Fetch OHLCV data from Yahoo Finance v8 chart API
The system SHALL download daily OHLCV data from `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}` using aiohttp with async concurrency.

#### Scenario: Successful fetch for a single ticker
- **WHEN** the Yahoo Finance API returns HTTP 200 with valid JSON for a ticker
- **THEN** the system SHALL parse the response into (symbol, date, open, high, low, close, volume) tuples and pass them to the database writer

#### Scenario: Ticker returns HTTP 429 (rate limited)
- **WHEN** the API returns HTTP 429 for a ticker
- **THEN** the system SHALL retry with exponential backoff (base delay × 2^attempt) up to the configured maximum retry attempts

#### Scenario: Network timeout or connection error
- **WHEN** a request times out or fails with a connection error
- **THEN** the system SHALL retry with exponential backoff, and after exhausting retries, log the failure and skip the ticker without crashing

#### Scenario: Ticker has no data or invalid JSON
- **WHEN** the API returns 200 but the JSON lacks expected fields (chart.result[0].timestamp, indicators.quote)
- **THEN** the system SHALL return an empty result for that ticker and log a warning

### Requirement: Concurrent fetching with semaphore
The system SHALL use `asyncio.Semaphore` with a configurable limit (default 40) to cap the number of in-flight HTTP requests.

#### Scenario: All tickers fetched concurrently within semaphore limit
- **WHEN** 2,300+ tickers are submitted for fetching
- **THEN** no more than the configured semaphore limit of requests SHALL be active simultaneously

### Requirement: Full and delta fetch modes
The system SHALL support two fetch modes controlled by a `--mode` CLI argument.

#### Scenario: Full fetch mode
- **WHEN** the script is run with `--mode full`
- **THEN** the system SHALL request 1 year of daily data (range=1y) for every ticker

#### Scenario: Delta fetch mode
- **WHEN** the script is run with `--mode delta`
- **THEN** the system SHALL request 5 days of daily data (range=5d) for every ticker, using INSERT OR REPLACE to avoid duplicates

### Requirement: Minimum price filter
The system SHALL skip OHLCV rows where the close price is below the configured minimum price threshold (default ₹20).

#### Scenario: Close price below threshold
- **WHEN** a candle has a close price of ₹15
- **THEN** that row SHALL be excluded from the database write

### Requirement: Windows compatibility
The system SHALL set `asyncio.WindowsSelectorEventLoopPolicy()` on Windows platforms and use `TCPConnector(ssl=False)` to avoid event loop and SSL errors.

#### Scenario: Running on Windows
- **WHEN** the script runs on a Windows system
- **THEN** the system SHALL use the Selector event loop policy and disable SSL verification on the TCP connector
