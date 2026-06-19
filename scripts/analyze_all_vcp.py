import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.vcp.detector import VCPPattern
from scanner.patterns.pivots import find_swing_pivots

def debug(symbol):
    conn = get_connection()
    detector = VCPPattern()
    rows = read_ohlcv(symbol, conn=conn)
    if not rows: return
    candles = rows_to_candles(rows)
    pivots = find_swing_pivots(candles, lookback=120)
    
    signal = detector.detect(candles, pivots)
    if signal:
        print(f"{symbol}: Found VCP with {signal.contraction_count} contractions. Final depth: {signal.contraction_depth}%")
        # To see the actual depths, we have to look inside the logic
        swing_highs, swing_lows = pivots
        current_price = candles[-1].close
        lookback = detector.config.extras.setdefault("pivot_lookback", 120)
        lookback_start = max(0, len(candles) - lookback)
        recent_highs = [sh for sh in swing_highs if sh.index >= lookback_start]
        for pivot in sorted(recent_highs, key=lambda h: h.price, reverse=True):
            if signal.pivot_high == round(pivot.price, 2):
                pivot_price = pivot.price
                pivot_idx = pivot.index
                post_pivot_lows = [sl for sl in swing_lows if sl.index > pivot_idx]
                first_pullback_max_depth = 35.0
                min_pullback_depth = 1.5
                pullbacks = []
                for sl in post_pivot_lows:
                    depth_pct = (pivot_price - sl.price) / pivot_price * 100
                    if depth_pct < min_pullback_depth or depth_pct > first_pullback_max_depth: continue
                    pullbacks.append({"depth_pct": depth_pct})
                print(f"  All valid depths under pivot {pivot_price}: {[round(p['depth_pct'], 2) for p in pullbacks]}")
                break
    else:
        print(f"{symbol}: No VCP found")

if __name__ == "__main__":
    for sym in sys.argv[1:]:
        debug(sym)
