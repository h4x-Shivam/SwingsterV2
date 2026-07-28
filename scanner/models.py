"""
models.py — Data structures for the scanner pipeline.

Typed dataclasses for every intermediate and output structure:
  • Candle       — single OHLCV bar
  • PatternSignal — detected chart pattern with buy point
  • TrendStatus  — Minervini Stage 2 result
  • RSRank       — relative strength vs Nifty 50
  • VolumeMetrics — volume analysis result
  • RiskReward   — support/resistance/stop/target/RR ratio
  • ScanResult   — full composite output per symbol
"""

from dataclasses import dataclass, field
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Pattern Config
# ---------------------------------------------------------------------------

@dataclass
class PatternConfig:
    # Identity
    name:         str
    full_name:    str
    version:      str

    # UI metadata
    color:        str
    icon:         str
    description:  str
    timeframe:    str

    # Candle requirements
    min_candles:  int

    # Filtering thresholds
    min_signal_score:          int
    min_candidate_score:       float
    max_candidates:            int
    rr_hard_minimum:           float

    # Volume direction
    vol_contraction_required:  bool

    # Engine pipeline thresholds (moved from hardcoded dicts in engine.py)
    stage2_min_score:          int = 60    # minimum stage2_score to run this pattern
    pivot_lookback:            int = 120   # lookback window for swing pivot detection

    # Scoring weights — must sum to 1.0
    weight_signal:  float = 0.0
    weight_volume:  float = 0.0
    weight_rr:      float = 0.0
    weight_stage2:  float = 0.0
    weight_rs:      float = 0.0

    # Pattern-specific extras
    extras: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        total = (self.weight_signal + self.weight_volume +
                 self.weight_rr + self.weight_stage2 + self.weight_rs)
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"{self.name}: scoring weights must sum to 1.0, got {total:.3f}"
            )


# ---------------------------------------------------------------------------
# Candle
# ---------------------------------------------------------------------------

@dataclass
class Candle:
    """Single daily OHLCV bar."""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


# ---------------------------------------------------------------------------
# Pattern Signal
# ---------------------------------------------------------------------------

@dataclass
class PatternSignal:
    """Result of a chart-pattern detector."""
    name: str                      # "vcp", "pole_flag", "cup_handle", "breakout"
    strength: float                # 0–100
    buy_point: float               # trigger price (breakout level + buffer)
    distance_from_buy_pct: float   # (buy_point - current_price) / current_price * 100
    breakout_level: float = 0.0    # raw breakout level (before buffer)
    pivot_high: float = 0.0        # highest relevant pivot high
    contraction_depth: float = 0.0 # final contraction range %  (VCP-specific)
    contraction_count: int = 0     # number of contractions      (VCP-specific)
    pattern_stop_loss: float | None = None  # pattern-geometry derived stop
    pattern_target: float | None = None     # pattern-geometry derived target


# ---------------------------------------------------------------------------
# Trend Status — Minervini Stage 2
# ---------------------------------------------------------------------------

@dataclass
class TrendStatus:
    """Minervini Stage 2 uptrend evaluation."""
    is_stage2: bool = False
    above_150ma: bool = False
    above_200ma: bool = False
    ma150_above_ma200: bool = False
    ma200_trending_up: bool = False
    within_25pct_of_52w_high: bool = False
    stage2_score: float = 0.0      # 0–100  (each condition = 20 pts)


# ---------------------------------------------------------------------------
# Relative-Strength Rank
# ---------------------------------------------------------------------------

@dataclass
class RSRank:
    """12-month relative-strength comparison vs Nifty 50."""
    symbol_return_12m: float = 0.0
    nifty_return_12m: float = 0.0
    rs_score: float = 50.0         # 0–100
    outperforming: bool = False


# ---------------------------------------------------------------------------
# Volume Metrics
# ---------------------------------------------------------------------------

@dataclass
class VolumeMetrics:
    """Volume analysis result."""
    avg_volume_20d: float = 0.0
    relative_volume: float = 1.0   # current_vol / 20d avg
    is_spike: bool = False         # ratio > 1.5
    trend: str = "flat"            # "increasing" / "decreasing" / "flat"
    is_illiquid: bool = False      # avg_volume_20d < 50_000
    volume_score: float = 0.0      # 0–100


# ---------------------------------------------------------------------------
# Risk-Reward
# ---------------------------------------------------------------------------

@dataclass
class RiskReward:
    """Support/resistance levels, stop-loss, target, and RR ratio."""
    support: float = 0.0
    resistance: float = 0.0
    stop_loss: float = 0.0
    target: float = 0.0
    ratio: float = 0.0
    score: float = 0.0             # 0–100


# ---------------------------------------------------------------------------
# Scan Result — final composite per symbol
# ---------------------------------------------------------------------------

@dataclass
class ScanResult:
    """Full analysis output for a single symbol."""
    symbol: str
    pattern: str                    # pattern name
    signal_strength: float          # 0–100
    volume_score: float             # 0–100
    rr_score: float                 # 0–100
    stage2_score: float             # 0–100
    rs_score: float                 # 0–100
    composite_score: float          # 0–100
    buy_point: float
    stop_loss: float
    target: float
    rr_ratio: float
    current_price: float
    distance_from_buy_pct: float
    scan_mode: str = "ALL"                    # which mode produced this result





# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rows_to_candles(
    rows: list[tuple[str, float, float, float, float, int]],
) -> list[Candle]:
    """
    Convert raw tuples from ``db_writer.read_ohlcv()`` into a list of
    ``Candle`` dataclasses.

    Each input row is ``(date, open, high, low, close, volume)``.
    """
    return [
        Candle(date=r[0], open=r[1], high=r[2], low=r[3], close=r[4], volume=r[5])
        for r in rows
    ]
