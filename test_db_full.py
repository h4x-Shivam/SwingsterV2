import time
from fetcher.db_writer import get_connection, get_eligible_symbols, read_ohlcv_batch

def test_full_fetch():
    print("Getting eligible symbols...")
    symbols = get_eligible_symbols()
    print(f"Got {len(symbols)} symbols")
    
    if not symbols:
        return
        
    print(f"Fetching ALL {len(symbols)} symbols...")
    start = time.time()
    
    conn = get_connection()
    try:
        data = read_ohlcv_batch(symbols, conn=conn)
        print(f"Got data for {len(data)} symbols in {time.time() - start:.2f} seconds")
    finally:
        conn.close()

if __name__ == "__main__":
    test_full_fetch()
