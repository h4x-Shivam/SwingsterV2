from scanner.patterns.base import BasePattern
from scanner.patterns.breakout.config import BREAKOUT_CONFIG
from scanner.models import PatternSignal, Candle

class BreakoutPattern(BasePattern):

    config = BREAKOUT_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        try:
            if not self.is_eligible(candles):
                return None

            swing_highs, _ = pivots

            min_resistance_tests = self.config.extras.setdefault("min_resistance_tests", 2)
            if len(swing_highs) < min_resistance_tests:
                return None

            current_price = candles[-1].close
            current_volume = candles[-1].volume

            vol_avg_window = self.config.extras.setdefault("vol_avg_window", 20)
            vol_20d = sum(c.volume for c in candles[-vol_avg_window:]) / min(vol_avg_window, len(candles))

            best_signal = None

            resistance_tolerance_pct = self.config.extras.setdefault("resistance_tolerance_pct", 2.5)
            min_test_spacing_days = self.config.extras.setdefault("min_test_spacing_days", 10)
            proximity_to_resistance = self.config.extras.setdefault("proximity_to_resistance", 3.0)
            breakout_vol_multiplier = self.config.extras.setdefault("breakout_vol_multiplier", 1.5)
            buy_point_buffer = self.config.extras.setdefault("buy_point_buffer", 0.10)

            for i, anchor in enumerate(swing_highs):
                cluster = [anchor]
                resistance_level = anchor.price

                for j in range(i + 1, len(swing_highs)):
                    other = swing_highs[j]
                    diff_pct = abs(other.price - resistance_level) / resistance_level * 100

                    if diff_pct <= resistance_tolerance_pct:
                        min_spacing = min(abs(other.index - m.index) for m in cluster)
                        if min_spacing >= min_test_spacing_days:
                            cluster.append(other)

                num_tests = len(cluster)
                if num_tests < min_resistance_tests:
                    continue

                avg_resistance = sum(h.price for h in cluster) / len(cluster)

                distance_below = ((avg_resistance - current_price) / avg_resistance * 100) if avg_resistance > 0 else 999
                if distance_below < 0 or distance_below > proximity_to_resistance:
                    if current_price > avg_resistance:
                        distance_below = 0.0
                    else:
                        continue

                if vol_20d > 0 and current_volume < vol_20d * breakout_vol_multiplier:
                    continue

                buy_point = avg_resistance + buy_point_buffer
                distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

                first_test = min(h.index for h in cluster)
                last_test = max(h.index for h in cluster)
                base_duration = last_test - first_test

                tests_for_90_score = self.config.extras.setdefault("tests_for_90_score", 4)
                tests_for_70_score = self.config.extras.setdefault("tests_for_70_score", 3)

                if num_tests >= tests_for_90_score:
                    strength = 90.0
                elif num_tests == tests_for_70_score:
                    strength = 70.0
                else:
                    strength = 50.0

                bonus_vol_ratio_25 = self.config.extras.setdefault("bonus_vol_ratio_25", 2.5)
                bonus_vol_ratio_20 = self.config.extras.setdefault("bonus_vol_ratio_20", 2.0)

                if vol_20d > 0:
                    vol_ratio = current_volume / vol_20d
                    if vol_ratio >= bonus_vol_ratio_25:
                        strength += 10
                    elif vol_ratio >= bonus_vol_ratio_20:
                        strength += 5

                bonus_base_duration_50 = self.config.extras.setdefault("bonus_base_duration_50", 50)
                bonus_base_duration_30 = self.config.extras.setdefault("bonus_base_duration_30", 30)

                if base_duration > bonus_base_duration_50:
                    strength += 10
                elif base_duration > bonus_base_duration_30:
                    strength += 5

                strength = min(strength, 100.0)

                if best_signal is None or strength > best_signal.strength:
                    best_signal = PatternSignal(
                        name="BREAKOUT",
                        strength=strength,
                        buy_point=round(buy_point, 2),
                        distance_from_buy_pct=round(distance_pct, 2),
                        breakout_level=round(avg_resistance, 2),
                        pivot_high=round(max(h.price for h in cluster), 2),
                    )

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
        For Horizontal Breakout patterns, look for:
        1. A clear, tested horizontal resistance level (multiple touches).
        2. Strong volume expansion exactly on the breakout candle.
        3. A well-defined base preceding the breakout.
        4. No overhead supply immediately above the breakout level.
        """
