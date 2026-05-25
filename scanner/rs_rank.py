"""
rs_rank.py — Relative Strength ranking vs Nifty 50 benchmark.

Computes 12-month return for both the symbol and ^NSEI, then maps the
outperformance magnitude to a 0–100 score with linear interpolation
between breakpoints.
"""

from scanner.models import Candle, RSRank


# ---------------------------------------------------------------------------
# Breakpoints for RS scoring
# ---------------------------------------------------------------------------
# (outperformance_pct, score)
_BREAKPOINTS: list[tuple[float, float]] = [
    (-20.0,   0.0),
    (-10.0,  20.0),
    (  0.0,  50.0),   # ±0 % → neutral
    ( 10.0,  80.0),
    ( 20.0, 100.0),
]


def _interpolate(value: float) -> float:
    """Linearly interpolate the RS score from breakpoints."""
    if value <= _BREAKPOINTS[0][0]:
        return _BREAKPOINTS[0][1]
    if value >= _BREAKPOINTS[-1][0]:
        return _BREAKPOINTS[-1][1]

    for i in range(len(_BREAKPOINTS) - 1):
        x0, y0 = _BREAKPOINTS[i]
        x1, y1 = _BREAKPOINTS[i + 1]
        if x0 <= value <= x1:
            t = (value - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)

    return 50.0  # fallback


def _return_12m(candles: list[Candle]) -> float:
    """Compute 12-month (252-day) return: (close[-1] - close[-252]) / close[-252]."""
    if len(candles) < 252:
        return 0.0
    old = candles[-252].close
    if old == 0:
        return 0.0
    return (candles[-1].close - old) / old


def compute_rs(
    symbol_candles: list[Candle],
    nifty_candles: list[Candle],
) -> RSRank:
    """
    Compute 12-month relative strength vs Nifty 50.

    Returns a default RSRank (score=50, outperforming=False) when either
    dataset has fewer than 252 candles.
    """
    if len(symbol_candles) < 252 or len(nifty_candles) < 252:
        return RSRank()

    sym_ret = _return_12m(symbol_candles)
    nifty_ret = _return_12m(nifty_candles)

    # Outperformance in percentage points (e.g. sym +30%, nifty +10% → +20 pp)
    outperformance = (sym_ret - nifty_ret) * 100.0

    score = _interpolate(outperformance)
    outperforming = sym_ret > nifty_ret

    return RSRank(
        symbol_return_12m=sym_ret,
        nifty_return_12m=nifty_ret,
        rs_score=round(score, 1),
        outperforming=outperforming,
    )
