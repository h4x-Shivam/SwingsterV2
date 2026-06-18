from scanner.patterns.base import BasePattern
from scanner.patterns.vcp.config import VCP_CONFIG
from scanner.models import PatternSignal, Candle
from typing import List, Tuple, Dict, Any, Optional

def count_touches_near_level(candles: list[Candle], level_price: float, tolerance_pct: float = 0.015) -> int:
    """Count how many candles had a high within tolerance_pct of level_price."""
    count = 0
    for c in candles:
        if abs(c.high - level_price) / level_price <= tolerance_pct:
            count += 1
    return count

def get_volume_at_pivot(candles: list[Candle], pivot_index: int, window: int = 3) -> float:
    """Average volume in the few candles surrounding the pivot high."""
    start = max(0, pivot_index - window)
    end = min(len(candles), pivot_index + window + 1)
    nearby = candles[start:end]
    return sum(c.volume for c in nearby) / len(nearby) if nearby else 0

def find_candidate_pivots(
    recent_candles: list[Candle],
    recent_highs: list,
    min_separation_pct: float = 0.03,
    min_touch_count: int = 2,
    max_candidates: int = 4
) -> list:
    """
    Identify multiple swing-high candidates within the lookback window,
    instead of only the single absolute maximum. This allows the detector
    to recognize secondary/nested bases that form below an older, higher
    peak.

    Returns candidates ordered by recency (most recent first).
    """
    # GUARDRAIL 1: Require minimum touch count.
    filtered_highs = [
        sh for sh in recent_highs
        if count_touches_near_level(recent_candles, sh.price, tolerance_pct=0.015) >= min_touch_count
    ]

    # GUARDRAIL 2: Deduplicate clustered pivots.
    swing_highs_sorted = sorted(filtered_highs, key=lambda h: h.index, reverse=True)
    candidates = []
    for sh in swing_highs_sorted:
        is_distinct = all(
            abs(sh.price - c.price) / c.price > min_separation_pct
            for c in candidates
        )
        if is_distinct:
            candidates.append(sh)

    return candidates[:max_candidates]

def classify_vcp_subtype(initial_pullback_depth_pct: float) -> str:
    """Classifies the VCP based on the depth of the initial flush."""
    if initial_pullback_depth_pct >= 0.12:
        return "VCP_CLASSIC"
    else:
        return "VCP_FLAT_BASE"

def is_forgivable_wick(candles: List[Candle], pivot_price: float, spike_high_idx: int, max_reversion_candles: int = 15) -> Tuple[bool, float]:
    """
    Determines whether an excursion above the pivot was a brief wick (forgivable)
    or a sustained breakout that held above the pivot (not forgivable).
    """
    spike_candle = candles[spike_high_idx]
    excursion_pct = (spike_candle.high - pivot_price) / pivot_price

    for offset in range(1, max_reversion_candles + 1):
        if spike_high_idx + offset >= len(candles):
            break
        if candles[spike_high_idx + offset].close < pivot_price:
            return True, excursion_pct
            
    return False, excursion_pct

class VCPPattern(BasePattern):

    config = VCP_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        """
        Volatility Contraction Pattern
        """
        try:
            if not self.is_eligible(candles):
                return None

            swing_highs, swing_lows = pivots

            # 1. Find candidate pivots
            lookback = self.config.extras.setdefault("pivot_lookback", 120)
            lookback_start = max(0, len(candles) - lookback)
            recent_candles = candles[lookback_start:]
            recent_highs = [sh for sh in swing_highs if sh.index >= lookback_start]

            if not recent_highs:
                return None

            candidates = find_candidate_pivots(
                recent_candles=recent_candles,
                recent_highs=recent_highs,
                min_separation_pct=0.03,
                min_touch_count=2,
                max_candidates=4
            )

            if not candidates:
                return None

            valid_results = []
            
            for pivot in candidates:
                result = self._evaluate_vcp_against_pivot(candles, swing_lows, pivot)
                if result is not None:
                    valid_results.append((pivot, result))
                    
            if not valid_results:
                return None
                
            # Secondary Enhancement: If multiple candidates produce valid VCPs, 
            # prefer the pivot where the high was made on declining or average volume.
            if len(valid_results) > 1:
                valid_results.sort(key=lambda x: get_volume_at_pivot(candles, x[0].index))
                
            return valid_results[0][1]

        except Exception:
            return None

    def _evaluate_vcp_against_pivot(self, candles: list[Candle], swing_lows: list, pivot) -> PatternSignal | None:
        current_price = candles[-1].close
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

        # --- GUARDRAIL 1: Wick vs Breakout ---
        post_pivot_excursions = []
        for i in range(pivot_idx + 1, len(candles)):
            if candles[i].high > pivot_price:
                post_pivot_excursions.append(i)
                
        for spike_idx in post_pivot_excursions:
            is_forgivable, exc_pct = is_forgivable_wick(candles, pivot_price, spike_idx, max_reversion_candles=15)
            if not is_forgivable and exc_pct > 0.01:
                return None

        # 2. Collect pullback troughs
        post_pivot_lows = [sl for sl in swing_lows if sl.index > pivot_idx]
        if len(post_pivot_lows) < 2:
            return None

        first_pullback_max_depth = self.config.extras.setdefault("first_pullback_max_depth", 35.0)
        min_pullback_depth = self.config.extras.setdefault("min_pullback_depth", 1.5)
        vol_avg_window = self.config.extras.setdefault("vol_avg_window", 5)

        pullbacks: list[dict] = []
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
            best_run = best_run[:max_contractions + 1]
            num_contractions = len(best_run)

        # --- GUARDRAIL 4: No Volatility Expansion ---
        for sl in pullbacks:
            if sl["index"] > best_run[-1]["index"]:
                if sl["depth_pct"] >= best_run[-1]["depth_pct"]:
                    return None

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
        is_valid = True

        for i in range(len(best_run) - 1):
            low1_idx = best_run[i]["index"]
            low2_idx = best_run[i + 1]["index"]

            if low2_idx - low1_idx < min_candles_between:
                is_valid = False
                break

            between_high = max(
                candles[k].high for k in range(low1_idx + 1, low2_idx)
            )

            pullback_range = pivot_price - best_run[i]["low"]
            if pullback_range <= 0:
                is_valid = False
                break

            recovery_pct = (
                (between_high - best_run[i]["low"]) / pullback_range * 100
            )
            if recovery_pct < min_recovery_pct:
                is_valid = False
                break
        if not is_valid:
            return None

        # --- GUARDRAIL 2: Tight right side ---
        tight_zone_pct = self.config.extras.setdefault("tight_zone_pct", 0.08)
        final_pullback_depth = best_run[-1]["depth_pct"] / 100.0
        if final_pullback_depth > tight_zone_pct:
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

        # --- GUARDRAIL 3: Subtype Classification ---
        initial_depth = best_run[0]["depth_pct"] / 100.0
        subtype = classify_vcp_subtype(initial_depth)

        return PatternSignal(
            name=subtype,
            strength=strength,
            buy_point=round(buy_point, 2),
            distance_from_buy_pct=round(distance_pct, 2),
            breakout_level=round(pivot_price, 2),
            pivot_high=round(pivot_price, 2),
            contraction_depth=round(final_depth, 2),
            contraction_count=num_contractions,
        )

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

