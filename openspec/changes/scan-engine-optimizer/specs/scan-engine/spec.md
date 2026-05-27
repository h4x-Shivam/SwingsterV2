## MODIFIED Requirements

### Requirement: Batch scan all symbols with thread pool
The system SHALL expose a `scan_all() -> list[ScanResult]` function that reads and pre-filters eligible symbols from the database, and scans each using `scan_symbol()` via a `ProcessPoolExecutor` with `NUM_AGENTS` workers, returning results sorted by composite score descending. The database query SHALL pre-filter symbols to exclude those that are clearly illiquid (average volume < 50k) or have fewer than 30 candles before loading their full OHLCV history into memory.

#### Scenario: Full batch scan
- **WHEN** `scan_all()` is called with 2,300 symbols in the database
- **THEN** the system SHALL pre-filter and scan eligible symbols using parallel processes and return results sorted by score descending

#### Scenario: Empty database
- **WHEN** `scan_all()` is called AND the database has no symbols
- **THEN** the system SHALL return an empty list

### Requirement: Performance target
The system SHALL complete a full scan of 2,300 symbols in under 8 seconds on a standard desktop machine using a process pool. Pre-filtering in SQL and process-level parallelism SHALL eliminate bottleneck latency.

#### Scenario: Full scan timing
- **WHEN** `scan_all()` is run against 2,300 symbols
- **THEN** the scan SHALL complete in under 8 seconds wall-clock time
