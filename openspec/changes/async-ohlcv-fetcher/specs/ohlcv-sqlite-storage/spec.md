## ADDED Requirements

### Requirement: Initialize SQLite database with OHLCV schema
The system SHALL create (or open) a SQLite database at the configured path and ensure the `ohlcv` table exists with columns: `symbol` (TEXT), `date` (TEXT), `open` (REAL), `high` (REAL), `low` (REAL), `close` (REAL), `volume` (INTEGER), with a composite primary key of `(symbol, date)`.

#### Scenario: First run — database does not exist
- **WHEN** the database file does not exist
- **THEN** the system SHALL create the file, create the `ohlcv` table, and create an index on `symbol`

#### Scenario: Subsequent run — database already exists
- **WHEN** the database file and table already exist
- **THEN** the system SHALL open the database without modifying the existing schema (using IF NOT EXISTS)

### Requirement: WAL journal mode for concurrent access
The system SHALL enable WAL (Write-Ahead Logging) journal mode on every connection to support concurrent reads from scanner threads while the fetcher writes.

#### Scenario: Multiple readers during write
- **WHEN** scanner threads read OHLCV data while the fetcher is writing new rows
- **THEN** reads SHALL succeed without blocking or errors due to WAL mode

### Requirement: Upsert OHLCV rows with INSERT OR REPLACE
The system SHALL write OHLCV rows using `INSERT OR REPLACE` so that delta fetches update existing rows and insert new ones without creating duplicates.

#### Scenario: New rows inserted
- **WHEN** the fetcher writes rows for dates not yet in the database
- **THEN** the rows SHALL be inserted as new records

#### Scenario: Existing rows updated
- **WHEN** the fetcher writes rows for (symbol, date) pairs that already exist
- **THEN** the existing rows SHALL be replaced with the new values

### Requirement: Read OHLCV data for a single symbol
The system SHALL provide a function to retrieve all OHLCV rows for a given symbol, ordered by date ascending.

#### Scenario: Symbol exists in database
- **WHEN** a consumer requests data for a symbol that has rows in the database
- **THEN** the system SHALL return a list of (date, open, high, low, close, volume) tuples sorted by date ascending

#### Scenario: Symbol not in database
- **WHEN** a consumer requests data for a symbol with no rows
- **THEN** the system SHALL return an empty list

### Requirement: Query all stored symbols
The system SHALL provide a function to return a sorted list of all distinct symbols in the database.

#### Scenario: Database has data
- **WHEN** the database contains OHLCV rows for multiple symbols
- **THEN** the system SHALL return a sorted list of unique symbol strings
