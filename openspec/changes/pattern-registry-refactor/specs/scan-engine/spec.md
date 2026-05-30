## ADDED Requirements

### Requirement: Score-Based Candidate Filtering
The scan engine SHALL filter candidates by enforcing a score-based minimum threshold rather than a hard cap on candidate volume.

#### Scenario: Scanning for single pattern
- **WHEN** scan_all is invoked for a specific pattern mode
- **THEN** it must use the pattern's config.min_candidate_score to admit candidates

#### Scenario: Scanning for all patterns
- **WHEN** scan_all is invoked with "ALL" mode
- **THEN** it must use the global minimum score threshold for candidate selection
