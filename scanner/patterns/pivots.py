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
