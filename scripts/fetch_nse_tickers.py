"""
Fetch the official equity ticker list from NSE India and save it to data/symbols.csv.

Usage:
    python scripts/fetch_nse_tickers.py

This script:
1. Establishes an HTTP session with NSE (impersonating Chrome's TLS fingerprint
   via curl_cffi to satisfy anti-bot checks).
2. Downloads EQUITY_L.csv from NSE archives.
3. Parses and validates the CSV content.
4. Writes the result to data/symbols.csv.

Re-running the script will overwrite data/symbols.csv with the latest data.
"""

import csv
import io
import os
import sys

from curl_cffi import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NSE_BASE_URL = "https://www.nseindia.com"
EQUITY_CSV_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

# Path is relative to the project root (one level up from scripts/)
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "symbols.csv")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# Chrome version to impersonate (TLS fingerprint)
IMPERSONATE_BROWSER = "chrome120"


# ---------------------------------------------------------------------------
# HTTP Session & Download  (Tasks 2.1 – 2.5)
# ---------------------------------------------------------------------------

def create_nse_session() -> requests.Session:
    """Create an HTTP session with browser-like headers and TLS fingerprint for NSE."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/",
    })
    return session


def warm_up_session(session: requests.Session) -> None:
    """Visit the NSE home page to capture session cookies."""
    try:
        resp = session.get(NSE_BASE_URL, impersonate=IMPERSONATE_BROWSER, timeout=15)
    except requests.errors.RequestsError as exc:
        raise SystemExit(
            f"[ERROR] Network error — could not reach {NSE_BASE_URL}.\n"
            f"        Check your internet connection.\n"
            f"        Details: {exc}"
        )

    if resp.status_code != 200:
        raise SystemExit(
            f"[ERROR] NSE home page returned HTTP {resp.status_code}. "
            f"Cannot establish session."
        )


def download_equity_csv(session: requests.Session) -> str:
    """Download EQUITY_L.csv from NSE archives and return raw text."""
    try:
        resp = session.get(EQUITY_CSV_URL, impersonate=IMPERSONATE_BROWSER, timeout=30)
    except requests.errors.RequestsError as exc:
        raise SystemExit(
            f"[ERROR] Network error — could not reach {EQUITY_CSV_URL}.\n"
            f"        Details: {exc}"
        )

    if resp.status_code != 200:
        raise SystemExit(
            f"[ERROR] Failed to download EQUITY_L.csv — HTTP {resp.status_code}.\n"
            f"        URL: {EQUITY_CSV_URL}"
        )

    return resp.text


# ---------------------------------------------------------------------------
# CSV Parsing & Persistence  (Tasks 3.1 – 3.4)
# ---------------------------------------------------------------------------

def parse_csv(raw_text: str) -> tuple[list[str], list[list[str]]]:
    """
    Parse the raw CSV text into (headers, rows).

    Returns:
        headers: list of column names from the first row
        rows:    list of data rows (each a list of strings)

    Raises SystemExit if the CSV is empty or lacks a header row.
    """
    raw_text = raw_text.strip()
    if not raw_text:
        raise SystemExit("[ERROR] Downloaded CSV is empty. Aborting — existing data/symbols.csv is preserved.")

    reader = csv.reader(io.StringIO(raw_text))
    headers = next(reader, None)

    if not headers or len(headers) < 2:
        raise SystemExit(
            "[ERROR] CSV has no recognizable header row. Aborting — existing data/symbols.csv is preserved."
        )

    # Strip whitespace from header names
    headers = [h.strip() for h in headers]

    rows: list[list[str]] = []
    for row in reader:
        # Skip completely empty rows
        if any(cell.strip() for cell in row):
            rows.append([cell.strip() for cell in row])

    if not rows:
        raise SystemExit(
            "[ERROR] CSV header found but contains no data rows. Aborting — existing data/symbols.csv is preserved."
        )

    return headers, rows


def save_to_file(headers: list[str], rows: list[list[str]], output_path: str) -> int:
    """
    Write the parsed ticker data to a CSV file.

    Returns the number of data rows written.
    """
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    return len(rows)


# ---------------------------------------------------------------------------
# Main  (Tasks 4.1 – 4.2)
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("  NSE Equity Ticker Fetcher")
    print("=" * 60)

    # Step 1: Create session
    print("\n[1/4] Creating HTTP session...")
    session = create_nse_session()

    # Step 2: Warm up (get cookies)
    print("[2/4] Visiting NSE to establish session cookies...")
    warm_up_session(session)
    print("      Session established [OK]")

    # Step 3: Download CSV
    print("[3/4] Downloading EQUITY_L.csv from NSE archives...")
    raw_csv = download_equity_csv(session)
    print(f"      Downloaded {len(raw_csv):,} bytes [OK]")

    # Step 4: Parse & save
    print("[4/4] Parsing and saving to data/symbols.csv...")
    headers, rows = parse_csv(raw_csv)
    count = save_to_file(headers, rows, OUTPUT_PATH)

    print(f"\n      Saved {count} tickers to {OUTPUT_PATH}")
    print(f"      Columns: {', '.join(headers)}")
    print("\nDone! [OK]")


if __name__ == "__main__":
    main()
