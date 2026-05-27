## Context

The SwingsterV2 scan engine will support selectable pattern mode scanning (`SCAN_MODE`). Gating specific detectors (VCP, FLAG_POLE, CUP_HANDLE, BREAKOUT, or ALL) allows targeted scanning and significantly reduces execution latency. This document outlines the technical design for routing the mode parameter from CLI/configuration to worker processes and the single-symbol pipeline, ensuring full determinism and Windows multiprocessing spawn safety.

## Goals / Non-Goals

**Goals:**
- Implement selectable pattern modes via `SCAN_MODE` and `SCAN_MODES` in `config.py`.
- Thread `mode` parameters safely through all scanning layers: `scan_all()`, `_scan_batch()`, `scan_symbol()`, and `detect_patterns()`.
- Ensure `find_swing_pivots()` is ALWAYS executed unconditionally at the top of `detect_patterns()`, before any mode gates, as pivots are required by all active detectors.
- Maintain full Windows spawn safety for `ProcessPoolExecutor` by packing arguments as `(batch, mode)` tuples for task submission and unpacking inside `_scan_batch()`.
- Add `scan_mode` to `ScanResult` to track which pattern setup produced each result.
- Create `main.py` CLI accepting a `--mode` flag with descriptive startup banners.
- Serialize final scan candidates to `data/results.json` in JSON format as a placeholder for the downstream judging agent.

**Non-Goals:**
- Modifying the core mathematical algorithms inside any individual pattern detector.
- Modifying trend/Stage 2 filters, volume analysis, risk-reward ratios, or composite scoring weights.
- Building the actual LLM judging agent logic inside this change.

## Decisions

### Decision 1: Gating inside detect_patterns()
- **Approach**: Keep `find_swing_pivots()` unconditional at the top of the function. Introduce `if mode in ("<PATTERN>", "ALL")` gates for calling `_detect_vcp()`, `_detect_pole_flag()`, `_detect_cup_handle()`, and `_detect_breakout()`.
  ```python
  def detect_patterns(candles, mode="ALL"):
      pivots = find_swing_pivots(candles)  # unconditional
      signals = []
      
      if mode in ("VCP", "ALL"):
          # run VCP...
      # other gates...
      
      return max(signals, key=lambda s: s.strength) if signals else None
  ```
- **Rationale**: All pattern detectors rely on swing pivots. Computing them unconditionally avoids code duplication and ensures exact pivot coordinates are supplied to active detectors.

### Decision 2: Packed Tuple Arguments for Processes
- **Approach**: Submit `worker_args = [(batch, mode) for batch in batches]` to the `ProcessPoolExecutor`. Inside the worker, unpack immediately: `batch, mode = args`.
- **Rationale**: Process task submission on Windows requires a single picklable argument. Packing arguments into a single tuple conforms to this signature safely.

### Decision 3: Intermediate JSON Serialization
- **Approach**: Save all generated candidates to `data/results.json` after sorting by composite score, using `json.dump([vars(c) for c in candidates], f, indent=2)`.
- **Rationale**: This acts as a robust decoupled handoff file for the upcoming LLM judging agent, allowing Phase 4 to read the candidates smoothly.

## Risks / Trade-offs

- **[Risk]**: Mismatch in logging formatting.
  - **Mitigation**: Progress logging inside `scan_all()` will explicitly print the active mode on every line: `Progress: {total_scanned}/{len(eligible)} | {len(all_results)} {mode} candidates found` to maintain high visibility.
