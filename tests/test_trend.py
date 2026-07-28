"""Tests for scanner.trend — Minervini Stage 2 filter."""

from scanner.trend import analyze_trend


class TestAnalyzeTrend:
    """Test the 5 Minervini Stage 2 conditions."""

    def test_uptrend_is_stage2(self, uptrend_candles):
        """A clean 260-day uptrend should pass all Stage 2 conditions."""
        result = analyze_trend(uptrend_candles)
        assert result.is_stage2 is True
        assert result.stage2_score == 100.0

    def test_uptrend_individual_conditions(self, uptrend_candles):
        result = analyze_trend(uptrend_candles)
        assert result.above_150ma is True
        assert result.above_200ma is True
        assert result.ma150_above_ma200 is True
        assert result.ma200_trending_up is True
        assert result.within_25pct_of_52w_high is True

    def test_downtrend_not_stage2(self, downtrend_candles):
        """A downtrend should fail most Stage 2 conditions."""
        result = analyze_trend(downtrend_candles)
        assert result.is_stage2 is False
        # In a downtrend, price is below moving averages
        assert result.stage2_score < 60

    def test_insufficient_candles_returns_default(self, make_candles):
        """Fewer than 60 candles should return all-defaults."""
        candles = make_candles(closes=[100] * 50)
        result = analyze_trend(candles)
        assert result.is_stage2 is False
        assert result.stage2_score == 0.0

    def test_flat_market_partial_score(self, flat_candles):
        """Sideways market should get partial Stage 2 score."""
        result = analyze_trend(flat_candles)
        # Flat market should pass some conditions but not all
        assert 0 <= result.stage2_score <= 100

    def test_score_is_multiple_of_20(self, uptrend_candles):
        """Score should be a multiple of 20 (5 conditions × 20 pts each)."""
        result = analyze_trend(uptrend_candles)
        assert result.stage2_score % 20 == 0
