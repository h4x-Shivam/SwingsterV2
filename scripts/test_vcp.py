import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.vcp.detector import VCPPattern
from scanner.patterns.pivots import find_swing_pivots

def test_vcp(symbols):
    conn = get_connection()
    detector = VCPPattern()
    
    print(f"{'Symbol':<15} {'Result':<10} {'Details'}")
    print("-" * 80)
    
    for symbol in symbols:
        rows = read_ohlcv(symbol, conn=conn)
        if not rows:
            print(f"{symbol:<15} {'NO DATA':<10}")
            continue
            
        candles = rows_to_candles(rows)
        if len(candles) < 120:
            print(f"{symbol:<15} {'TOO SHORT':<10}")
            continue
            
        pivots = find_swing_pivots(candles, lookback=120)
        signal = detector.detect(candles, pivots)
        
        if signal:
            print(f"{symbol:<15} {'PASS':<10} {signal.contraction_count} contractions, score: {signal.strength:.1f}")
        else:
            print(f"{symbol:<15} {'FAIL':<10}")
            
    conn.close()

if __name__ == "__main__":
    group1 = ["LUMAXTECH", "GVT&D", "RELAXO"]
    group2 = ["360ONE", "GPIL", "VTL"]
    group3 = ["ZOMATO", "TCS", "RELIANCE", "INFY", "HDFCBANK", "ITC", "SBIN", "BHARTIARTL", "BAJFINANCE", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "NTPC"]
    
    print("Group 1 (Expected Pass):")
    test_vcp(group1)
    
    print("\nGroup 2 (Expected Fail):")
    test_vcp(group2)
    
    print("\nGroup 3 (New Test Set):")
    test_vcp(group3)
