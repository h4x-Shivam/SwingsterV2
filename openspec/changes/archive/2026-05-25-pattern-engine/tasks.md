# SwingsterV2 — Phase 3: Pattern Detection Engine
# Updated spec by quant review — all gaps and threshold errors fixed

---

## 1. Package Setup & Data Models

- [x] 1.1 Create `scanner/` package directory with `__init__.py`
- [x] 1.2 Create `scanner/models.py` with dataclasses:
        `Candle`, `PatternSignal`, `VolumeMetrics`, `RiskReward`, `TrendStatus`, `RSRank`, `ScanResult`
- [x] 1.3 `PatternSignal` fields:
        `name`, `strength` (0–100), `buy_point`, `distance_from_buy_pct`,
        `breakout_level`, `pivot_high`, `contraction_depth`, `contraction_count`
- [x] 1.4 `TrendStatus` fields:
        `is_stage2` (bool), `above_150ma` (bool), `above_200ma` (bool),
        `ma150_above_ma200` (bool), `ma200_trending_up` (bool),
        `within_25pct_of_52w_high` (bool), `stage2_score` (0–100)
- [x] 1.5 `RSRank` fields:
        `symbol_return_12m` (float), `nifty_return_12m` (float),
        `rs_score` (0–100), `outperforming` (bool)
- [x] 1.6 `ScanResult` fields:
        `symbol`, `pattern`, `signal_strength`, `volume_score`, `rr_score`,
        `stage2_score`, `rs_score`, `composite_score`,
        `buy_point`, `stop_loss`, `target`, `rr_ratio`,
        `current_price`, `distance_from_buy_pct`
- [x] 1.7 Add helper in `models.py` to convert raw OHLCV tuples from
        `db_writer.read_ohlcv()` into list of `Candle` dataclasses
- [x] 1.8 Add `MIN_CANDLES_VCP = 60`, `MIN_CANDLES_FLAG = 30`,
        `MIN_CANDLES_CUP = 100`, `MIN_CANDLES_BREAKOUT = 30` guards to models

---

## 2. Trend Filter — Stage 2 (Build FIRST, before patterns)

> Minervini Stage 2 is the most important filter.
> A pattern on a downtrending stock is worthless.
> This filter alone eliminates 60–70% of false signals.

- [x] 2.1 Create `scanner/trend.py` with `analyze_trend(candles) → TrendStatus`
- [x] 2.2 Compute 150-day and 200-day simple moving averages of Close
- [x] 2.3 Check: current price > 150 MA → `above_150ma`
- [x] 2.4 Check: current price > 200 MA → `above_200ma`
- [x] 2.5 Check: 150 MA > 200 MA → `ma150_above_ma200`
- [x] 2.6 Check: 200 MA today > 200 MA 20 days ago → `ma200_trending_up`
- [x] 2.7 Compute 52-week high, check current price > 52w_high × 0.75 → `within_25pct_of_52w_high`
- [x] 2.8 Compute `stage2_score`:
        Each condition true = 20 points (5 conditions × 20 = 100 max)
- [x] 2.9 Set `is_stage2 = True` only when ALL 5 conditions pass
- [x] 2.10 Fallback: fewer than 200 candles → return default TrendStatus with all False, score=0
- [x] 2.11 In `engine.py` — skip symbol entirely if `stage2_score < 60`
         (allows partial stage 2, catches early-stage breakouts)

---

## 3. Relative Strength Rank

> Stocks outperforming Nifty 50 have institutional backing.
> A perfect VCP on an underperforming stock is a trap.

- [x] 3.1 Create `scanner/rs_rank.py` with `compute_rs(symbol_candles, nifty_candles) → RSRank`
- [x] 3.2 Fetch Nifty 50 (`^NSEI`) OHLCV from DB — add `^NSEI` to `symbols.csv` as a benchmark
- [x] 3.3 Compute 12-month return for symbol: `(close[-1] - close[-252]) / close[-252]`
- [x] 3.4 Compute 12-month return for Nifty 50 same way
- [x] 3.5 RS score mapping:
        symbol_return >> nifty_return by 20%+ → 100
        symbol_return >> nifty_return by 10% → 80
        in line with nifty → 50
        underperforming by 10% → 20
        underperforming by 20%+ → 0
