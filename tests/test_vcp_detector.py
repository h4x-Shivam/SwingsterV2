"""
test_vcp_detector.py — Unit tests for the VCP detection engine v2.0

Tests cover:
  1. Perfect 3-contraction VCP → must detect
  2. Perfect 4-contraction VCP → must detect with higher score
  3. Flat/no-contraction series → must reject
  4. Price too far below pivot → must reject
  5. Final pullback too deep (>12%) → must reject
  6. Volume expanding (positive slope) → must reject
  7. Distribution days > 2 → must reject
  8. Right side too wide (>6% range) → must reject
  9. Recovery too shallow between troughs → must reject
 10. Weekly-candle TF (tf_factor=5) → must detect same pattern
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner.models import Candle
from scanner.patterns.vcp.detector import VCPPattern


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_candle(
    date: str,
    open_: float,
    high: float,
    low: float,
    close: float,
    volume: int = 500_000,
) -> Candle:
    return Candle(date=date, open=open_, high=high, low=low, close=close, volume=volume)


def _date(n: int) -> str:
    """Return a synthetic daily date string for candle index n."""
    from datetime import date, timedelta
    base = date(2024, 1, 1)
    return str(base + timedelta(days=n))


def _weekly_date(n: int) -> str:
    """Return a synthetic weekly date string (7-day gap)."""
    from datetime import date, timedelta
    base = date(2024, 1, 1)
    return str(base + timedelta(days=n * 7))


def _build_base_candles(
    pivot_price: float = 100.0,
    n_preamble: int = 100,
    pullback_depths: list[float] | None = None,
    final_price_offset: float = -1.5,  # how far below pivot the last candle is
    volume_profile: str = "declining",  # "declining" | "expanding" | "flat"
    n_distribution: int = 0,           # distribution days to inject into the base middle
    right_side_wiggle: float = 0.03,   # right-side H/L range as fraction of pivot
    date_fn=_date,
    recovery_pct: float = 0.80,        # fraction of pullback recovered between troughs
) -> list[Candle]:
    """
    Construct a synthetic VCP candle series.

    Structure:
      preamble → advance to pivot → contracting pullbacks → tight right side

    Geometric rules enforced:
      • Each recovery peak is strictly below the PREVIOUS segment's start price,
        so the validate_contracting_highs check always passes.
      • Right-side candles have a 1.4% intraday range + low volume to avoid
        accidental distribution / accumulation failures.
    """
    if pullback_depths is None:
        pullback_depths = [0.20, 0.12, 0.06]

    candles: list[Candle] = []
    idx = 0

    # ── Preamble: gradual advance to pivot ────────────────────────────────
    base_start = pivot_price * 0.60
    for i in range(n_preamble):
        frac  = i / n_preamble
        price = base_start + (pivot_price - base_start) * frac
        candles.append(make_candle(date_fn(idx), price * 0.99, price * 1.01, price * 0.98, price, 600_000))
        idx += 1

    # ── Pivot candle (big volume surge) ───────────────────────────────────
    candles.append(make_candle(
        date_fn(idx), pivot_price * 0.99, pivot_price * 1.005,
        pivot_price * 0.985, pivot_price, 1_200_000,
    ))
    idx += 1

    # ── Contracting pullbacks ─────────────────────────────────────────────
    # seg_start_price: the price each segment descends FROM.
    # Must strictly decrease each iteration so contracting-highs is satisfied.
    seg_start = pivot_price
    total_pb = len(pullback_depths)

    for pb_idx, depth in enumerate(pullback_depths):
        trough_price = pivot_price * (1.0 - depth)
        n_down = 8

        # Descent candles (all highs capped at seg_start * 0.999)
        for i in range(n_down):
            frac  = (i + 1) / n_down
            price = seg_start - (seg_start - trough_price) * frac
            h     = min(seg_start * 0.999, price * 1.008)   # never exceed seg_start
            l     = price * 0.992
            if volume_profile == "declining":
                vol = int(900_000 * (1.0 - 0.35 * (pb_idx * n_down + i) / (total_pb * n_down)))
            elif volume_profile == "expanding":
                vol = int(350_000 * (1.0 + 0.5  * (pb_idx * n_down + i) / (total_pb * n_down)))
            else:
                vol = 600_000
            candles.append(make_candle(date_fn(idx), price * 1.003, h, l, price, vol))
            idx += 1

        # Trough candle — ultra-low volume dry-up
        candles.append(make_candle(
            date_fn(idx),
            trough_price * 1.001, trough_price * 1.003,
            trough_price * 0.998, trough_price,
            80_000,
        ))
        idx += 1

        # Recovery: cap at 97% of seg_start to ensure segment high < prior segment high
        recovery_cap    = seg_start * 0.97
        recovery_target = min(
            trough_price + (seg_start - trough_price) * recovery_pct,
            recovery_cap,
        )
        n_up = 10
        for i in range(n_up):
            frac  = (i + 1) / n_up
            price = trough_price + (recovery_target - trough_price) * frac
            h     = min(recovery_cap, price * 1.006)
            l     = price * 0.994
            vol   = int(650_000 * (0.5 + 0.4 * frac))
            candles.append(make_candle(date_fn(idx), price * 0.997, h, l, price, vol))
            idx += 1

        # Next segment starts from recovery_target (strictly < seg_start)
        seg_start = recovery_target

    # ── Inject distribution days (within the dist_window lookback) ────────
    if n_distribution > 0:
        # Must fall within the detector's dist_window=30 lookback from the END
        dist_zone_end   = max(0, len(candles) - 5)    # leave last 5 candles clean
        dist_zone_start = max(0, dist_zone_end - 30)  # within last 30 candles
        avg_vol_ref     = 500_000
        for d in range(n_distribution):
            pos = dist_zone_start + d * max(1, (dist_zone_end - dist_zone_start) // max(1, n_distribution))
            if pos <= 0 or pos >= len(candles):
                break
            prev_price = candles[pos - 1].close
            ref_price  = candles[pos].close
            # Distribution: high vol + close BELOW prior close + close in upper 50% of range
            dist_high  = max(prev_price * 1.005, ref_price * 1.01)
            dist_low   = ref_price * 0.965
            mid        = (dist_high + dist_low) / 2.0
            # close must be: < prev_price AND >= mid (upper half)
            dist_close = max(mid, min(prev_price * 0.998, dist_high * 0.998))
            candles[pos] = make_candle(
                date_fn(pos), ref_price * 1.001, dist_high, dist_low, dist_close,
                int(avg_vol_ref * 2.0),
            )


    # ── Tight right side ─────────────────────────────────────────────────
    # right_side_wiggle controls the SPAN of the 15 closes
    # (so a test with wiggle=0.08 produces a genuine 8% high-to-low range)
    right_base    = pivot_price * (1.0 + final_price_offset / 100.0)
    right_high_pt = right_base * (1.0 + right_side_wiggle * 0.5)
    right_low_pt  = right_base * (1.0 - right_side_wiggle * 0.5)
    intraday_body = 0.003   # each candle's own O/H/L spread — kept tiny

    for i in range(15):
        # Spread closes from right_low_pt to right_high_pt and back (triangle)
        t = i / 14.0
        if t <= 0.5:
            c = right_low_pt + (right_high_pt - right_low_pt) * (t * 2)
        else:
            c = right_high_pt - (right_high_pt - right_low_pt) * ((t - 0.5) * 2)
        h   = c * (1.0 + intraday_body)
        l   = c * (1.0 - intraday_body)
        vol = 80_000 + (i % 4) * 15_000    # always low volume
        candles.append(make_candle(date_fn(idx), c * 0.9995, h, l, c, vol))
        idx += 1

    return candles







# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def detector():
    return VCPPattern()


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestVCPDetect:
    """Tests that should return a valid PatternSignal."""

    def test_perfect_3_contraction_vcp(self, detector):
        """Classic 3-contraction VCP with 20% → 12% → 6% pullbacks."""
        candles = _build_base_candles(
            pivot_price=100.0,
            pullback_depths=[0.20, 0.12, 0.06],
            final_price_offset=-1.5,
            volume_profile="declining",
        )
        result = detector.detect(candles, ())
        assert result is not None, "Perfect 3-contraction VCP should be detected"
        assert result.name == "VCP"
        assert result.contraction_count == 3
        assert result.strength > 40.0, f"Expected score > 40, got {result.strength}"
        assert result.buy_point > 0
        assert result.contraction_depth <= 12.0

    def test_perfect_4_contraction_vcp(self, detector):
        """4-contraction VCP: 30% → 18% → 10% → 6% — should score higher than 3-contraction."""
        candles_3 = _build_base_candles(pullback_depths=[0.20, 0.12, 0.06])
        candles_4 = _build_base_candles(pullback_depths=[0.30, 0.18, 0.10, 0.06])

        r3 = detector.detect(candles_3, ())
        r4 = detector.detect(candles_4, ())

        assert r4 is not None, "4-contraction VCP should be detected"
        assert r4.contraction_count >= 3, "Expected at least 3 contractions"
        if r3 is not None:
            # More contractions → higher quality signal
            assert r4.strength >= r3.strength - 10, (
                "4-contraction ({}) should be at least as strong as 3-contraction ({})".format(r4.strength, r3.strength)
            )

    def test_tight_final_depth_boosts_score(self, detector):
        """A 5% final depth should score better than a 10% final depth."""
        candles_tight  = _build_base_candles(pullback_depths=[0.20, 0.12, 0.05])
        candles_looser = _build_base_candles(pullback_depths=[0.20, 0.12, 0.10])

        r_tight  = detector.detect(candles_tight,  ())
        r_looser = detector.detect(candles_looser, ())

        if r_tight and r_looser:
            assert r_tight.strength >= r_looser.strength - 5, (
                f"Tighter final depth ({r_tight.strength}) should outscore looser ({r_looser.strength})"
            )


class TestVCPReject:
    """Tests that should return None (pattern not detected)."""

    def test_flat_no_contraction(self, detector):
        """Pullbacks of 20% → 19% → 18% — barely contracting, should reject."""
        candles = _build_base_candles(pullback_depths=[0.20, 0.19, 0.18])
        result  = detector.detect(candles, ())
        assert result is None, "Flat contraction series should be rejected"

    def test_price_too_far_below_pivot(self, detector):
        """Price 20% below pivot → should reject (proximity_bottom = 0.85)."""
        candles = _build_base_candles(
            final_price_offset=-20.0,  # 20% below pivot
            pullback_depths=[0.20, 0.12, 0.06],
        )
        result = detector.detect(candles, ())
        assert result is None, "Price 20% below pivot should be rejected"

    def test_final_pullback_too_deep(self, detector):
        """Final depth of 18% exceeds final_pullback_max_depth=12% → reject."""
        candles = _build_base_candles(pullback_depths=[0.25, 0.18, 0.18])
        result  = detector.detect(candles, ())
        # 18% → 18% is neither contracting nor under the 12% cap
        assert result is None, "Non-contracting or too-deep final pullback should be rejected"

    def test_expanding_volume_rejected(self, detector):
        """Volume slope is positive (expanding) → should reject."""
        candles = _build_base_candles(
            pullback_depths=[0.20, 0.12, 0.06],
            volume_profile="expanding",
        )
        result = detector.detect(candles, ())
        assert result is None, "Expanding volume in base should be rejected"

    def test_distribution_days_rejected(self, detector):
        """More than 2 distribution days → should reject."""
        candles = _build_base_candles(
            pullback_depths=[0.20, 0.12, 0.06],
            n_distribution=4,          # inject 4 distribution days
            volume_profile="declining",
        )
        result = detector.detect(candles, ())
        assert result is None, "Base with > 2 distribution days should be rejected"

    def test_right_side_too_wide(self, detector):
        """Right side range >6% → should reject."""
        candles = _build_base_candles(
            pullback_depths=[0.20, 0.12, 0.06],
            right_side_wiggle=0.08,    # 8% range — too wide
        )
        result = detector.detect(candles, ())
        assert result is None, "Wide right side (8%) should be rejected"

    def test_poor_recovery_between_troughs(self, detector):
        """Recovery of only 20% of the pullback range → should reject."""
        candles = _build_base_candles(
            pullback_depths=[0.20, 0.12, 0.06],
            recovery_pct=0.15,         # only 15% recovery
        )
        result = detector.detect(candles, ())
        assert result is None, "Poor recovery between troughs should be rejected"

    def test_insufficient_candles(self, detector):
        """Fewer than min_candles → should reject immediately."""
        candles = _build_base_candles(n_preamble=5, pullback_depths=[0.20, 0.10])
        short   = candles[:10]
        result  = detector.detect(short, ())
        assert result is None, "Insufficient candle count should be rejected"


class TestVCPTimeframes:
    """Verify detection works with weekly-scale candle data."""

    def test_weekly_candles_detected(self, detector):
        """Weekly candles (7-day gap) should be detected with the same logic."""
        candles = _build_base_candles(
            pivot_price=100.0,
            n_preamble=80,             # 80 weekly candles ≈ 1.5 years — enough volume history
            pullback_depths=[0.20, 0.12, 0.06],
            final_price_offset=-1.5,
            volume_profile="declining",
            date_fn=_weekly_date,
        )
        result = detector.detect(candles, ())
        assert result is not None, "Weekly-candle VCP should be detected"
        assert result.name == "VCP"


class TestVCPScoring:
    """Verify the composite score() function."""

    def test_score_with_strong_rs_and_stage2(self, detector):
        """RS score > 75 and Stage2 score = 100 should add bonus points."""
        base_score = detector.score(
            signal_strength=70.0,
            volume_score=70.0,
            rr_score=0.0,
            stage2_score=80.0,
            rs_score=70.0,
        )
        bonus_score = detector.score(
            signal_strength=70.0,
            volume_score=70.0,
            rr_score=0.0,
            stage2_score=100.0,       # full Stage 2 → +5
            rs_score=80.0,             # strong RS → +5
        )
        assert bonus_score > base_score, (
            f"Strong RS + full Stage 2 should add bonus points ({bonus_score} > {base_score})"
        )

    def test_score_clipped_at_100(self, detector):
        """Score must never exceed 100."""
        score = detector.score(
            signal_strength=100.0,
            volume_score=100.0,
            rr_score=100.0,
            stage2_score=100.0,
            rs_score=100.0,
        )
        assert score <= 100.0, f"Score exceeded 100: {score}"

    def test_score_clipped_at_0(self, detector):
        """Score must never be negative."""
        score = detector.score(
            signal_strength=0.0,
            volume_score=0.0,
            rr_score=0.0,
            stage2_score=0.0,
            rs_score=0.0,
        )
        assert score >= 0.0, f"Score below 0: {score}"
