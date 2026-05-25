## ADDED Requirements

### Requirement: Identify swing low support levels
The system SHALL identify support levels by finding swing lows — candles whose low is lower than the `n` candles on either side (default `n=3`). The system SHALL return the most recent swing low within the last 20 candles as the primary support level.

#### Scenario: Clear swing low found
- **WHEN** candle[i].low < all neighbors within n=3 on each side
- **THEN** candle[i].low SHALL be identified as a swing low support level

#### Scenario: No swing low in lookback window
- **WHEN** no candle in the last 20 candles qualifies as a swing low
- **THEN** the system SHALL fall back to the minimum low of the last 20 candles as support

### Requirement: Identify swing high resistance levels
The system SHALL identify resistance levels by finding swing highs above the current price. The nearest swing high above the current price SHALL be the primary resistance/target level.

#### Scenario: Resistance above current price
- **WHEN** a swing high exists at price 500 AND the current price is 450
- **THEN** the system SHALL return 500 as the resistance level

#### Scenario: No resistance found above current price
- **WHEN** no swing high exists above the current price
- **THEN** the system SHALL use the maximum high of the last 20 candles as resistance

### Requirement: Calculate stop-loss level
The system SHALL calculate stop-loss as `support × 0.99` (1% buffer below the support price).

#### Scenario: Stop-loss with buffer
- **WHEN** the identified support level is 400.00
- **THEN** the stop-loss SHALL be 396.00

### Requirement: Calculate target price
The system SHALL calculate the target price as the next resistance level above the current price.

#### Scenario: Target at resistance
- **WHEN** the identified resistance level is 550.00
- **THEN** the target price SHALL be 550.00

### Requirement: Compute risk-reward ratio
The system SHALL compute the risk-reward ratio as `(target - entry) / (entry - stop_loss)` where entry is the current price. Division by zero SHALL be guarded (return 0.0 when entry equals stop-loss).

#### Scenario: Favorable risk-reward
- **WHEN** entry is 450, stop-loss is 430, target is 510
- **THEN** the risk-reward ratio SHALL be (510-450)/(450-430) = 3.0

#### Scenario: Entry equals stop-loss
- **WHEN** entry equals the stop-loss level
- **THEN** the risk-reward ratio SHALL be 0.0

### Requirement: Map risk-reward to a 0–100 score
The system SHALL map the risk-reward ratio to a score with updated breakpoints: RR < 1.0 → 0, RR 1.0–2.0 → 30, RR 2.0–3.0 → 60, RR 3.0–4.0 → 80, RR 4.0+ → 100. Linear interpolation SHALL be used between breakpoints.

#### Scenario: Poor risk-reward
- **WHEN** the risk-reward ratio is 0.5
- **THEN** the risk-reward score SHALL be 0

#### Scenario: Acceptable risk-reward
- **WHEN** the risk-reward ratio is 2.0
- **THEN** the risk-reward score SHALL be 60

#### Scenario: Good risk-reward
- **WHEN** the risk-reward ratio is 3.0
- **THEN** the risk-reward score SHALL be 80

#### Scenario: Excellent risk-reward
- **WHEN** the risk-reward ratio is 4.0+
- **THEN** the risk-reward score SHALL be 100

### Requirement: Return structured RiskReward result
The `RiskReward` dataclass SHALL contain: support level, resistance level, stop_loss, target, ratio, and score. All fields SHALL be floating-point numbers.

#### Scenario: Complete RiskReward object
- **WHEN** support=400, resistance=550, current_price=450
- **THEN** the `RiskReward` SHALL contain support=400, resistance=550, stop_loss=396.0, target=550.0, ratio and score computed accordingly

### Requirement: Handle insufficient data for pivot detection
The system SHALL return a default `RiskReward` with ratio 0.0 and score 0 when the symbol has fewer than 10 candles.

#### Scenario: New listing with 5 candles
- **WHEN** a symbol has only 5 candles of data
- **THEN** the system SHALL return a default `RiskReward` with ratio=0.0 and score=0
