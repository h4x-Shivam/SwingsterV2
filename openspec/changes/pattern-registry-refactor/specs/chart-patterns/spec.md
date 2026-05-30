## ADDED Requirements

### Requirement: Pattern-Specific Configuration
Each pattern SHALL maintain its own isolated configuration object defining thresholds, scoring weights, and UI metadata.

#### Scenario: Pattern evaluation config retrieval
- **WHEN** a pattern algorithm checks a threshold parameter like volume contraction
- **THEN** it must retrieve it from its own config object rather than a global constant

### Requirement: Independent Pattern Scoring
Each pattern SHALL calculate its own final score based on custom weights summing to 1.0.

#### Scenario: Scoring a breakout
- **WHEN** a breakout pattern is scored
- **THEN** it applies a heavier weight to volume expansion based on its config compared to a VCP pattern
