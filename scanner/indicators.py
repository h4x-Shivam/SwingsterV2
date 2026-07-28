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
