# SwingsterV2 — Pattern Mode Selector
# Final reviewed and corrected task spec

---

## 1. Configuration and Models

- [x] 1.1 Add to `config.py`:
          ```python
          SCAN_MODES = ["VCP", "FLAG_POLE", "CUP_HANDLE", "BREAKOUT", "ALL"]
          SCAN_MODE  = "VCP"   # default mode — change per run
          ```

- [x] 1.2 Add `scan_mode: str = "ALL"` field to `ScanResult` dataclass
          in `scanner/models.py`

---

## 2. Pattern Gating Implementation

- [x] 2.1 Call `find_swing_pivots()` BEFORE any mode gate inside
          `detect_patterns()` — pivots are required by ALL detectors
          and must never be conditional:
          ```python
          def detect_patterns(candles, mode="ALL"):
              pivots = find_swing_pivots(candles)   # always runs
              signals = []
              # mode gates below...
          ```

- [x] 2.2 Update `detect_patterns()` signature in `scanner/patterns.py`
          to accept `mode: str = "ALL"` as second parameter

- [x] 2.3 Gate each detector call based on active mode:
          ```python
          if mode in ("VCP", "ALL"):
              sig = _detect_vcp(candles, pivots)
              if sig: signals.append(sig)

          if mode in ("FLAG_POLE", "ALL"):
              sig = _detect_pole_flag(candles, pivots)
              if sig: signals.append(sig)

          if mode in ("CUP_HANDLE", "ALL"):
              sig = _detect_cup_handle(candles, pivots)
              if sig: signals.append(sig)

          if mode in ("BREAKOUT", "ALL"):
              sig = _detect_breakout(candles, pivots)
              if sig: signals.append(sig)
          ```

- [x] 2.4 Return highest strength signal from collected signals,
          or None if signals list is empty:
          ```python
          return max(signals, key=lambda s: s.strength) if signals else None
          ```

---

## 3. Scan Engine — Mode Threading

- [x] 3.1 Update `scan_symbol()` signature in `scanner/engine.py`:
          ```python
          # BEFORE
          def scan_symbol(symbol, conn, nifty_candles) -> ScanResult | None:
          # AFTER
          def scan_symbol(symbol, conn, nifty_candles, mode: str = "ALL") -> ScanResult | None:
          ```
          Pass `mode` to `detect_patterns()` and set `scan_mode = mode`
          on the returned `ScanResult`

- [x] 3.2 Update `_scan_batch()` worker function to accept a single
          tuple argument (required for ProcessPoolExecutor on Windows):
          ```python
          # BEFORE
          def _scan_batch(batch: list[str]) -> tuple[list[ScanResult], int]:
          # AFTER
          def _scan_batch(args: tuple) -> tuple[list[ScanResult], int]:
              batch, mode = args
          ```
          Pass `mode` down to `scan_symbol()` inside the worker loop

- [x] 3.3 Update `scan_all()` signature:
          ```python
          # BEFORE
          def scan_all() -> list[ScanResult]:
          # AFTER
          def scan_all(mode: str = SCAN_MODE) -> list[ScanResult]:
          ```

- [x] 3.4 Add mode validation at the top of `scan_all()`:
          ```python
          if mode not in SCAN_MODES:
              raise ValueError(
                  f"Invalid mode '{mode}'. Must be one of: {SCAN_MODES}"
              )
          ```

- [x] 3.5 Pack mode into worker args tuple before submitting:
          ```python
          worker_args = [(batch, mode) for batch in batches]
          futures = [executor.submit(_scan_batch, args) for args in worker_args]
          ```

- [x] 3.6 Update progress log inside `scan_all()` to include active mode:
          ```python
          print(f"Progress: {total_scanned}/{len(eligible)} | "
                f"{len(all_results)} {mode} candidates found")
          ```
          Mode must be visible in every progress line —
          not just "candidates found"

- [x] 3.7 Add final summary log after all futures complete:
          ```python
          print(f"\nScan complete — mode: {mode} | "
                f"{len(eligible)} scanned | "
                f"{len(all_results)} matches → "
                f"top {TOP_N_CANDIDATES} sent to judge")
          ```

---

## 4. Main Entry Point

- [x] 4.1 Create `main.py` at project root with argparse CLI:
          ```python
          import argparse
          from config import SCAN_MODE, SCAN_MODES

          if __name__ == "__main__":
              parser = argparse.ArgumentParser(description="SwingsterV2 Scanner")
              parser.add_argument(
                  "--mode",
                  choices=SCAN_MODES,
                  default=SCAN_MODE,
                  help=f"Pattern to scan for. Options: {SCAN_MODES}"
              )
              args = parser.parse_args()
          ```

