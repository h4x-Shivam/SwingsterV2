## ADDED Requirements

### Requirement: Qualitative momentum ranking via Groq LPU API
The system SHALL support ranking pre-screened technical analysis stock candidates using the Groq LPU inference API. The primary model SHALL be `llama-3.3-70b-versatile` triggered with a low temperature setting (<= 0.3, preferably 0.1) and a structured system prompt tailored to the active scan mode ("VCP", "FLAG_POLE", "CUP_HANDLE", "BREAKOUT", "ALL"). If the primary model call encounters a `RateLimitError` (HTTP 429), the system SHALL retry exactly once using the fallback model `llama-3.1-8b-instant` with identical arguments. Any other exception SHALL immediately trigger `_fallback_ranking()`.

#### Scenario: Running qualitative VCP ranking with fallback retry
- **WHEN** `run_judge(candidates, "VCP")` is executed and a RateLimitError is raised on the primary model
- **THEN** the system SHALL catch the RateLimitError, retry the call exactly once using the fallback model `llama-3.1-8b-instant`, log token usage, and return the ranked setups

### Requirement: Portfolio sector diversification warning
The system SHALL instruct the LLM judge in the prompt to restrict the final top 10 selections to a maximum of 2 stocks from the same NSE sector. The response validator SHALL compute sector counts and log a warning if any sector appears more than 2 times in the top 10 list, but the validator SHALL NOT remove or replace any items.

#### Scenario: Sector diversification validator warning
- **WHEN** the parsed top 10 results contain 3 stocks from the "IT" sector
- **THEN** the system SHALL log a warning indicating that the "IT" sector exceeded the concentration threshold, but keep all items intact in the returned list

### Requirement: Robust JSON parsing and fallback ranking
The system SHALL parse the Groq LLM response securely using a precise multi-stage sequence:
1. Strip markdown fences (` ```json `, ` ```JSON `, ` ``` `).
2. Extract the text boundary between the first `[` and last `]`, returning fallback if not found.
3. Parse JSON with `json.loads()`.
4. Validate list type and non-empty.
5. Trim results to exactly 10 if more than 10.
6. Pad results if fewer than 10 by filling from original candidates sorted by `composite_score` descending (excluding symbols already in results), using specific fallback fields.
7. Validate all 19 required fields per candidate. Fill missing values from original candidates (strings default to `""`, numbers to `0`).
8. Protect calculated fields (`buy_point`, `stop_loss`, `target`, `rr_ratio`) by overwriting them with original values from the scanner.
9. Log a warning if any sector appears more than 2 times.
10. Re-index ranks cleanly from 1 to 10.

If any phase fails, the system SHALL execute `_fallback_ranking()` to sort all candidates by `composite_score` descending, padding with composite-score sorting, and re-indexing the ranks 1 to 10.

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
