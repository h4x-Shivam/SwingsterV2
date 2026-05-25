## ADDED Requirements

### Requirement: Detect VCP (Volatility Contraction Pattern)
The system SHALL detect a VCP when a stock forms 2–4 successive contraction bases where each base's range (swing high to swing low) is ≤ 85% of the previous base's range. The final contraction range MUST be ≤ 8% of the current price. The average volume in each successive base MUST be < 75% of the volume in the previous base (volume dry-up). The system SHALL return a `PatternSignal` with name `vcp`, buy point (highest high of last contraction + ₹0.10), and contraction count. Minimum 60 candles required.

#### Scenario: Classic 3-contraction VCP with volume dry-up
- **WHEN** a stock forms 3 successive contractions with ranges 15%, 10%, 4% AND volume in each base decreases by >25%
- **THEN** the system SHALL return a `PatternSignal` with name `vcp`, strength 70–90, contraction_count=3

#### Scenario: 2-contraction VCP (minimum valid)
- **WHEN** a stock forms 2 contractions where second range ≤ 85% of first AND volume decreases
- **THEN** the system SHALL return a `PatternSignal` with name `vcp`, strength 50–70, contraction_count=2

#### Scenario: Final contraction too wide
- **WHEN** the final contraction range exceeds 8% of current price
- **THEN** the system SHALL NOT detect a VCP and SHALL return `None`

#### Scenario: Volume not contracting
- **WHEN** successive contractions have decreasing price ranges but volume increases or stays flat
- **THEN** the system SHALL NOT detect a VCP (supply not drying up)

#### Scenario: Non-contracting ranges (expanding volatility)
- **WHEN** successive base ranges are increasing
- **THEN** the system SHALL NOT detect a VCP

#### Scenario: VCP signal strength scoring
- **WHEN** a valid VCP is detected
- **THEN** strength SHALL be: 2 contractions → base 50, 3 → base 70, 4 → base 90, plus up to 10 bonus for tight final zone (<5% range), plus up to 10 bonus for strong volume dry-up (<50% of prior base volume)

### Requirement: Detect Pole & Flag pattern
The system SHALL detect a Pole & Flag when a stock has an impulsive move up (pole: ≥ 8% gain within ≤ 15 candles) followed by a tight consolidation (flag: 5–20 candles, retracing ≤ 35% of pole gain, flat or slightly downward slope). The flag volume MUST be < 60% of average pole volume. Upward-sloping flags are invalid. Minimum 30 candles required.

#### Scenario: Textbook pole and flag
- **WHEN** a stock gains 12% in 8 candles (pole) followed by a 12-candle consolidation retracing 20% of the pole, with flat/downward slope and low volume
- **THEN** the system SHALL return a `PatternSignal` with name `pole_flag`, strength 70–90

#### Scenario: Flag retraces too much
- **WHEN** the flag retraces more than 35% of the pole's gain
- **THEN** the system SHALL NOT detect a Pole & Flag

#### Scenario: Pole too slow
- **WHEN** a stock gains 8% but takes more than 15 candles
- **THEN** the system SHALL NOT detect a Pole & Flag

#### Scenario: Upward-sloping flag (invalid)
- **WHEN** the flag consolidation has an upward slope (slope of closes > 0.1% per day)
- **THEN** the system SHALL NOT detect a Pole & Flag

#### Scenario: Flag volume too high
- **WHEN** the flag's average volume is ≥ 60% of the pole's average volume
- **THEN** the system SHALL NOT detect a Pole & Flag (no volume dry-up)

#### Scenario: Signal strength scoring
- **WHEN** a valid Pole & Flag is detected
- **THEN** strength SHALL be: pole gain 8–12% → 50, 12–20% → 70, 20%+ → 90, plus up to 10 bonus for tight flag (≤20% retracement), plus up to 10 bonus for volume dry-up

### Requirement: Detect Cup & Handle pattern
The system SHALL detect a Cup & Handle when a stock forms a U-shaped recovery (cup: 30–150 candles, 12–33% retracement from left lip) where the right side recovers within 5% of the left lip, followed by a shallow pullback (handle: 5–25 candles, ≤ 12% pullback from right lip, above cup midpoint, downward or sideways slope only). Handle volume MUST dry up to < 70% of cup volume. Upward-sloping handles are invalid. Minimum 100 candles required.

#### Scenario: Symmetric cup with shallow handle
- **WHEN** a stock drops 20% from 500, bases at 400, recovers to 490, then handles down to 475 with declining volume
- **THEN** the system SHALL return a `PatternSignal` with name `cup_handle`, strength 70–90

#### Scenario: Cup too shallow
- **WHEN** the cup retraces less than 12% from the left lip
- **THEN** the system SHALL NOT detect a Cup & Handle (too shallow, likely noise)

#### Scenario: Cup too deep
- **WHEN** the cup retraces more than 33% from the left lip
- **THEN** the system SHALL NOT detect a Cup & Handle

#### Scenario: Handle too deep
- **WHEN** the handle drops below the cup's midpoint
- **THEN** the system SHALL NOT detect a Cup & Handle

#### Scenario: Upward-sloping handle (invalid)
- **WHEN** the handle has an upward slope
- **THEN** the system SHALL NOT detect a Cup & Handle

