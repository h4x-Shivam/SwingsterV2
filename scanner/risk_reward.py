"""
risk_reward.py — Support / Resistance identification and Risk-Reward ratio.

Uses swing-pivot analysis (n=3, lookback 20 candles) to find support/
resistance, then computes stop-loss (1% buffer below support), target
(nearest resistance above current price), and maps the RR ratio to a
0–100 score.
"""

from typing import Optional

from scanner.models import Candle, RiskReward


import logging

logger = logging.getLogger(__name__)

def _rr_to_score(ratio: float) -> float:
    if ratio < 0.8:  return 0.0
    if ratio < 1.5:  return 20.0
    if ratio < 2.0:  return 45.0
    if ratio < 3.0:  return 70.0
    if ratio < 4.0:  return 85.0
    return 100.0


def _find_swing_low(candles: list[Candle], n: int = 3) -> Optional[float]:
    """Find the most recent swing low in the last 20 candles."""
    start = max(0, len(candles) - 20)
    end = len(candles)

    for i in range(end - 1 - n, start + n - 1, -1):
        if i < n or i >= len(candles) - n:
            continue
        c_low = candles[i].low
        is_sl = True
        for j in range(i - n, i + n + 1):
            if j == i:
                continue
            if j < 0 or j >= len(candles):
                is_sl = False
                break
            if candles[j].low <= c_low:
                is_sl = False
                break
        if is_sl:
            return c_low

    return None


def _find_swing_high_above(candles: list[Candle], current_price: float, n: int = 3) -> Optional[float]:
    """Find the nearest swing high above current price."""
    best: Optional[float] = None

    start = max(0, len(candles) - 252)

    for i in range(start + n, len(candles) - n):
        c_high = candles[i].high
        if c_high <= current_price:
            continue

        is_sh = True
        for j in range(i - n, i + n + 1):
            if j == i:
                continue
            if candles[j].high >= c_high:
                is_sh = False
                break
        if is_sh:
            if best is None or c_high < best:
                best = c_high

    return best


def compute_risk_reward(
    candles: list[Candle],
    rr_hard_minimum: float = 0.8,
) -> RiskReward:
    """
    Compute risk-reward metrics for the symbol.
    """
    if len(candles) < 10:
        return RiskReward()

    entry = candles[-1].close

    # Support: most recent swing low (n=3, lookback 20 candles)
    support = _find_swing_low(candles)
    if support is None:
        # Fallback: min low of last 20 candles
        lookback_start = max(0, len(candles) - 20)
        support = min(c.low for c in candles[lookback_start:])

    # Stop loss: 1% buffer below support
    stop_loss = support * 0.99

    # HARD GUARD — stop must always be BELOW entry
    if stop_loss >= entry:
        stop_loss = min(c.low for c in candles[-20:]) * 0.99
        logger.debug(f"Inverted stop detected, using fallback stop: {stop_loss:.2f}")

    # Resistance / target: nearest swing high above entry
    resistance = _find_swing_high_above(candles, entry)
    if resistance is None:
        resistance = entry * 1.15

    # Target: resistance level
    target = resistance

    # HARD GUARD — target must always be ABOVE entry
    if target <= entry:
        target = entry * 1.15
        logger.debug(f"Inverted target detected, using fallback target: {target:.2f}")

    risk   = entry - stop_loss
    reward = target - entry

    if risk <= 0:
        return RiskReward(
            support=round(support, 2) if support else 0.0,
            resistance=round(resistance, 2) if resistance else 0.0,
            stop_loss=round(stop_loss, 2),
            target=round(target, 2),
            ratio=0.0,
            score=0.0,
        )

    ratio = reward / risk

    if ratio < rr_hard_minimum:
        return RiskReward(
            support=round(support, 2) if support else 0.0,
            resistance=round(resistance, 2) if resistance else 0.0,
            stop_loss=round(stop_loss, 2),
            target=round(target, 2),
            ratio=round(ratio, 2),
            score=0.0,
        )

    score = _rr_to_score(ratio)

    return RiskReward(
        support=round(support, 2) if support else 0.0,
        resistance=round(resistance, 2) if resistance else 0.0,
        stop_loss=round(stop_loss, 2),
        target=round(target, 2),
        ratio=round(ratio, 2),
        score=round(score, 1),
    )
