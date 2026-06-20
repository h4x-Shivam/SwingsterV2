from scanner.patterns.base import BasePattern
from scanner.patterns.flag_pole.config import FLAG_POLE_CONFIG
from scanner.models import PatternSignal, Candle
import numpy as np

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
            max_pole_candles = self.config.extras.setdefault("max_pole_candles", 12)
            min_pole_gain_pct = self.config.extras.setdefault("min_pole_gain_pct", 12.0)
            max_pole_gain_pct = self.config.extras.setdefault("max_pole_gain_pct", 50.0)
            min_pole_velocity = self.config.extras.setdefault("min_pole_velocity", 1.0)
            min_flag_candles = self.config.extras.setdefault("min_flag_candles", 3)
            max_flag_candles = self.config.extras.setdefault("max_flag_candles", 20)
            flag_range_max_ratio = self.config.extras.setdefault("flag_range_max_ratio", 0.40)
            flag_max_upward_slope = self.config.extras.setdefault("flag_max_upward_slope", 0.003)
            flag_min_downward_slope = self.config.extras.setdefault("flag_min_downward_slope", -0.008)
            pole_high_candle_tolerance = self.config.extras.setdefault("pole_high_candle_tolerance", 2)
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
                    if pole_gain_pct > max_pole_gain_pct:
                        continue

                    pole_velocity = pole_gain_pct / pole_len
                    if pole_velocity < min_pole_velocity:
                        continue

                    pole_candles = candles[pole_start : pole_end + 1]
                    pole_highs = [c.high for c in pole_candles]
                    absolute_high_idx = pole_highs.index(max(pole_highs))
                    if absolute_high_idx < len(pole_candles) - pole_high_candle_tolerance:
                        continue

                    flag_candles = candles[flag_start : flag_end + 1]
                    flag_low = min(c.low for c in flag_candles)
                    pole_gain = pole_high - pole_low

                    retracement = pole_high - flag_low
                    retrace_pct = (retracement / pole_gain * 100) if pole_gain > 0 else 999
                    max_flag_retracement = self.config.extras.setdefault("max_flag_retracement", 35.0)
                    if retrace_pct > max_flag_retracement:
                        continue

                    flag_closes = [c.close for c in flag_candles]
                    if len(flag_closes) < 3:
                        continue

                    # Linear regression on closes to find slope and central trendline
                    x = np.arange(len(flag_closes))
                    m, b = np.polyfit(x, flag_closes, 1)
                    
                    flag_slope_pct = m / flag_closes[0]
                    if flag_slope_pct > flag_max_upward_slope:
                        continue
                    if flag_slope_pct < flag_min_downward_slope:
                        continue

                    # Check channel tightness (deviation from the sloping trendline)
                    trendline_vals = m * x + b
                    max_deviation = max(abs(flag_closes[i] - trendline_vals[i]) for i in range(len(flag_closes))) / b
                    max_allowed_deviation = self.config.extras.setdefault("max_channel_deviation", 0.035)
                    if max_deviation > max_allowed_deviation:
                        continue

                    # Calculate upper trendline using highs for accurate breakout level
                    flag_highs = [c.high for c in flag_candles]
                    m_high, b_high = np.polyfit(x, flag_highs, 1)
                    current_day_x = len(candles) - 1 - flag_start
                    upper_trendline_now = m_high * current_day_x + b_high
                    
                    # For flag_range_pct (used in scoring), we use the actual high and low closes
                    flag_high_close = max(flag_closes)
                    flag_low_close = min(flag_closes)
                    flag_range_pct = (flag_high_close - flag_low_close) / flag_low_close * 100

                    avg_pole_vol = get_avg_vol(pole_start, pole_end) if pole_end >= pole_start else 1
                    avg_flag_vol = get_avg_vol(flag_start, flag_end) if flag_end >= flag_start else 0

                    if avg_pole_vol > 0 and avg_flag_vol >= avg_pole_vol * vol_flag_factor:
                        continue

                    current_price = candles[-1].close
                    # If upper trendline is somehow below current price already, 
                    # use the max high of the flag as a fallback to avoid premature signals
                    flag_high = max(flag_highs)
                    breakout_ref = max(upper_trendline_now, flag_high * 0.95) 
                    buy_point = breakout_ref * (1.0 + buy_point_buffer / 100.0)
                    distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

                    strength = 50.0

                    if pole_velocity >= 3.0:
                        strength += 25
                    elif pole_velocity >= 2.0:
                        strength += 15
                    elif pole_velocity >= 1.5:
                        strength += 8
                    elif pole_velocity >= 1.0:
                        strength += 0

                    if pole_len <= 4:
                        strength += 15
                    elif pole_len <= 6:
                        strength += 10
                    elif pole_len <= 8:
                        strength += 5

                    flag_to_pole_ratio = flag_range_pct / pole_gain_pct
                    if flag_to_pole_ratio < 0.20:
                        strength += 10
                    elif flag_to_pole_ratio < 0.30:
                        strength += 5

                    if -0.003 <= flag_slope_pct <= 0.000:
                        strength += 8
                    elif flag_slope_pct < -0.003:
                        strength += 3

                    strength = min(strength, 100.0)

                    if best_signal is None or strength > best_signal.strength:
                        best_signal = PatternSignal(
                            name="FLAG_POLE",
                            strength=strength,
                            buy_point=round(buy_point, 2),
                            distance_from_buy_pct=round(distance_pct, 2),
                            breakout_level=round(breakout_ref, 2),
                            pivot_high=round(pole_high, 2),
                            pattern_stop_loss=round(flag_low * 0.99, 2),
                            pattern_target=round(buy_point + pole_gain, 2),
                        )
                        best_signal.pole_start_date = candles[pole_start].date
                        best_signal.pole_end_date = candles[pole_end].date
                        best_signal.pole_len = pole_len
                        best_signal.pole_gain_pct = round(pole_gain_pct, 2)
                        best_signal.pole_velocity = round(pole_velocity, 2)
                        best_signal.flag_len = len(flag_candles)
                        best_signal.flag_range_pct = round(flag_range_pct, 2)
                        best_signal.flag_slope_pct = round(flag_slope_pct, 4)

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
