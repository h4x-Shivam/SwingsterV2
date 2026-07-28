"""Tests for scanner.rs_rank — Relative Strength ranking vs Nifty 50."""

from scanner.rs_rank import compute_rs


class TestComputeRS:
    """Test RS score computation and breakpoints."""

    def test_outperforming_stock_high_score(self, make_candles):
        """Stock that beats Nifty by 20%+ → score=100."""
        # Stock: 100 → 160 (+60%)
        n = 260
        stock_closes = [100 + (60 * i / n) for i in range(n)]
        # Nifty: 100 → 110 (+10%)
        nifty_closes = [100 + (10 * i / n) for i in range(n)]

        stock = make_candles(closes=stock_closes)
        nifty = make_candles(closes=nifty_closes)

        result = compute_rs(stock, nifty)
        assert result.outperforming is True
        assert result.rs_score >= 80.0

    def test_underperforming_stock_low_score(self, make_candles):
        """Stock that lags Nifty by 20%+ → score=0."""
        n = 260
        # Stock: 100 → 90 (-10%)
        stock_closes = [100 - (10 * i / n) for i in range(n)]
        # Nifty: 100 → 130 (+30%)
        nifty_closes = [100 + (30 * i / n) for i in range(n)]

        stock = make_candles(closes=stock_closes)
        nifty = make_candles(closes=nifty_closes)

        result = compute_rs(stock, nifty)
        assert result.outperforming is False
        assert result.rs_score <= 20.0

    def test_matching_returns_neutral_score(self, make_candles):
        """Stock matching Nifty → score=50."""
        n = 260
        closes = [100 + (15 * i / n) for i in range(n)]
        stock = make_candles(closes=closes)
        nifty = make_candles(closes=closes)

        result = compute_rs(stock, nifty)
        assert result.rs_score == 50.0

    def test_insufficient_data_returns_default(self, make_candles):
        """Fewer than 252 candles → default RSRank (score=50)."""
        short = make_candles(closes=[100] * 200)
        nifty = make_candles(closes=[100] * 200)

        result = compute_rs(short, nifty)
        assert result.rs_score == 50.0
        assert result.outperforming is False

    def test_score_within_bounds(self, make_candles):
        """Score should always be 0–100."""
        n = 260
        stock = make_candles(closes=[100 + i * 0.5 for i in range(n)])
        nifty = make_candles(closes=[100 + i * 0.3 for i in range(n)])

        result = compute_rs(stock, nifty)
        assert 0 <= result.rs_score <= 100
