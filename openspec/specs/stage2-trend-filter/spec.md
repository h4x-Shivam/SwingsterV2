## ADDED Requirements

### Requirement: Analyze Minervini Stage 2 uptrend
The system SHALL compute a `TrendStatus` for each symbol by evaluating 5 moving average conditions that define a Stage 2 uptrend per Mark Minervini's methodology. Each condition contributes 20 points to a `stage2_score` (0–100). The system SHALL set `is_stage2 = True` only when all 5 conditions pass simultaneously.

#### Scenario: Full Stage 2 uptrend
- **WHEN** all 5 conditions are true (price > 150 MA, price > 200 MA, 150 MA > 200 MA, 200 MA trending up, within 25% of 52-week high)
- **THEN** `is_stage2` SHALL be `True` and `stage2_score` SHALL be 100

#### Scenario: Partial Stage 2 (4 of 5 conditions)
- **WHEN** 4 of the 5 conditions are true
- **THEN** `is_stage2` SHALL be `False` and `stage2_score` SHALL be 80

#### Scenario: No conditions met
- **WHEN** none of the 5 conditions are true
- **THEN** `is_stage2` SHALL be `False` and `stage2_score` SHALL be 0

### Requirement: Check price above 150-day moving average
The system SHALL compute the 150-day simple moving average of closing prices and set `above_150ma = True` when the current price is above this average.

#### Scenario: Price above 150 MA
- **WHEN** the current closing price is 500 AND the 150-day SMA is 450
- **THEN** `above_150ma` SHALL be `True`

#### Scenario: Price below 150 MA
- **WHEN** the current closing price is 400 AND the 150-day SMA is 450
- **THEN** `above_150ma` SHALL be `False`

### Requirement: Check price above 200-day moving average
The system SHALL compute the 200-day simple moving average of closing prices and set `above_200ma = True` when the current price is above this average.

#### Scenario: Price above 200 MA
- **WHEN** the current closing price is 500 AND the 200-day SMA is 420
- **THEN** `above_200ma` SHALL be `True`

### Requirement: Check 150 MA above 200 MA
The system SHALL set `ma150_above_ma200 = True` when the 150-day SMA is greater than the 200-day SMA, confirming medium-term trend strength.

#### Scenario: 150 MA crosses above 200 MA
- **WHEN** the 150-day SMA is 460 AND the 200-day SMA is 420
- **THEN** `ma150_above_ma200` SHALL be `True`

### Requirement: Check 200 MA trending up
The system SHALL set `ma200_trending_up = True` when the current 200-day SMA is greater than the 200-day SMA from 20 trading days ago, confirming the long-term trend direction.

#### Scenario: 200 MA rising
- **WHEN** the 200-day SMA today is 425 AND the 200-day SMA 20 days ago was 415
- **THEN** `ma200_trending_up` SHALL be `True`

#### Scenario: 200 MA declining
- **WHEN** the 200-day SMA today is 410 AND the 200-day SMA 20 days ago was 420
- **THEN** `ma200_trending_up` SHALL be `False`

### Requirement: Check within 25% of 52-week high
The system SHALL compute the 52-week high (maximum high of last 252 candles) and set `within_25pct_of_52w_high = True` when the current price is above 75% of the 52-week high.

#### Scenario: Near 52-week high
- **WHEN** the 52-week high is 600 AND the current price is 520 (86.7% of high)
- **THEN** `within_25pct_of_52w_high` SHALL be `True`

#### Scenario: Far from 52-week high
- **WHEN** the 52-week high is 600 AND the current price is 400 (66.7% of high)
- **THEN** `within_25pct_of_52w_high` SHALL be `False`

### Requirement: Skip symbols with Stage 2 score below threshold
The scan engine SHALL skip symbols entirely when `stage2_score < 60`, preventing pattern detection from running on stocks not in or near a Stage 2 uptrend.

#### Scenario: Stage 2 score 80 — proceed with scanning
- **WHEN** a symbol's `stage2_score` is 80
- **THEN** the engine SHALL proceed with pattern detection

#### Scenario: Stage 2 score 40 — skip symbol
- **WHEN** a symbol's `stage2_score` is 40
- **THEN** the engine SHALL skip the symbol and return `None`

### Requirement: Handle insufficient data for trend analysis
The system SHALL return a default `TrendStatus` with all conditions set to `False` and `stage2_score = 0` when the symbol has fewer than 200 candles of data.

#### Scenario: New listing with 150 candles
- **WHEN** a symbol has only 150 candles of data
- **THEN** the system SHALL return default TrendStatus (all False, score=0)