- [x] 3.6 Set `outperforming = True` if `symbol_return > nifty_return`
- [x] 3.7 Fallback: fewer than 252 candles → rs_score=50, outperforming=False

---

## 4. Swing Pivot Utility

- [x] 4.1 Create shared utility `find_swing_pivots(candles, n=3) → (list[SwingHigh], list[SwingLow])`
        in `scanner/patterns.py`
- [x] 4.2 SwingHigh: candle.high > all neighbors within n candles on each side
- [x] 4.3 SwingLow: candle.low < all neighbors within n candles on each side
- [x] 4.4 Return only pivots from last 252 candles (1 year max lookback)

---

## 5. Chart Pattern Detection

### 5A — VCP (Volatility Contraction Pattern)

- [x] 5A.1 Implement `_detect_vcp(candles, pivots) → PatternSignal | None`
- [x] 5A.2 Require minimum `MIN_CANDLES_VCP = 60` candles
- [x] 5A.3 Identify 2–4 contraction bases using swing pivots:
          each base = distance between consecutive SwingHigh and SwingLow
- [x] 5A.4 **Contraction rule**: each base range must be ≤ 85% of previous base range
- [x] 5A.5 **Volume contraction rule** (critical — was missing):
          average volume in each base must be < 75% of volume in previous base
- [x] 5A.6 **Tight zone check**: final contraction range must be ≤ 8% of current price
          (not 15% — 15% is too wide, produces false signals)
- [x] 5A.7 **Buy point**: highest high of the last (tightest) contraction + 0.10 buffer
- [x] 5A.8 `distance_from_buy_pct`: `(buy_point - current_price) / current_price × 100`
          — only actionable if within 5% of buy point
- [x] 5A.9 Signal strength scoring:
          2 contractions → base 50, 3 contractions → base 70, 4 contractions → base 90
          + up to 10 bonus for tight final zone (< 5% range)
          + up to 10 bonus for strong volume dry-up (< 50% of prior base volume)
- [x] 5A.10 Return None if fewer than 2 valid contractions found

### 5B — Flag & Pole

- [x] 5B.1 Implement `_detect_pole_flag(candles, pivots) → PatternSignal | None`
- [x] 5B.2 Require minimum `MIN_CANDLES_FLAG = 30` candles
- [x] 5B.3 **Pole**: impulsive move ≥ 8% gain in ≤ 15 candles
          (NOT 15% — too aggressive, misses most flags on NSE)
- [x] 5B.4 **Flag retracement**: ≤ 35% of pole gain
          (NOT 50% — 50% is a correction not a flag)
- [x] 5B.5 **Flag duration**: 5–20 candles (tight consolidation)
- [x] 5B.6 **Flag slope**: flat or slightly downward (slope of closes < 0.1% per day)
          — upward sloping flag is invalid, add slope check
- [x] 5B.7 **Volume in flag**: must be < 60% of average volume during pole
- [x] 5B.8 **Buy point**: highest high of flag + 0.10 buffer
- [x] 5B.9 Signal strength scoring:
          pole gain 8–12% → 50, 12–20% → 70, 20%+ → 90
          + up to 10 bonus for tight flag (≤ 20% retracement)
          + up to 10 bonus for volume dry-up in flag

### 5C — Cup & Handle

- [x] 5C.1 Implement `_detect_cup_handle(candles, pivots) → PatternSignal | None`
- [x] 5C.2 Require minimum `MIN_CANDLES_CUP = 100` candles
- [x] 5C.3 **Cup depth**: 12–33% retracement from left lip to cup bottom
          (ADD minimum 12% — was missing, prevents shallow fake cups)