#### Scenario: Right lip not recovered
- **WHEN** the right side only recovers to 90% of the left lip (not within 5%)
- **THEN** the system SHALL NOT detect a Cup & Handle

#### Scenario: Cup too short in duration
- **WHEN** the U-shaped formation spans fewer than 30 candles
- **THEN** the system SHALL NOT detect a Cup & Handle

#### Scenario: Signal strength scoring
- **WHEN** a valid Cup & Handle is detected
- **THEN** strength SHALL be: U-shape smoothness → +30, right lip within 3% of left lip → +30 (vs 5% → +20), handle slope valid → +20, volume dry-up in handle → +20

### Requirement: Detect Horizontal Breakout pattern
The system SHALL detect a Breakout when the current price is within 3% of a horizontal resistance level tested 2+ times (swing highs within 2.5% of each other, spaced ≥ 10 trading days apart). The breakout candle volume MUST be ≥ 1.5× the 20-day average volume. Minimum 30 candles required.

#### Scenario: Price near double-tested resistance with volume
- **WHEN** a stock has 2 swing highs at 500 and 505 (within 2.5%), spaced 15 days apart, AND current price is 495 (within 3%), AND today's volume is 2× the 20-day average
- **THEN** the system SHALL return a `PatternSignal` with name `breakout`, strength 55–75

#### Scenario: Triple-tested resistance (stronger)
- **WHEN** resistance tested 3 times over ≥ 30 days with current volume spike
- **THEN** strength SHALL be 70–90

#### Scenario: Price too far from resistance
- **WHEN** current price is more than 3% below the resistance level
- **THEN** the system SHALL NOT detect a Breakout

#### Scenario: Only one resistance test
- **WHEN** resistance tested only once
- **THEN** the system SHALL NOT detect a Breakout

#### Scenario: Tests too close together
- **WHEN** 2 swing highs occur only 3 trading days apart (< 10 day minimum)
- **THEN** the system SHALL NOT count them as separate tests

#### Scenario: Low volume near resistance
- **WHEN** current price is near resistance BUT today's volume is < 1.5× the 20-day average
- **THEN** the system SHALL NOT detect a Breakout (insufficient conviction)

#### Scenario: Signal strength scoring
- **WHEN** a valid Breakout is detected
- **THEN** strength SHALL be: 2 tests → 50, 3 tests → 70, 4+ tests → 90, plus up to 10 bonus for high volume, plus up to 10 bonus for long base duration (>30 days)

### Requirement: Shared swing pivot detection
The system SHALL implement a shared utility function `find_swing_pivots(candles, n=3) → (list[SwingHigh], list[SwingLow])` that identifies swing highs and swing lows. A swing high is a candle whose high is greater than the n candles on either side. A swing low is a candle whose low is less than the n candles on either side. Only pivots from the last 252 candles SHALL be returned. All 4 pattern detectors SHALL use this shared function.

#### Scenario: Clear swing high
- **WHEN** candle[i].high > all candles within n=3 on each side
- **THEN** candle[i] SHALL be identified as a swing high

#### Scenario: Edge of data
- **WHEN** fewer than n candles exist on one side of a potential pivot
- **THEN** the system SHALL skip that candle

### Requirement: Calculate buy point per pattern
The system SHALL calculate a buy point for each detected pattern. VCP: highest high of last contraction + ₹0.10. Pole & Flag: highest high of flag + ₹0.10. Cup & Handle: highest high of handle + ₹0.10. Breakout: resistance level + ₹0.10. The `PatternSignal` SHALL include `buy_point` and `distance_from_buy_pct` (percentage distance from current price to buy point).

#### Scenario: VCP buy point
- **WHEN** a VCP is detected with last contraction high at 500.00
- **THEN** `buy_point` SHALL be 500.10 AND `distance_from_buy_pct` SHALL reflect `(500.10 - current_price) / current_price × 100`

#### Scenario: Stock at buy point
- **WHEN** current price equals the buy point
- **THEN** `distance_from_buy_pct` SHALL be approximately 0.0

### Requirement: Pattern functions return None for insufficient data
The system SHALL return `None` when candle count is below pattern minimums: VCP requires ≥ 60, Pole & Flag ≥ 30, Cup & Handle ≥ 100, Breakout ≥ 30.

#### Scenario: 50 candles for VCP
- **WHEN** a symbol has 50 candles AND VCP detection is called
- **THEN** the system SHALL return `None`

#### Scenario: 40 candles for Pole & Flag
- **WHEN** a symbol has 40 candles AND Pole & Flag detection is called
- **THEN** the system SHALL proceed (40 ≥ 30 minimum)

### Requirement: Return strongest pattern when multiple match
The system SHALL evaluate all 4 pattern detectors and return only the strongest `PatternSignal` (highest strength score). If no pattern is detected, return `None`.

#### Scenario: VCP and Breakout both detected
- **WHEN** VCP strength is 80 AND Breakout strength is 65
- **THEN** the system SHALL return the VCP signal

#### Scenario: No patterns detected
- **WHEN** none of the 4 patterns match
- **THEN** the system SHALL return `None`
