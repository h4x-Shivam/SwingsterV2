import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fetcher.db_writer import read_ohlcv, get_connection
from scanner.models import rows_to_candles
from scanner.patterns.vcp.detector import VCPPattern
from scanner.patterns.pivots import find_swing_pivots

def debug_vcp(symbol):
    conn = get_connection()
    detector = VCPPattern()
    
    rows = read_ohlcv(symbol, conn=conn)
    if not rows:
        print(f"{symbol}: NO DATA")
        return
        
    candles = rows_to_candles(rows)
    pivots = find_swing_pivots(candles, lookback=120)
    
    # We will simulate detector logic step by step to find where it returns None
    swing_highs, swing_lows = pivots
    current_price = candles[-1].close
    
    lookback = detector.config.extras.setdefault("pivot_lookback", 120)
    lookback_start = max(0, len(candles) - lookback)
    recent_highs = [sh for sh in swing_highs if sh.index >= lookback_start]
    
    if not recent_highs:
        print(f"{symbol}: FAIL at recent_highs")
        return
        
    pivot = max(recent_highs, key=lambda h: h.price)
    pivot_price = pivot.price
    pivot_idx = pivot.index
    
    min_candles_post_pivot = detector.config.extras.setdefault("min_candles_post_pivot", 10)
    if len(candles) - 1 - pivot_idx < min_candles_post_pivot:
        print(f"{symbol}: FAIL at min_candles_post_pivot")
        return
        
    pivot_proximity_bottom = detector.config.extras.setdefault("pivot_proximity_bottom", 0.80)
    if current_price < pivot_price * pivot_proximity_bottom:
        print(f"{symbol}: FAIL at pivot_proximity_bottom")
        return
        
    pivot_proximity_top = detector.config.extras.setdefault("pivot_proximity_top", 1.03)
    if current_price > pivot_price * pivot_proximity_top:
        print(f"{symbol}: FAIL at pivot_proximity_top")
        return
        
    post_pivot_lows = [sl for sl in swing_lows if sl.index > pivot_idx]
    if len(post_pivot_lows) < 2:
        print(f"{symbol}: FAIL at post_pivot_lows count")
        return
        
    first_pullback_max_depth = detector.config.extras.setdefault("first_pullback_max_depth", 35.0)
    min_pullback_depth = detector.config.extras.setdefault("min_pullback_depth", 1.5)
    vol_avg_window = detector.config.extras.setdefault("vol_avg_window", 5)
    
    pullbacks = []
    for sl in post_pivot_lows:
        depth_pct = (pivot_price - sl.price) / pivot_price * 100
        if depth_pct < min_pullback_depth or depth_pct > first_pullback_max_depth:
            continue
            
        vol_start = max(0, sl.index - vol_avg_window)
        vol_end = min(len(candles), sl.index + vol_avg_window + 1)
        vols = [candles[k].volume for k in range(vol_start, vol_end)]
        avg_vol = sum(vols) / len(vols) if vols else 0
        pullbacks.append({
            "index": sl.index,
            "low": sl.price,
            "depth_pct": depth_pct,
            "avg_vol": avg_vol,
        })
        
    if len(pullbacks) < 2:
        print(f"{symbol}: FAIL at pullbacks count < 2 (found {len(pullbacks)})")
        return
        
    best_run = []
    current_run = [pullbacks[0]]
    for i in range(1, len(pullbacks)):
        prev = current_run[-1]
        curr = pullbacks[i]
        
        depth_contracting = curr["depth_pct"] < prev["depth_pct"]
        ascending_low = curr["low"] > prev["low"]
        
        if depth_contracting and ascending_low:
            current_run.append(curr)
        else:
            if len(current_run) > len(best_run):
                best_run = current_run
            current_run = [curr]
            
    if len(current_run) > len(best_run):
        best_run = current_run
        
    num_contractions = len(best_run)
    min_contractions = 2
    if num_contractions < min_contractions:
        print(f"{symbol}: FAIL at min_contractions ({num_contractions} < {min_contractions})")
        return
        
    max_contractions = detector.config.extras.get("max_contractions", 4)
    if num_contractions > max_contractions:
        best_run = best_run[-max_contractions:]
        num_contractions = max_contractions
        
    def validate_contracting_highs(candles, contractions, pivot_idx):
        segment_highs = []
        for i in range(len(contractions)):
            start_idx = contractions[i - 1]["index"] if i > 0 else pivot_idx
            end_idx = contractions[i]["index"]
            if end_idx <= start_idx:
                return False, f"malformed segment i={i}"
            segment = candles[start_idx:end_idx + 1]
            if not segment:
                return False, f"empty segment i={i}"
            segment_high = max(c.high for c in segment)
            segment_highs.append(segment_high)
        for i in range(1, len(segment_highs)):
            if segment_highs[i] >= segment_highs[i - 1]:
                return False, f"highs not contracting: {segment_highs[i]} >= {segment_highs[i-1]}"
        return True, ""

    ok, reason = validate_contracting_highs(candles, best_run, pivot_idx)
    if not ok:
        print(f"{symbol}: FAIL at validate_contracting_highs ({reason})")
        return
        
    first_depth = best_run[0]["depth_pct"]
    final_depth = best_run[-1]["depth_pct"]
    
    first_pullback_min_depth = detector.config.extras.setdefault("first_pullback_min_depth", 8.0)
    if first_depth < first_pullback_min_depth or first_depth > first_pullback_max_depth:
        print(f"{symbol}: FAIL at first_depth {first_depth}")
        return
        
    final_pullback_max_depth = detector.config.extras.setdefault("final_pullback_max_depth", 15.0)
    if final_depth > final_pullback_max_depth:
        print(f"{symbol}: FAIL at final_depth {final_depth}")
        return
        
    min_candles_between = detector.config.extras.setdefault("min_candles_between_pullbacks", 3)
    min_recovery_pct = detector.config.extras.setdefault("min_recovery_pct", 50.0)
    
    for i in range(len(best_run) - 1):
        low1_idx = best_run[i]["index"]
        low2_idx = best_run[i + 1]["index"]
        if low2_idx - low1_idx < min_candles_between:
            print(f"{symbol}: FAIL at min_candles_between {low2_idx - low1_idx}")
            return
            
        between_high = max(candles[k].high for k in range(low1_idx + 1, low2_idx))
        pullback_range = pivot_price - best_run[i]["low"]
        if pullback_range <= 0:
            print(f"{symbol}: FAIL at pullback_range <= 0")
            return
            
        recovery_pct = (between_high - best_run[i]["low"]) / pullback_range * 100
        if recovery_pct < min_recovery_pct:
            print(f"{symbol}: FAIL at recovery_pct {recovery_pct} < {min_recovery_pct}")
            return
            
    vol_dry_up_tolerance = detector.config.extras.setdefault("vol_dry_up_tolerance", 1.05)
    for i in range(1, len(best_run)):
        current_trough_vol = best_run[i]["avg_vol"]
        previous_trough_vol = best_run[i - 1]["avg_vol"]
        print(f"{symbol}: Volume dry-up check {i}: {current_trough_vol} <= {previous_trough_vol * vol_dry_up_tolerance} (Strict: {current_trough_vol < previous_trough_vol})")
        if current_trough_vol > previous_trough_vol * vol_dry_up_tolerance:
            print(f"{symbol}: FAIL at volume dry up ({current_trough_vol} > {previous_trough_vol * vol_dry_up_tolerance})")
            return
            
    def check_right_side_accumulation(candles, window=12, min_ratio=1.25):
        recent = candles[-window:]
        up_day_volumes = [c.volume for c in recent if c.close > c.open]
        down_day_volumes = [c.volume for c in recent if c.close <= c.open]
        if len(up_day_volumes) < 3 or len(down_day_volumes) < 3:
            return None, 0, 0
        avg_up_vol = sum(up_day_volumes) / len(up_day_volumes)
        avg_down_vol = sum(down_day_volumes) / len(down_day_volumes)
        return avg_up_vol >= avg_down_vol * min_ratio, avg_up_vol, avg_down_vol

    accumulation_result, up_vol, down_vol = check_right_side_accumulation(candles, window=12)
    print(f"{symbol}: Accumulation Check: Result={accumulation_result}, Avg Up Vol={up_vol}, Avg Down Vol={down_vol}")
    if accumulation_result is False:
        print(f"{symbol}: FAIL at right side accumulation")
        return

    print(f"{symbol}: PASS")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for sym in sys.argv[1:]:
            debug_vcp(sym)
    else:
        for sym in ['LUMAXTECH', 'GVT&D', 'RELAXO', '360ONE', 'VTL']:
            debug_vcp(sym)
