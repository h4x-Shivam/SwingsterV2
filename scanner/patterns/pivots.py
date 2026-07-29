from dataclasses import dataclass
from scanner.models import Candle

@dataclass
class SwingHigh:
    index: int
    price: float

@dataclass
class SwingLow:
    index: int
    price: float


def find_swing_pivots(
    candles: list[Candle],
    n: int = 3,
    lookback: int = 252
) -> tuple[list[SwingHigh], list[SwingLow]]:
    """
    Identify swing highs and swing lows in the last `lookback` candles.

    A swing high at index *i* has ``candle[i].high > all candles within
    n candles on each side``.  Symmetric rule for swing lows with ``.low``.
    """
    start = max(0, len(candles) - lookback)
    highs: list[SwingHigh] = []
    lows: list[SwingLow] = []

    for i in range(start + n, len(candles) - n):
        # --- swing high ---
        c_high = candles[i].high
        is_sh = True
        for j in range(i - n, i + n + 1):
            if j == i:
                continue
            if candles[j].high >= c_high:
                is_sh = False
                break
        if is_sh:
            highs.append(SwingHigh(index=i, price=c_high))

        # --- swing low ---
        c_low = candles[i].low
        is_sl = True
        for j in range(i - n, i + n + 1):
            if j == i:
                continue
            if candles[j].low <= c_low:
                is_sl = False
                break
        if is_sl:
            lows.append(SwingLow(index=i, price=c_low))

    return highs, lows


def find_swing_pivots_adaptive(
    candles: list[Candle],
    atr_pct: float,
    lookback: int = 252,
) -> tuple[list[SwingHigh], list[SwingLow]]:
    """
    ATR-normalized variant of ``find_swing_pivots``.

    The neighbourhood size ``n`` is derived from the stock's own daily ATR
    expressed as a percentage of price:

    - Very tight stock  (ATR ≈ 0.5% → n = 4):  needs a wider neighbourhood to
      avoid crowning every tiny bump as a swing high.
    - Volatile stock   (ATR ≈ 3.0% → n = 2):  a narrower window is sufficient
      because real pivots are naturally separated by large moves.

    Formula:  n = clamp( round(0.01 / atr_pct), 2, 5 )

    Falls back to ``n = 3`` when ``atr_pct`` is zero or unavailable.
    """
    if atr_pct > 0:
        n = int(round(0.01 / atr_pct))
        n = max(2, min(5, n))
    else:
        n = 3
    return find_swing_pivots(candles, n=n, lookback=lookback)


def calculate_atr_pct(candles: list, period: int = 14) -> float:
    """
    Average True Range as a PERCENTAGE of current price.
    This is the stock's own normal daily volatility, normalized.
    Use this instead of fixed percentages anywhere in pattern detection.
    """
    if len(candles) < period + 1:
        return 0.02  # 2% fallback for insufficient data

    true_ranges = []
    for i in range(1, len(candles)):
        high_low   = candles[i].high - candles[i].low
        high_close = abs(candles[i].high - candles[i-1].close)
        low_close  = abs(candles[i].low - candles[i-1].close)
        true_ranges.append(max(high_low, high_close, low_close))

    atr = sum(true_ranges[-period:]) / period
    current_price = candles[-1].close
    return atr / current_price if current_price > 0 else 0.02
