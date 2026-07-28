from scanner.patterns.base import BasePattern
from scanner.patterns.vcp.config import VCP_CONFIG
from scanner.models import PatternSignal, Candle
from scanner.patterns.pivots import calculate_atr_pct, find_swing_pivots
from log import get_logger

logger = get_logger(__name__)

class VCPPattern(BasePattern):

    config = VCP_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        try:
            if not self.is_eligible(candles):
                return None

            current_price = candles[-1].close
            atr_pct = calculate_atr_pct(candles)
            
            if not pivots or len(pivots) != 2:
                pivots = find_swing_pivots(candles, lookback=120)
                
            swing_highs, swing_lows = pivots
            
            lookback = self.config.extras.get("pivot_lookback", 120)
            lookback_start = max(0, len(candles) - lookback)
            recent_highs = [sh for sh in swing_highs if sh.index >= lookback_start]
            
            if not recent_highs:
                logger.debug(f"Rejected - no recent highs found in lookback {lookback}")
                return None
                
            pivot = max(recent_highs, key=lambda h: h.price)
            pivot_price = pivot.price
            pivot_idx = pivot.index
            
            min_candles_post_pivot = self.config.extras.get("min_candles_post_pivot", 10)
            if len(candles) - 1 - pivot_idx < min_candles_post_pivot:
                logger.debug(f"Rejected - not enough candles after pivot ({len(candles) - 1 - pivot_idx} < {min_candles_post_pivot})")
                return None
                
            pivot_proximity_bottom = self.config.extras.get("pivot_proximity_bottom", 0.80)
            if current_price < pivot_price * pivot_proximity_bottom:
                logger.debug(f"Rejected - price too far below pivot ({current_price} < {pivot_price * pivot_proximity_bottom})")
                return None
                
            pivot_proximity_top = self.config.extras.get("pivot_proximity_top", 1.03)
            if current_price > pivot_price * pivot_proximity_top:
                logger.debug(f"Rejected - price extended above pivot ({current_price} > {pivot_price * pivot_proximity_top})")
                return None
                
            post_pivot_lows = [sl for sl in swing_lows if sl.index > pivot_idx]
            if len(post_pivot_lows) < 2:
                logger.debug(f"Rejected - not enough post-pivot lows (found {len(post_pivot_lows)})")
                return None
                
            first_pullback_max_depth = self.config.extras.get("first_pullback_max_depth", 35.0)
            min_pullback_depth = self.config.extras.get("min_pullback_depth", 1.5)
            vol_avg_window = self.config.extras.get("vol_avg_window", 5)
            
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
                logger.debug(f"Rejected - not enough valid pullbacks (found {len(pullbacks)})")
                return None
                
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
            min_contractions = self.config.extras.get("min_contractions", 2)
            if num_contractions < min_contractions:
                logger.debug(f"Rejected - min contractions not met ({num_contractions} < {min_contractions})")
                return None
                
            max_contractions = self.config.extras.get("max_contractions", 4)
            if num_contractions > max_contractions:
                best_run = best_run[-max_contractions:]
                num_contractions = max_contractions
                
            def validate_contracting_highs(cndls, conts, piv_idx):
                seg_highs = []
                for i in range(len(conts)):
                    s_idx = conts[i - 1]["index"] if i > 0 else piv_idx
                    e_idx = conts[i]["index"]
                    if e_idx <= s_idx:
                        return False, f"malformed segment i={i}"
                    seg = cndls[s_idx:e_idx + 1]
                    if not seg:
                        return False, f"empty segment i={i}"
                    seg_high = max(c.high for c in seg)
                    seg_highs.append(seg_high)
                for i in range(1, len(seg_highs)):
                    if seg_highs[i] >= seg_highs[i - 1]:
                        return False, f"highs not contracting: {seg_highs[i]} >= {seg_highs[i-1]}"
                return True, ""

            ok, reason = validate_contracting_highs(candles, best_run, pivot_idx)
            if not ok:
                logger.debug(f"Rejected - validate_contracting_highs failed: {reason}")
                return None
                
            first_depth = best_run[0]["depth_pct"]
            final_depth = best_run[-1]["depth_pct"]
            
            first_pullback_min_depth = self.config.extras.get("first_pullback_min_depth", 8.0)
            if first_depth < first_pullback_min_depth or first_depth > first_pullback_max_depth:
                logger.debug(f"Rejected - first pullback depth {first_depth:.2f} out of range ({first_pullback_min_depth}-{first_pullback_max_depth})")
                return None
                
            final_pullback_max_depth = self.config.extras.get("final_pullback_max_depth", 15.0)
            if final_depth > final_pullback_max_depth:
                logger.debug(f"Rejected - final pullback depth {final_depth:.2f} > {final_pullback_max_depth}")
                return None
                
            min_candles_between = self.config.extras.get("min_candles_between_pullbacks", 3)
            min_recovery_pct = self.config.extras.get("min_recovery_pct", 50.0)
            
            for i in range(len(best_run) - 1):
                low1_idx = best_run[i]["index"]
                low2_idx = best_run[i + 1]["index"]
                if low2_idx - low1_idx < min_candles_between:
                    logger.debug(f"Rejected - min candles between pullbacks failed ({low2_idx - low1_idx} < {min_candles_between})")
                    return None
                    
                between_high = max(candles[k].high for k in range(low1_idx + 1, low2_idx))
                pullback_range = pivot_price - best_run[i]["low"]
                if pullback_range <= 0:
                    return None
                    
                recovery_pct = (between_high - best_run[i]["low"]) / pullback_range * 100
                if recovery_pct < min_recovery_pct:
                    logger.debug(f"Rejected - recovery {recovery_pct:.1f}% < {min_recovery_pct}%")
                    return None
                    
            vol_dry_up_tolerance = self.config.extras.get("vol_dry_up_tolerance", 1.05)
            for i in range(1, len(best_run)):
                current_trough_vol = best_run[i]["avg_vol"]
                previous_trough_vol = best_run[i - 1]["avg_vol"]
                if current_trough_vol > previous_trough_vol * vol_dry_up_tolerance:
                    logger.debug(f"Rejected - volume did not dry up ({current_trough_vol} > {previous_trough_vol * vol_dry_up_tolerance})")
                    return None
                    
            def check_right_side_accumulation(cndls, window=12, min_ratio=1.25):
                recent = cndls[-window:]
                up_day_volumes = [c.volume for c in recent if c.close > c.open]
                down_day_volumes = [c.volume for c in recent if c.close <= c.open]
                if len(up_day_volumes) < 3 or len(down_day_volumes) < 3:
                    return None, 0, 0
                avg_up_vol = sum(up_day_volumes) / len(up_day_volumes)
                avg_down_vol = sum(down_day_volumes) / len(down_day_volumes)
                return avg_up_vol >= avg_down_vol * min_ratio, avg_up_vol, avg_down_vol

            accumulation_result, up_vol, down_vol = check_right_side_accumulation(candles, window=12)
            if accumulation_result is False:
                logger.debug(f"Rejected - right side accumulation failed. Up: {up_vol}, Down: {down_vol}")
                return None
            # --- Strict Tightness and Volume Checks ---
            
            # 1. Price Tightness (Right Side Range)
            rs_range_days = self.config.extras.get("right_side_range_days", 15)
            rs_max_range_pct = self.config.extras.get("right_side_max_range_pct", 1.08)
            recent_candles = candles[-rs_range_days:]
            if len(recent_candles) >= rs_range_days:
                rs_high = max(c.high for c in recent_candles)
                rs_low = min(c.low for c in recent_candles)
                if rs_low > 0:
                    rs_range = rs_high / rs_low
                    if rs_range > rs_max_range_pct:
                        logger.debug(f"Rejected - right side range too wide ({rs_range:.3f} > {rs_max_range_pct})")
                        return None
                        
            # 2. ATR Contraction
            atr_ratio_threshold = self.config.extras.get("atr_contraction_ratio", 0.5)
            def get_atr(cndls, period):
                if len(cndls) < period + 1: return 0.0
                tr_sum = 0.0
                for j in range(len(cndls)-period, len(cndls)):
                    h = cndls[j].high
                    l = cndls[j].low
                    pc = cndls[j-1].close
                    tr = max(h - l, abs(h - pc), abs(l - pc))
                    tr_sum += tr
                return tr_sum / period

            atr_5 = get_atr(candles, 5)
            atr_20 = get_atr(candles, 20)
            if atr_20 > 0:
                atr_ratio = atr_5 / atr_20
                if atr_ratio > atr_ratio_threshold:
                    logger.debug(f"Rejected - ATR not contracting enough ({atr_ratio:.3f} > {atr_ratio_threshold})")
                    return None
                    
            # 3 & 4. Volume Contraction and Dry-Up Count
            vol_dry_up_days = self.config.extras.get("vol_dry_up_days", 10)
            vol_dry_up_min_count = self.config.extras.get("vol_dry_up_min_count", 3)
            vol_dry_up_threshold = self.config.extras.get("vol_dry_up_threshold", 0.5)
            
            if len(candles) >= 50:
                avg_vol_50 = sum(c.volume for c in candles[-50:]) / 50.0
                avg_vol_5 = sum(c.volume for c in candles[-5:]) / 5.0
                
                # Check if short-term volume is less than long-term volume
                if avg_vol_5 > avg_vol_50:
                    logger.debug(f"Rejected - 5d vol > 50d vol ({avg_vol_5} > {avg_vol_50})")
                    return None
                    
                # Count dry up days
                recent_vols = [c.volume for c in candles[-vol_dry_up_days:]]
                dry_days = sum(1 for v in recent_vols if v < (avg_vol_50 * vol_dry_up_threshold))
                if dry_days < vol_dry_up_min_count:
                    logger.debug(f"Rejected - not enough volume dry up days ({dry_days} < {vol_dry_up_min_count})")
                    return None
                    
            # --- End Strict Checks ---

            # Scoring based on geometry and tightness
            geometry_score = 100
            for i in range(len(best_run) - 1):
                ratio = best_run[i+1]['depth_pct'] / best_run[i]['depth_pct']
                if ratio <= 1.0:
                    adjustment = 15 - ((ratio - 0.5) / 0.5) * 27
                    geometry_score += adjustment
                else:
                    geometry_score -= 25
                    
            tightness = final_depth / 100.0  # convert back to ratio
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
            
            distance_pct = (current_price - pivot_price) / pivot_price * 100
            if -2.0 <= distance_pct <= 2.0:
                strength += 10
                
            strength = max(0.0, min(strength, 100.0))

            if is_debug:
                print(f"ACCEPTED! Symbol passed strict VCP checks. Score: {strength:.1f}")

            signal = PatternSignal(
                name="VCP",
                strength=strength,
                buy_point=round(pivot_price, 2),
                distance_from_buy_pct=round(distance_pct, 2),
                breakout_level=round(pivot_price, 2),
                pivot_high=round(pivot_price, 2),
                contraction_depth=round(final_depth, 2),
                contraction_count=len(best_run),
            )
            
            return signal

        except Exception:
            logger.debug("VCP detection failed", exc_info=True)
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
