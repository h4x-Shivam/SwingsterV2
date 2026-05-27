## Why

The current system runs all pattern detectors on every stock during scanning, resulting in a mixed output of setups. The user wants to scan for and retrieve a specific selected chart pattern (e.g. VCP, FLAG_POLE, CUP_HANDLE, or BREAKOUT) at a time, allowing for dedicated strategy-specific scanning and ranking before passing results to the judging agent.

## What Changes

- **Modified**: Introduce selectable scanning modes under `config.py` (`SCAN_MODES` and `SCAN_MODE`).
- **Modified**: Update the pattern detection entry point `detect_patterns()` in `patterns.py` to accept and gate detectors based on a `mode` parameter.
- **Modified**: Thread the `mode` parameter through `engine.py`'s processes, using packed tuple arguments in `_scan_batch` for Windows safety.
- **Modified**: Add the `scan_mode` field to `ScanResult` in `models.py` to identify which pattern scan produced the setup.
- **NEW**: Expose a standard command-line interface `--mode` flag in `main.py` to execute dedicated pattern runs.

## Capabilities

### New Capabilities

### Modified Capabilities
- `scan-engine`: Expose pattern mode selection during batch orchestration, allowing processes to only invoke specific subset of pattern rules, and add `scan_mode` to scan results.

## Impact

- `config.py`: Add `SCAN_MODES` and `SCAN_MODE` constants.
- `scanner/models.py`: Add `scan_mode` field to `ScanResult`.
- `scanner/patterns.py`: Gated calling in `detect_patterns()`.
- `scanner/engine.py`: Parameter threading through `scan_symbol`, `_scan_batch`, and `scan_all`.
- `main.py`: Create CLI interface for mode scanning.