- [x] 4.2 Add startup banner before scan begins:
          ```python
          print(f"\n{'─' * 50}")
          print(f"  SwingsterV2 — Pattern Mode: {args.mode}")
          print(f"{'─' * 50}\n")
          ```

- [x] 4.3 Call `scan_all(mode=args.mode)` inside `if __name__ == "__main__"`
          guard — never at module level

- [x] 4.4 Add temporary output placeholder until judge_agent.py is built:
          Print top 10 candidates by composite_score to console as
          formatted JSON so results can be visually verified:
          ```python
          import json

          candidates = scan_all(mode=args.mode)

          print(f"\nTop 10 — {args.mode} setups:\n")
          top10 = sorted(candidates,
                         key=lambda x: x.composite_score,
                         reverse=True)[:10]
          for i, r in enumerate(top10, 1):
              print(f"  #{i:>2}  {r.symbol:<12} "
                    f"score={r.composite_score:.1f}  "
                    f"pattern={r.pattern:<12} "
                    f"buy=₹{r.buy_point:.2f}  "
                    f"rr={r.rr_ratio:.1f}x")

          # also save full candidates to data/results.json for judge agent
          with open("data/results.json", "w") as f:
              json.dump([vars(c) for c in candidates], f, indent=2)
          print(f"\nFull {len(candidates)} candidates saved → data/results.json")
          ```

          This placeholder will be replaced by the judge agent call
          in the next phase. Do not build judge logic here.

---

## 5. Files to Modify

| File | What changes |
|---|---|
| `config.py` | Add SCAN_MODES and SCAN_MODE constants |
| `scanner/models.py` | Add scan_mode field to ScanResult |
| `scanner/patterns.py` | Add mode param to detect_patterns() |
| `scanner/engine.py` | Add mode param to scan_symbol(), _scan_batch(), scan_all() |
| `main.py` | Create with argparse CLI, banner, placeholder output |

---

## 6. Files to NOT touch

| File | Reason |
|---|---|
| `fetcher/fetch_all.py` | Mode-agnostic — no change needed |
| `fetcher/db_writer.py` | Mode-agnostic — no change needed |
| `scanner/trend.py` | Stage 2 runs regardless of mode |
| `scanner/volume.py` | Volume runs regardless of mode |
| `scanner/risk_reward.py` | R/R runs regardless of mode |
| `scanner/scoring.py` | Composite score runs regardless of mode |
| `judge/judge_agent.py` | Not built yet — do not touch |

---

## 7. Verification

- [x] 7.1 Run `python main.py --mode VCP`
          PASS: all results have `pattern == "vcp"`
          FAIL: any result shows "pole_flag", "cup_handle", or "breakout"

- [x] 7.2 Run `python main.py --mode CUP_HANDLE`
          PASS: all results have `pattern == "cup_handle"`
          FAIL: any other pattern appears in results

- [x] 7.3 Run `python main.py --mode ALL`
          PASS: mixed patterns appear across results
          FAIL: only one pattern type appears (gating is broken)

- [x] 7.4 Run `python main.py --mode INVALID`
          PASS: `ValueError` raised with message listing valid modes
          FAIL: scan runs anyway or crashes with unhandled exception

- [x] 7.5 Measure and compare execution time:
          ```python
          # run both and record times
          python main.py --mode VCP    # time this
          python main.py --mode ALL    # time this
          ```
          PASS: VCP-only scan is faster than ALL scan
          FAIL: VCP-only is same speed or slower → mode gating
                is not working, detectors are still all running

- [x] 7.6 Verify `data/results.json` is created after every run
          and contains valid JSON with correct pattern field
          matching the mode that was run

- [x] 7.7 Verify progress logs show mode name on every line:
          PASS: `"Progress: 400/1847 | 6 VCP candidates found"`
          FAIL: `"Progress: 400/1847 | 6 candidates found"` (mode missing)

---

## 8. Rules for implementation

1. Never hardcode pattern name strings anywhere except
   `config.py SCAN_MODES` and the `if mode in (...)` blocks
   inside `detect_patterns()`. All other references use the
   mode variable.

2. `find_swing_pivots()` must always be called regardless of mode.
   It is never inside a mode gate. If an agent puts it inside
   an `if mode == "VCP"` block that is a bug — fix it immediately.

3. Do not change any pattern detection algorithm logic inside
   `_detect_vcp`, `_detect_pole_flag`, `_detect_cup_handle`,
   or `_detect_breakout`. This task is ONLY about which detectors
   get called. The math inside each detector stays unchanged.

4. The mode parameter must have a default value everywhere it
   appears. Default is always `SCAN_MODE` imported from `config.py`.
   No function should require mode to be explicitly passed.

5. Do not build judge agent logic in this task.
   The placeholder output in main.py (top 10 printed to console
   + saved to results.json) is sufficient for this phase.
   Judge agent is the next separate task.