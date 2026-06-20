import sys
import os
import sqlite3
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.flag_pole.detector import FlagPolePattern
from scanner.patterns.pivots import find_swing_pivots

def analyze():
    conn = get_connection()
    detector = FlagPolePattern()
    
    # Get all symbols
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT symbol FROM ohlcv")
    symbols = [row[0] for row in cursor.fetchall()]
    
    found_patterns = []
    total_scanned = 0
    
    print(f"Scanning {len(symbols)} symbols for Flag & Pole...")
    
    for symbol in symbols:
        rows = read_ohlcv(symbol, conn=conn)
        if not rows or len(rows) < 100:
            continue
            
        total_scanned += 1
        candles = rows_to_candles(rows)
        pivots = find_swing_pivots(candles, lookback=120)
        
        signal = detector.detect(candles, pivots)
        if signal:
            found_patterns.append({
                "symbol": symbol,
                "strength": signal.strength,
                "buy_point": signal.buy_point,
                "distance_pct": signal.distance_from_buy_pct,
                "breakout_level": signal.breakout_level,
                "pivot_high": signal.pivot_high,
                "pattern_target": signal.pattern_target
            })

    print(f"\n--- Flag & Pole Analysis Report ---")
    print(f"Total symbols scanned: {total_scanned}")
    print(f"Total patterns found: {len(found_patterns)}")
    
    if found_patterns:
        df = pd.DataFrame(found_patterns)
        print(f"Hit rate: {len(found_patterns) / total_scanned * 100:.2f}%")
        print("\nStrength Distribution:")
        print(df['strength'].describe())
        print("\nDistance from Buy % Distribution:")
        print(df['distance_pct'].describe())
        
        print("\nTop 10 strongest matches:")
        top = df.sort_values(by='strength', ascending=False).head(10)
        print(top.to_string())
    else:
        print("No patterns found. The criteria might be too strict.")

if __name__ == "__main__":
    analyze()
