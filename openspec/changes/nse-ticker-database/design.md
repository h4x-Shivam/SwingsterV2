## Context

SwingsterV2 is a trading/screening application that needs a master list of NSE equity tickers. Currently `data/symbols.csv` is empty. The National Stock Exchange of India publishes an official CSV of all listed equities at `https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv`. This file contains columns such as SYMBOL, NAME OF COMPANY, SERIES, DATE OF LISTING, PAID UP VALUE, MARKET LOT, ISIN NUMBER, and FACE VALUE.

NSE's website has anti-bot protections — direct programmatic requests without proper headers and session cookies are rejected (HTTP 403). A working solution must mimic a browser session.

## Goals / Non-Goals

**Goals:**
- Download the official `EQUITY_L.csv` from NSE archives reliably.
- Handle NSE's anti-bot protections (User-Agent header, session cookie via initial page visit).
- Parse the CSV and write a clean, normalized `data/symbols.csv` with relevant columns.
- Make the script re-runnable so the ticker database can be refreshed at any time.

**Non-Goals:**
- Real-time or scheduled auto-refresh — this is a manual on-demand tool for now.
- Downloading historical price data, derivatives, or indices — only the equity master list.
- Building a UI around the download — it is a script/CLI tool only.
- Handling ETFs, SME, debt, or other non-equity segments.

## Decisions

### 1. Language: Python
**Rationale:** Python's `requests` library with `Session` objects makes it straightforward to handle cookies and custom headers. The `csv` module (stdlib) handles CSV parsing. Python is widely available and commonly used for financial data scripts in the Indian market ecosystem.
**Alternatives considered:**
- Node.js with `axios` — viable but heavier setup for a simple data-fetch script.
- `curl`/shell script — fragile for CSV parsing and cookie handling.

### 2. HTTP session approach: Two-step request
**Rationale:** NSE sets required cookies when you first visit their main site. The approach is:
1. `GET https://www.nseindia.com` with a browser User-Agent → captures session cookies.
2. `GET https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv` with the same session → returns the CSV.
This mimics browser behavior and satisfies their bot-detection.
**Alternatives considered:**
- Selenium/headless browser — works but massive overkill for downloading a single CSV.

### 3. Output format: Retain all columns from EQUITY_L.csv
**Rationale:** The source CSV is already well-structured. Rather than dropping columns prematurely, we retain all of them in `data/symbols.csv` so downstream features can use any field they need (ISIN for demat matching, SERIES for filtering EQ vs BE, etc.).
**Alternatives considered:**
- Stripping to only SYMBOL + NAME — too limiting for future use cases.

### 4. Script location: `scripts/fetch_nse_tickers.py`
**Rationale:** A dedicated `scripts/` directory keeps utility scripts separate from application code. The name clearly communicates what the script does.

## Risks / Trade-offs

- **NSE may change their anti-bot strategy** → Mitigation: The two-step session approach is well-documented and widely used. If NSE changes, we only need to update headers or add a retry. The script is isolated so changes are contained.
- **NSE may change the CSV URL or format** → Mitigation: The URL has been stable for years. Column parsing uses header names (not positional indices), so minor column additions won't break anything.
- **Rate limiting / IP blocking** → Mitigation: The script is run manually and makes only 2 requests. This is negligible traffic. No mitigation needed beyond standard retry logic.
- **Network dependency** → Mitigation: The script clearly reports errors if the download fails. The persisted `data/symbols.csv` remains valid until the next successful refresh.
