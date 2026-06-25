import sys
import os
import cProfile
import pstats
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import get_connection, read_ohlcv, get_eligible_symbols
from scanner.models import rows_to_candles
from scanner.engine import scan_symbol

def profile_scan():
    conn = get_connection()
    symbols = get_eligible_symbols()[:100]  # Take 100 symbols
    
    nifty_rows = read_ohlcv("^NSEI", conn=conn)
    nifty_candles = rows_to_candles(nifty_rows) if nifty_rows else []
    
    pr = cProfile.Profile()
    pr.enable()
    
    for sym in symbols:
        try:
            scan_symbol(sym, conn=conn, nifty_candles=nifty_candles, mode="ALL")
        except Exception:
            pass
            
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(25)
    print(s.getvalue())

if __name__ == "__main__":
    profile_scan()
