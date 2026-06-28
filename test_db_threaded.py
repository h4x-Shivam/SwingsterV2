import time
import os
import psycopg2
from fetcher.db_writer import get_connection, get_eligible_symbols, DATABASE_URL
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_chunk(chunk):
    conn = get_connection(DATABASE_URL)
    result = {sym: [] for sym in chunk}
    try:
        placeholders = ', '.join(['%s'] * len(chunk))
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT symbol, date, open, high, low, close, volume "
                f"FROM ohlcv WHERE symbol IN ({placeholders}) "
                "ORDER BY symbol, date ASC;",
                chunk
            )
            rows = cursor.fetchall()
            for row in rows:
                sym = row[0]
                if sym in result:
                    result[sym].append((row[1], row[2], row[3], row[4], row[5], row[6]))
        return result
    finally:
        conn.close()

def test_threaded_fetch():
    print("Getting eligible symbols...")
    symbols = get_eligible_symbols()
    print(f"Got {len(symbols)} symbols")
    
    if not symbols:
        return
        
    print(f"Fetching ALL {len(symbols)} symbols with threads...")
    start = time.time()
    
    chunk_size = 500
    chunks = [symbols[i:i+chunk_size] for i in range(0, len(symbols), chunk_size)]
    
    final_data = {}
    with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
        futures = {executor.submit(fetch_chunk, c): c for c in chunks}
        for future in as_completed(futures):
            res = future.result()
            final_data.update(res)
            
    print(f"Got data for {len(final_data)} symbols in {time.time() - start:.2f} seconds")

if __name__ == "__main__":
    test_threaded_fetch()
