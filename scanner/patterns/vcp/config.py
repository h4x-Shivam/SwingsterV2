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
    min_signal_score     = 60,
    min_candidate_score  = 62.0,
    max_candidates       = 20,
    rr_hard_minimum      = 0.8,
    vol_contraction_required = True,
    weight_signal  = 0.60,
    weight_volume  = 0.20,
    weight_rr      = 0.05,
    weight_stage2  = 0.10,
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
    }
)
