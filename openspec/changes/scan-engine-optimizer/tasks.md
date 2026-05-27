# SwingsterV2 — Multiprocessing Migration & DB Pre-filtering
# Reviewed and corrected — all gaps fixed

---

## 1. Database Pre-Filtering

> Goal: eliminate dead, illiquid, stale, and penny stocks at the SQL layer
> before any Python process touches them. Faster and cleaner than filtering
> inside worker processes.

- [x] 1.1 Implement `get_eligible_symbols() -> list[str]` in `fetcher/db_writer.py`
          using a single optimized SQL query with ALL four filters below

- [x] 1.2 Filter 1 — Minimum candle count:
          `COUNT(date) >= 60` per symbol
          (ensures enough history for pattern detection)

- [x] 1.3 Filter 2 — Liquidity filter:
          `AVG(volume) >= 50000` over all available candles
          (eliminates illiquid stocks where patterns don't work)

- [x] 1.4 Filter 3 — Minimum price filter:
          `latest_close >= 20.0`
          (penny stocks under ₹20 produce false pattern signals)
          Compute as: `MAX(close)` on latest date per symbol

- [x] 1.5 Filter 4 — Data freshness check (critical — prevents stale patterns):
          `MAX(date) >= date('now', '-7 days')`
          (excludes symbols not traded in last 7 days — suspended, delisted,
          or simply missing from recent Yahoo Finance responses)

- [x] 1.6 Full SQL query structure:
          ```sql
          SELECT symbol
          FROM ohlcv
          GROUP BY symbol
          HAVING COUNT(date)     >= 60
             AND AVG(volume)     >= 50000
             AND (SELECT close FROM ohlcv o2 WHERE o2.symbol = ohlcv.symbol ORDER BY o2.date DESC LIMIT 1) >= 20.0
             AND MAX(date)       >= date('now', '-7 days')
          ORDER BY symbol
          ```

- [x] 1.7 Log pre-filter summary on startup:
          `"Pre-filter: {total} total → {eligible} eligible
          ({skipped} removed — {illiquid} illiquid,
          {stale} stale, {penny} penny, {short} insufficient history)"`

- [x] 1.8 Verify `get_eligible_symbols()` — run standalone, print count,
          spot-check 10 symbols manually in DB to confirm filters are correct

- [x] 1.9 Verify `^NSEI` (Nifty 50 benchmark) is present in `ohlcv.db`
          before scan starts — raise `RuntimeError` with clear message if missing:
          `"^NSEI not found in ohlcv.db. Add it to symbols.csv and re-run
          --mode full to fetch benchmark data."`

---

## 2. Multiprocessing Migration

> Replace ThreadPoolExecutor with ProcessPoolExecutor for true CPU parallelism.
> Each process gets its own Python interpreter, its own GIL, its own CPU core.
> ThreadPoolExecutor is blocked by the GIL on CPU-bound pattern math — useless.

- [x] 2.1 In `scanner/engine.py`, replace:
          ```python
          # REMOVE THIS
          from concurrent.futures import ThreadPoolExecutor
          ```
          with:
          ```python
          # USE THIS
          from concurrent.futures import ProcessPoolExecutor
          import multiprocessing
          ```

- [x] 2.2 Refactor per-symbol processing into a **top-level module function**
          (not a method, not a lambda, not a nested function):
          ```python
          # TOP LEVEL — must be importable by child processes on Windows
          def _scan_batch(batch: list[str]) -> list[ScanResult]:
              conn = get_connection()       # each process opens its OWN connection
              results = []
              for symbol in batch:
                  try:
                      result = scan_symbol(symbol, conn)
                      if result:
                          results.append(result)
                  except Exception as e:
                      # log to stderr — safe in multiprocessing
                      print(f"[WARN] {symbol}: {e}", file=sys.stderr)
              conn.close()
              return results
          ```
          Reason: Windows uses `spawn` (not `fork`) — child processes
          re-import the module from scratch. Nested functions are not
          picklable and will crash with `AttributeError` on Windows.

- [x] 2.3 Each worker reads `^NSEI` candles **independently from ohlcv.db**:
          ```python
          def _scan_batch(batch):
              conn = get_connection()
              nifty_candles = read_ohlcv("^NSEI", conn)  # each worker reads own copy
              ...
          ```
          Do NOT pass Nifty candles from parent to worker via arguments —
          pickle serialization adds overhead and breaks when data grows.
          SQLite WAL mode allows unlimited simultaneous readers — use it.

- [x] 2.4 Safe progress tracking across processes:
          Each worker returns a tuple: `(results: list[ScanResult], scanned: int)`
          Parent process collects and prints unified progress:
          ```python
          total_scanned = 0
          all_results = []
          for future in as_completed(futures):
              batch_results, batch_count = future.result()
              all_results.extend(batch_results)
              total_scanned += batch_count
              print(f"Progress: {total_scanned}/{total_eligible} scanned
                    | {len(all_results)} candidates found")
          ```

- [x] 2.5 Do NOT use `multiprocessing.Manager().Queue()` for logging —
          it adds IPC overhead. Use `print(..., file=sys.stderr)` inside
          workers for warnings. Parent handles all INFO-level logging.

- [x] 2.6 Batch splitting strategy:
          ```python
          # split eligible symbols into NUM_AGENTS batches
          # use round-robin slice — ensures even distribution even
          # if symbol count is not divisible by NUM_AGENTS
          batches = [eligible_symbols[i::NUM_AGENTS] for i in range(NUM_AGENTS)]
          ```

---

## 3. Main Execution & Safety Guards

- [x] 3.1 Add `if __name__ == '__main__':` guard to ALL entry points:
          - `main.py`
          - `scanner/engine.py` (if runnable directly)
          - any script that calls `scan_all()`

          Without this on Windows, each spawned child process re-runs
          the top-level code and spawns MORE children → infinite loop →
          system crash or hang.

- [x] 3.2 Worker count formula — add to `config.py`:
          ```python
          import os
          # Leave 1 core free for OS + main process
          # Never exceed NUM_AGENTS setting
          # Always use at least 1
          WORKER_COUNT = max(1, min(NUM_AGENTS, os.cpu_count() - 1))
          ```

- [x] 3.3 Add startup diagnostic log before scan begins:
          ```
          ── SwingsterV2 Scan Engine ──────────────────────
          CPU cores available : 8
          Workers to be used  : 5
          Eligible symbols    : 1,847
          Batch size per worker: ~369
          Estimated scan time : ~8s
          ─────────────────────────────────────────────────
          ```

- [x] 3.4 Add graceful shutdown on `KeyboardInterrupt`:
          ```python
          try:
              results = scan_all()
          except KeyboardInterrupt:
              print("\nScan interrupted by user.")
              executor.shutdown(wait=False, cancel_futures=True)
          ```

---

## 4. Verification & Benchmarking

- [x] 4.1 Performance benchmark — target: full scan < 10 seconds:
          ```python
          import time
          start = time.perf_counter()
          results = scan_all()
          elapsed = time.perf_counter() - start
          print(f"Scan complete: {len(results)} candidates
                in {elapsed:.2f}s ({2337/elapsed:.0f} symbols/sec)")
          ```

- [x] 4.2 Functional correctness — run scan twice back to back,
          assert top 10 results are identical both runs.
          Any difference = race condition or shared state bug.

- [x] 4.3 RS rank correctness — manually verify:
          Pick 3 known NSE outperformers (e.g. stocks up 40%+ in last year).
          Confirm their `rs_score > 60` and `outperforming = True`.
          Pick 2 known underperformers. Confirm `rs_score < 40`.

- [x] 4.4 Stage 2 filter correctness:
          Confirm all results have `stage2_score >= 60`.
          Print count of symbols eliminated by stage2 filter in summary log.

- [x] 4.5 Pre-filter correctness:
          Confirm no result has `avg_volume < 50000`.
          Confirm no result has `current_price < ₹20`.
          Confirm no result has `latest_date` older than 7 days.

- [x] 4.6 Windows spawn safety — test WITHOUT `if __name__ == '__main__':`
          guard deliberately once. Should produce `RuntimeError` or clear
          multiprocessing error, NOT an infinite process spawn loop.
          Restore guard immediately after.

- [x] 4.7 Memory check:
          Monitor RAM during scan via Task Manager.
          5 processes × reading ~580k rows = expect 300–500MB peak.
          If above 1GB → batch size is too large, reduce per-worker load.

- [x] 4.8 Edge case — fewer symbols than workers:
          If `len(eligible_symbols) < NUM_AGENTS`, reduce worker count
          to `len(eligible_symbols)` to avoid spawning empty processes.
          ```python
          actual_workers = min(WORKER_COUNT, len(eligible_symbols))
          ```

---

## Summary of all fixes vs previous version

| Issue in previous task.md | Fix applied |
|---|---|
| Missing ₹20 price filter in SQL | Added as Filter 3 in Section 1 |
| Missing data freshness check | Added as Filter 4 — 7-day staleness cutoff |
| No filter summary log | Added in 1.7 |
| No ^NSEI existence check | Added in 1.9 with clear RuntimeError |
| Passing Nifty candles via pickle | Each worker reads DB independently (2.3) |
| Nested function not picklable on Windows | Top-level `_scan_batch()` required (2.2) |
| Manager().Queue() overhead | Removed — stderr print in workers instead (2.5) |
| Dynamic worker count unspecified | Explicit formula in config.py (3.2) |
| No startup diagnostic | Added in 3.3 |
| No graceful KeyboardInterrupt | Added in 3.4 |
| Vague verification tasks | Explicit checks with code samples (4.1–4.8) |
| No empty-batch edge case | Handled in 4.8 |
