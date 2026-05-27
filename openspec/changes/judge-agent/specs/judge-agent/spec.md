## ADDED Requirements

### Requirement: Qualitative momentum ranking via Groq LPU API
The system SHALL support ranking pre-screened technical analysis stock candidates using the Groq LPU inference API. The primary model SHALL be `llama-3.3-70b-versatile` (with fallback `llama-3.1-8b-instant`), triggered with a low temperature setting (<= 0.3, preferably 0.1) and a structured system prompt tailored to the active scan mode ("VCP", "FLAG_POLE", "CUP_HANDLE", "BREAKOUT", "ALL").

#### Scenario: Running qualitative VCP ranking
- **WHEN** `run_judge(candidates, "VCP")` is executed
- **THEN** the system SHALL invoke the Groq API using VCP qualitative criteria (contractions count, volume drying, proximity to pivot point) and return the ranked setups

### Requirement: Portfolio sector diversification
The system SHALL restrict the final top 10 selections to a maximum of 2 stocks from the same NSE sector. If the original candidates contain multiple stocks from the same sector, the system SHALL rotate in next-best candidates from other sectors to ensure broad diversification.

#### Scenario: Sector diversification enforcement
- **WHEN** the Groq judge receives multiple candidates from the same sector
- **THEN** the final returned top 10 list SHALL contain at most 2 stocks belonging to any single sector

### Requirement: Robust JSON parsing and fallback ranking
The system SHALL parse the Groq LLM response securely by removing markdown wrappers and extracting the text boundary between the first `[` and last `]`. If the Groq API call fails, times out, or returns invalid JSON, the system SHALL execute `_fallback_ranking()` to sort all candidates by `composite_score` descending, padding with composite-score sorting, and re-indexing the ranks 1 to 10.

#### Scenario: Groq API failure fallback
- **WHEN** the Groq API call raises an exception or times out
- **THEN** the system SHALL log a warning, generate a deterministic ranking of 10 candidates sorted by composite score, populate the `judge_verdict` with fallback info, and return the list without crashing

### Requirement: Quantitative pricing and ratio safeguard
The system SHALL protect calculated metrics (`buy_point`, `stop_loss`, `target`, `rr_ratio`) by overwriting any judge response values with the exact quantitative values from the original scanned candidates list, completely preventing LLM hallucination of financial fields.

#### Scenario: Overwriting hallucinated values
- **WHEN** the Groq judge returns the ranked top 10 list
- **THEN** the system SHALL restore the values of `buy_point`, `stop_loss`, `target`, and `rr_ratio` from the original scan results for each candidate symbol

### Requirement: Curated top 10 persistence
The system SHALL persist the final curated portfolio to `data/top10.json`. The output JSON file SHALL contain: `scan_mode`, `scan_time`, `total_picks` (exactly 10), and `results` (containing all 19 required candidate fields).

#### Scenario: Saving curated portfolio
- **WHEN** `save_top10(top10, mode)` is called
- **THEN** the system SHALL create/overwrite `data/top10.json` with a structured document matching the spec schema
