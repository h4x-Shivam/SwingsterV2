## ADDED Requirements

### Requirement: Parse NSE CSV into structured data
The system SHALL parse the downloaded `EQUITY_L.csv` content, using the CSV header row to identify columns, and produce a structured list of equity ticker records.

#### Scenario: Valid CSV with header row
- **WHEN** the downloaded CSV content contains a valid header row and data rows
- **THEN** the system SHALL parse each row into a record keyed by column names from the header (e.g., SYMBOL, NAME OF COMPANY, SERIES, DATE OF LISTING, ISIN NUMBER, FACE VALUE)

#### Scenario: Empty or malformed CSV
- **WHEN** the downloaded CSV content is empty or lacks a recognizable header row
- **THEN** the system SHALL raise a clear error message and SHALL NOT overwrite any existing `data/symbols.csv`

### Requirement: Persist ticker data to data/symbols.csv
The system SHALL write the parsed ticker records to `data/symbols.csv`, retaining all columns from the source CSV, with the original header row preserved.

#### Scenario: Successful write
- **WHEN** parsing succeeds and records are available
- **THEN** the system SHALL write a CSV file at `data/symbols.csv` containing the header row followed by all data rows, overwriting any previous content

#### Scenario: Write reports record count
- **WHEN** the file is written successfully
- **THEN** the system SHALL print a summary message indicating the number of ticker records saved (e.g., "Saved 2100 tickers to data/symbols.csv")

### Requirement: Script is re-runnable
The system SHALL support being executed multiple times. Each execution SHALL fetch fresh data from NSE and overwrite the existing `data/symbols.csv` with the latest data.

#### Scenario: Re-run overwrites previous data
- **WHEN** `data/symbols.csv` already exists and the script is run again
- **THEN** the system SHALL download fresh data and overwrite the file completely with the new data
