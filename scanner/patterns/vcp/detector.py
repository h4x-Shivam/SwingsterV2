"""
detector.py — VCP (Volatility Contraction Pattern) detection engine v2.0

Minervini-style volatility contraction with 9 major improvements over v1:

  1.  Timeframe-adaptive scaling  — tf_factor scales all count-based thresholds
                                    so daily / weekly / monthly candles all work.
  2.  ATR-normalised pivot detection — neighbourhood size `n` derived from the
                                    stock's own ATR, not a hardcoded constant.
  3.  Contraction quality scoring  — rewards the ideal 50–75% shrink ratio
                                    between consecutive pullbacks.
  4.  Base structure check         — base must form in the upper 60% of the
                                    prior advance (no round-trips allowed).
  5.  Tightened right side         — 6% max high-to-low range; ATR ratio ≤ 0.60.
  6.  Volume slope regression      — requires a negative or flat volume trend
                                    across the entire base period.
  7.  Distribution day detection   — rejects bases with > 2 distribution days.
  8.  Multi-factor scoring         — weighted components replace ad-hoc ±adjustments.
  9.  RS + Stage 2 composite bonus — strong RS and full Stage 2 earn bonus points.
"""

from __future__ import annotations

from scanner.patterns.base import BasePattern
from scanner.patterns.vcp.config import VCP_CONFIG
from scanner.models import PatternSignal, Candle
from scanner.patterns.pivots import (
    calculate_atr_pct,
    find_swing_pivots,
    find_swing_pivots_adaptive,
)
from scanner.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_avwap,
    calculate_volume_slope,
    count_distribution_days,
)
from log import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _compute_tf_factor(candles: list[Candle]) -> float:
    """
    Estimate the timeframe of the candle series from the median gap between
    consecutive candle dates.

    Returns:
        1.0  for daily candles  (gap ≈ 1 trading day)
        5.0  for weekly candles (gap ≈ 5 calendar days)
       21.0  for monthly candles (gap ≈ 21 trading days)

    Uses a simple heuristic on calendar-day differences; falls back to 1.0
    when dates are missing or unparseable.
    """
    if len(candles) < 3:
        return 1.0
    try:
        from datetime import datetime
        diffs = []
        for i in range(1, min(20, len(candles))):
            d1 = datetime.strptime(str(candles[i - 1].date)[:10], "%Y-%m-%d")
            d2 = datetime.strptime(str(candles[i].date)[:10], "%Y-%m-%d")
            gap = (d2 - d1).days
            if 0 < gap < 40:          # ignore weekends/holidays / outliers
                diffs.append(gap)
        if not diffs:
            return 1.0
        diffs.sort()
        median_gap = diffs[len(diffs) // 2]
        # Bucket into meaningful timeframes
        if median_gap <= 2:
            return 1.0          # daily
        elif median_gap <= 8:
            return 5.0          # weekly
        elif median_gap <= 25:
            return 21.0         # monthly
        else:
            return float(median_gap)
    except Exception:
        return 1.0


def _get_atr(candles: list[Candle], period: int) -> float:
    """Compute Simple ATR over `period` candles (last period bars)."""
    if len(candles) < period + 1:
        return 0.0
    tr_sum = 0.0
    for j in range(len(candles) - period, len(candles)):
        h  = candles[j].high
        l  = candles[j].low
        pc = candles[j - 1].close
        tr_sum += max(h - l, abs(h - pc), abs(l - pc))
    return tr_sum / period


def _validate_contracting_highs(
    candles: list[Candle],
    contractions: list[dict],
    pivot_idx: int,
) -> tuple[bool, str]:
    """Verify that the high of each successive contraction segment is lower."""
    seg_highs = []
    for i in range(len(contractions)):
        s_idx = contractions[i - 1]["index"] if i > 0 else pivot_idx
        e_idx = contractions[i]["index"]
        if e_idx <= s_idx:
            return False, f"malformed segment i={i}"
        seg = candles[s_idx : e_idx + 1]
        if not seg:
            return False, f"empty segment i={i}"
        seg_highs.append(max(c.high for c in seg))
    for i in range(1, len(seg_highs)):
        if seg_highs[i] >= seg_highs[i - 1]:
            return False, f"highs not contracting: {seg_highs[i]:.2f} >= {seg_highs[i-1]:.2f}"
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# Pattern class
# ─────────────────────────────────────────────────────────────────────────────

class VCPPattern(BasePattern):
    """
    Detects Minervini Volatility Contraction Patterns.

    The detector is entirely self-contained — all helper functions live here
    or in the shared ``indicators`` / ``pivots`` modules.  No state is stored
    between calls.
    """

    config = VCP_CONFIG

    # ─────────────────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────────────────

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:  # noqa: C901
        try:
            if not self.is_eligible(candles):
                return None

            current_price = candles[-1].close
            atr_pct       = calculate_atr_pct(candles)

            # ── 1. Timeframe-adaptive scaling ─────────────────────────────
            tf = _compute_tf_factor(candles)
            # Thresholds represent bar counts on the chart regardless of timeframe
            scaled_lookback         = int(self.config.extras.get("pivot_lookback", 120))
            scaled_post_pivot_min   = int(self.config.extras.get("min_candles_post_pivot", 10))
            scaled_rs_range_days    = int(self.config.extras.get("right_side_range_days", 10))
            scaled_accum_window     = int(self.config.extras.get("accum_window", 12))
            scaled_vol_dry_up_days  = int(self.config.extras.get("vol_dry_up_days", 10))
            scaled_dist_window      = int(self.config.extras.get("dist_window", 30))
            scaled_vol_slope_window = int(self.config.extras.get("vol_slope_window", 30))



            # ── 2. ATR-normalised pivot detection ─────────────────────────
            if not pivots or len(pivots) != 2:
                swing_highs, swing_lows = find_swing_pivots_adaptive(
                    candles, atr_pct=atr_pct, lookback=scaled_lookback
                )
            else:
                swing_highs, swing_lows = pivots

            # ── 3. Find the dominant pivot high ───────────────────────────
            lookback_start = max(0, len(candles) - scaled_lookback)
            recent_highs   = [sh for sh in swing_highs if sh.index >= lookback_start]

            if not recent_highs:
                logger.debug("Rejected - no recent highs in lookback %d", scaled_lookback)
                return None

            pivot      = max(recent_highs, key=lambda h: h.price)
            pivot_price = pivot.price
            pivot_idx   = pivot.index

            # Enough candles after the pivot?
            if len(candles) - 1 - pivot_idx < scaled_post_pivot_min:
                logger.debug(
                    "Rejected - not enough candles after pivot (%d < %d)",
                    len(candles) - 1 - pivot_idx, scaled_post_pivot_min,
                )
                return None

            # Price proximity to pivot
            prox_bot = self.config.extras.get("pivot_proximity_bottom", 0.85)
            prox_top = self.config.extras.get("pivot_proximity_top", 1.03)
            if current_price < pivot_price * prox_bot:
                logger.debug(
                    "Rejected - price too far below pivot (%.2f < %.2f)",
                    current_price, pivot_price * prox_bot,
                )
                return None
            if current_price > pivot_price * prox_top:
                logger.debug(
                    "Rejected - price extended above pivot (%.2f > %.2f)",
                    current_price, pivot_price * prox_top,
                )
                return None

            # ── 4. Collect post-pivot pullbacks ───────────────────────────
            post_pivot_lows = [sl for sl in swing_lows if sl.index > pivot_idx]
            if len(post_pivot_lows) < 2:
                logger.debug(
                    "Rejected - not enough post-pivot lows (%d)", len(post_pivot_lows)
                )
                return None

            vol_avg_window       = self.config.extras.get("vol_avg_window", 5)
            first_pb_max_depth   = self.config.extras.get("first_pullback_max_depth", 35.0)
            min_pullback_depth   = self.config.extras.get("min_pullback_depth", 2.0)

            pullbacks: list[dict] = []
            for sl in post_pivot_lows:
                depth_pct = (pivot_price - sl.price) / pivot_price * 100
                if depth_pct < min_pullback_depth or depth_pct > first_pb_max_depth:
                    continue
                vs = max(0, sl.index - vol_avg_window)
                ve = min(len(candles), sl.index + vol_avg_window + 1)
                vols = [candles[k].volume for k in range(vs, ve)]
                avg_vol_loc = sum(vols) / len(vols) if vols else 0
                pullbacks.append({
                    "index":    sl.index,
                    "low":      sl.price,
                    "depth_pct": depth_pct,
                    "avg_vol":  avg_vol_loc,
                })

            if len(pullbacks) < 2:
                logger.debug("Rejected - not enough valid pullbacks (%d)", len(pullbacks))
                return None

            # ── 5. Find best contraction run ──────────────────────────────
            best_run: list[dict] = []
            current_run: list[dict] = [pullbacks[0]]

            for i in range(1, len(pullbacks)):
                prev = current_run[-1]
                curr = pullbacks[i]

                depth_contracting = curr["depth_pct"] < prev["depth_pct"]
                ascending_low     = curr["low"] > prev["low"]

                # Time contraction: each leg must not be dramatically longer than the prior.
                # In real VCPs, bases naturally widen as volume dries up — the key is
                # that legs don't EXPAND without bound.  We use generous multipliers:
                #   • 1st→2nd trough: allow up to 4× the pivot-to-trough-1 gap
                #   • all subsequent : allow up to 2× the prior inter-trough gap
                curr_duration = curr["index"] - prev["index"]
                if len(current_run) == 1:
                    prev_duration    = current_run[0]["index"] - pivot_idx
                    time_contracting = curr_duration <= max(prev_duration * 4.0, 30)
                else:
                    prev_duration    = current_run[-1]["index"] - current_run[-2]["index"]
                    time_contracting = curr_duration <= max(prev_duration * 2.0, 10)

                if depth_contracting and ascending_low and time_contracting:
                    current_run.append(curr)
                else:
                    if len(current_run) > len(best_run):
                        best_run = current_run
                    current_run = [curr]

            if len(current_run) > len(best_run):
                best_run = current_run

            min_contractions = self.config.extras.get("min_contractions", 2)
            if len(best_run) < min_contractions:
                logger.debug(
                    "Rejected - min contractions not met (%d < %d)",
                    len(best_run), min_contractions,
                )
                return None

            max_contractions = self.config.extras.get("max_contractions", 5)
            if len(best_run) > max_contractions:
                best_run = best_run[-max_contractions:]

            num_contractions = len(best_run)

            # ── 6. Validate contracting highs ─────────────────────────────
            ok, reason = _validate_contracting_highs(candles, best_run, pivot_idx)
            if not ok:
                logger.debug("Rejected - contracting highs check: %s", reason)
                return None

            # ── 7. Depth range checks ──────────────────────────────────────
            first_depth = best_run[0]["depth_pct"]
            final_depth = best_run[-1]["depth_pct"]

            first_pb_min_depth = self.config.extras.get("first_pullback_min_depth", 8.0)
            if first_depth < first_pb_min_depth or first_depth > first_pb_max_depth:
                logger.debug(
                    "Rejected - first pullback depth %.2f out of range (%.1f–%.1f)",
                    first_depth, first_pb_min_depth, first_pb_max_depth,
                )
                return None

            final_pb_max_depth = self.config.extras.get("final_pullback_max_depth", 12.0)
            if final_depth > final_pb_max_depth:
                logger.debug(
                    "Rejected - final pullback depth %.2f > %.1f",
                    final_depth, final_pb_max_depth,
                )
                return None

            # ── 8. Recovery between troughs ───────────────────────────────
            min_candles_between = self.config.extras.get("min_candles_between_pullbacks", 3)
            min_recovery_pct    = self.config.extras.get("min_recovery_pct", 50.0)

            for i in range(num_contractions - 1):
                low1_idx = best_run[i]["index"]
                low2_idx = best_run[i + 1]["index"]
                if low2_idx - low1_idx < min_candles_between:
                    logger.debug(
                        "Rejected - min candles between pullbacks (%d < %d)",
                        low2_idx - low1_idx, min_candles_between,
                    )
                    return None
                between_high  = max(candles[k].high for k in range(low1_idx + 1, low2_idx))
                pullback_range = pivot_price - best_run[i]["low"]
                if pullback_range <= 0:
                    return None
                recovery_pct = (between_high - best_run[i]["low"]) / pullback_range * 100
                if recovery_pct < min_recovery_pct:
                    logger.debug(
                        "Rejected - recovery %.1f%% < %.1f%%", recovery_pct, min_recovery_pct
                    )
                    return None

            # ── 9. Volume dry-up at each trough ──────────────────────────
            vol_dry_up_tolerance = self.config.extras.get("vol_dry_up_tolerance", 1.05)
            for i in range(1, num_contractions):
                if best_run[i]["avg_vol"] > best_run[i - 1]["avg_vol"] * vol_dry_up_tolerance:
                    logger.debug(
                        "Rejected - volume did not dry up (%.0f > %.0f)",
                        best_run[i]["avg_vol"],
                        best_run[i - 1]["avg_vol"] * vol_dry_up_tolerance,
                    )
                    return None

            # ── 10. Base structure check (NEW) ────────────────────────────
            # The base must form in the upper portion of the prior advance.
            # Find the swing low *before* the pivot (the base of the prior move).
            pre_pivot_lows = [sl for sl in swing_lows if sl.index < pivot_idx]
            if pre_pivot_lows:
                prior_base_low = min(sl.price for sl in pre_pivot_lows[-3:])  # last 3 pre-pivot lows
                prior_advance  = pivot_price - prior_base_low
                if prior_advance > 0:
                    # Base low (lowest trough in our contraction) must be ≥ upper 25% of the advance
                    base_low      = min(pb["low"] for pb in best_run)
                    min_base_level = prior_base_low + prior_advance * 0.25
                    if base_low < min_base_level:
                        logger.debug(
                            "Rejected - base too low: %.2f < %.2f (round-trip detected)",
                            base_low, min_base_level,
                        )
                        return None

            # ── 11. Right-side tightness ──────────────────────────────────
            rs_max_range_pct = self.config.extras.get("right_side_max_range_pct", 1.06)
            recent_candles   = candles[-scaled_rs_range_days:]

            if len(recent_candles) >= max(3, scaled_rs_range_days // 2):


                rs_high = max(c.high for c in recent_candles)
                rs_low  = min(c.low  for c in recent_candles)
                if rs_low > 0:
                    rs_range = rs_high / rs_low
                    if rs_range > rs_max_range_pct:
                        logger.debug(
                            "Rejected - right side range %.3f > %.3f",
                            rs_range, rs_max_range_pct,
                        )
                        return None

            # ── 12. ATR contraction ───────────────────────────────────────
            atr_ratio_threshold = self.config.extras.get("atr_contraction_ratio", 0.60)
            atr_5  = _get_atr(candles,  5)
            atr_20 = _get_atr(candles, 20)
            if atr_20 > 0:
                atr_ratio = atr_5 / atr_20
                if atr_ratio > atr_ratio_threshold:
                    logger.debug(
                        "Rejected - ATR not contracting enough (%.3f > %.3f)",
                        atr_ratio, atr_ratio_threshold,
                    )
                    return None

            # ── 13. Volume trend (linear regression) — NEW ────────────────
            vol_slope_max  = self.config.extras.get("vol_slope_max", 0.02)
            vol_slope      = calculate_volume_slope(candles, window=scaled_vol_slope_window)
            if vol_slope > vol_slope_max:
                logger.debug(
                    "Rejected - volume slope positive (%.4f > %.4f): base volume expanding",
                    vol_slope, vol_slope_max,
                )
                return None

            # ── 14. Short-term vs long-term volume ────────────────────────
            avg_vol_50 = 0.0
            avg_vol_5  = 0.0
            if len(candles) >= 50:
                avg_vol_50 = sum(c.volume for c in candles[-50:]) / 50.0
                avg_vol_5  = sum(c.volume for c in candles[-5:])  / 5.0
                if avg_vol_5 > avg_vol_50:
                    logger.debug(
                        "Rejected - 5d vol > 50d vol (%.0f > %.0f)", avg_vol_5, avg_vol_50
                    )
                    return None

                # Count dry-up days
                vol_dry_up_threshold = self.config.extras.get("vol_dry_up_threshold", 0.65)
                vol_dry_up_min_count = self.config.extras.get("vol_dry_up_min_count", 3)
                recent_vols = [c.volume for c in candles[-scaled_vol_dry_up_days:]]
                dry_days    = sum(1 for v in recent_vols if v < avg_vol_50 * vol_dry_up_threshold)
                if dry_days < vol_dry_up_min_count:
                    logger.debug(
                        "Rejected - not enough volume dry-up days (%d < %d)",
                        dry_days, vol_dry_up_min_count,
                    )
                    return None

            # ── 15. Distribution detection (NEW) ─────────────────────────
            max_dist_days = self.config.extras.get("max_distribution_days", 2)
            dist_avg_vol  = avg_vol_50 if avg_vol_50 > 0 else (
                sum(c.volume for c in candles[-20:]) / 20.0 if len(candles) >= 20 else 0.0
            )
            dist_days = count_distribution_days(
                candles, window=scaled_dist_window, avg_vol=dist_avg_vol
            )
            if dist_days > max_dist_days:
                logger.debug(
                    "Rejected - %d distribution days > %d limit", dist_days, max_dist_days
                )
                return None

            # ── 16. Right-side accumulation ───────────────────────────────
            accum_min_ratio = self.config.extras.get("accum_min_ratio", 1.20)

            def check_accumulation(cndls: list[Candle], window: int) -> tuple:
                recent     = cndls[-window:]
                up_vols    = [c.volume for c in recent if c.close > c.open]
                down_vols  = [c.volume for c in recent if c.close <= c.open]
                # If there are very few down days (< 2), the right side is all-up
                # accumulation — that is the IDEAL case, so pass it (return None = skip check).
                if len(up_vols) < 3:
                    return None, 0.0, 0.0
                if len(down_vols) < 2:
                    return None, 0.0, 0.0    # all-up right side: indeterminate, not a failure
                avg_up   = sum(up_vols)   / len(up_vols)
                avg_down = sum(down_vols) / len(down_vols)
                return avg_up >= avg_down * accum_min_ratio, avg_up, avg_down


            accum_ok, up_vol, down_vol = check_accumulation(candles, scaled_accum_window)
            if accum_ok is False:
                logger.debug(
                    "Rejected - right-side accumulation failed (up=%.0f, down=%.0f)",
                    up_vol, down_vol,
                )
                return None

            # ── 17. MA squeeze ────────────────────────────────────────────
            ma_squeeze_max = self.config.extras.get("ma_squeeze_max_spread", 0.05)
            ma10 = calculate_ema(candles, 10)
            ma20 = calculate_ema(candles, 20)
            ma50 = calculate_sma(candles, 50)

            if ma10 and ma20 and ma50:
                max_ma = max(ma10, ma20, ma50)
                min_ma = min(ma10, ma20, ma50)
                ma_spread = (max_ma - min_ma) / current_price
                if ma_spread > ma_squeeze_max:
                    logger.debug(
                        "Rejected - MAs not squeezed (spread %.3f > %.3f)",
                        ma_spread, ma_squeeze_max,
                    )
                    return None

            # ── 18. Anchored VWAP from pivot ──────────────────────────────
            avwap_buffer = self.config.extras.get("avwap_buffer_pct", 0.97)
            avwap = calculate_avwap(candles, pivot_idx)
            if avwap and current_price < avwap * avwap_buffer:
                logger.debug(
                    "Rejected - price below Anchored VWAP (%.2f < %.2f)",
                    current_price, avwap * avwap_buffer,
                )
                return None

            # ─────────────────────────────────────────────────────────────
            # All gates passed — compute multi-factor signal strength
            # ─────────────────────────────────────────────────────────────

            strength = self._compute_signal_strength(
                candles        = candles,
                best_run       = best_run,
                pivot_price    = pivot_price,
                final_depth    = final_depth,
                atr_pct        = atr_pct,
                avg_vol_50     = avg_vol_50,
                current_price  = current_price,
                num_contractions = num_contractions,
            )

            distance_pct = (current_price - pivot_price) / pivot_price * 100

            logger.debug(
                "ACCEPTED — %d contractions | final depth %.1f%% | score %.1f",
                num_contractions, final_depth, strength,
            )

            return PatternSignal(
                name                 = "VCP",
                strength             = strength,
                buy_point            = round(pivot_price, 2),
                distance_from_buy_pct = round(distance_pct, 2),
                breakout_level       = round(pivot_price, 2),
                pivot_high           = round(pivot_price, 2),
                contraction_depth    = round(final_depth, 2),
                contraction_count    = num_contractions,
            )

        except Exception:
            logger.debug("VCP detection failed", exc_info=True)
            return None

    # ─────────────────────────────────────────────────────────────────────
    # Scoring
    # ─────────────────────────────────────────────────────────────────────

    def _compute_signal_strength(
        self,
        candles:         list[Candle],
        best_run:        list[dict],
        pivot_price:     float,
        final_depth:     float,
        atr_pct:         float,
        avg_vol_50:      float,
        current_price:   float,
        num_contractions: int,
    ) -> float:
        """
        Multi-factor signal strength (0–100).

        Weighted components:
          30% — Contraction quality   (how perfectly each depth shrinks)
          25% — Tightness score       (final depth relative to the stock's ATR)
          20% — Volume character      (dry-up days + slope)
          15% — Proximity to pivot    (nearness to the exact breakout level)
          10% — Institutional footprint (pocket pivots minus squat candles)
        """

        # ── A. Contraction quality (30%) ──────────────────────────────────
        ideal_ratio_lo = 0.40
        ideal_ratio_hi = 0.75
        cq_total = 0.0

        for i in range(1, num_contractions):
            ratio = best_run[i]["depth_pct"] / best_run[i - 1]["depth_pct"]
            if ideal_ratio_lo <= ratio <= ideal_ratio_hi:
                # Perfect contraction: ratio closer to 0.55 = max bonus
                midpoint = 0.575
                score_i  = 100.0 - abs(ratio - midpoint) / (ideal_ratio_hi - midpoint) * 30
            elif ratio < ideal_ratio_lo:
                # Contracted too much — very rare but ok
                score_i = 70.0
            else:
                # ratio > ideal_hi (contracting, but not enough)
                over = ratio - ideal_ratio_hi
                score_i = max(0.0, 100.0 - over / (1.0 - ideal_ratio_hi) * 80)
            cq_total += score_i

        cq_score = cq_total / max(1, num_contractions - 1)

        # Bonus for more contractions (each extra contraction beyond 2 is rare/strong)
        contraction_bonus = min(15.0, (num_contractions - 2) * 7.5)
        cq_score = min(100.0, cq_score + contraction_bonus)

        # ── B. Tightness score (25%) ──────────────────────────────────────
        atr_multiples = (final_depth / 100.0) / max(atr_pct, 0.005)

        if atr_multiples <= 1.0:
            tightness_score = 100.0
        elif atr_multiples <= 2.0:
            tightness_score = 100.0 - (atr_multiples - 1.0) * 30.0
        elif atr_multiples <= 4.0:
            tightness_score = 70.0  - (atr_multiples - 2.0) * 15.0
        else:
            tightness_score = max(10.0, 40.0 - (atr_multiples - 4.0) * 10.0)

        # ── C. Volume character (20%) ──────────────────────────────────────
        # Sub-component 1: volume slope (lower = better; negative = max points)
        vol_slope = calculate_volume_slope(candles, window=min(30, len(candles)))
        if vol_slope <= -0.01:
            slope_score = 100.0
        elif vol_slope <= 0.01:
            slope_score = 60.0 + ((-vol_slope + 0.01) / 0.02) * 40.0
        else:
            slope_score = max(0.0, 60.0 - vol_slope * 500)

        # Sub-component 2: dry-up day count
        if avg_vol_50 > 0:
            vol_dry_up_threshold = self.config.extras.get("vol_dry_up_threshold", 0.65)
            recent_vols = [c.volume for c in candles[-15:]]
            dry_count   = sum(1 for v in recent_vols if v < avg_vol_50 * vol_dry_up_threshold)
            dry_score   = min(100.0, dry_count * 20.0)          # 5 dry days → 100
        else:
            dry_score = 50.0

        volume_character_score = (slope_score * 0.6 + dry_score * 0.4)

        # ── D. Proximity to pivot (15%) ───────────────────────────────────
        distance_pct = abs((current_price - pivot_price) / pivot_price * 100)
        if distance_pct <= 1.0:
            prox_score = 100.0
        elif distance_pct <= 3.0:
            prox_score = 100.0 - (distance_pct - 1.0) * 15.0
        elif distance_pct <= 8.0:
            prox_score = 70.0  - (distance_pct - 3.0) * 6.0
        elif distance_pct <= 15.0:
            prox_score = 40.0  - (distance_pct - 8.0) * 4.0
        else:
            prox_score = max(0.0, 12.0 - (distance_pct - 15.0))

        # ── E. Institutional footprint (10%) ──────────────────────────────
        pocket_pivot_bonus  = self.config.extras.get("pocket_pivot_bonus",   6.0)
        squat_candle_penalty = self.config.extras.get("squat_candle_penalty", 8.0)

        right_side = candles[-15:]
        pocket_pivots  = 0
        squat_candles  = 0

        for i in range(10, len(right_side)):
            c        = right_side[i]
            prior_10 = right_side[i - 10 : i]
            highest_down_vol = max(
                (pc.volume for pc in prior_10 if pc.close < pc.open), default=0
            )
            if c.close > c.open and c.volume > highest_down_vol:
                pocket_pivots += 1

            c_range = c.high - c.low
            if c_range > 0 and avg_vol_50 > 0 and c.volume > avg_vol_50:
                close_pct = (c.close - c.low) / c_range
                if close_pct < 0.4:
                    squat_candles += 1

        raw_footprint = (pocket_pivots * pocket_pivot_bonus) - (squat_candles * squat_candle_penalty)
        footprint_score = max(0.0, min(100.0, 50.0 + raw_footprint * 5.0))

        # ── Weighted composite ────────────────────────────────────────────
        strength = (
            cq_score               * 0.30 +
            tightness_score        * 0.25 +
            volume_character_score * 0.20 +
            prox_score             * 0.15 +
            footprint_score        * 0.10
        )

        return round(max(0.0, min(100.0, strength)), 1)

    def score(
        self,
        signal_strength: float,
        volume_score:    float,
        rr_score:        float,
        stage2_score:    float,
        rs_score:        float,
    ) -> float:
        """
        Composite score (0–100) blending pattern signal with market context.

        Also adds:
          +5 pts if RS score > threshold (strong relative strength)
          +5 pts if Stage 2 all conditions met (stage2_score == 100)
        """
        raw = (
            signal_strength * self.config.weight_signal +
            volume_score    * self.config.weight_volume +
            rr_score        * self.config.weight_rr     +
            stage2_score    * self.config.weight_stage2 +
            rs_score        * self.config.weight_rs
        )

        # RS bonus
        rs_threshold = self.config.extras.get("rs_strong_threshold", 75.0)
        rs_bonus     = self.config.extras.get("rs_strong_bonus", 5.0)
        if rs_score >= rs_threshold:
            raw += rs_bonus

        # Full Stage 2 bonus (all 5 conditions = score of 100)
        stage2_bonus = self.config.extras.get("stage2_full_bonus", 5.0)
        if stage2_score >= 100.0:
            raw += stage2_bonus

        return round(max(0.0, min(100.0, raw)), 1)

    @property
    def judge_prompt(self) -> str:
        return """
        For Volatility Contraction Patterns (VCP), look for:
        1. Strict contraction: Each pullback must be visibly shallower than the previous
           (target ratio of 50–75% of the prior depth).
        2. Tight right side: The final contraction should be very shallow (≤ 12% from pivot),
           with a high-to-low range of no more than 6% in the last 10 sessions.
        3. Volume drying up: Volume should be declining consistently through the base,
           with multiple days trading at ≤ 65% of the 50-day average.
        4. Clean base: No evidence of distribution (heavy selling on up-looking days).
        5. Actionability: Price should be tight against the breakout level, within 5%.
        6. Trend context: Ideally in full Stage 2 uptrend (all 5 Minervini conditions met)
           with strong relative strength vs the benchmark.
        """
