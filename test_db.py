import sys
import time
from fetcher.db_writer import get_connection, get_eligible_symbols, read_ohlcv_batch

def test():
    print("Getting eligible symbols...")
    symbols = get_eligible_symbols()
    print(f"Got {len(symbols)} symbols")
    
    if not symbols:
        return
        
    test_batch = symbols[:300]
    
    print(f"Fetching batch of {len(test_batch)} symbols...")
    start = time.time()
    
    conn = get_connection()
    try:
        data = read_ohlcv_batch(test_batch, conn=conn)
        print(f"Got data for {len(data)} symbols in {time.time() - start:.2f} seconds")
    finally:
        conn.close()

if __name__ == "__main__":
    test()
