## ADDED Requirements

### Requirement: Fetch EQUITY_L.csv from NSE
The system SHALL download the official equity ticker CSV from `https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv` using an HTTP session that mimics browser behavior.

#### Scenario: Successful download
- **WHEN** the script is executed and NSE is reachable
- **THEN** the system SHALL establish a session by first visiting `https://www.nseindia.com` to obtain cookies, then download `EQUITY_L.csv` and return its raw content

#### Scenario: NSE rejects the request (403 Forbidden)
- **WHEN** the initial session request to `nseindia.com` fails or the CSV download returns a non-200 status
- **THEN** the system SHALL raise a clear error message indicating the download failed, including the HTTP status code

#### Scenario: Network unavailable
- **WHEN** the script is executed and NSE is unreachable (DNS failure, timeout)
- **THEN** the system SHALL raise a clear error message indicating a network connectivity issue and SHALL NOT overwrite any existing `data/symbols.csv`

### Requirement: Use browser-like HTTP headers
The system SHALL send a `User-Agent` header mimicking a modern browser (e.g., Chrome on Windows) with every HTTP request to NSE, to satisfy their anti-bot protections.

#### Scenario: Headers are set correctly
- **WHEN** the system makes any HTTP request to NSE domains
- **THEN** the request SHALL include at minimum a `User-Agent` header with a value that identifies as a modern desktop browser
