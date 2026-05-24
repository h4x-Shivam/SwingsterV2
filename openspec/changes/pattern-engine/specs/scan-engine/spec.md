## ADDED Requirements

### Requirement: Orchestrate single-symbol scanning with multi-stage funnel
The system SHALL expose a `scan_symbol(symbol: str) → ScanResult | None` function that runs a multi-stage pipeline per symbol:
1. Read OHLCV data from SQLite
2. Convert to Candle dataclasses
3. `analyze_trend()` — skip if `stage2_score < 60`
4. `analyze_volume()` — skip if illiquid (avg volume < 50k)
5. `detect_patterns()` — skip if `None`
6. `compute_rs()` against Nifty 50
7. `compute_risk_reward()`
8. `compute_composite_score()`
9. Return `ScanResult`

The function SHALL return `None` at any stage that fails its gate condition.

#### Scenario: Symbol passes all gates
- **WHEN** `scan_symbol("RELIANCE")` is called AND RELIANCE is in Stage 2, liquid, and has a VCP pattern
- **THEN** the system SHALL return a complete `ScanResult` with all sub-scores

#### Scenario: Symbol fails Stage 2
- **WHEN** `scan_symbol("WEAKSTOCK")` is called AND its `stage2_score` is 40
- **THEN** the system SHALL skip pattern detection and return `None`

#### Scenario: Symbol is illiquid
- **WHEN** `scan_symbol("LOWVOL")` is called AND its 20-day avg volume is 20,000
- **THEN** the system SHALL skip pattern detection and return `None`

#### Scenario: Symbol has no pattern
- **WHEN** `scan_symbol("INFY")` is called AND no chart pattern is detected
- **THEN** the system SHALL return `None`

#### Scenario: Symbol not in database
- **WHEN** `scan_symbol("UNKNOWN")` is called AND no OHLCV data exists
- **THEN** the system SHALL return `None` and log a warning

### Requirement: Batch scan all symbols with thread pool
The system SHALL expose a `scan_all() → list[ScanResult]` function that reads all symbols from the database, scans each using `scan_symbol()` via a `ThreadPoolExecutor` with `NUM_AGENTS` workers (default 5), and returns results sorted by composite score descending.

#### Scenario: Full batch scan
- **WHEN** `scan_all()` is called with 2,300 symbols in the database
- **THEN** the system SHALL scan all symbols using 5 parallel threads and return results sorted by score descending

#### Scenario: Empty database
- **WHEN** `scan_all()` is called AND the database has no symbols
- **THEN** the system SHALL return an empty list

### Requirement: Compute 5-factor composite score
The system SHALL compute the composite score as: `signal_strength × 0.40 + volume_score × 0.25 + rr_score × 0.20 + stage2_score × 0.10 + rs_score × 0.05`. Weights are imported from `config.py`. The result SHALL be rounded to 1 decimal place and clamped to 0–100.

#### Scenario: Strong across all factors
- **WHEN** signal=85, volume=80, rr=70, stage2=100, rs=90
- **THEN** composite SHALL be 85×0.40 + 80×0.25 + 70×0.20 + 100×0.10 + 90×0.05 = 34.0 + 20.0 + 14.0 + 10.0 + 4.5 = 82.5

#### Scenario: Weak RS but strong pattern
- **WHEN** signal=90, volume=75, rr=60, stage2=100, rs=20
- **THEN** composite SHALL be 90×0.40 + 75×0.25 + 60×0.20 + 100×0.10 + 20×0.05 = 36.0 + 18.75 + 12.0 + 10.0 + 1.0 = 77.8

### Requirement: Cap score for non-Stage-2 stocks
The system SHALL cap the composite score at 50 for any symbol where `is_stage2 = False`, regardless of how strong the pattern, volume, and risk-reward scores are. This ensures non-trending stocks never rank above trending ones.

#### Scenario: Strong pattern but not in Stage 2
- **WHEN** a symbol has signal=95, volume=90, rr=85 BUT `is_stage2 = False` (stage2_score=60)
- **THEN** the computed composite score SHALL be capped at 50

#### Scenario: Full Stage 2 — no cap
- **WHEN** a symbol has `is_stage2 = True`
- **THEN** the composite score SHALL NOT be capped

### Requirement: Filter results by minimum signal score
The system SHALL exclude any `ScanResult` with a composite score below `MIN_SIGNAL_SCORE` (default 55) from the `scan_all()` output.

#### Scenario: Score above threshold
- **WHEN** a symbol has composite score 72
- **THEN** the symbol SHALL be included in the results

#### Scenario: Score below threshold
- **WHEN** a symbol has composite score 40
- **THEN** the symbol SHALL be excluded

### Requirement: Cap results at TOP_N_CANDIDATES
The system SHALL return at most `TOP_N_CANDIDATES` (default 30) results from `scan_all()`.

#### Scenario: More candidates than cap
- **WHEN** 50 symbols pass the minimum score threshold
- **THEN** the system SHALL return only the top 30 by composite score

#### Scenario: Fewer candidates than cap
- **WHEN** only 12 symbols pass the minimum score threshold
- **THEN** the system SHALL return all 12

### Requirement: ScanResult contains full analysis data
The `ScanResult` dataclass SHALL contain: `symbol`, `pattern` (name), `signal_strength`, `volume_score`, `rr_score`, `stage2_score`, `rs_score`, `composite_score`, `buy_point`, `stop_loss`, `target`, `rr_ratio`, `current_price`, `distance_from_buy_pct`.

#### Scenario: Complete result structure
- **WHEN** a symbol passes scanning with all metrics computed
- **THEN** the `ScanResult` SHALL contain all fields populated

### Requirement: Graceful error handling per symbol
The system SHALL catch exceptions during individual symbol scanning, log them, and skip the symbol without crashing the batch.

#### Scenario: Corrupted data for one symbol
- **WHEN** scanning raises an unexpected exception
- **THEN** the system SHALL log the error, skip that symbol, and continue

### Requirement: Detailed funnel logging
The system SHALL log a final summary after `scan_all()` completes: total symbols scanned, passed Stage 2, passed volume filter, patterns found, final candidates, and total time taken. Progress logging SHALL occur every 100 symbols.

#### Scenario: Full scan summary
- **WHEN** `scan_all()` completes
- **THEN** the system SHALL log: "Scanned 2300 | Stage2: 850 | Liquid: 780 | Patterns: 45 | Candidates: 30 | Time: 8.2s"

### Requirement: Performance target
The system SHALL complete a full scan of 2,300 symbols in under 15 seconds on a standard desktop machine using 5 threads. Stage 2 filtering eliminates the majority of symbols before expensive pattern detection.

#### Scenario: Full scan timing
- **WHEN** `scan_all()` is run against 2,300 symbols
- **THEN** the scan SHALL complete in under 15 seconds wall-clock time
