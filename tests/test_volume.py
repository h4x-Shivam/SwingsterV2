"""Tests for scanner.volume — Volume analysis and liquidity filter."""

from scanner.volume import analyze_volume


class TestAnalyzeVolume:
    """Test volume metrics, illiquidity detection, and score interpolation."""

    def test_normal_volume_not_illiquid(self, make_candles):
        """Avg volume above 50k → not illiquid."""
        candles = make_candles(
            closes=[100] * 25,
            volumes=[100_000] * 25,
        )
        result = analyze_volume(candles)
        assert result.is_illiquid is False
        assert result.avg_volume_20d >= 50_000

    def test_low_volume_is_illiquid(self, make_candles):
        """Avg volume below 50k → illiquid."""
        candles = make_candles(
            closes=[100] * 25,
            volumes=[30_000] * 25,
        )
        result = analyze_volume(candles)
        assert result.is_illiquid is True
        assert result.volume_score == 0.0

    def test_spike_detection(self, make_candles):
        """Current volume > 1.5x avg → spike."""
        volumes = [100_000] * 24 + [200_000]
        candles = make_candles(closes=[100] * 25, volumes=volumes)
        result = analyze_volume(candles)
        assert result.is_spike is True

    def test_no_spike_normal_volume(self, make_candles):
        """Steady volume → no spike."""
        candles = make_candles(
            closes=[100] * 25,
            volumes=[100_000] * 25,
        )
        result = analyze_volume(candles)
        assert result.is_spike is False

    def test_volume_trend_increasing(self, make_candles):
        """Recent 5d volume >> 20d avg → 'increasing'."""
        volumes = [80_000] * 20 + [150_000] * 5
        candles = make_candles(closes=[100] * 25, volumes=volumes)
        result = analyze_volume(candles)
        assert result.trend == "increasing"

    def test_volume_trend_decreasing(self, make_candles):
        """Recent 5d volume << 20d avg → 'decreasing'."""
        volumes = [150_000] * 20 + [80_000] * 5
        candles = make_candles(closes=[100] * 25, volumes=volumes)
        result = analyze_volume(candles)
        assert result.trend == "decreasing"

    def test_insufficient_candles_returns_default(self, make_candles):
        """Fewer than 20 candles → default VolumeMetrics."""
        candles = make_candles(closes=[100] * 15)
        result = analyze_volume(candles)
        assert result.volume_score == 0.0
        assert result.relative_volume == 1.0

    def test_score_within_bounds(self, make_candles):
        """Score should always be 0–100."""
        candles = make_candles(
            closes=[100] * 25,
            volumes=[100_000] * 25,
        )
        result = analyze_volume(candles)
        assert 0 <= result.volume_score <= 100
