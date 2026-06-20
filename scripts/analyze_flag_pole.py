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
            current_price = candles[-1].close
            found_patterns.append({
                "symbol": symbol,
                "current_price": current_price,
                "strength": signal.strength,
                "pole_start": getattr(signal, "pole_start_date", ""),
                "pole_end": getattr(signal, "pole_end_date", ""),
                "pole_len": getattr(signal, "pole_len", 0),
                "pole_gain": getattr(signal, "pole_gain_pct", 0),
                "pole_vel": getattr(signal, "pole_velocity", 0),
                "flag_len": getattr(signal, "flag_len", 0),
                "flag_range": getattr(signal, "flag_range_pct", 0),
                "flag_slope": getattr(signal, "flag_slope_pct", 0),
                "flag_end_date": candles[-1].date
            })

    print(f"\n--- Flag & Pole Analysis Report ---")
    print(f"Total symbols scanned: {total_scanned}")
    print(f"Total patterns found: {len(found_patterns)}")
    
    if found_patterns:
        df = pd.DataFrame(found_patterns)
        print(f"Hit rate: {len(found_patterns) / total_scanned * 100:.2f}%")
        print(f"Mean Score: {df['strength'].mean():.2f}")
        
        print("\n--- Qualitative Validation (Top 5 matches) ---")
        top_5 = df.sort_values(by='strength', ascending=False).head(5)
        for _, row in top_5.iterrows():
            slope_dir = "downward" if row['flag_slope'] < 0 else "upward" if row['flag_slope'] > 0 else "flat"
            print(f"\n[ {row['symbol']} ] - Price: {row['current_price']} | Strength: {row['strength']}")
            print(f"  Pole: {row['pole_start']} to {row['pole_end']} | {row['pole_len']} days | Gain: {row['pole_gain']}% | Vel: {row['pole_vel']}%/day")
            print(f"  Flag: length {row['flag_len']} days | Range: {row['flag_range']}% | Slope: {slope_dir} ({row['flag_slope']}) | End Date: {row['flag_end_date']}")
    else:
        print("No patterns found. The criteria might be too strict.")

if __name__ == "__main__":
    analyze()
