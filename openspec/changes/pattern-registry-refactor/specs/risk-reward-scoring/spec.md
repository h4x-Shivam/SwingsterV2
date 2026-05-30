## ADDED Requirements

### Requirement: Hard Guards for Negative Risk/Reward Parameters
The risk/reward calculation system SHALL enforce safeguards ensuring that the stop loss and profit targets fall into structurally correct zones relative to the entry point.

#### Scenario: Stop loss exceeds entry point
- **WHEN** swing low detection yields a resistance point mathematically higher than the current entry point
- **THEN** it must revert the stop loss to a fallback of the minimum of the last 20 candles multiplied by 0.99

#### Scenario: Target drops below entry point
- **WHEN** swing high detection yields a target point mathematically lower than the current entry point
- **THEN** it must revert the target to a fallback 15% above the current entry point

### Requirement: Adjustable Hard RR Minimum
The risk/reward calculator SHALL evaluate structural invalidity via a dynamically passed `rr_hard_minimum` to filter broken trades instead of filtering via a static quality score.

#### Scenario: Passing parameter validation
- **WHEN** a scan engine evaluates a candidate
- **THEN** it enforces the `rr_hard_minimum` specific to the candidate's pattern using the pattern's configuration
