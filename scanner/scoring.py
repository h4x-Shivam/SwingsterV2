"""
scoring.py — 5-factor composite scoring for SwingsterV2.

Weighted formula:
  signal × 0.40 + volume × 0.25 + rr × 0.20 + stage2 × 0.10 + rs × 0.05

Hard cap: if ``is_stage2 = False``, composite is capped at 50.
"""

from config import (
    WEIGHT_SIGNAL,
    WEIGHT_VOLUME,
    WEIGHT_RR,
    WEIGHT_STAGE2,
    WEIGHT_RS,
)


def compute_composite_score(
    signal_strength: float,
    volume_score: float,
    rr_score: float,
    stage2_score: float,
    rs_score: float,
    is_stage2: bool,
) -> float:
    """
    Compute the 5-factor composite score (0–100), rounded to 1 decimal.

    If ``is_stage2`` is False the result is capped at 50 regardless of
    how strong the individual components are.
    """
    raw = (
        signal_strength * WEIGHT_SIGNAL
        + volume_score * WEIGHT_VOLUME
        + rr_score * WEIGHT_RR
        + stage2_score * WEIGHT_STAGE2
        + rs_score * WEIGHT_RS
    )

    # Clamp 0–100
    raw = max(0.0, min(100.0, raw))

    # Hard cap for non-Stage-2 stocks
    if not is_stage2:
        raw = min(raw, 50.0)

    return round(raw, 1)
