import sys
import os
import sqlite3
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles

def reverse_engineer():
    conn = get_connection()
    symbols = ["PAISALO", "ELGIEQUIP", "NRBBEARING", "TATACOMM"]
    
    for symbol in symbols:
        rows = read_ohlcv(symbol, conn=conn)
        if not rows: continue
        candles = rows_to_candles(rows)
        
        # We will try to find the BEST pole and flag ending at the current day (or recently)
        # by relaxing all constraints and just printing the ones with the highest score
        # or we just print the stats of the biggest recent moves.
        
        flag_end = len(candles) - 1
        
        print(f"\n--- {symbol} ---")
        
        # Look back up to 60 days for a pole
        best_gain = 0
        best_stats = None
        
        for flag_len in range(3, 40):
            flag_start = flag_end - flag_len + 1
            if flag_start <= 0: continue
            
            for pole_len in range(5, 60):
                pole_start = flag_start - pole_len
                if pole_start < 0: continue
                
                pole_end = flag_start - 1
                pole_low = candles[pole_start].low
                if pole_low <= 0: continue
                
                pole_candles = candles[pole_start:pole_end+1]
                pole_highs = [c.high for c in pole_candles]
                pole_high = max(pole_highs)
                
                # Assume the pole high is near the end of the pole
                absolute_high_idx = pole_highs.index(pole_high)
                if absolute_high_idx < len(pole_candles) - 5:
                    continue # Not a valid pole if the high is too early
                
                pole_gain_pct = ((pole_high - pole_low) / pole_low) * 100
                
                if pole_gain_pct > best_gain:
                    best_gain = pole_gain_pct
                    
                    flag_candles = candles[flag_start:flag_end+1]
                    flag_closes = [c.close for c in flag_candles]
                    flag_low = min(c.low for c in flag_candles)
                    retracement = pole_high - flag_low
                    retrace_pct = (retracement / (pole_high - pole_low) * 100) if pole_high > pole_low else 999
                    
                    x = np.arange(len(flag_closes))
                    m, b = np.polyfit(x, flag_closes, 1)
                    flag_slope_pct = m / flag_closes[0]
                    
                    trendline_vals = m * x + b
                    max_deviation = max(abs(flag_closes[i] - trendline_vals[i]) for i in range(len(flag_closes))) / b
                    
                    vols = [c.volume for c in candles]
                    vol_prefix = [0] * (len(vols) + 1)
                    for idx in range(len(vols)):
                        vol_prefix[idx + 1] = vol_prefix[idx] + vols[idx]

                    def get_avg_vol(start, end):
                        if end < start: return 0
                        return (vol_prefix[end + 1] - vol_prefix[start]) / (end - start + 1)
                        
                    avg_pole_vol = get_avg_vol(pole_start, pole_end)
                    avg_flag_vol = get_avg_vol(flag_start, flag_end)
                    vol_ratio = avg_flag_vol / avg_pole_vol if avg_pole_vol > 0 else 999
                    
                    best_stats = {
                        "pole_len": pole_len,
                        "pole_gain_pct": pole_gain_pct,
                        "pole_velocity": pole_gain_pct / pole_len,
                        "flag_len": flag_len,
                        "retrace_pct": retrace_pct,
                        "flag_slope_pct": flag_slope_pct,
                        "max_deviation": max_deviation,
                        "vol_ratio": vol_ratio
                    }
        
        if best_stats:
            for k, v in best_stats.items():
                print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    reverse_engineer()
