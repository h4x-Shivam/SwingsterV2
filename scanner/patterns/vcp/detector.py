from scanner.patterns.base import BasePattern
from scanner.patterns.vcp.config import VCP_CONFIG
from scanner.models import PatternSignal, Candle
import os

class VCPPattern(BasePattern):

    config = VCP_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        try:
            if not self.is_eligible(candles):
                return None

            current_price = candles[-1].close
            windows = [120, 90, 60, 40, 25]
            
            best_signal = None
            is_debug = os.environ.get("DEBUG_VCP") == "1"
            
            for lookback in windows:
                if len(candles) < lookback:
                    continue
                    
                recent_candles = candles[-lookback:]
                
                # 1. Base start is the highest high in this window that occurred at least 15 days ago
                if len(recent_candles) < 15:
                    if is_debug: print(f"Window {lookback}: Rejected - window too small")
                    continue
                    
                eligible_for_base = recent_candles[:-14]
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
                        elif c.high > trough * 1.04: # 4% bounce validates the trough
                            swings.append({'type': 'trough', 'price': trough, 'index': i})
                            direction = 'up'
                            peak = c.high
                    else: # up
                        if c.high > peak:
                            peak = c.high
                        elif c.low < peak * 0.96: # 4% drop validates the peak
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
                                
                        # Right side must be tight (< 10% depth)
                        if is_strict and seq[-1]['depth'] > 0.10:
                            if is_debug: print(f"  SeqLen {seq_len}: Rejected - Final depth {seq[-1]['depth']*100:.1f}% > 10%")
                            is_strict = False
                            
                        # Actionability: price near the last peak
                        if is_strict:
                            last_peak = seq[-1]['peak_price']
                            dist_from_buy = (current_price - last_peak) / last_peak
                            
                            # Too extended (> 5%) or too deep below (< -12%)
                            if dist_from_buy > 0.05 or dist_from_buy < -0.12:
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
                            
                            if last_leg_vol <= first_leg_vol * 1.10: # Allow slight volume increase, but prefer dry up
                                valid_seq = seq
                                if is_debug: print(f"  SeqLen {seq_len}: ACCEPTED!")
                                break # Found best sequence!
                            else:
                                if is_debug: print(f"  SeqLen {seq_len}: Rejected - Volume didn't dry up enough ({last_leg_vol} vs {first_leg_vol})")
                                
                if valid_seq:
                    buy_point = valid_seq[-1]['peak_price']
                    distance_pct = (current_price - buy_point) / buy_point * 100
                    
                    # 6. Scoring
                    # Reward perfectly descending geometry
                    geometry_score = 100
                    for i in range(len(valid_seq) - 1):
                        ratio = valid_seq[i+1]['depth'] / valid_seq[i]['depth']
                        if ratio < 0.8: geometry_score += 5   # Great contraction
                        if ratio > 1.0: geometry_score -= 15  # Sloppy contraction
                        
                    # Reward tight right side
                    tightness = valid_seq[-1]['depth'] * 100
                    tightness_score = 100 - (tightness * 5) # 4% depth = 80, 10% depth = 50
                    
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

