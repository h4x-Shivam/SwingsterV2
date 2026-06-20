import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import get_connection, read_ohlcv
from scanner.models import rows_to_candles
from scanner.engine import scan_symbol

def test_engine():
    conn = get_connection()
    nifty_rows = read_ohlcv("^NSEI", conn=conn)
    nifty_candles = rows_to_candles(nifty_rows) if nifty_rows else []
    
    symbols = ["PAISALO", "ELGIEQUIP", "NRBBEARING", "TATACOMM", "ADANIPORTS"]
    for sym in symbols:
        try:
            res = scan_symbol(sym, conn=conn, nifty_candles=nifty_candles, mode="FLAG_POLE")
            if res:
                print(f"{sym}: composite={res.composite_score:.2f}, signal={res.signal_strength:.2f}, "
                      f"vol={res.volume_score:.2f}, rr={res.rr_score:.2f}, "
                      f"stage2={res.stage2_score:.2f}, rs={res.rs_score:.2f}")
            else:
                print(f"{sym}: REJECTED")
        except Exception as e:
            print(f"{sym}: ERROR {e}")

if __name__ == "__main__":
    test_engine()
