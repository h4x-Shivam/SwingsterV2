## ADDED Requirements

### Requirement: Compute 12-month relative strength vs Nifty 50
The system SHALL compute an RS rank by comparing the symbol's 12-month return against the Nifty 50 (`^NSEI`) 12-month return. The 12-month return is calculated as `(close[-1] - close[-252]) / close[-252]`. The system SHALL return an `RSRank` dataclass with both returns, an `rs_score` (0–100), and an `outperforming` flag.

#### Scenario: Stock significantly outperforming Nifty
- **WHEN** a stock's 12-month return is +45% AND Nifty 50's 12-month return is +15% (outperform by 30%)
- **THEN** `rs_score` SHALL be 100 AND `outperforming` SHALL be `True`

#### Scenario: Stock in line with Nifty
- **WHEN** a stock's 12-month return is +16% AND Nifty 50's 12-month return is +15%
- **THEN** `rs_score` SHALL be approximately 50 AND `outperforming` SHALL be `True`

#### Scenario: Stock underperforming Nifty significantly
- **WHEN** a stock's 12-month return is -5% AND Nifty 50's 12-month return is +15% (underperform by 20%)
- **THEN** `rs_score` SHALL be 0 AND `outperforming` SHALL be `False`

### Requirement: RS score mapping by outperformance magnitude
The system SHALL map RS score as follows based on the difference between symbol return and Nifty return:
- Outperforming by 20%+ → score 100
- Outperforming by 10% → score 80
- In line with Nifty (within ±5%) → score 50
- Underperforming by 10% → score 20
- Underperforming by 20%+ → score 0
Linear interpolation SHALL be used between breakpoints.

#### Scenario: Moderate outperformance
- **WHEN** a stock outperforms Nifty by 10%
- **THEN** `rs_score` SHALL be 80

#### Scenario: Slight underperformance
- **WHEN** a stock underperforms Nifty by 10%
- **THEN** `rs_score` SHALL be 20

### Requirement: Set outperforming flag
The system SHALL set `outperforming = True` when the symbol's 12-month return exceeds the Nifty 50's 12-month return.

#### Scenario: Stock beating index
- **WHEN** symbol return is +25% AND Nifty return is +15%
- **THEN** `outperforming` SHALL be `True`

#### Scenario: Stock lagging index
- **WHEN** symbol return is +10% AND Nifty return is +15%
- **THEN** `outperforming` SHALL be `False`

### Requirement: Require Nifty 50 data in database
The system SHALL read `^NSEI` OHLCV data from the database for benchmark comparison. The `^NSEI` ticker MUST be included in the fetch pipeline alongside regular NSE symbols.

#### Scenario: Nifty data available
- **WHEN** `^NSEI` has 252+ candles in the database
- **THEN** the RS computation SHALL proceed normally

#### Scenario: Nifty data missing
- **WHEN** `^NSEI` has no data in the database
- **THEN** the system SHALL return a default RSRank with `rs_score = 50` and `outperforming = False`

### Requirement: Handle insufficient data for RS computation
The system SHALL return a default `RSRank` with `rs_score = 50` and `outperforming = False` when either the symbol or Nifty 50 has fewer than 252 candles.

#### Scenario: New listing with 100 candles
- **WHEN** a symbol has only 100 candles of data
- **THEN** `rs_score` SHALL be 50 and `outperforming` SHALL be `False`
