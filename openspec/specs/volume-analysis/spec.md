## ADDED Requirements

### Requirement: Compute relative volume ratio
The system SHALL compute the relative volume ratio as the current candle's volume divided by the 20-day simple moving average (SMA) of volume. The system SHALL return this ratio as part of a `VolumeMetrics` dataclass.

#### Scenario: Normal volume day
- **WHEN** today's volume is 1,000,000 AND the 20-day average volume is 1,000,000
- **THEN** the relative volume ratio SHALL be 1.0

#### Scenario: Volume spike day
- **WHEN** today's volume is 3,000,000 AND the 20-day average volume is 1,000,000
- **THEN** the relative volume ratio SHALL be 3.0

### Requirement: Minimum liquidity filter
The system SHALL flag a symbol as illiquid when the 20-day average volume is below 50,000 shares. Illiquid symbols SHALL have `volume_score` set to 0 and SHALL be skipped by the scan engine. The `VolumeMetrics` SHALL include an `is_illiquid` flag.

#### Scenario: Illiquid stock
- **WHEN** the 20-day average volume is 30,000 shares
- **THEN** `is_illiquid` SHALL be `True` AND `volume_score` SHALL be 0

#### Scenario: Liquid stock
- **WHEN** the 20-day average volume is 500,000 shares
- **THEN** `is_illiquid` SHALL be `False` AND volume scoring SHALL proceed normally

### Requirement: Detect volume spikes
The system SHALL flag a volume spike when the relative volume ratio exceeds 1.5. The system SHALL set `is_spike=True` in the `VolumeMetrics` when this threshold is met.

#### Scenario: Volume above spike threshold
- **WHEN** the relative volume ratio is 2.3
- **THEN** `is_spike` SHALL be `True`

#### Scenario: Volume below spike threshold
- **WHEN** the relative volume ratio is 1.2
- **THEN** `is_spike` SHALL be `False`

### Requirement: Compute volume trend
The system SHALL compute a volume trend by comparing the 5-day volume SMA to the 20-day volume SMA. A 5-day SMA above the 20-day SMA indicates `trend="increasing"`, below indicates `trend="decreasing"`, and within 10% indicates `trend="flat"`.

#### Scenario: Increasing volume trend
- **WHEN** the 5-day volume SMA is 1,500,000 AND the 20-day volume SMA is 1,000,000
- **THEN** the volume trend SHALL be `"increasing"`

#### Scenario: Decreasing volume trend
- **WHEN** the 5-day volume SMA is 600,000 AND the 20-day volume SMA is 1,000,000
- **THEN** the volume trend SHALL be `"decreasing"`

#### Scenario: Flat volume trend
- **WHEN** the 5-day volume SMA is 1,050,000 AND the 20-day volume SMA is 1,000,000 (within 10%)
- **THEN** the volume trend SHALL be `"flat"`

### Requirement: Map volume metrics to a 0–100 score
The system SHALL map the relative volume ratio to a score with updated breakpoints: ratio < 1.0 → 30, ratio 1.0–1.5 → 60, ratio 1.5–2.0 → 80, ratio 2.0+ → 100. Linear interpolation SHALL be used between breakpoints.

#### Scenario: Below-average volume
- **WHEN** relative volume ratio is 0.5
- **THEN** the volume score SHALL be 30

#### Scenario: Average volume
- **WHEN** relative volume ratio is 1.0
- **THEN** the volume score SHALL be 60

#### Scenario: Volume spike
- **WHEN** relative volume ratio is 1.5
- **THEN** the volume score SHALL be 80

#### Scenario: Extreme volume
- **WHEN** relative volume ratio is 2.0+
- **THEN** the volume score SHALL be 100

### Requirement: Handle insufficient volume data
The system SHALL return a default `VolumeMetrics` with ratio 1.0, `is_spike=False`, `trend="flat"`, `is_illiquid=False`, and score 0 when the symbol has fewer than 20 candles of volume data.

#### Scenario: New listing with 10 days of data
- **WHEN** a symbol has only 10 candles of data
- **THEN** the volume metrics SHALL use defaults (ratio=1.0, score=0)
