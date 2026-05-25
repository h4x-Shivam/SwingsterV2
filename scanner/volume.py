"""
volume.py — Volume analysis for SwingsterV2.

Computes:
  • 20-day volume SMA and relative volume ratio
  • Volume spike detection (ratio > 1.5)
  • Volume trend (5d vs 20d SMA)
  • Minimum liquidity filter (avg vol < 50k → illiquid)
  • Volume score 0–100 from ratio breakpoints
"""

from scanner.models import Candle, VolumeMetrics


# ---------------------------------------------------------------------------
# Score breakpoints: (ratio, score) — linear interpolation between them
# ---------------------------------------------------------------------------
_BREAKPOINTS: list[tuple[float, float]] = [
    (0.0,  30.0),
    (1.0,  60.0),
    (1.5,  80.0),
    (2.0, 100.0),
]


def _interpolate_score(ratio: float) -> float:
    """Map relative volume ratio → score with linear interpolation."""
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

    return 30.0  # fallback


def analyze_volume(candles: list[Candle]) -> VolumeMetrics:
    """
    Compute volume metrics for the symbol.

    Returns defaults (ratio=1.0, score=0) when fewer than 20 candles
    are available.
    """
    if len(candles) < 20:
        return VolumeMetrics()

    volumes = [c.volume for c in candles]

    # 20-day SMA
    avg_20d = sum(volumes[-20:]) / 20

    # Liquidity filter
    if avg_20d < 50_000:
        return VolumeMetrics(
            avg_volume_20d=avg_20d,
            relative_volume=0.0,
            is_illiquid=True,
            volume_score=0.0,
        )

    # Relative volume ratio
    current_vol = volumes[-1]
    rel_vol = current_vol / avg_20d if avg_20d > 0 else 0.0

    # Spike detection
    is_spike = rel_vol > 1.5

    # Volume trend: 5d SMA vs 20d SMA
    avg_5d = sum(volumes[-5:]) / 5
    ratio_5_20 = avg_5d / avg_20d if avg_20d > 0 else 1.0

    if ratio_5_20 > 1.10:
        trend = "increasing"
    elif ratio_5_20 < 0.90:
        trend = "decreasing"
    else:
        trend = "flat"

    # Score
    score = _interpolate_score(rel_vol)

    return VolumeMetrics(
        avg_volume_20d=round(avg_20d, 0),
        relative_volume=round(rel_vol, 2),
        is_spike=is_spike,
        trend=trend,
        is_illiquid=False,
        volume_score=round(score, 1),
    )
