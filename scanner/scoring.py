"""
scoring.py — Thin wrapper delegating scoring to individual patterns.
"""

from scanner.patterns.base import BasePattern

def compute_composite_score(
    pattern: BasePattern,
    signal_strength: float,
    volume_score: float,
    rr_score: float,
    stage2_score: float,
    rs_score: float,
) -> float:
    """
    Delegate composite score calculation to the specific pattern's config and logic.
    """
    return pattern.score(
        signal_strength=signal_strength,
        volume_score=volume_score,
        rr_score=rr_score,
        stage2_score=stage2_score,
        rs_score=rs_score,
    )
