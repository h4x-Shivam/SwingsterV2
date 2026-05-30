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

            for i in range(start, len(candles) - min_flag_candles):
                pole_low = candles[i].low
                if pole_low <= 0:
                    continue

                for pole_len in range(min_pole_candles, min(max_pole_candles + 1, len(candles) - i)):
                    pole_end = i + pole_len
                    if pole_end >= len(candles):
                        break

                    pole_high = max(c.high for c in candles[i : pole_end + 1])
                    pole_gain_pct = ((pole_high - pole_low) / pole_low) * 100

                    if pole_gain_pct < min_pole_gain_pct:
                        continue

                    pole_high_idx = i
                    for k in range(i, pole_end + 1):
                        if candles[k].high == pole_high:
                            pole_high_idx = k
                            break

                    flag_start = pole_high_idx + 1
                    if flag_start >= len(candles):
                        continue

                    for flag_len in range(min_flag_candles, min(max_flag_candles + 1, len(candles) - flag_start + 1)):
                        flag_end = flag_start + flag_len - 1
                        if flag_end >= len(candles):
                            break

                        flag_candles = candles[flag_start : flag_end + 1]

                        flag_low = min(c.low for c in flag_candles)
                        retracement = pole_high - flag_low
                        pole_gain = pole_high - pole_low
                        retrace_pct = (retracement / pole_gain * 100) if pole_gain > 0 else 999

                        if retrace_pct > max_flag_retracement:
                            continue

                        flag_closes = [c.close for c in flag_candles]
                        if len(flag_closes) >= 2:
                            slope_per_candle = (flag_closes[-1] - flag_closes[0]) / (len(flag_closes) - 1)
                            avg_price = sum(flag_closes) / len(flag_closes)
                            slope_pct = (slope_per_candle / avg_price * 100) if avg_price > 0 else 0
                            if slope_pct > max_flag_slope_pct:
                                continue
                        else:
                            continue

                        pole_vols = [candles[k].volume for k in range(i, pole_end + 1)]
                        flag_vols = [c.volume for c in flag_candles]
                        avg_pole_vol = sum(pole_vols) / len(pole_vols) if pole_vols else 1
                        avg_flag_vol = sum(flag_vols) / len(flag_vols) if flag_vols else 0

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
