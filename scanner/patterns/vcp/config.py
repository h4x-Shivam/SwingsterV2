from scanner.models import PatternConfig

VCP_CONFIG = PatternConfig(
    name         = "VCP",
    full_name    = "Volatility Contraction Pattern",
    version      = "2.0.0",
    color        = "#00f5c4",
    icon         = "📉",
    description  = "Minervini-style successive contractions with volume dry-up",
    timeframe    = "Swing trade — 3 to 8 weeks",
    min_candles  = 18,
    min_signal_score     = 55,
    min_candidate_score  = 55.0,
    max_candidates       = 20,
    rr_hard_minimum      = 0.0,
    vol_contraction_required = True,
    stage2_min_score     = 60,       # require at least partial Stage 2 uptrend
    pivot_lookback       = 120,
    weight_signal  = 0.60,
    weight_volume  = 0.30,
    weight_rr      = 0.0,
    weight_stage2  = 0.05,
    weight_rs      = 0.05,
    extras = {
        # ── Contraction structure ─────────────────────────────────────────
        "min_contractions":          2,
        "max_contractions":          5,        # raised from 4; 5-contraction setups are extremely strong
        "contraction_factor":        0.75,     # ideal depth ratio between consecutive pullbacks (target ~0.5–0.75)
        "pivot_lookback":            120,

        # ── Depth limits (% of pivot price) ──────────────────────────────
        "min_pullback_depth":        4.0,      # raised from 2.0: right-side wiggles (2-3%) are not pullbacks
        "first_pullback_min_depth":  8.0,      # first contraction must be real (≥ 8%)
        "first_pullback_max_depth":  35.0,     # first contraction can be large (emerging from base)
        "final_pullback_max_depth":  12.0,     # tightened from 15 → forces tight right side

        # ── Proximity to pivot ────────────────────────────────────────────
        "pivot_proximity_bottom":    0.85,     # price must be within 15% of pivot
        "pivot_proximity_top":       1.03,     # price can be up to 3% above pivot (not extended)
        "min_candles_post_pivot":    10,

        # ── Recovery between troughs ──────────────────────────────────────
        "min_candles_between_pullbacks": 3,
        "min_recovery_pct":          50.0,     # must recover ≥ 50% of the prior pullback's range

        # ── Right-side tightness ──────────────────────────────────────────
        "right_side_range_days":     10,       # scaled by tf_factor in detector
        "right_side_max_range_pct":  1.06,     # tightened from 1.12 → only 6% high-to-low allowed

        # ── ATR-based volatility contraction ──────────────────────────────
        "atr_contraction_ratio":     0.80,     # short-term ATR must be ≤ 80% of medium-term ATR

        # ── Volume dry-up ─────────────────────────────────────────────────
        "vol_avg_window":            5,
        "vol_dry_up_tolerance":      1.05,
        "vol_dry_up_days":           10,       # scaled by tf_factor in detector
        "vol_dry_up_min_count":      3,        # raised from 1 → need 3+ clear dry-up days
        "vol_dry_up_threshold":      0.65,     # tightened from 0.7 → must be ≤ 65% of 50d avg

        # ── Volume trend (linear regression) ─────────────────────────────
        "vol_slope_window":          30,       # window for volume linear regression (candles)
        "vol_slope_max":             0.02,     # slope must be ≤ +0.02 (flat or declining acceptable)

        # ── Accumulation (right side) ─────────────────────────────────────
        "accum_window":              12,       # scaled by tf_factor
        "accum_min_ratio":           1.10,     # up-day vol must be ≥ 1.10× down-day vol

        # ── Distribution detection (NEW) ──────────────────────────────────
        "dist_window":               30,       # look back this many candles for distribution
        "max_distribution_days":     2,        # more than 2 → reject (stock being distributed)

        # ── MA squeeze ────────────────────────────────────────────────────
        "ma_squeeze_max_spread":     0.06,     # 6% max spread — MAs converge toward pivot

        # ── AVWAP ─────────────────────────────────────────────────────────
        "avwap_buffer_pct":          0.97,     # price must hold ≥ 97% of Anchored VWAP

        # ── Scoring footprint bonuses/penalties ───────────────────────────
        "pocket_pivot_bonus":        6.0,      # pts per pocket pivot on right side
        "squat_candle_penalty":      8.0,      # pts deducted per squat candle

        # ── RS + Stage 2 composite bonus (NEW) ───────────────────────────
        "stage2_full_bonus":         5.0,      # bonus if all 5 Stage 2 conditions met
        "rs_strong_bonus":           5.0,      # bonus if RS score > threshold
        "rs_strong_threshold":       75.0,     # RS score above this = "strong RS"
    }
)