- [x] 5C.4 **Cup duration**: 30–150 candles — U-shaped base
- [x] 5C.5 **Cup shape**: right lip must recover within 5% of left lip high
- [x] 5C.6 **Handle**: 5–25 candles, must form above cup midpoint
- [x] 5C.7 **Handle depth**: ≤ 12% pullback from right lip (shallow drift)
- [x] 5C.8 **Handle slope**: downward or sideways ONLY
          — upward sloping handle = invalid, add slope check
- [x] 5C.9 **Handle volume**: must dry up vs cup volume (< 70%)
- [x] 5C.10 **Buy point**: highest high of handle + 0.10 buffer
- [x] 5C.11 Signal strength scoring:
           proper U-shape (smooth curve) → +30
           right lip within 3% of left lip → +30 (vs 5% → +20)
           handle slope valid → +20
           volume dry-up in handle → +20

### 5D — Horizontal Breakout

- [x] 5D.1 Implement `_detect_breakout(candles, pivots) → PatternSignal | None`
- [x] 5D.2 Require minimum `MIN_CANDLES_BREAKOUT = 30` candles
- [x] 5D.3 **Resistance zone**: 2+ SwingHighs within 2.5% of each other
          (NOT 1.5% — too tight for NSE spread, use 2–3%)
- [x] 5D.4 **Minimum test count**: resistance must be tested at least 2× over ≥ 10 trading days apart
          (prevents single-day double tops from triggering)
- [x] 5D.5 **Proximity**: current price within 3% below resistance
- [x] 5D.6 **Breakout volume** (critical — was missing):
          breakout candle volume must be ≥ 1.5× the 20-day average volume
          — low volume breakout = fake breakout, skip it
- [x] 5D.7 **Buy point**: resistance level + 0.10 buffer
- [x] 5D.8 Signal strength scoring:
           2 tests → 50, 3 tests → 70, 4+ tests → 90
           + up to 10 bonus for high volume on breakout candle
           + up to 10 bonus for long base duration (> 30 days at resistance)

### 5E — Pattern Entry Point

- [x] 5E.1 Create entry point `detect_patterns(candles) → PatternSignal | None`
- [x] 5E.2 Run all 4 detectors with candle count guards per pattern
- [x] 5E.3 Collect all signals that are not None
- [x] 5E.4 Return signal with highest `strength` score
- [x] 5E.5 If no pattern found return None

---

## 6. Volume Analysis

- [x] 6.1 Create `scanner/volume.py` with `analyze_volume(candles) → VolumeMetrics`
- [x] 6.2 Compute 20-day volume SMA
- [x] 6.3 Compute relative volume ratio: `current_volume / 20d_avg`
- [x] 6.4 **Minimum liquidity check** (was missing):
          if 20-day avg volume < 50,000 shares → mark as illiquid,
          set volume_score = 0, skip in engine
- [x] 6.5 Detect volume spike: ratio > 1.5
- [x] 6.6 Volume trend: 5-day SMA vs 20-day SMA → "increasing" / "decreasing" / "flat"
- [x] 6.7 Volume score mapping:
          ratio < 1.0 → 30, 1.0–1.5 → 60, 1.5–2.0 → 80, 2.0+ → 100
- [x] 6.8 Fallback: < 20 candles → default VolumeMetrics with score=0

---

## 7. Risk-Reward Scoring

- [x] 7.1 Create `scanner/risk_reward.py` with `compute_risk_reward(candles) → RiskReward`
- [x] 7.2 Swing low detection (n=3, lookback=20 candles) → support level
- [x] 7.3 Swing high detection above current price (n=3) → resistance / target
- [x] 7.4 Fallback: min low / max high of last 20 candles if no pivots found
- [x] 7.5 Stop loss: `support × 0.99` (1% buffer below support)
- [x] 7.6 Target: next resistance level above current price
- [x] 7.7 RR ratio: `(target - entry) / (entry - stop_loss)` with division-by-zero guard
- [x] 7.8 RR score mapping:
          ratio < 1.0 → 0, 1.0–2.0 → 30, 2.0–3.0 → 60, 3.0–4.0 → 80, 4.0+ → 100
