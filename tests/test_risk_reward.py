"""Tests for scanner.risk_reward — Risk-Reward computation."""

from scanner.risk_reward import compute_risk_reward
from scanner.models import PatternSignal


class TestComputeRiskReward:
    """Test R:R ratio, stop loss, target, and edge cases."""

    def test_basic_risk_reward(self, make_candles):
        """Basic case: should compute valid support, target, and ratio."""
        # Build 30 candles with a clear support and recent price near high
        closes = list(range(100, 130))
        candles = make_candles(closes=[float(c) for c in closes])

        result = compute_risk_reward(candles)
        assert result.stop_loss > 0
        assert result.target > 0
        assert result.ratio >= 0

    def test_insufficient_candles_returns_default(self, make_candles):
        """Fewer than 10 candles → default RiskReward."""
        candles = make_candles(closes=[100.0] * 5)
        result = compute_risk_reward(candles)
        assert result.ratio == 0.0
        assert result.score == 0.0

    def test_stop_loss_below_entry(self, make_candles):
        """Stop loss should always be below current price."""
        closes = [float(100 + i * 0.5) for i in range(30)]
        candles = make_candles(closes=closes)

        result = compute_risk_reward(candles)
        entry = candles[-1].close
        if result.ratio > 0:
            assert result.stop_loss < entry

    def test_target_above_entry(self, make_candles):
        """Target should always be above current price."""
        closes = [float(100 + i * 0.5) for i in range(30)]
        candles = make_candles(closes=closes)

        result = compute_risk_reward(candles)
        entry = candles[-1].close
        if result.ratio > 0:
            assert result.target > entry

    def test_high_rr_gets_high_score(self, make_candles):
        """R:R ratio >= 4 → score = 100."""
        # Pattern with explicit geometry giving 4:1 R:R
        signal = PatternSignal(
            name="VCP",
            strength=80,
            buy_point=100.0,
            distance_from_buy_pct=0.0,
            pattern_stop_loss=95.0,    # 5% risk
            pattern_target=120.0,      # 20% reward → 4:1
        )
        candles = make_candles(closes=[float(100)] * 20)
        result = compute_risk_reward(candles, pattern_signal=signal)
        assert result.score >= 85.0

    def test_rr_below_hard_minimum_zero_score(self, make_candles):
        """R:R below hard minimum → score = 0."""
        signal = PatternSignal(
            name="VCP",
            strength=80,
            buy_point=100.0,
            distance_from_buy_pct=0.0,
            pattern_stop_loss=99.0,     # 1% risk
            pattern_target=100.5,       # 0.5% reward → 0.5:1
        )
        candles = make_candles(closes=[float(100)] * 20)
        result = compute_risk_reward(candles, rr_hard_minimum=1.5, pattern_signal=signal)
        assert result.score == 0.0

    def test_score_within_bounds(self, make_candles):
        """Score should always be 0–100."""
        closes = [float(100 + i) for i in range(30)]
        candles = make_candles(closes=closes)

        result = compute_risk_reward(candles)
        assert 0 <= result.score <= 100
