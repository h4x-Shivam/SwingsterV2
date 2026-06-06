"""Temporary diagnostic: check DB data freshness and eligibility counts."""
from fetcher.db_writer import get_prefilter_counts, get_eligible_symbols, get_connection

counts = get_prefilter_counts()
print("Pre-filter counts:", counts)

conn = get_connection()
res = conn.execute(
    "SELECT MAX(date), MIN(date), COUNT(DISTINCT symbol) FROM ohlcv WHERE symbol != '^NSEI';"
).fetchone()
today = conn.execute("SELECT date('now'), date('now', '-7 days');").fetchone()
conn.close()

print(f"DB date range  : {res[1]} -> {res[0]}  ({res[2]} symbols total)")
print(f"Today (UTC)    : {today[0]},  staleness threshold: {today[1]}")
eligible = get_eligible_symbols()
print(f"Eligible symbols: {len(eligible)}")
if eligible:
    print("Sample eligible:", eligible[:5])