- [x] 7.9 Fallback: < 10 candles → RiskReward(ratio=0, score=0)

---

## 8. Composite Scoring

- [x] 8.1 Create `scanner/scoring.py` with `compute_composite_score(...) → float`
- [x] 8.2 Updated weighted formula:
          `signal × 0.40 + volume × 0.25 + rr × 0.20 + stage2 × 0.10 + rs × 0.05`
- [x] 8.3 Round to 1 decimal, clamp 0–100
- [x] 8.4 Any symbol with `is_stage2 = False` gets composite score capped at 50
          regardless of pattern quality

---

## 9. Scan Engine Orchestrator

- [x] 9.1 Create `scanner/engine.py` with `scan_symbol(symbol) → ScanResult | None`
- [x] 9.2 Full pipeline per symbol:
          read OHLCV from DB
          → convert to Candles
          → `analyze_trend()` — skip if stage2_score < 60
          → `analyze_volume()` — skip if illiquid (avg_vol < 50k)
          → `detect_patterns()` — skip if None
          → `compute_rs()` against Nifty 50
          → `compute_risk_reward()`
          → `compute_composite_score()`
          → return ScanResult
- [x] 9.3 Implement `scan_all() → list[ScanResult]` using `ThreadPoolExecutor(NUM_AGENTS)`
- [x] 9.4 Apply `MIN_SIGNAL_SCORE` filter, sort by composite_score descending
- [x] 9.5 Return top `TOP_N_CANDIDATES` (30) to judge agent
- [x] 9.6 Per-symbol error handling: catch all exceptions, log warning, skip, continue
- [x] 9.7 Progress logging every 100 symbols with timing
- [x] 9.8 Final summary log: total scanned, passed stage2, passed volume,
          patterns found, time taken

---

## 10. Verification

- [x] 10.1 Run `scan_all()` on live `ohlcv.db`, verify results returned
- [x] 10.2 Verify all ScanResults have valid pattern names, stage2 status,
           RS rank, volume metrics, RR data, composite scores
- [x] 10.3 Verify Stage 2 filter is working — results should all have stage2_score ≥ 60
- [x] 10.4 Verify no illiquid stocks (avg volume < 50k) appear in results
- [x] 10.5 Verify performance: full scan of ~2,300 symbols completes in < 15 seconds
- [x] 10.6 Verify edge cases: symbols with < 30 candles handled gracefully, no crashes
- [x] 10.7 Spot-check 5 known NSE stocks with recent VCP setups manually
           and confirm algo catches them

---

## Key fixes from original spec

| Issue | Original | Fixed |
|---|---|---|
| VCP tight zone | ≤ 15% of breakout | ≤ 8% of current price |
| VCP volume contraction | Missing entirely | Required — each base < 75% prior volume |
| Flag pole gain | ≥ 15% in 10 days | ≥ 8% in 15 days |
| Flag retracement | < 50% | ≤ 35% |
| Flag slope check | Missing | Added — upward slope = invalid |
| Cup minimum depth | Missing | 12% minimum added |
| Handle slope check | Missing | Added — upward slope = invalid |
| Breakout resistance tolerance | 1.5% | 2.5% |
| Breakout volume requirement | Missing | ≥ 1.5× avg volume required |
| Minimum test spacing | Missing | ≥ 10 trading days apart |
| Stage 2 trend filter | Missing entirely | Full Minervini Stage 2 added |
| RS Rank | Missing entirely | 12-month vs Nifty 50 added |
| Liquidity filter | Missing | avg volume < 50k → skip |
| Buy point calculation | Missing | Added per pattern |
| Composite weights | signal 45 vol 30 rr 25 | signal 40 vol 25 rr 20 stage2 10 rs 5 |
| Stage 2 cap | Missing | False stage2 → score capped at 50 |