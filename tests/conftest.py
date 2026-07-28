"""
conftest.py — Shared fixtures for the SwingsterV2 test suite.

Provides factories and pre-built data for testing the pure-function
pipeline stages (trend, volume, RS rank, risk-reward, patterns, judge).
"""

import pytest
from scanner.models import Candle


@pytest.fixture
def make_candles():
    """
    Factory that builds a list of Candle objects from OHLCV parameters.

    Usage::

        candles = make_candles(
            closes=[100, 102, 104, 103, 105],
            volumes=[50000, 60000, 55000, 48000, 70000],
        )

    If only ``closes`` is provided, open/high/low are synthesized from close.
    """

    def _make(
        closes: list[float],
        opens: list[float] | None = None,
        highs: list[float] | None = None,
        lows: list[float] | None = None,
        volumes: list[int] | None = None,
        start_date: str = "2025-01-01",
    ) -> list[Candle]:
        n = len(closes)
        if opens is None:
            opens = [c * 0.998 for c in closes]
        if highs is None:
            highs = [c * 1.01 for c in closes]
        if lows is None:
            lows = [c * 0.99 for c in closes]
        if volumes is None:
            volumes = [100_000] * n

        # Generate sequential dates
        from datetime import datetime, timedelta

        base = datetime.strptime(start_date, "%Y-%m-%d")
        dates = [(base + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n)]

        return [
            Candle(
                date=dates[i],
                open=opens[i],
                high=highs[i],
                low=lows[i],
                close=closes[i],
                volume=volumes[i],
            )
            for i in range(n)
        ]

    return _make


@pytest.fixture
def uptrend_candles(make_candles):
    """
    252+ candles in a Stage 2 uptrend.

    Price starts at 100 and trends up ~0.15% per day with small noise,
    ensuring all 5 Minervini conditions pass.
    """
    n = 260
    closes = []
    price = 100.0
    for i in range(n):
        price *= 1.0015  # ~0.15% daily gain → ~46% over 260 days
        closes.append(round(price, 2))

    return make_candles(closes=closes, volumes=[150_000] * n)


@pytest.fixture
def flat_candles(make_candles):
    """60 candles going sideways around 100."""
    import random

    random.seed(42)
    closes = [100 + random.uniform(-2, 2) for _ in range(60)]
    return make_candles(closes=closes)


@pytest.fixture
def downtrend_candles(make_candles):
    """100 candles in a clear downtrend."""
    n = 100
    closes = []
    price = 200.0
    for i in range(n):
        price *= 0.997  # ~0.3% daily loss
        closes.append(round(price, 2))
    return make_candles(closes=closes, volumes=[120_000] * n)
