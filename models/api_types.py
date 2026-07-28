"""
api_types.py — Shared data transfer objects for the SwingsterV2 API.

These DTOs define the exact contract between the Python backend and
the Next.js frontend via Supabase. Changing a field here should trigger
a regeneration of the TypeScript types.

Usage::

    from models.api_types import FinalPickDTO, ScanSummaryDTO
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ScanSummaryDTO:
    """Matches the Supabase ``scan_summary`` table schema."""

    mode: str
    total_scanned: int
    pattern_match_count: int
    rejected_by_rr: list[str]


@dataclass
class FinalPickDTO:
    """
    Matches the Supabase ``final_picks`` table schema.

    This is the canonical definition — the TypeScript ``FinalPick``
    interface in ``frontend/.../data-fetcher.ts`` must mirror this exactly.
    """

    rank: int
    symbol: str
    pattern: str
    scan_mode: str
    composite_score: float
    conviction: str  # "HIGH" | "MEDIUM"
    buy_point: float
    stop_loss: float
    target: float
    rr_ratio: float
    current_price: float
    distance_from_buy_pct: float
    signal_strength: float
    volume_score: float
    rr_score: float
    stage2_score: float
    rs_score: float
    judge_verdict: str
    flags: str
    pledge_pct: Optional[float] = None
    sector: Optional[str] = None
    target2: Optional[float] = None
    pattern_age: Optional[int] = None
    trend: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for Supabase insertion."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "FinalPickDTO":
        """Create a DTO from a raw dict (e.g. from judge output)."""
        return cls(
            rank=data.get("rank", 0),
            symbol=data.get("symbol", ""),
            pattern=data.get("pattern", ""),
            scan_mode=data.get("scan_mode", ""),
            composite_score=data.get("composite_score", 0.0),
            conviction=data.get("conviction", "MEDIUM"),
            buy_point=data.get("buy_point", 0.0),
            stop_loss=data.get("stop_loss", 0.0),
            target=data.get("target", 0.0),
            rr_ratio=data.get("rr_ratio", 0.0),
            current_price=data.get("current_price", 0.0),
            distance_from_buy_pct=data.get("distance_from_buy_pct", 0.0),
            signal_strength=data.get("signal_strength", 0.0),
            volume_score=data.get("volume_score", 0.0),
            rr_score=data.get("rr_score", 0.0),
            stage2_score=data.get("stage2_score", 0.0),
            rs_score=data.get("rs_score", 0.0),
            judge_verdict=data.get("judge_verdict", ""),
            flags=data.get("flags", ""),
            pledge_pct=data.get("pledge_pct"),
            sector=data.get("sector"),
            target2=data.get("target2"),
            pattern_age=data.get("pattern_age"),
            trend=data.get("trend"),
        )
