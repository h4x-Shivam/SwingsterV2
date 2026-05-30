## Context

Currently, `SwingsterV2` relies on a monolithic `scanner/patterns.py` to evaluate four distinct chart patterns (VCP, Flag & Pole, Cup & Handle, Breakout). These patterns share hardcoded thresholds in the root `config.py` and a single generic scoring formula in `scanner/scoring.py`. This structure causes significant friction when attempting to add new patterns, tune existing pattern constraints independently, or manage risk/reward metrics specific to the behavior of a particular pattern (e.g., volume contraction in VCP vs. volume expansion in Breakout).

## Goals / Non-Goals

**Goals:**
- Completely isolate each pattern into its own self-contained module (`scanner/patterns/<name>/`).
- Provide dedicated config objects for each pattern to manage their thresholds, UI metadata, and scoring weights independently.
- Abstract the invocation of patterns through a centralized Pattern Registry.
- Allow for dynamic, pattern-specific candidate pool limits and scoring filtering.
- Allow `judge_agent.py` to dynamically pull pattern prompts from the registry instead of hardcoding them.
- Fix negative risk/reward inverted stop loss calculation bug and loosen risk/reward requirements.

**Non-Goals:**
- We are *not* rewriting the mathematical logic of the pattern detection functions; the exact algorithms will be moved verbatim into the new architecture. Thresholds will be abstracted to config.
- We will *not* change `fetcher/`, `trend.py`, `volume.py`, `rs_rank.py`, or any of the underlying data files.

## Decisions

- **PatternConfig DataClass**: We will introduce a strongly-typed `PatternConfig` in `scanner/models.py`. 
  - *Rationale*: It enforces structure across patterns, holding identity, UI metadata, filtering thresholds, and scoring weights. The `__post_init__` validation ensures scoring weights always sum to exactly 1.0 to prevent silent mathematical failures.

- **BasePattern Abstract Class**: We will define an abstract `BasePattern` class in `scanner/patterns/base.py`.
  - *Rationale*: Standardizes the interface (`detect()`, `score()`, `is_eligible()`, `get_meta()`, and the `judge_prompt` property) so that consumers (like the scanning engine and judge agent) can blindly interact with any pattern.

- **Pivots Utility Extraction**: `find_swing_pivots()` will be extracted from the monolithic file into `scanner/patterns/pivots.py`.
  - *Rationale*: It is a shared utility required by multiple independent detectors and should not be duplicated.

- **Module Isolation for Detectors**: Each pattern (VCP, Flag Pole, Cup Handle, Breakout) gets its own package with a `config.py` (instantiating `PatternConfig`) and a `detector.py` (implementing `BasePattern`).
  - *Rationale*: Guarantees zero cross-pattern side effects. Adding a new pattern in the future requires creating a single isolated directory without touching existing code.

- **Pattern Registry Concept**: We will create `scanner/patterns/registry.py` defining a `PATTERN_REGISTRY` mapping.
  - *Rationale*: Provides a single source of truth. The engine, judge, and UI will use functions like `get_patterns(mode)` and `get_all_metadata()` without knowing what patterns exist.

- **Dynamic Scoring and Candidate Pools**: Instead of hard global limits on the number of candidates (`TOP_N_CANDIDATES`) or generic minimum composite scores, the scanning engine will defer to each pattern's `config.min_candidate_score` and `config.max_candidates`. Global settings are only used in "ALL" mode.
  - *Rationale*: Breakouts are time-critical and rarer, whereas VCPs are more common. Their candidate pools and filtering thresholds should scale independently.

- **Risk/Reward Hard Limits**: `scanner/risk_reward.py` will receive hard guards to prevent an inverted stop loss (e.g., reverting to a 20-candle low) or an inverted target (reverting to entry * 1.15). The function will accept `rr_hard_minimum` parametrically from the pattern configuration.
  - *Rationale*: Solves a known bug where swing low detection picks resistance above price as "support" for some stocks.

- **Judge Prompt Isolation**: The judge will read mode-specific prompts from the pattern instance's `judge_prompt` property rather than maintaining a hardcoded dictionary.
  - *Rationale*: Criteria for evaluating a pattern belongs alongside the logic for detecting the pattern.

## Risks / Trade-offs

- **Risk**: A circular dependency may occur if `config.py` imports `PATTERN_REGISTRY` to determine `SCAN_MODES` while `PATTERN_REGISTRY` depends on elements requiring config constants.
  **Mitigation**: We will keep `SCAN_MODES` manually listed in `config.py` but introduce a `_validate_registry()` runtime check at the top of `main.py` before execution to ensure exact synchronization between `config.py` and `scanner/patterns/registry.py`.

- **Trade-off**: Slightly more boilerplate code per pattern due to isolated packages.
  **Mitigation**: The boilerplate isolates each pattern, massively reducing long-term coupling and debug complexity.

## Migration Plan

1. **Foundations**: Add `PatternConfig` to `models.py`, create `scanner/patterns/base.py`, and move `find_swing_pivots()` to `pivots.py`.
2. **Implementations**: Build the isolated directory, `config.py`, and `detector.py` for each of the four patterns without changing the underlying mathematical logic. Use `config.extras` for all threshold constants.
3. **Registry Wiring**: Create `registry.py` to map the new implementations.
4. **Integration Refactors**: Update `engine.py`, `risk_reward.py`, `scoring.py`, `config.py`, and `judge_agent.py` to route through the new registry and utilize dynamic configurations.
5. **Validation**: Execute specific V1-V8 validation queries (e.g., verifying `__post_init__` validation works, confirming inverted stop bugs are fixed, ensuring `ALL` mode scans accurately) to confirm 100% feature parity.
6. **Cleanup**: Add `_validate_registry()` to `main.py`, delete the obsolete `scanner/patterns.py`, and commit the atomic changes.
