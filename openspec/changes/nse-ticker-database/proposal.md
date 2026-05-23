## Why

SwingsterV2 needs a reliable, up-to-date database of all equity tickers listed on the National Stock Exchange (NSE) of India. Currently the `data/symbols.csv` file is empty, meaning no ticker data is available for any downstream features (screening, charting, analysis). By downloading the official `EQUITY_L.csv` from the NSE archives, we get an authoritative master list of all listed equities — symbols, company names, ISIN codes, series, and listing dates — directly from the exchange.

## What Changes

- **Add a script/module** that downloads `EQUITY_L.csv` from `https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv` with proper browser-like headers (User-Agent, cookies) to satisfy NSE's anti-bot requirements.
- **Parse and normalize** the downloaded CSV into the project's `data/symbols.csv` format — keeping the columns relevant to SwingsterV2 (symbol, company name, series, ISIN, listing date).
- **Persist the ticker database** to `data/symbols.csv` so it can be consumed by the rest of the application.
- **Support re-running** the script to refresh the ticker database with the latest listings from NSE at any time.

## Capabilities

### New Capabilities
- `nse-ticker-fetch`: Downloading the official EQUITY_L.csv from NSE archives with proper HTTP session handling (User-Agent headers, cookies).
- `ticker-database-persist`: Parsing, normalizing, and saving the fetched ticker data into the project's `data/symbols.csv` file.

### Modified Capabilities
_(none — this is the first feature in the project)_

## Impact

- **New file**: A script/module to fetch and process the NSE equity CSV.
- **Modified file**: `data/symbols.csv` — will be populated with ticker data instead of being empty.
- **External dependency**: Requires network access to `nsearchives.nseindia.com` at runtime.
- **Library dependencies**: HTTP client with session/cookie support (e.g., Python `requests` or Node `fetch`/`axios`).
