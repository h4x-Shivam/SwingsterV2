"""
indicators.py — Shared technical analysis calculations.

These functions compute common indicators using the standard Candle list,
avoiding the need for heavyweight Pandas/NumPy dependencies for simple maths.
"""

from typing import List, Optional
from scanner.models import Candle

def calculate_sma(candles: List[Candle], period: int) -> Optional[float]:
    """Calculate Simple Moving Average of the close price for the last `period` candles."""
    if len(candles) < period or period <= 0:
        return None
    
    subset = candles[-period:]
    return sum(c.close for c in subset) / period

def calculate_ema(candles: List[Candle], period: int) -> Optional[float]:
    """
    Calculate Exponential Moving Average of the close price.
    Returns the EMA for the final candle in the list.
    """
    if len(candles) < period or period <= 0:
        return None
    
    # Start with SMA as the initial EMA seed
    k = 2.0 / (period + 1.0)
    ema = sum(c.close for c in candles[:period]) / period
    
    # Apply EMA multiplier for the rest of the series
    for c in candles[period:]:
        ema = (c.close - ema) * k + ema
        
    return ema

def calculate_volume_slope(candles: List[Candle], window: int = 20) -> float:
    """
    Compute the linear regression slope of volume over the last `window` candles,
    normalised to the average volume over that window.

    Returns a value roughly in the range [-1, +1]:
      • Negative  → volume is declining  (good for a VCP base)
      • Positive  → volume is expanding  (potentially distribution / no dry-up)
      • 0.0       → flat / insufficient data
    """
    subset = candles[-window:] if len(candles) >= window else candles
    n = len(subset)
    if n < 4:
        return 0.0

    vols = [float(c.volume) for c in subset]
    avg_vol = sum(vols) / n
    if avg_vol <= 0:
        return 0.0

    # Least-squares slope: b = (n·Σxy - Σx·Σy) / (n·Σx² - (Σx)²)
    sum_x = sum_y = sum_xy = sum_x2 = 0.0
    for i, v in enumerate(vols):
        x = float(i)
        y = v / avg_vol          # normalise so result is scale-free
        sum_x  += x
        sum_y  += y
        sum_xy += x * y
        sum_x2 += x * x

    denom = n * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-12:
        return 0.0

    return (n * sum_xy - sum_x * sum_y) / denom


def count_distribution_days(
    candles: List[Candle],
    window: int = 30,
    avg_vol: float = 0.0,
) -> int:
    """
    Count "distribution days" inside the last `window` candles.

    A distribution day requires ALL of:
      1. Close < prior close          (selling pressure)
      2. Volume > avg_vol             (above-average volume confirms institutions)
      3. Close in upper 50% of the day's own range  (looks bullish but is actually distributing)

    This combination reveals quiet institutional selling inside what looks like
    a healthy base — the most dangerous pattern to buy into.

    Returns 0 when there is insufficient data.
    """
    subset = candles[-window:] if len(candles) >= window else candles
    if len(subset) < 2 or avg_vol <= 0:
        return 0

    count = 0
    for i in range(1, len(subset)):
        c     = subset[i]
        prev  = subset[i - 1]
        c_rng = c.high - c.low

        close_below_prior = c.close < prev.close
        high_volume       = c.volume > avg_vol
        upper_half_close  = (c_rng > 0) and ((c.close - c.low) / c_rng >= 0.50)

        if close_below_prior and high_volume and upper_half_close:
            count += 1

    return count


def calculate_avwap(candles: List[Candle], start_index: int) -> Optional[float]:
    """
    Calculate Anchored Volume Weighted Average Price (AVWAP).
    Anchored from `start_index` to the end of the `candles` list.
    Uses typical price: (High + Low + Close) / 3
    """
    if start_index < 0 or start_index >= len(candles):
        return None
    
    subset = candles[start_index:]
    if not subset:
        return None
        
    cum_vol = 0
    cum_vol_price = 0.0
    
    for c in subset:
        typical_price = (c.high + c.low + c.close) / 3.0
        cum_vol += c.volume
        cum_vol_price += typical_price * c.volume
        
    if cum_vol == 0:
        return None
        
    return cum_vol_price / cum_vol
