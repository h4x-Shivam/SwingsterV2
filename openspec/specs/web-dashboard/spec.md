### Requirement: Display Live Pattern Detection Dashboard
The system SHALL provide a web-based Next.js application that visualizes the results of the Python scanning engine. The frontend SHALL NOT connect directly to the SQL database but instead SHALL read the pre-processed output JSON files (`data/results.json`, `data/scan_summary.json`, and `data/final_picks.json`).

#### Scenario: User navigates to the dashboard
- **WHEN** the user visits the `/dashboard` route
- **THEN** the system SHALL load the latest data from `final_picks.json` and `scan_summary.json`
- **AND** display a Hero Stats header with the total tickers scanned and a dropdown list of the matching VCP symbols with a "Copy" utility.
- **AND** display a data grid containing the Rank, Symbol, Current Price, Distance to Buy, Risk/Reward (R:R), and Conviction badges.

### Requirement: Sliding Scanner Transition
The system SHALL provide a dynamic micro-interaction when a user manually triggers a pattern scan from the library UI.

#### Scenario: User runs a live scan from the library
- **GIVEN** the user is viewing the pattern library (StickyScroll layout)
- **WHEN** the user selects a pattern card and clicks "RUN SCAN"
- **THEN** the system SHALL fade out the left-side text description
- **AND** smoothly slide the pattern chart card to the left using layout animations
- **AND** slide a "Scan Progress Terminal" into view on the right side
- **AND** simulate a scrolling terminal output showing the multi-stage filter pipeline (fetching, Stage 2, pattern detection, RR filtering, Judge grading).

### Requirement: Scanner Output Integration
The dashboard UI SHALL accurately reflect the 5-part composite score logic used by the backend scan engine.

#### Scenario: User expands a candidate row
- **WHEN** the user clicks on a candidate row in the data grid
- **THEN** the system SHALL display an expanded detail view or drawer
- **AND** render the AI Judge's qualitative verdict and any warning flags
- **AND** display the breakdown of the composite score: Signal Strength (45% for VCP), Volume Score (30%), Risk-Reward (10%), Stage 2 Trend (10%), and Relative Strength (5%).
