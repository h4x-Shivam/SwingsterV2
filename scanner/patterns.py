"""
patterns.py — Chart pattern detectors for SwingsterV2.

Detects 4 multi-day price-structure patterns:
  • VCP  (Volatility Contraction Pattern)
  • Pole & Flag
  • Cup & Handle
  • Horizontal Breakout

Each detector returns ``PatternSignal | None``.  The public entry point
``detect_patterns()`` runs all 4, collects hits, and returns the strongest.

Shared utility: ``find_swing_pivots()`` — used by all 4 detectors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from scanner.models import (
    Candle,
    PatternSignal,
    MIN_CANDLES_VCP,
    MIN_CANDLES_FLAG,
    MIN_CANDLES_CUP,
    MIN_CANDLES_BREAKOUT,
)


# ═══════════════════════════════════════════════════════════════════════════
# Swing Pivot Utility
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SwingHigh:
    index: int
    price: float

@dataclass
class SwingLow:
    index: int
    price: float


def find_swing_pivots(
    candles: list[Candle],
    n: int = 3,
) -> tuple[list[SwingHigh], list[SwingLow]]:
    """
    Identify swing highs and swing lows in the last 252 candles.

    A swing high at index *i* has ``candle[i].high > all candles within
    n candles on each side``.  Symmetric rule for swing lows with ``.low``.
    """
    # Limit to last 252 candles (1 year)
    start = max(0, len(candles) - 252)
    highs: list[SwingHigh] = []
    lows: list[SwingLow] = []

    for i in range(start + n, len(candles) - n):
        # --- swing high ---
        c_high = candles[i].high
        is_sh = True
        for j in range(i - n, i + n + 1):
            if j == i:
                continue
            if candles[j].high >= c_high:
                is_sh = False
                break
        if is_sh:
            highs.append(SwingHigh(index=i, price=c_high))

        # --- swing low ---
        c_low = candles[i].low
        is_sl = True
        for j in range(i - n, i + n + 1):
            if j == i:
                continue
            if candles[j].low <= c_low:
                is_sl = False
                break
        if is_sl:
            lows.append(SwingLow(index=i, price=c_low))

    return highs, lows


# ═══════════════════════════════════════════════════════════════════════════
# 5A — VCP (Volatility Contraction Pattern)
# ═══════════════════════════════════════════════════════════════════════════

def _detect_vcp(
    candles: list[Candle],
    pivots: tuple[list[SwingHigh], list[SwingLow]],
) -> Optional[PatternSignal]:
    """
    Detect a VCP: 2–4 successive contraction bases where each base's
    price range and volume shrink relative to the prior base.
    """
    if len(candles) < MIN_CANDLES_VCP:
        return None

    swing_highs, swing_lows = pivots

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return None

    # Build bases: pair each swing high with the nearest following swing low
    bases: list[dict] = []
    lo_idx = 0
    for sh in swing_highs:
        # find the first swing low AFTER this swing high
        while lo_idx < len(swing_lows) and swing_lows[lo_idx].index <= sh.index:
            lo_idx += 1
        if lo_idx >= len(swing_lows):
            break
        sl = swing_lows[lo_idx]

        base_range = sh.price - sl.price
        if base_range <= 0:
            continue

        # Avg volume between the high and low
        start_i = sh.index
        end_i = sl.index
        vols = [candles[k].volume for k in range(start_i, min(end_i + 1, len(candles)))]
        avg_vol = sum(vols) / len(vols) if vols else 0

        bases.append({
            "high": sh.price,
            "low": sl.price,
            "range": base_range,
            "avg_vol": avg_vol,
            "high_idx": sh.index,
            "low_idx": sl.index,
        })

    if len(bases) < 2:
        return None

    # Find the longest run of contracting bases (price + volume)
    best_run: list[dict] = []
    current_run: list[dict] = [bases[0]]

    for i in range(1, len(bases)):
        prev = current_run[-1]
        curr = bases[i]

        price_contracting = curr["range"] <= prev["range"] * 0.85
        vol_contracting = (
            curr["avg_vol"] < prev["avg_vol"] * 0.75
            if prev["avg_vol"] > 0
            else True
        )

        if price_contracting and vol_contracting:
            current_run.append(curr)
        else:
            if len(current_run) > len(best_run):
                best_run = current_run
            current_run = [curr]

    if len(current_run) > len(best_run):
        best_run = current_run

    num_contractions = len(best_run)
    if num_contractions < 2:
        return None

    # Cap at 4
    if num_contractions > 4:
        best_run = best_run[-4:]
        num_contractions = 4

    # Tight zone check: final contraction range ≤ 8% of current price
    current_price = candles[-1].close
    final_range = best_run[-1]["range"]
    final_range_pct = (final_range / current_price) * 100 if current_price > 0 else 999

    if final_range_pct > 8.0:
        return None

    # Buy point: highest high of last contraction + 0.10
    buy_point = best_run[-1]["high"] + 0.10
    distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

    # Signal strength scoring
    base_scores = {2: 50, 3: 70, 4: 90}
    strength = base_scores.get(num_contractions, 90)

    # Bonus: tight final zone (< 5%)
    if final_range_pct < 5.0:
        strength += 10
    elif final_range_pct < 6.5:
        strength += 5

    # Bonus: strong volume dry-up (< 50% of prior base)
    if num_contractions >= 2 and best_run[-2]["avg_vol"] > 0:
        vol_ratio = best_run[-1]["avg_vol"] / best_run[-2]["avg_vol"]
        if vol_ratio < 0.50:
            strength += 10
        elif vol_ratio < 0.65:
            strength += 5

    strength = min(strength, 100.0)

    return PatternSignal(
        name="vcp",
        strength=strength,
        buy_point=round(buy_point, 2),
        distance_from_buy_pct=round(distance_pct, 2),
        breakout_level=round(best_run[-1]["high"], 2),
        pivot_high=round(best_run[0]["high"], 2),
        contraction_depth=round(final_range_pct, 2),
        contraction_count=num_contractions,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 5B — Pole & Flag
# ═══════════════════════════════════════════════════════════════════════════

def _detect_pole_flag(
    candles: list[Candle],
    pivots: tuple[list[SwingHigh], list[SwingLow]],
) -> Optional[PatternSignal]:
    """
    Detect a Pole & Flag:
      Pole = impulsive ≥ 8% gain in ≤ 15 candles
      Flag = 5–20 candle consolidation, ≤ 35% retracement, flat/down slope,
             volume < 60% of pole avg.
    """
    if len(candles) < MIN_CANDLES_FLAG:
        return None

    # Scan for poles in the recent data (last 60 candles)
    lookback = min(len(candles), 60)
    start = len(candles) - lookback

    best_signal: Optional[PatternSignal] = None

    for i in range(start, len(candles) - 5):
        pole_low = candles[i].low
        if pole_low <= 0:
            continue

        # Try pole lengths 3–15
        for pole_len in range(3, min(16, len(candles) - i)):
            pole_end = i + pole_len
            if pole_end >= len(candles):
                break

            pole_high = max(c.high for c in candles[i : pole_end + 1])
            pole_gain_pct = ((pole_high - pole_low) / pole_low) * 100

            if pole_gain_pct < 8.0:
                continue

            # Pole found — look for flag after it
            pole_high_idx = i
            for k in range(i, pole_end + 1):
                if candles[k].high == pole_high:
                    pole_high_idx = k
                    break

            flag_start = pole_high_idx + 1
            if flag_start >= len(candles):
                continue

            # Try flag lengths 5–20
            for flag_len in range(5, min(21, len(candles) - flag_start + 1)):
                flag_end = flag_start + flag_len - 1
                if flag_end >= len(candles):
                    break

                flag_candles = candles[flag_start : flag_end + 1]

                # Flag retracement
                flag_low = min(c.low for c in flag_candles)
                retracement = pole_high - flag_low
                pole_gain = pole_high - pole_low
                retrace_pct = (retracement / pole_gain * 100) if pole_gain > 0 else 999

                if retrace_pct > 35.0:
                    continue

                # Flag slope: compute slope of closes (per candle)
                flag_closes = [c.close for c in flag_candles]
                if len(flag_closes) >= 2:
                    slope_per_candle = (flag_closes[-1] - flag_closes[0]) / (len(flag_closes) - 1)
                    avg_price = sum(flag_closes) / len(flag_closes)
                    slope_pct = (slope_per_candle / avg_price * 100) if avg_price > 0 else 0
                    if slope_pct > 0.1:  # upward sloping = invalid
                        continue
                else:
                    continue

                # Volume dry-up: flag vol < 60% of pole vol
                pole_vols = [candles[k].volume for k in range(i, pole_end + 1)]
                flag_vols = [c.volume for c in flag_candles]
                avg_pole_vol = sum(pole_vols) / len(pole_vols) if pole_vols else 1
                avg_flag_vol = sum(flag_vols) / len(flag_vols) if flag_vols else 0

                if avg_pole_vol > 0 and avg_flag_vol >= avg_pole_vol * 0.60:
                    continue

                # Valid pole & flag found
                current_price = candles[-1].close
                flag_high = max(c.high for c in flag_candles)
                buy_point = flag_high + 0.10
                distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

                # Strength scoring
                if pole_gain_pct >= 20:
                    strength = 90.0
                elif pole_gain_pct >= 12:
                    strength = 70.0
                else:
                    strength = 50.0

                # Bonus: tight flag (≤ 20% retracement)
                if retrace_pct <= 20:
                    strength += 10
                elif retrace_pct <= 25:
                    strength += 5

                # Bonus: volume dry-up
                if avg_pole_vol > 0:
                    vr = avg_flag_vol / avg_pole_vol
                    if vr < 0.30:
                        strength += 10
                    elif vr < 0.45:
                        strength += 5

                strength = min(strength, 100.0)

                if best_signal is None or strength > best_signal.strength:
                    best_signal = PatternSignal(
                        name="pole_flag",
                        strength=strength,
                        buy_point=round(buy_point, 2),
                        distance_from_buy_pct=round(distance_pct, 2),
                        breakout_level=round(flag_high, 2),
                        pivot_high=round(pole_high, 2),
                    )

            # If we found a strong signal, no need to keep searching
            if best_signal and best_signal.strength >= 90:
                return best_signal

    return best_signal


# ═══════════════════════════════════════════════════════════════════════════
# 5C — Cup & Handle
# ═══════════════════════════════════════════════════════════════════════════

def _detect_cup_handle(
    candles: list[Candle],
    pivots: tuple[list[SwingHigh], list[SwingLow]],
) -> Optional[PatternSignal]:
    """
    Detect a Cup & Handle:
      Cup  = U-shaped 30–150 candle base, 12–33% depth,
             right lip within 5% of left lip.
      Handle = 5–25 candle pullback ≤ 12% from right lip, above cup
               midpoint, flat/downward slope, volume dry-up vs cup.
    """
    if len(candles) < MIN_CANDLES_CUP:
        return None

    swing_highs, swing_lows = pivots

    if len(swing_highs) < 2 or len(swing_lows) < 1:
        return None

    best_signal: Optional[PatternSignal] = None

    # Look for left-lip (swing high) → cup bottom (swing low) → right lip (swing high)
    for lh_i, left_high in enumerate(swing_highs):
        left_lip = left_high.price
        if left_lip <= 0:
            continue

        # Find a swing low after the left lip (cup bottom)
        for sl in swing_lows:
            if sl.index <= left_high.index:
                continue

            cup_bottom = sl.price
            cup_depth_pct = ((left_lip - cup_bottom) / left_lip) * 100

            if cup_depth_pct < 12.0 or cup_depth_pct > 33.0:
                continue

            # Find a right lip (swing high after the cup bottom)
            for rh in swing_highs:
                if rh.index <= sl.index:
                    continue

                right_lip = rh.price

                # Cup duration
                cup_duration = rh.index - left_high.index
                if cup_duration < 30 or cup_duration > 150:
                    continue

                # Right lip recovery: within 5% of left lip
                lip_diff_pct = abs(right_lip - left_lip) / left_lip * 100
                if right_lip < left_lip * 0.95:
                    continue

                # Handle: look for pullback after right lip
                handle_start = rh.index + 1
                if handle_start >= len(candles):
                    continue

                remaining = len(candles) - handle_start
                if remaining < 5:
                    continue

                handle_len = min(remaining, 25)
                handle_candles = candles[handle_start : handle_start + handle_len]

                if len(handle_candles) < 5:
                    continue

                # Handle depth ≤ 12% from right lip
                handle_low = min(c.low for c in handle_candles)
                handle_depth_pct = ((right_lip - handle_low) / right_lip * 100) if right_lip > 0 else 999
                if handle_depth_pct > 12.0:
                    continue

                # Handle must be above cup midpoint
                cup_midpoint = (left_lip + cup_bottom) / 2
                if handle_low < cup_midpoint:
                    continue

                # Handle slope: downward or sideways (not upward)
                handle_closes = [c.close for c in handle_candles]
                if len(handle_closes) >= 2:
                    h_slope = (handle_closes[-1] - handle_closes[0]) / (len(handle_closes) - 1)
                    h_avg = sum(handle_closes) / len(handle_closes)
                    h_slope_pct = (h_slope / h_avg * 100) if h_avg > 0 else 0
                    if h_slope_pct > 0.1:
                        continue

                # Handle volume dry-up: < 70% of cup volume
                cup_start = left_high.index
                cup_end = rh.index
                cup_vols = [candles[k].volume for k in range(cup_start, min(cup_end + 1, len(candles)))]
                handle_vols = [c.volume for c in handle_candles]
                avg_cup_vol = sum(cup_vols) / len(cup_vols) if cup_vols else 1
                avg_handle_vol = sum(handle_vols) / len(handle_vols) if handle_vols else 0

                if avg_cup_vol > 0 and avg_handle_vol >= avg_cup_vol * 0.70:
                    continue

                # Valid cup & handle
                current_price = candles[-1].close
                handle_high = max(c.high for c in handle_candles)
                buy_point = handle_high + 0.10
                distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

                # Strength scoring
                strength = 0.0

                # U-shape smoothness: approximate by checking symmetry
                # (cup bottom near center of duration)
                cup_bottom_pos = (sl.index - left_high.index) / cup_duration if cup_duration > 0 else 0.5
                if 0.35 <= cup_bottom_pos <= 0.65:
                    strength += 30  # good U shape
                elif 0.25 <= cup_bottom_pos <= 0.75:
                    strength += 20
                else:
                    strength += 10

                # Right lip proximity to left lip
                if lip_diff_pct <= 3.0:
                    strength += 30
                else:
                    strength += 20

                # Handle slope valid (already checked)
                strength += 20

                # Volume dry-up in handle
                if avg_cup_vol > 0:
                    vol_ratio = avg_handle_vol / avg_cup_vol
                    if vol_ratio < 0.50:
                        strength += 20
                    elif vol_ratio < 0.60:
                        strength += 15
                    else:
                        strength += 10

                strength = min(strength, 100.0)

                if best_signal is None or strength > best_signal.strength:
                    best_signal = PatternSignal(
                        name="cup_handle",
                        strength=strength,
                        buy_point=round(buy_point, 2),
                        distance_from_buy_pct=round(distance_pct, 2),
                        breakout_level=round(handle_high, 2),
                        pivot_high=round(left_lip, 2),
                    )

    return best_signal


# ═══════════════════════════════════════════════════════════════════════════
# 5D — Horizontal Breakout
# ═══════════════════════════════════════════════════════════════════════════

def _detect_breakout(
    candles: list[Candle],
    pivots: tuple[list[SwingHigh], list[SwingLow]],
) -> Optional[PatternSignal]:
    """
    Detect a horizontal breakout:
      2+ swing highs within 2.5% of each other, spaced ≥ 10 days,
      current price within 3% below resistance,
      breakout candle volume ≥ 1.5× 20-day avg.
    """
    if len(candles) < MIN_CANDLES_BREAKOUT:
        return None

    swing_highs, _ = pivots

    if len(swing_highs) < 2:
        return None

    current_price = candles[-1].close
    current_volume = candles[-1].volume

    # 20-day average volume
    vol_20d = sum(c.volume for c in candles[-20:]) / min(20, len(candles))

    # Group swing highs into resistance zones (within 2.5% of each other)
    best_signal: Optional[PatternSignal] = None

    for i, anchor in enumerate(swing_highs):
        cluster = [anchor]
        resistance_level = anchor.price

        for j in range(i + 1, len(swing_highs)):
            other = swing_highs[j]
            diff_pct = abs(other.price - resistance_level) / resistance_level * 100

            if diff_pct <= 2.5:
                # Check minimum spacing: ≥ 10 trading days apart from all
                # existing cluster members
                min_spacing = min(abs(other.index - m.index) for m in cluster)
                if min_spacing >= 10:
                    cluster.append(other)

        num_tests = len(cluster)
        if num_tests < 2:
            continue

        # Compute average resistance level
        avg_resistance = sum(h.price for h in cluster) / len(cluster)

        # Proximity: current price within 3% below resistance
        distance_below = ((avg_resistance - current_price) / avg_resistance * 100) if avg_resistance > 0 else 999
        if distance_below < 0 or distance_below > 3.0:
            # If price is above resistance, it could be a breakout candle
            if current_price > avg_resistance:
                distance_below = 0.0
            else:
                continue

        # Breakout volume: ≥ 1.5× 20-day avg
        if vol_20d > 0 and current_volume < vol_20d * 1.5:
            continue

        # Valid breakout
        buy_point = avg_resistance + 0.10
        distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

        # Base duration: days between first and last test
        first_test = min(h.index for h in cluster)
        last_test = max(h.index for h in cluster)
        base_duration = last_test - first_test

        # Strength scoring
        if num_tests >= 4:
            strength = 90.0
        elif num_tests == 3:
            strength = 70.0
        else:
            strength = 50.0

        # Bonus: high volume on breakout candle
        if vol_20d > 0:
            vol_ratio = current_volume / vol_20d
            if vol_ratio >= 2.5:
                strength += 10
            elif vol_ratio >= 2.0:
                strength += 5

        # Bonus: long base duration (> 30 days)
        if base_duration > 50:
            strength += 10
        elif base_duration > 30:
            strength += 5

        strength = min(strength, 100.0)

        if best_signal is None or strength > best_signal.strength:
            best_signal = PatternSignal(
                name="breakout",
                strength=strength,
                buy_point=round(buy_point, 2),
                distance_from_buy_pct=round(distance_pct, 2),
                breakout_level=round(avg_resistance, 2),
                pivot_high=round(max(h.price for h in cluster), 2),
            )

    return best_signal


# ═══════════════════════════════════════════════════════════════════════════
# 5E — Entry Point
# ═══════════════════════════════════════════════════════════════════════════

def detect_patterns(candles: list[Candle], mode: str = "ALL") -> Optional[PatternSignal]:
    """
    Run the selected pattern detectors based on the mode, return the signal
    with the highest ``strength`` score, or ``None`` if no pattern is found.
    """
    pivots = find_swing_pivots(candles)  # always runs unconditionally

    signals: list[PatternSignal] = []

    if mode in ("VCP", "ALL"):
        sig = _detect_vcp(candles, pivots)
        if sig:
            signals.append(sig)

    if mode in ("FLAG_POLE", "ALL"):
        sig = _detect_pole_flag(candles, pivots)
        if sig:
            signals.append(sig)

    if mode in ("CUP_HANDLE", "ALL"):
        sig = _detect_cup_handle(candles, pivots)
        if sig:
            signals.append(sig)

    if mode in ("BREAKOUT", "ALL"):
        sig = _detect_breakout(candles, pivots)
        if sig:
            signals.append(sig)

    if not signals:
        return None

    return max(signals, key=lambda s: s.strength)
