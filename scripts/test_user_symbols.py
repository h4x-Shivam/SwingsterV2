import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.flag_pole.detector import FlagPolePattern

def test_user_symbols():
    conn = get_connection()
    symbols = ["PAISALO", "ELGIEQUIP", "NRBBEARING", "TATACOMM"]
    detector = FlagPolePattern()
    
    for symbol in symbols:
        rows = read_ohlcv(symbol, conn=conn)
        if not rows:
            print(f"{symbol}: No data")
            continue
        candles = rows_to_candles(rows)
        # Assuming detect checks the end of the series
        result = detector.detect(candles, ())
        print(f"{symbol}: {'PASS' if result else 'FAIL'}")

if __name__ == "__main__":
    test_user_symbols()
