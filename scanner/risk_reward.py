"""
risk_reward.py — Support / Resistance identification and Risk-Reward ratio.

Uses swing-pivot analysis (n=3, lookback 20 candles) to find support/
resistance, then computes stop-loss (1% buffer below support), target
(nearest resistance above current price), and maps the RR ratio to a
0–100 score.
"""

from typing import Optional

from scanner.models import Candle, RiskReward


# ---------------------------------------------------------------------------
# Score breakpoints: (rr_ratio, score) — linear interpolation
# ---------------------------------------------------------------------------
_BREAKPOINTS: list[tuple[float, float]] = [
    (0.0,   0.0),
    (1.0,   0.0),
    (2.0,  30.0),
    (3.0,  60.0),
    (4.0,  80.0),
    (5.0, 100.0),
]


def _interpolate_score(ratio: float) -> float:
    """Map RR ratio → 0–100 score."""
    if ratio <= _BREAKPOINTS[0][0]:
        return _BREAKPOINTS[0][1]
    if ratio >= _BREAKPOINTS[-1][0]:
        return _BREAKPOINTS[-1][1]

    for i in range(len(_BREAKPOINTS) - 1):
        x0, y0 = _BREAKPOINTS[i]
        x1, y1 = _BREAKPOINTS[i + 1]
        if x0 <= ratio <= x1:
            t = (ratio - x0) / (x1 - x0) if (x1 - x0) > 0 else 0
            return y0 + t * (y1 - y0)

    return 0.0


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


def compute_risk_reward(candles: list[Candle]) -> RiskReward:
    """
    Compute risk-reward metrics for the symbol.

    Returns defaults (ratio=0, score=0) when fewer than 10 candles
    are available.
    """
    if len(candles) < 10:
        return RiskReward()

    current_price = candles[-1].close

    # Support: most recent swing low (n=3, lookback 20 candles)
    support = _find_swing_low(candles)
    if support is None:
        # Fallback: min low of last 20 candles
        lookback_start = max(0, len(candles) - 20)
        support = min(c.low for c in candles[lookback_start:])

    # Resistance: nearest swing high above current price
    resistance = _find_swing_high_above(candles, current_price)
    if resistance is None:
        # Fallback: max high of last 20 candles
        lookback_start = max(0, len(candles) - 20)
        resistance = max(c.high for c in candles[lookback_start:])

    # Stop loss: 1% buffer below support
    stop_loss = support * 0.99

    # Target: resistance level
    target = resistance

    # RR ratio: (target - entry) / (entry - stop_loss)
    denominator = current_price - stop_loss
    if denominator <= 0:
        ratio = 0.0
    else:
        ratio = (target - current_price) / denominator

    ratio = max(ratio, 0.0)

    score = _interpolate_score(ratio)

    return RiskReward(
        support=round(support, 2),
        resistance=round(resistance, 2),
        stop_loss=round(stop_loss, 2),
        target=round(target, 2),
        ratio=round(ratio, 2),
        score=round(score, 1),
    )
