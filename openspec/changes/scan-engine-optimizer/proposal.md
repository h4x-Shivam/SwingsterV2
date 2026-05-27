## Why

The current ThreadPoolExecutor-based scan orchestrator suffers from Python's Global Interpreter Lock (GIL) limitations, causing heavy CPU pattern calculations to run sequentially and taking ~20 seconds for 2,180 symbols. Upgrading to a multi-core ProcessPoolExecutor and implementing SQL-level filtering will reduce scan time to under 8 seconds.

## What Changes

- **Modified**: Replace ThreadPoolExecutor with ProcessPoolExecutor in the scan engine for true multi-core parallel processing of CPU-bound calculations.
- **Modified**: Implement SQLite pre-filtering to eliminate illiquid symbols or symbols with insufficient candles before loading candle data into memory.
- **Modified**: Ensure complete compatibility with Windows `spawn` start method requirements, including ensuring all worker arguments and results are fully picklable and protecting execution entry points.

## Capabilities

### New Capabilities
<!-- Capabilities being introduced. Replace <name> with kebab-case identifier (e.g., user-auth, data-export, api-rate-limiting). Each creates specs/<name>/spec.md -->

### Modified Capabilities
- `scan-engine`: Optimize batch orchestration from threads to processes, reduce file/db loads via SQL pre-filtering, and ensure Windows multiprocessing compatibility.

## Impact

- `scanner/engine.py`: Replaced `ThreadPoolExecutor` with `ProcessPoolExecutor`.
- `fetcher/db_writer.py`: Added SQL-level pre-filtering helper.
- `config.py`: Adjust NUM_AGENTS configuration as process workers.
- Any main CLI run script (e.g., `main.py` or similar): Wrapped under `__main__` guards for Windows spawn safety.
