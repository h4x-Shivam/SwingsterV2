## Context

The current `scan_all()` orchestrator in `scanner/engine.py` uses `ThreadPoolExecutor(5)` to scan every symbol in the database. Due to Python's Global Interpreter Lock (GIL), the CPU-heavy calculations (such as VCP pattern detection, Stage 2 scoring, volume spikes, and risk-reward ratio checks) are executed sequentially on a single core. This results in a total batch scan time of ~20 seconds for 2,180 symbols, exceeding the target of <15 seconds (and ideally <8 seconds).

Furthermore, the current system reads the full historical OHLCV data from the SQLite database for *every single symbol*, even if that symbol is ultimately rejected immediately due to having too few candles or failing the minimum volume threshold (avg volume < 50,000).

## Goals / Non-Goals

**Goals:**
- Transition the scanner orchestrator to a `ProcessPoolExecutor` to utilize all available CPU cores for true parallel execution.
- Implement an efficient SQLite-level pre-filter to drop illiquid symbols or symbols with fewer than 30 candles before attempting expensive processing.
- Maintain full compatibility with Windows `spawn` start method constraints (picklable arguments/results, main-guards).
- Reduce total scan execution time for 2,180 symbols to **under 8 seconds**.

**Non-Goals:**
- Altering the mathematical logic or algorithms of any pattern detector, relative strength ranker, or trend analysis module.
- Changing the schema of the SQLite `ohlcv` database table.

## Decisions

### Decision 1: Worker-level SQLite querying vs. Massive Parent Serialization
- **Option A (Massive Parent Serialization)**: The parent process queries all OHLCV rows, converts them to `Candle` objects, caches them in a giant dictionary, and passes the chunks of `Candle` objects to the child processes.
- **Option B (Worker-level Querying - SELECTED)**: The parent process queries only the list of *eligible symbol names* (strings) and distributes these strings to the child processes. Each child process utilizes a local SQLite database connection to query the OHLCV rows for its assigned symbols directly.
- **Rationale**: In Windows, process spawning requires pickling and serializing all function arguments. Passing lists of hundreds of thousands of `Candle` objects over IPC creates massive serialization latency. In contrast, SQLite in WAL mode handles concurrent read queries with extremely high efficiency. Spreading the lightweight DB queries across workers avoids IPC bottlenecks and provides a dramatic performance boost.

### Decision 2: SQLite-level Pre-filtering
- **Option A (Query everything and filter in Python - CURRENT)**: Load all rows for all symbols, then filter in python memory.
- **Option B (Pre-filter in SQL - SELECTED)**: Implement a optimized SQLite query that filters out symbols with fewer than 30 candles or with an average volume below 50,000 over their entire available history.
  ```sql
  SELECT symbol FROM ohlcv GROUP BY symbol HAVING COUNT(*) >= 30 AND AVG(volume) >= 50000;
  ```
- **Rationale**: Over 60% of symbols in the database are either highly illiquid or have insufficient historical candle data. Pre-filtering them out at the database query level avoids loading and converting millions of unnecessary database rows, saving massive CPU cycles and disk I/O.

### Decision 3: Nifty Index Candle Cache Passing
- **Problem**: The relative strength (RS) rank requires ^NSEI (Nifty 50) index candles, which are loaded once. Since child processes do not share global memory, each child needs access to this index data.
- **Solution**: Load the Nifty 50 index candles once in the parent process and pass them as a small, lightweight list to the worker function. Since it is a single list of ~252 candles, the pickling overhead is negligible.

### Decision 4: Execution safety and Windows main-guard
- **Problem**: In Windows, spawning processes imports the parent module, which can trigger infinite recursion of process pools if not protected.
- **Solution**: Any script or entry point running the batch scan *must* protect the execution with an `if __name__ == '__main__':` block.

## Risks / Trade-offs

- **[Risk]**: Process startup overhead on Windows.
  - **Mitigation**: We will reuse a single `ProcessPoolExecutor` with workers configured based on CPU count or system cores (via `NUM_AGENTS` in config). We will chunk the work efficiently so that process creation cost is amortized.
- **[Risk]**: Database contention with concurrent reads.
  - **Mitigation**: Enable SQLite WAL (Write-Ahead Logging) mode, which allows multiple reader processes to execute queries concurrently without locking.
