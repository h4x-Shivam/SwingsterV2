import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.flag_pole.detector import FlagPolePattern

def check_score():
    conn = get_connection()
    detector = FlagPolePattern()
    
    rows = read_ohlcv("ELGIEQUIP", conn=conn)
    candles = rows_to_candles(rows)
    result = detector.detect(candles, ())
    if result:
        print(f"ELGIEQUIP passed with strength: {result.strength}")
    else:
        print("ELGIEQUIP failed.")

if __name__ == "__main__":
    check_score()
