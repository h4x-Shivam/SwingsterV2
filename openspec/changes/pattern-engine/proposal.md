## Why

The OHLCV data pipeline is complete — 2,300+ NSE tickers with 1 year of daily candle data sitting in `ohlcv.db`. But raw price data is useless without analysis. SwingsterV2 needs its core brain: a pattern engine that scans every symbol's price history, detects actionable swing trade setups, computes scoring metrics, and produces a ranked candidate list for the downstream AI judge. Without this engine, the project is a database with no intelligence.

## What Changes

- **New module `scanner/patterns.py`**: Chart pattern detectors for 4 multi-day price structure patterns — VCP (Volatility Contraction Pattern), Pole & Flag, Cup & Handle, and Breakout. Each analyzes weeks/months of price history using swing pivot analysis, includes volume contraction rules, slope validation, and returns a signal with pattern name, strength (0–100), buy point, and key levels. Shared `find_swing_pivots()` utility used by all detectors.
- **New module `scanner/trend.py`**: Minervini Stage 2 trend filter — the most critical filter. Checks 5 conditions (price > 150 MA, price > 200 MA, 150 MA > 200 MA, 200 MA trending up, within 25% of 52-week high). Symbols failing Stage 2 are skipped entirely or capped at score 50.
- **New module `scanner/rs_rank.py`**: Relative Strength ranking — computes 12-month return vs Nifty 50 benchmark (`^NSEI`). Stocks outperforming the index score higher; underperformers are penalized.
- **New module `scanner/volume.py`**: Volume analysis functions — relative volume ratio (current vs 20-day average), volume spike detection, volume trend confirmation, and minimum liquidity filter (avg volume < 50k → skip as illiquid).
- **New module `scanner/risk_reward.py`**: Support/resistance detection using pivot-point swing lows/highs, stop-loss placement at recent swing low (1% buffer), target calculation at nearest resistance, and risk-reward ratio computation.
- **New module `scanner/scoring.py`**: Composite scoring engine with updated 5-factor weights: signal strength (40%), volume (25%), risk-reward (20%), Stage 2 trend (10%), RS rank (5%). Symbols without Stage 2 confirmation get score capped at 50.
- **New module `scanner/engine.py`**: The orchestrator — pipeline per symbol: OHLCV → Stage 2 filter → liquidity filter → pattern detection → RS rank → risk-reward → composite scoring. Multi-threaded batch scanning with `ThreadPoolExecutor`. Detailed funnel logging (total → passed stage2 → passed volume → patterns found).
- **New module `scanner/models.py`**: Dataclass definitions for `Candle`, `PatternSignal`, `VolumeMetrics`, `RiskReward`, `TrendStatus`, `RSRank`, and `ScanResult`. `PatternSignal` includes `buy_point`, `distance_from_buy_pct`, `contraction_count`. `ScanResult` carries all sub-scores.
- **Updated `config.py`**: Needs updated scoring weights (0.40/0.25/0.20/0.10/0.05), Stage 2 threshold, and liquidity filter constant. Existing scanner constants (`NUM_AGENTS`, `MIN_SIGNAL_SCORE`, `TOP_N_CANDIDATES`) unchanged.

## Capabilities

### New Capabilities
- `chart-patterns`: Detection of 4 chart patterns (VCP, Pole & Flag, Cup & Handle, Breakout) from daily OHLCV data with corrected thresholds — VCP tight zone ≤8%, flag retracement ≤35%, cup minimum depth 12%, breakout resistance tolerance 2.5%. Includes volume contraction rules, slope validation, and buy point calculation per pattern.
- `stage2-trend-filter`: Minervini Stage 2 uptrend confirmation — 5 moving average conditions that eliminate 60–70% of false signals by filtering out downtrending stocks before pattern detection runs.
- `relative-strength-rank`: 12-month performance comparison vs Nifty 50 benchmark — identifies stocks with institutional backing that outperform the index.
- `volume-analysis`: Volume spike detection, relative volume ratio, volume trend confirmation, and minimum liquidity filter (avg volume < 50k → illiquid, skip).
- `risk-reward-scoring`: Support/resistance identification from swing pivots, stop-loss/target calculation, and risk-reward ratio computation.
- `scan-engine`: Orchestration layer with multi-stage funnel pipeline (Stage 2 → liquidity → patterns → RS → RR → scoring), 5-factor composite scoring, and multi-threaded batch scanning.

### Modified Capabilities
_(none — no existing specs to modify)_

## Impact

- **New files**: `scanner/__init__.py`, `scanner/models.py`, `scanner/patterns.py`, `scanner/trend.py`, `scanner/rs_rank.py`, `scanner/volume.py`, `scanner/risk_reward.py`, `scanner/scoring.py`, `scanner/engine.py`
- **Modified files**: `config.py` (updated scoring weights, new constants for Stage 2 threshold and liquidity filter)
- **Dependencies on existing code**: Reads from `fetcher/db_writer.read_ohlcv()` and `fetcher/db_writer.get_all_symbols()`. Uses constants from `config.py`.
- **Data dependency**: Requires `^NSEI` (Nifty 50) OHLCV data in the database for RS rank computation.
- **Library dependencies**: Only Python stdlib + `numpy` (already in `requirements.txt`). No new external dependencies.
- **Output**: `scan_all()` returns a list of `ScanResult` dicts sorted by composite score, filtered by `MIN_SIGNAL_SCORE`. The top `TOP_N_CANDIDATES` are passed downstream to the Claude judge (Phase 4).
- **Performance target**: Full scan of 2,300 symbols should complete in <15 seconds using 5 `ThreadPoolExecutor` workers reading from SQLite WAL-mode.
