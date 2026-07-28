"""Tests for judge.judge_agent — Auto-Judge deterministic scoring."""

from judge.judge_agent import _auto_judge_candidate, run_judge


class TestAutoJudgeCandidate:
    """Test conviction, verdict, and flag generation."""

    def test_high_conviction_on_high_score(self):
        """composite_score >= 85 → HIGH conviction."""
        item = {
            "composite_score": 90.0,
            "signal_strength": 85.0,
            "volume_score": 80.0,
            "pattern": "VCP",
            "symbol": "RELIANCE",
            "distance_from_buy_pct": 1.0,
        }
        result = _auto_judge_candidate(item)
        assert result["conviction"] == "HIGH"

    def test_medium_conviction_on_moderate_score(self):
        """composite_score < 85 and signal_strength < 90 → MEDIUM."""
        item = {
            "composite_score": 70.0,
            "signal_strength": 70.0,
            "volume_score": 60.0,
            "pattern": "VCP",
            "symbol": "INFY",
            "distance_from_buy_pct": 1.0,
        }
        result = _auto_judge_candidate(item)
        assert result["conviction"] == "MEDIUM"

    def test_vcp_verdict_high_strength(self):
        """VCP with signal_strength >= 85 → exceptional verdict."""
        item = {
            "composite_score": 88.0,
            "signal_strength": 90.0,
            "volume_score": 80.0,
            "pattern": "VCP",
            "symbol": "TCS",
            "distance_from_buy_pct": 0.5,
        }
        result = _auto_judge_candidate(item)
        assert "contraction" in result["judge_verdict"].lower()

    def test_flag_pole_verdict(self):
        """FLAG_POLE pattern should generate appropriate verdict."""
        item = {
            "composite_score": 75.0,
            "signal_strength": 70.0,
            "volume_score": 50.0,
            "pattern": "FLAG_POLE",
            "symbol": "HDFC",
            "distance_from_buy_pct": 1.0,
        }
        result = _auto_judge_candidate(item)
        assert "consolidation" in result["judge_verdict"].lower() or \
               "flag" in result["judge_verdict"].lower() or \
               "momentum" in result["judge_verdict"].lower()

    def test_pledge_flag_generated(self):
        """Pledge > 20% → HIGH RISK flag."""
        item = {
            "composite_score": 80.0,
            "signal_strength": 80.0,
            "volume_score": 70.0,
            "pattern": "VCP",
            "symbol": "SUZLON",
            "pledge_pct": 35.0,
            "distance_from_buy_pct": 1.0,
        }
        result = _auto_judge_candidate(item)
        assert "HIGH RISK" in result["flags"]
        assert "35" in result["flags"]

    def test_no_pledge_flag_below_threshold(self):
        """Pledge <= 20% → no flag."""
        item = {
            "composite_score": 80.0,
            "signal_strength": 80.0,
            "volume_score": 70.0,
            "pattern": "VCP",
            "symbol": "INFY",
            "pledge_pct": 5.0,
            "distance_from_buy_pct": 1.0,
        }
        result = _auto_judge_candidate(item)
        assert "HIGH RISK" not in result.get("flags", "")

    def test_extended_past_buy_flag(self):
        """distance_from_buy_pct > 4.0 → warning flag."""
        item = {
            "composite_score": 80.0,
            "signal_strength": 80.0,
            "volume_score": 70.0,
            "pattern": "VCP",
            "symbol": "TCS",
            "distance_from_buy_pct": 5.0,
        }
        result = _auto_judge_candidate(item)
        assert "extended" in result["flags"].lower()

    def test_volume_footprint_bonus(self):
        """volume_score >= 80 → 'Excellent volume footprint' in verdict."""
        item = {
            "composite_score": 80.0,
            "signal_strength": 80.0,
            "volume_score": 85.0,
            "pattern": "VCP",
            "symbol": "RELIANCE",
            "distance_from_buy_pct": 1.0,
        }
        result = _auto_judge_candidate(item)
        assert "volume footprint" in result["judge_verdict"].lower()


class TestRunJudge:
    """Test the full judge pipeline."""

    def test_empty_candidates_returns_empty(self):
        result = run_judge([], mode="VCP")
        assert result == []

    def test_ranking_order(self):
        """HIGH conviction should rank above MEDIUM, then by score desc."""
        candidates = [
            {"composite_score": 90.0, "signal_strength": 95.0, "volume_score": 80.0,
             "pattern": "VCP", "symbol": "A", "distance_from_buy_pct": 1.0},
            {"composite_score": 70.0, "signal_strength": 70.0, "volume_score": 60.0,
             "pattern": "VCP", "symbol": "B", "distance_from_buy_pct": 1.0},
            {"composite_score": 60.0, "signal_strength": 60.0, "volume_score": 50.0,
             "pattern": "VCP", "symbol": "C", "distance_from_buy_pct": 1.0},
        ]
        result = run_judge(candidates, mode="VCP")
        assert len(result) == 3
        assert result[0]["rank"] == 1
        assert result[0]["symbol"] == "A"
        # Ranks should be sequential
        assert [r["rank"] for r in result] == [1, 2, 3]

    def test_all_picks_have_required_fields(self):
        """Every pick should have rank, conviction, judge_verdict, flags."""
        candidates = [
            {"composite_score": 80.0, "signal_strength": 80.0, "volume_score": 70.0,
             "pattern": "VCP", "symbol": "TEST", "distance_from_buy_pct": 1.0},
        ]
        result = run_judge(candidates, mode="VCP")
        pick = result[0]
        assert "rank" in pick
        assert "conviction" in pick
        assert "judge_verdict" in pick
        assert "flags" in pick
