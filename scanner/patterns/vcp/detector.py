from scanner.patterns.base import BasePattern
from scanner.patterns.vcp.config import VCP_CONFIG
from scanner.models import PatternSignal, Candle

class VCPPattern(BasePattern):

    config = VCP_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        """
        Volatility Contraction Pattern
        Algorithm moved from scanner/patterns.py verbatim.
        """
        try:
            if not self.is_eligible(candles):
                return None

            swing_highs, swing_lows = pivots
            current_price = candles[-1].close

            # 1. Find the pivot
            lookback = self.config.extras.setdefault("pivot_lookback", 120)
            lookback_start = max(0, len(candles) - lookback)
            recent_highs = [sh for sh in swing_highs if sh.index >= lookback_start]

            if not recent_highs:
                return None

            pivot = max(recent_highs, key=lambda h: h.price)
            pivot_price = pivot.price
            pivot_idx = pivot.index

            min_candles_post_pivot = self.config.extras.setdefault("min_candles_post_pivot", 10)
            if len(candles) - 1 - pivot_idx < min_candles_post_pivot:
                return None

            pivot_proximity_bottom = self.config.extras.setdefault("pivot_proximity_bottom", 0.80)
            if current_price < pivot_price * pivot_proximity_bottom:
                return None

            pivot_proximity_top = self.config.extras.setdefault("pivot_proximity_top", 1.03)
            if current_price > pivot_price * pivot_proximity_top:
                return None

            # 2. Collect pullback troughs
            post_pivot_lows = [sl for sl in swing_lows if sl.index > pivot_idx]
            if len(post_pivot_lows) < 2:
                return None

            first_pullback_max_depth = self.config.extras.setdefault("first_pullback_max_depth", 35.0)
            vol_avg_window = self.config.extras.setdefault("vol_avg_window", 5)

            pullbacks: list[dict] = []
            for sl in post_pivot_lows:
                depth_pct = (pivot_price - sl.price) / pivot_price * 100
                if depth_pct <= 0 or depth_pct > first_pullback_max_depth:
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
                return None

            # 3. Find the longest run of contracting depths with ascending lows
            best_run: list[dict] = []
            current_run: list[dict] = [pullbacks[0]]

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
                return None

            max_contractions = self.config.extras.get("max_contractions", 4)
            if num_contractions > max_contractions:
                best_run = best_run[-max_contractions:]
                num_contractions = max_contractions

            # 4. Validate pullback depths
            first_depth = best_run[0]["depth_pct"]
            final_depth = best_run[-1]["depth_pct"]

            first_pullback_min_depth = self.config.extras.setdefault("first_pullback_min_depth", 8.0)
            if first_depth < first_pullback_min_depth or first_depth > first_pullback_max_depth:
                return None

            final_pullback_max_depth = self.config.extras.setdefault("final_pullback_max_depth", 15.0)
            if final_depth > final_pullback_max_depth:
                return None

            # 5. Rally-back check
            min_candles_between = self.config.extras.setdefault("min_candles_between_pullbacks", 3)
            min_recovery_pct = self.config.extras.setdefault("min_recovery_pct", 50.0)

            for i in range(len(best_run) - 1):
                low1_idx = best_run[i]["index"]
                low2_idx = best_run[i + 1]["index"]

                if low2_idx - low1_idx < min_candles_between:
                    return None

                between_high = max(
                    candles[k].high for k in range(low1_idx + 1, low2_idx)
                )

                pullback_range = pivot_price - best_run[i]["low"]
                if pullback_range <= 0:
                    return None

                recovery_pct = (
                    (between_high - best_run[i]["low"]) / pullback_range * 100
                )
                if recovery_pct < min_recovery_pct:
                    return None

            # 6. Volume dry-up
            vol_dry_up = True
            vol_dry_up_multiplier = self.config.extras.setdefault("vol_dry_up_multiplier", 1.2)
            for i in range(1, len(best_run)):
                if best_run[i]["avg_vol"] > best_run[i - 1]["avg_vol"] * vol_dry_up_multiplier:
                    vol_dry_up = False
                    break

            # 7. Buy point & distance
            buy_point_buffer = self.config.extras.setdefault("buy_point_buffer", 0.10)
            buy_point = pivot_price + buy_point_buffer
            distance_pct = (
                ((buy_point - current_price) / current_price * 100)
                if current_price > 0
                else 0
            )

            # 8. Signal strength scoring
            base_scores = {2: 50, 3: 70, 4: 90}
            strength = float(base_scores.get(num_contractions, 90))

            bonus_tight_5 = self.config.extras.setdefault("bonus_tight_final_depth_5", 5.0)
            bonus_tight_8 = self.config.extras.setdefault("bonus_tight_final_depth_8", 8.0)
            if final_depth < bonus_tight_5:
                strength += 10
            elif final_depth < bonus_tight_8:
                strength += 5

            if vol_dry_up:
                strength += 10

            bonus_ratio = self.config.extras.setdefault("bonus_contraction_ratio", 0.3)
            if first_depth > 0 and final_depth / first_depth < bonus_ratio:
                strength += 5

            penalty_dist = self.config.extras.setdefault("penalty_distance_pct", 10.0)
            if distance_pct > penalty_dist:
                strength -= 10
            elif distance_pct < 0:
                strength += 5

            strength = max(0.0, min(strength, 100.0))

            return PatternSignal(
                name="VCP",
                strength=strength,
                buy_point=round(buy_point, 2),
                distance_from_buy_pct=round(distance_pct, 2),
                breakout_level=round(pivot_price, 2),
                pivot_high=round(pivot_price, 2),
                contraction_depth=round(final_depth, 2),
                contraction_count=num_contractions,
            )

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
        For Volatility Contraction Patterns (VCP), look for:
        1. Well-defined pivot resistance.
        2. Progressively shallower pullbacks.
        3. Volume dry-up near the right side of the base.
        4. Tight price action before the breakout.
        """
