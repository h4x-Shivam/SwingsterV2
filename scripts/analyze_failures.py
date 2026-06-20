import sys
import os
import sqlite3
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.flag_pole.detector import FlagPolePattern
from scanner.patterns.pivots import find_swing_pivots

def analyze_failures():
    conn = get_connection()
    detector = FlagPolePattern()
    
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT symbol FROM ohlcv")
    symbols = [row[0] for row in cursor.fetchall()]
    
    reasons_count = {
        "pole_gain_low": 0,
        "pole_gain_high": 0,
        "pole_velocity": 0,
        "pole_high_too_early": 0,
        "retrace_pct": 0,
        "flag_range": 0,
        "flag_deviation": 0,
        "flag_slope_up": 0,
        "flag_slope_down": 0,
        "volume_factor": 0,
        "passed": 0
    }
    
    min_pole_candles = 3
    max_pole_candles = 12
    min_pole_gain_pct = 12.0
    max_pole_gain_pct = 50.0
    min_pole_velocity = 2.0
    min_flag_candles = 3
    max_flag_candles = 20
    flag_range_max_ratio = 0.40
    flag_max_upward_slope = 0.003
    flag_min_downward_slope = -0.008
    pole_high_candle_tolerance = 2
    vol_flag_factor = 0.60
    max_flag_retracement = 35.0
    MAX_POLE_AGE_CANDLES = 30

    for symbol in symbols:
        rows = read_ohlcv(symbol, conn=conn)
        if not rows or len(rows) < 100:
            continue
            
        candles = rows_to_candles(rows)
        flag_end = len(candles) - 1
        
        vols = [c.volume for c in candles]
        vol_prefix = [0] * (len(vols) + 1)
        for idx in range(len(vols)):
            vol_prefix[idx + 1] = vol_prefix[idx] + vols[idx]

        def get_avg_vol(start, end):
            if end < start: return 0
            return (vol_prefix[end + 1] - vol_prefix[start]) / (end - start + 1)
            
        best_strength = -1
        symbol_reason = "none"

        for flag_len in range(min_flag_candles, max_flag_candles + 1):
            flag_start = flag_end - flag_len + 1
            pole_end = flag_start - 1
            if pole_end < 0: continue

            for pole_len in range(min_pole_candles, max_pole_candles + 1):
                pole_start = flag_start - pole_len
                if pole_start < 0: continue
                if pole_start < (len(candles) - MAX_POLE_AGE_CANDLES): continue

                pole_low = candles[pole_start].low
                if pole_low <= 0: continue

                pole_high = max(c.high for c in candles[pole_start : pole_end + 1])
                pole_gain_pct = ((pole_high - pole_low) / pole_low) * 100

                if pole_gain_pct < min_pole_gain_pct:
                    if symbol_reason == "none": symbol_reason = "pole_gain_low"
                    continue
                if pole_gain_pct > max_pole_gain_pct:
                    if symbol_reason == "none": symbol_reason = "pole_gain_high"
                    continue

                pole_velocity = pole_gain_pct / pole_len
                if pole_velocity < min_pole_velocity:
                    if symbol_reason in ["none", "pole_gain_low", "pole_gain_high"]: symbol_reason = "pole_velocity"
                    continue

                pole_candles = candles[pole_start : pole_end + 1]
                pole_highs = [c.high for c in pole_candles]
                absolute_high_idx = pole_highs.index(max(pole_highs))
                if absolute_high_idx < len(pole_candles) - pole_high_candle_tolerance:
                    if symbol_reason in ["none", "pole_gain_low", "pole_gain_high", "pole_velocity"]: symbol_reason = "pole_high_too_early"
                    continue

                flag_candles = candles[flag_start : flag_end + 1]
                flag_low = min(c.low for c in flag_candles)
                pole_gain = pole_high - pole_low

                retracement = pole_high - flag_low
                retrace_pct = (retracement / pole_gain * 100) if pole_gain > 0 else 999
                if retrace_pct > max_flag_retracement:
                    if symbol_reason in ["none", "pole_gain_low", "pole_gain_high", "pole_velocity", "pole_high_too_early"]: symbol_reason = "retrace_pct"
                    continue

                flag_closes = [c.close for c in flag_candles]
                if len(flag_closes) < 2: continue

                flag_high_close = max(flag_closes)
                flag_low_close = min(flag_closes)
                flag_range_pct = (flag_high_close - flag_low_close) / flag_low_close * 100

                max_flag_range = pole_gain_pct * flag_range_max_ratio
                if flag_range_pct >= max_flag_range:
                    symbol_reason = "flag_range"
                    continue

                mean_close = sum(flag_closes) / len(flag_closes)
                max_deviation = max(abs(c - mean_close) for c in flag_closes) / mean_close
                max_allowed_deviation = max(0.02, flag_range_max_ratio * pole_gain_pct / 200)
                if max_deviation > max_allowed_deviation:
                    symbol_reason = "flag_deviation"
                    continue

                flag_slope_pct = (flag_closes[-1] - flag_closes[0]) / flag_closes[0] / len(flag_closes)
                if flag_slope_pct > flag_max_upward_slope:
                    symbol_reason = "flag_slope_up"
                    continue
                if flag_slope_pct < flag_min_downward_slope:
                    symbol_reason = "flag_slope_down"
                    continue

                avg_pole_vol = get_avg_vol(pole_start, pole_end) if pole_end >= pole_start else 1
                avg_flag_vol = get_avg_vol(flag_start, flag_end) if flag_end >= flag_start else 0

                if avg_pole_vol > 0 and avg_flag_vol >= avg_pole_vol * vol_flag_factor:
                    symbol_reason = "volume_factor"
                    continue

                best_strength = 100
                symbol_reason = "passed"
                break
            
            if best_strength > 0:
                break
                
        reasons_count[symbol_reason] += 1

    print("--- Failure Distribution ---")
    for reason, count in reasons_count.items():
        print(f"{reason}: {count}")

if __name__ == "__main__":
    analyze_failures()
