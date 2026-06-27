"""
trend.py — Minervini Stage 2 uptrend filter.

Evaluates 5 moving-average conditions that define a Stage 2 uptrend:
  1. Price > 150-day MA
  2. Price > 200-day MA
  3. 150 MA > 200 MA
  4. 200 MA trending up (today > 20 days ago)
  5. Price within 25% of 52-week high

Each condition = 20 points → stage2_score 0–100.
``is_stage2`` is True only when ALL 5 conditions pass.
"""

from scanner.models import Candle, TrendStatus


def _sma(values: list[float], period: int) -> float:
    """Simple moving average of the last *period* values."""
    return sum(values[-period:]) / period


def analyze_trend(candles: list[Candle]) -> TrendStatus:
    """
    Compute Minervini Stage 2 status for a list of daily candles.

    Gracefully handles stocks with fewer than 200 candles by using the
    maximum available history for long-term moving averages.
    """
    if len(candles) < 60:
        return TrendStatus()

    closes = [c.close for c in candles]
    highs = [c.high for c in candles]

    current_price = closes[-1]

    # Use max available up to the required period
    ma150_period = min(150, len(closes))
    ma200_period = min(200, len(closes))

    # Moving averages
    ma150 = _sma(closes, ma150_period)
    ma200_now = _sma(closes, ma200_period)

    # 200 MA from 20 days ago (or as far back as possible)
    if len(closes) >= ma200_period + 20:
        ma200_20ago = _sma(closes[:-20], ma200_period)
    else:
        # Approximate: use the oldest available MA
        ma200_20ago = _sma(closes[:ma200_period], ma200_period)

    # 52-week high (252 trading days, or all available if fewer)
    lookback = min(len(highs), 252)
    high_52w = max(highs[-lookback:])

    # Evaluate conditions
    above_150ma = current_price > ma150
    above_200ma = current_price > ma200_now
    ma150_above_ma200 = ma150 > ma200_now
    ma200_trending_up = ma200_now > ma200_20ago
    within_25pct = current_price > high_52w * 0.75

    # Scoring — 20 pts per condition
    conditions = [
        above_150ma,
        above_200ma,
        ma150_above_ma200,
        ma200_trending_up,
        within_25pct,
    ]
    score = sum(20 for c in conditions if c)

    return TrendStatus(
        is_stage2=all(conditions),
        above_150ma=above_150ma,
        above_200ma=above_200ma,
        ma150_above_ma200=ma150_above_ma200,
        ma200_trending_up=ma200_trending_up,
        within_25pct_of_52w_high=within_25pct,
        stage2_score=float(score),
    )
