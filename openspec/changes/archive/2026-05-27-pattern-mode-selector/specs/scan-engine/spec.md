## ADDED Requirements

### Requirement: Selectable pattern mode scanning
The system SHALL support pattern mode selection ("VCP", "FLAG_POLE", "CUP_HANDLE", "BREAKOUT", "ALL") via `scan_all(mode)` and the CLI `--mode` parameter. When a specific mode is selected, the scanner SHALL execute only the matching pattern detector, ignoring all other pattern types, and rank only matching candidate setups.

#### Scenario: VCP mode selected
- **WHEN** `scan_all("VCP")` is called
- **THEN** the system SHALL run only VCP pattern detection and return only VCP setups

#### Scenario: Invalid mode selected
- **WHEN** `scan_all("INVALID")` is called
- **THEN** the system SHALL raise a ValueError listing the valid modes

## MODIFIED Requirements

### Requirement: Orchestrate single-symbol scanning with multi-stage funnel
The system SHALL expose a `scan_symbol(symbol: str, conn=None, nifty_candles=None, mode: str = "ALL") → ScanResult | None` function that runs a multi-stage pipeline per symbol:
1. Read OHLCV data from SQLite
2. Convert to Candle dataclasses
3. `analyze_trend()` — skip if `stage2_score < 60`
4. `analyze_volume()` — skip if illiquid (avg volume < 50k)
5. `detect_patterns(candles, mode)` — only execute matching pattern detectors for the selected mode, skipping non-matching ones. Skip symbol if no matching pattern is found.
6. `compute_rs()` against Nifty 50
7. `compute_risk_reward()`
8. `compute_composite_score()`
9. Return `ScanResult` containing the `scan_mode` field populated with the active mode.

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
