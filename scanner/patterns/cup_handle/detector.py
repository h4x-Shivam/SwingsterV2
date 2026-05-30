from scanner.patterns.base import BasePattern
from scanner.patterns.cup_handle.config import CUP_HANDLE_CONFIG
from scanner.models import PatternSignal, Candle

class CupHandlePattern(BasePattern):

    config = CUP_HANDLE_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        try:
            if not self.is_eligible(candles):
                return None

            swing_highs, swing_lows = pivots

            if len(swing_highs) < 2 or len(swing_lows) < 1:
                return None

            best_signal = None

            min_cup_depth_pct = self.config.extras.setdefault("min_cup_depth_pct", 12.0)
            max_cup_depth_pct = self.config.extras.setdefault("max_cup_depth_pct", 33.0)
            min_cup_candles = self.config.extras.setdefault("min_cup_candles", 30)
            max_cup_candles = self.config.extras.setdefault("max_cup_candles", 150)
            lip_tolerance_bottom_pct = self.config.extras.setdefault("lip_tolerance_bottom_pct", 0.95)
            min_handle_candles = self.config.extras.setdefault("min_handle_candles", 5)
            max_handle_candles = self.config.extras.setdefault("max_handle_candles", 25)
            max_handle_drop_pct = self.config.extras.setdefault("max_handle_drop_pct", 12.0)
            max_handle_slope_pct = self.config.extras.setdefault("max_handle_slope_pct", 0.1)
            vol_handle_factor = self.config.extras.setdefault("vol_handle_factor", 0.70)
            buy_point_buffer = self.config.extras.setdefault("buy_point_buffer", 0.10)

            for lh_i, left_high in enumerate(swing_highs):
                left_lip = left_high.price
                if left_lip <= 0:
                    continue

                for sl in swing_lows:
                    if sl.index <= left_high.index:
                        continue

                    cup_bottom = sl.price
                    cup_depth_pct = ((left_lip - cup_bottom) / left_lip) * 100

                    if cup_depth_pct < min_cup_depth_pct or cup_depth_pct > max_cup_depth_pct:
                        continue

                    for rh in swing_highs:
                        if rh.index <= sl.index:
                            continue

                        right_lip = rh.price

                        cup_duration = rh.index - left_high.index
                        if cup_duration < min_cup_candles or cup_duration > max_cup_candles:
                            continue

                        lip_diff_pct = abs(right_lip - left_lip) / left_lip * 100
                        if right_lip < left_lip * lip_tolerance_bottom_pct:
                            continue

                        handle_start = rh.index + 1
                        if handle_start >= len(candles):
                            continue

                        remaining = len(candles) - handle_start
                        if remaining < min_handle_candles:
                            continue

                        handle_len = min(remaining, max_handle_candles)
                        handle_candles = candles[handle_start : handle_start + handle_len]

                        if len(handle_candles) < min_handle_candles:
                            continue

                        handle_low = min(c.low for c in handle_candles)
                        handle_depth_pct = ((right_lip - handle_low) / right_lip * 100) if right_lip > 0 else 999
                        if handle_depth_pct > max_handle_drop_pct:
                            continue

                        cup_midpoint = (left_lip + cup_bottom) / 2
                        if handle_low < cup_midpoint:
                            continue

                        handle_closes = [c.close for c in handle_candles]
                        if len(handle_closes) >= 2:
                            h_slope = (handle_closes[-1] - handle_closes[0]) / (len(handle_closes) - 1)
                            h_avg = sum(handle_closes) / len(handle_closes)
                            h_slope_pct = (h_slope / h_avg * 100) if h_avg > 0 else 0
                            if h_slope_pct > max_handle_slope_pct:
                                continue

                        cup_start = left_high.index
                        cup_end = rh.index
                        cup_vols = [candles[k].volume for k in range(cup_start, min(cup_end + 1, len(candles)))]
                        handle_vols = [c.volume for c in handle_candles]
                        avg_cup_vol = sum(cup_vols) / len(cup_vols) if cup_vols else 1
                        avg_handle_vol = sum(handle_vols) / len(handle_vols) if handle_vols else 0

                        if avg_cup_vol > 0 and avg_handle_vol >= avg_cup_vol * vol_handle_factor:
                            continue

                        current_price = candles[-1].close
                        handle_high = max(c.high for c in handle_candles)
                        buy_point = handle_high + buy_point_buffer
                        distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

                        strength = 0.0

                        cup_bottom_pos = (sl.index - left_high.index) / cup_duration if cup_duration > 0 else 0.5
                        shape_sym_bottom_inner = self.config.extras.setdefault("shape_sym_bottom_inner", 0.35)
                        shape_sym_top_inner = self.config.extras.setdefault("shape_sym_top_inner", 0.65)
                        shape_sym_bottom_outer = self.config.extras.setdefault("shape_sym_bottom_outer", 0.25)
                        shape_sym_top_outer = self.config.extras.setdefault("shape_sym_top_outer", 0.75)

                        if shape_sym_bottom_inner <= cup_bottom_pos <= shape_sym_top_inner:
                            strength += 30
                        elif shape_sym_bottom_outer <= cup_bottom_pos <= shape_sym_top_outer:
                            strength += 20
                        else:
                            strength += 10

                        bonus_lip_diff_3 = self.config.extras.setdefault("bonus_lip_diff_3", 3.0)
                        if lip_diff_pct <= bonus_lip_diff_3:
                            strength += 30
                        else:
                            strength += 20

                        strength += 20

                        bonus_vol_ratio_50 = self.config.extras.setdefault("bonus_vol_ratio_50", 0.50)
                        bonus_vol_ratio_60 = self.config.extras.setdefault("bonus_vol_ratio_60", 0.60)
                        if avg_cup_vol > 0:
                            vol_ratio = avg_handle_vol / avg_cup_vol
                            if vol_ratio < bonus_vol_ratio_50:
                                strength += 20
                            elif vol_ratio < bonus_vol_ratio_60:
                                strength += 15
                            else:
                                strength += 10

                        strength = min(strength, 100.0)

                        if best_signal is None or strength > best_signal.strength:
                            best_signal = PatternSignal(
                                name="CUP_HANDLE",
                                strength=strength,
                                buy_point=round(buy_point, 2),
                                distance_from_buy_pct=round(distance_pct, 2),
                                breakout_level=round(handle_high, 2),
                                pivot_high=round(left_lip, 2),
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
        For Cup & Handle patterns, look for:
        1. A smooth, U-shaped cup (not a V-shaped sharp drop).
        2. Depth between 12% and 33% (too shallow = not a base, too deep = broken trend).
        3. A shallow handle that drifts downward on light volume.
        4. The handle must stay above the midpoint of the cup.
        """
