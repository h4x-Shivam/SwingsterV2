from scanner.models import PatternConfig

VCP_CONFIG = PatternConfig(
    name         = "VCP",
    full_name    = "Volatility Contraction Pattern",
    version      = "1.0.0",
    color        = "#00f5c4",
    icon         = "📉",
    description  = "Minervini-style successive contractions with volume dry-up",
    timeframe    = "Swing trade — 3 to 8 weeks",
    min_candles  = 18,
    min_signal_score     = 50,
    min_candidate_score  = 50.0,
    max_candidates       = 20,
    rr_hard_minimum      = 0.0,
    vol_contraction_required = True,
    stage2_min_score     = 0,
    pivot_lookback       = 120,
    weight_signal  = 0.60,
    weight_volume  = 0.30,
    weight_rr      = 0.0,
    weight_stage2  = 0.05,
    weight_rs      = 0.05,
    extras = {
        "min_contractions":      2,
        "max_contractions":      4,
        "contraction_factor":    0.85,
        "tight_zone_pct":        0.08,
        "vol_dry_up_factor":     0.75,
        "near_pivot_max_pct":    0.05,
        "min_pullback_depth":    1.5,
        "pivot_proximity_bottom": 0.85,
        "right_side_range_days": 10,
        "right_side_max_range_pct": 1.12,
        "atr_contraction_ratio": 0.75,
        "vol_dry_up_days": 10,
        "vol_dry_up_min_count": 1,
        "vol_dry_up_threshold": 0.7,
        # Advanced VCP Metrics
        "ma_squeeze_max_spread": 0.04,   # 4% max spread between 10,20,50 MAs
        "avwap_buffer_pct": 0.98,        # Price must hold >= 98% of Anchored VWAP
        "pocket_pivot_bonus": 5.0,       # Points added per pocket pivot on right side
        "squat_candle_penalty": 10.0,    # Points deducted per squat candle on right side
    }
)
