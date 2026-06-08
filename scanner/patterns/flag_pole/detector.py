from scanner.patterns.base import BasePattern
from scanner.patterns.flag_pole.config import FLAG_POLE_CONFIG
from scanner.models import PatternSignal, Candle

class FlagPolePattern(BasePattern):

    config = FLAG_POLE_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        try:
            if not self.is_eligible(candles):
                return None

            pole_lookback = self.config.extras.setdefault("pole_lookback", 60)
            lookback = min(len(candles), pole_lookback)
            start = len(candles) - lookback

            best_signal = None

            min_pole_candles = self.config.extras.setdefault("min_pole_candles", 3)
            max_pole_candles = self.config.extras.setdefault("max_pole_candles", 15)
            min_pole_gain_pct = self.config.extras.setdefault("min_pole_gain_pct", 8.0)
            min_flag_candles = self.config.extras.setdefault("min_flag_candles", 5)
            max_flag_candles = self.config.extras.setdefault("max_flag_candles", 20)
            max_flag_retracement = self.config.extras.setdefault("max_flag_retracement", 35.0)
            max_flag_slope_pct = self.config.extras.setdefault("max_flag_slope_pct", 0.1)
            vol_flag_factor = self.config.extras.setdefault("vol_flag_factor", 0.60)
            buy_point_buffer = self.config.extras.setdefault("buy_point_buffer", 0.10)

            flag_end = len(candles) - 1
            MAX_POLE_AGE_CANDLES = 30

            vols = [c.volume for c in candles]
            vol_prefix = [0] * (len(vols) + 1)
            for idx in range(len(vols)):
                vol_prefix[idx + 1] = vol_prefix[idx] + vols[idx]

            def get_avg_vol(start, end):
                if end < start: return 0
                return (vol_prefix[end + 1] - vol_prefix[start]) / (end - start + 1)

            for flag_len in range(min_flag_candles, max_flag_candles + 1):
                flag_start = flag_end - flag_len + 1
                pole_end = flag_start - 1

                if pole_end < 0:
                    continue

                for pole_len in range(min_pole_candles, max_pole_candles + 1):
                    pole_start = flag_start - pole_len

                    if pole_start < 0:
                        continue

                    if pole_start < (len(candles) - MAX_POLE_AGE_CANDLES):
                        continue

                    pole_low = candles[pole_start].low
                    if pole_low <= 0:
                        continue

                    pole_high = max(c.high for c in candles[pole_start : pole_end + 1])
                    pole_gain_pct = ((pole_high - pole_low) / pole_low) * 100

                    if pole_gain_pct < min_pole_gain_pct:
                        continue

                    actual_pole_high_idx = pole_start
                    for k in range(pole_start, pole_end + 1):
                        if candles[k].high == pole_high:
                            actual_pole_high_idx = k
                            break

                    if actual_pole_high_idx != pole_end:
                        # True flag started earlier, will be handled by a larger flag_len iteration
                        continue

                    flag_candles = candles[flag_start : flag_end + 1]

                    flag_low = min(c.low for c in flag_candles)
                    retracement = pole_high - flag_low
                    pole_gain = pole_high - pole_low
                    retrace_pct = (retracement / pole_gain * 100) if pole_gain > 0 else 999

                    if retrace_pct > max_flag_retracement:
                        continue

                    flag_closes = [c.close for c in flag_candles]
                    if len(flag_closes) >= 2:
                        mean_close = sum(flag_closes) / len(flag_closes)
                        variance = max(abs(c - mean_close) for c in flag_closes) / mean_close
                        if variance > 0.04:
                            continue
                    else:
                        continue

                    avg_pole_vol = get_avg_vol(pole_start, pole_end) if pole_end >= pole_start else 1
                    avg_flag_vol = get_avg_vol(flag_start, flag_end) if flag_end >= flag_start else 0

                    if avg_pole_vol > 0 and avg_flag_vol >= avg_pole_vol * vol_flag_factor:
                        continue

                    current_price = candles[-1].close
                    flag_high = max(c.high for c in flag_candles)
                    buy_point = flag_high + buy_point_buffer
                    distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

                    strong_pole_90 = self.config.extras.setdefault("strong_pole_gain_pct_90", 20.0)
                    strong_pole_70 = self.config.extras.setdefault("strong_pole_gain_pct_70", 12.0)
                    
                    if pole_gain_pct >= strong_pole_90:
                        strength = 90.0
                    elif pole_gain_pct >= strong_pole_70:
                        strength = 70.0
                    else:
                        strength = 50.0

                    bonus_tight_20 = self.config.extras.setdefault("bonus_tight_flag_20", 20.0)
                    bonus_tight_25 = self.config.extras.setdefault("bonus_tight_flag_25", 25.0)

                    if retrace_pct <= bonus_tight_20:
                        strength += 10
                    elif retrace_pct <= bonus_tight_25:
                        strength += 5

                    bonus_vol_30 = self.config.extras.setdefault("bonus_vol_ratio_30", 0.30)
                    bonus_vol_45 = self.config.extras.setdefault("bonus_vol_ratio_45", 0.45)

                    if avg_pole_vol > 0:
                        vr = avg_flag_vol / avg_pole_vol
                        if vr < bonus_vol_30:
                            strength += 10
                        elif vr < bonus_vol_45:
                            strength += 5

                    strength = min(strength, 100.0)

                    if best_signal is None or strength > best_signal.strength:
                        best_signal = PatternSignal(
                            name="FLAG_POLE",
                            strength=strength,
                            buy_point=round(buy_point, 2),
                            distance_from_buy_pct=round(distance_pct, 2),
                            breakout_level=round(flag_high, 2),
                            pivot_high=round(pole_high, 2),
                            pattern_stop_loss=round(flag_low * 0.99, 2),
                            pattern_target=round(buy_point + pole_gain, 2),
                        )

                if best_signal and best_signal.strength >= 90:
                    return best_signal

            return best_signal

        except Exception:
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
        For Flag & Pole patterns, look for:
        1. An impulsive, powerful pole on high volume.
        2. A tight, orderly flag consolidation that does not retrace too deep.
        3. Significant volume dry-up during the flag formation.
        4. Clear resistance breakout level at the top of the flag.
        """
