import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.vcp.detector import VCPPattern

def check_vcp(symbol):
    conn = get_connection()
    detector = VCPPattern()
    
    rows = read_ohlcv(symbol, conn=conn)
    if not rows:
        print(f"No data for {symbol}")
        return
        
    candles = rows_to_candles(rows)
    result = detector.detect(candles, ())
    
    if result:
        print(f"[{symbol}] VALID VCP!")
        print(f"  Strength : {result.strength:.1f}")
        print(f"  Buy Point: {result.buy_point}")
        print(f"  Distance : {result.distance_from_buy_pct}%")
        print(f"  Contractions : {result.contraction_count}")
        print(f"  Final Depth  : {result.contraction_depth}%")
    else:
        print(f"[{symbol}] Failed VCP detection.")

if __name__ == "__main__":
    symbols = ["20MICRONS", "UTLSOLAR", "MAZDOCK", "RELIANCE"]
    for s in symbols:
        check_vcp(s)
        print("-" * 30)
