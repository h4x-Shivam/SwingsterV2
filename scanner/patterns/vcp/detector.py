from scanner.patterns.base import BasePattern
from scanner.patterns.vcp.config import VCP_CONFIG
from scanner.models import PatternSignal, Candle
from scanner.patterns.pivots import calculate_atr_pct
import os

class VCPPattern(BasePattern):

    config = VCP_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        try:
            if not self.is_eligible(candles):
                return None

            current_price = candles[-1].close
            windows = [120, 90, 60, 40, 25, 18]
            
            best_signal = None
            is_debug = os.environ.get("DEBUG_VCP") == "1"
            atr_pct = calculate_atr_pct(candles)
            swing_threshold = max(0.025, min(0.08, atr_pct * 2.5))
            
            for lookback in windows:
                if len(candles) < lookback:
                    continue
                    
                recent_candles = candles[-lookback:]
                
                trailing_exclude = min(14, max(5, int(lookback * 0.15)))
                min_required = trailing_exclude + 10

                if len(recent_candles) < min_required:
                    if is_debug: print(f"Window {lookback}: Rejected - window too small after exclusion")
                    continue
                    
                eligible_for_base = recent_candles[:-trailing_exclude]
                base_high_val = max(c.high for c in eligible_for_base)
                base_high_idx = next(i for i, c in enumerate(recent_candles) if c.high == base_high_val)
                
                base_candles = recent_candles[base_high_idx:]
                
                # 2. ZigZag Algorithm to find structural legs (filters out daily noise)
                direction = 'down'
                peak = base_candles[0].high
                trough = base_candles[0].low
                
                swings = [{'type': 'peak', 'price': peak, 'index': 0}]
                
                for i in range(1, len(base_candles)):
                    c = base_candles[i]
                    if direction == 'down':
                        if c.low < trough:
                            trough = c.low
                        elif c.high > trough * (1 + swing_threshold): # dynamic bounce validates the trough
                            swings.append({'type': 'trough', 'price': trough, 'index': i})
                            direction = 'up'
                            peak = c.high
                    else: # up
                        if c.high > peak:
                            peak = c.high
                        elif c.low < peak * (1 - swing_threshold): # dynamic drop validates the peak
                            swings.append({'type': 'peak', 'price': peak, 'index': i})
                            direction = 'down'
                            trough = c.low
                
                # Append final state
                if direction == 'down':
                    swings.append({'type': 'trough', 'price': trough, 'index': len(base_candles)-1})
                else:
                    swings.append({'type': 'peak', 'price': peak, 'index': len(base_candles)-1})
                    
                # 3. Calculate contraction depths
                contractions = []
                for i in range(0, len(swings) - 1):
                    if swings[i]['type'] == 'peak' and swings[i+1]['type'] == 'trough':
                        p = swings[i]['price']
                        t = swings[i+1]['price']
                        depth = (p - t) / p
                        contractions.append({
                            'depth': depth,
                            'peak_idx': swings[i]['index'],
                            'trough_idx': swings[i+1]['index'],
                            'peak_price': p
                        })
                        
                if is_debug:
                    print(f"Window {lookback}: Found {len(contractions)} contractions: {[round(c['depth']*100, 1) for c in contractions]}")
                        
                # 4. Check for STRICT Contraction in the last N legs
                valid_seq = None
                
                for seq_len in [4, 3, 2]:
                    if len(contractions) >= seq_len:
                        seq = contractions[-seq_len:]
                        
                        is_strict = True
                        for i in range(len(seq) - 1):
                            # Current depth must be smaller than previous (with 5% tolerance)
                            if seq[i+1]['depth'] > seq[i]['depth'] * 1.05:
                                if is_debug: print(f"  SeqLen {seq_len}: Rejected - Contraction {i+1} ({seq[i+1]['depth']*100:.1f}%) > {i} ({seq[i]['depth']*100:.1f}%)")
                                is_strict = False
                                break
                                
                        max_final_depth = max(0.05, min(0.15, atr_pct * 4))
                        if is_strict and seq[-1]['depth'] > max_final_depth:
                            if is_debug: print(f"  SeqLen {seq_len}: Rejected - Final depth {seq[-1]['depth']*100:.1f}% > {max_final_depth*100:.1f}%")
                            is_strict = False
                            
                        # Actionability: price near the last peak
                        if is_strict:
                            last_peak = seq[-1]['peak_price']
                            dist_from_buy = (current_price - last_peak) / last_peak
                            
                            max_extension = max(0.03, min(0.08, atr_pct * 2))
                            max_pullback   = max(0.08, min(0.20, atr_pct * 5))
                            
                            if dist_from_buy > max_extension or dist_from_buy < -max_pullback:
                                if is_debug: print(f"  SeqLen {seq_len}: Rejected - Dist from buy {dist_from_buy*100:.1f}% out of bounds")
                                is_strict = False
                            
                        if is_strict:
                            # 5. Volume Dry-up check
                            first_leg_vol = sum(c.volume for c in base_candles[seq[0]['peak_idx']:seq[0]['trough_idx']+1]) / max(1, (seq[0]['trough_idx'] - seq[0]['peak_idx']))
                            
                            # Exclude the breakout candle from the dry-up calculation if it's an up day
                            end_idx = len(base_candles)
                            if end_idx - 1 > seq[-1]['peak_idx'] and base_candles[-1].close > base_candles[-1].open:
                                end_idx -= 1
                                
                            last_leg_vol_sum = sum(c.volume for c in base_candles[seq[-1]['peak_idx']:end_idx])
                            last_leg_candles = max(1, end_idx - seq[-1]['peak_idx'])
                            last_leg_vol = last_leg_vol_sum / last_leg_candles
                            
                            # NOTE: volume tolerance (1.10) is intentionally NOT ATR-relative.
                            # Volume behavior doesn't correlate with price volatility the same
                            # way price thresholds do. Keep this fixed.
                            if last_leg_vol <= first_leg_vol * 1.10:
                                valid_seq = seq
                                if is_debug: print(f"  SeqLen {seq_len}: ACCEPTED!")
                                break # Found best sequence!
                            else:
                                if is_debug: print(f"  SeqLen {seq_len}: Rejected - Volume didn't dry up enough ({last_leg_vol} vs {first_leg_vol})")
                                
                if valid_seq:
                    buy_point = valid_seq[-1]['peak_price']
                    distance_pct = (current_price - buy_point) / buy_point * 100
                    
                    # 6. Scoring
                    geometry_score = 100
                    for i in range(len(valid_seq) - 1):
                        ratio = valid_seq[i+1]['depth'] / valid_seq[i]['depth']
                        if ratio <= 1.0:
                            adjustment = 15 - ((ratio - 0.5) / 0.5) * 27
                            geometry_score += adjustment
                        else:
                            geometry_score -= 25
                            
                    MIN_GEOMETRY_SCORE = 45
                    if geometry_score < MIN_GEOMETRY_SCORE:
                        if is_debug:
                            print(f"  SeqLen {seq_len}: Geometry score {geometry_score:.1f} below floor {MIN_GEOMETRY_SCORE} — rejecting weak shape")
                        continue
                        
                    tightness = valid_seq[-1]['depth']
                    atr_multiples = tightness / max(atr_pct, 0.005)

                    if atr_multiples <= 1.0:
                        tightness_score = 100
                    elif atr_multiples <= 2.0:
                        tightness_score = 100 - (atr_multiples - 1.0) * 30
                    elif atr_multiples <= 4.0:
                        tightness_score = 70 - (atr_multiples - 2.0) * 15
                    else:
                        tightness_score = max(10, 40 - (atr_multiples - 4.0) * 10)
                    
                    strength = (geometry_score + tightness_score) / 2.0
                    
                    # Actionability bonus
                    if -2.0 <= distance_pct <= 2.0:
                        strength += 10
                        
                    strength = max(0.0, min(strength, 100.0))

                    signal = PatternSignal(
                        name="VCP",
                        strength=strength,
                        buy_point=round(buy_point, 2),
                        distance_from_buy_pct=round(distance_pct, 2),
                        breakout_level=round(buy_point, 2),
                        pivot_high=round(base_high_val, 2),
                        contraction_depth=round(valid_seq[-1]['depth'] * 100, 2),
                        contraction_count=len(valid_seq),
                    )
                    
                    if best_signal is None or signal.strength > best_signal.strength:
                        best_signal = signal

            return best_signal

        except Exception as e:
            if os.environ.get("DEBUG_VCP") == "1": print(f"Exception: {e}")
            return None

    def score(
        self,
        signal_strength: float,
        volume_score:    float,
        rr_score:        float,
        stage2_score:    float,
        rs_score:        float,
    ) -> float:
        raw = (
            signal_strength * self.config.weight_signal +
            volume_score    * self.config.weight_volume +
            rr_score        * self.config.weight_rr     +
            stage2_score    * self.config.weight_stage2 +
            rs_score        * self.config.weight_rs
        )
        return round(max(0.0, min(100.0, raw)), 1)

    @property
    def judge_prompt(self) -> str:
        return """
        For Volatility Contraction Patterns (VCP), look for:
        1. Strict contraction: Each pullback must be visibly shallower than the previous.
        2. Tight right side: The final contraction should be very shallow (< 8%).
        3. Actionability: Price should be tight against the breakout level, not extended.
        """

