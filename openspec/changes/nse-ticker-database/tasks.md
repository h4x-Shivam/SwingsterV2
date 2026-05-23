## 1. Project Setup

- [x] 1.1 Create `scripts/` directory
- [x] 1.2 Create `scripts/fetch_nse_tickers.py` with boilerplate (imports, main guard)
- [x] 1.3 Add `requirements.txt` with `requests` dependency

## 2. HTTP Session & Download

- [x] 2.1 Implement `create_nse_session()` — creates a `requests.Session` with a Chrome User-Agent header
- [x] 2.2 Implement session warm-up: `GET https://www.nseindia.com` to capture cookies
- [x] 2.3 Implement `download_equity_csv(session)` — fetches `EQUITY_L.csv` from NSE archives, returns raw text content
- [x] 2.4 Add error handling: raise clear errors on non-200 status codes with the HTTP status included
- [x] 2.5 Add error handling: raise clear errors on network failures (DNS, timeout) without overwriting existing `data/symbols.csv`

## 3. CSV Parsing & Persistence

- [x] 3.1 Implement `parse_csv(raw_text)` — uses `csv.reader`/`csv.DictReader` with the header row to produce a list of records
- [x] 3.2 Add validation: raise error if CSV is empty or has no recognizable header row
- [x] 3.3 Implement `save_to_file(records, headers, output_path)` — writes parsed records to `data/symbols.csv` with the original header row
- [x] 3.4 Print summary message with the number of tickers saved (e.g., "Saved 2100 tickers to data/symbols.csv")

## 4. Main Script Wiring

- [x] 4.1 Wire `main()` function: create session → download → parse → save
- [x] 4.2 Ensure the script is re-runnable (each run overwrites `data/symbols.csv` with fresh data)

## 5. Verification

- [x] 5.1 Run the script end-to-end and verify `data/symbols.csv` is populated with ticker data
- [x] 5.2 Run the script a second time to verify re-run overwrites correctly
- [x] 5.3 Verify error handling by testing with a deliberately wrong URL
