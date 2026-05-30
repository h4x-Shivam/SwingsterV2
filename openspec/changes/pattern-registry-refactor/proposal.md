## Why

### The problem with current architecture

Every pattern (VCP, Flag & Pole, Cup & Handle, Breakout) currently shares the same thresholds, the same scoring weights, the same candidate pool size, and the same filtering pipeline — all defined in a single flat `config.py` and implemented across a handful of monolithic files.

This creates four compounding problems:
1. Adding a new pattern means touching 4–5 existing files and risking breakage of all other patterns in the process.
2. Debugging an issue with one pattern means scrolling past unrelated code with no isolation.
3. Changing one pattern's thresholds risks cascading into another pattern's behavior.
4. Scoring a Breakout the same way as a VCP is fundamentally wrong — Breakout needs volume expansion, whereas VCP needs volume contraction. Using one formula produces incorrect rankings.

### The solution — Pattern Registry

Each pattern becomes a fully self-contained module with its own:
- Detection algorithm
- Thresholds and constants
- Scoring weights
- Candidate pool settings
- Judge agent prompt
- UI metadata (color, icon, description)

A central registry will map mode keys to pattern instances. The engine, judge, and UI consume the registry without knowing or caring what patterns exist. Adding a new pattern in the future means creating one new folder and registering one new line, with zero changes to the engine, judge, or UI.

## What Changes

- **Add PatternConfig**: Introduce a strongly-typed `PatternConfig` dataclass in `scanner/models.py` with validation to ensure scoring weights sum to 1.0.
- **Base Pattern Class**: Create an abstract `BasePattern` class that standardizes detection, scoring, metadata, and judge prompts.
- **Isolate Pattern Modules**: Move existing detection logic verbatim into independent, self-contained modules (`vcp`, `flag_pole`, `cup_handle`, `breakout`), each with its own `config.py` and `detector.py`.
- **Swing Pivots Isolation**: Move `find_swing_pivots()` to its own module `scanner/patterns/pivots.py` to be shared among detectors.
- **Central Pattern Registry**: Implement `scanner/patterns/registry.py` to instantiate and expose all available patterns.
- **Update Engine**: Refactor `scanner/engine.py` to consume the registry and apply per-pattern pool sizes instead of a hard global cap.
- **Fix Risk/Reward Bugs**: Update `scanner/risk_reward.py` with a hard guard to prevent inverted stop losses and targets, and allow it to accept a pattern-specific `rr_hard_minimum`.
- **Global Config Cleanup**: Remove pattern-specific thresholds from the root `config.py`, keeping only global constants for "ALL" mode.
- **Dynamic Judge Prompt**: Update `judge/judge_agent.py` to read pattern-specific prompt criteria directly from the new pattern instances via the registry.
- **BREAKING**: Replaces the monolithic `scanner/patterns.py` with the new `scanner/patterns/` package.

## Capabilities

### New Capabilities
- `pattern-registry`: Core registry system (`scanner/patterns/registry.py`) and interface (`BasePattern`, `PatternConfig`) for defining dynamic pattern instances.

### Modified Capabilities
- `chart-patterns`: Refactored to use the self-contained module approach instead of a monolithic implementation.
- `scan-engine`: Updated to consume the new pattern registry and apply score-based dynamic pool sizes based on individual pattern configurations.
- `risk-reward-scoring`: Modified to use pattern-specific `rr_hard_minimum`, fix inverted stop/target logic, and loosen RR breakpoints for Indian market swing trades.

## Impact

- `scanner/patterns.py` will be entirely deleted.
- **New Directory Structure**: A new `scanner/patterns/` directory will contain the registry, base classes, utility files (`pivots.py`), and a sub-folder for every individual pattern.
- **Configuration Management**: Pattern thresholds will migrate from the root `config.py` to pattern-specific `config.py` files.
- `scanner/engine.py` will dynamically load active patterns and configurations from the registry.
- `scanner/risk_reward.py` and `scanner/scoring.py` will delegate logic to pattern-specific configuration values and methods.
- `judge/judge_agent.py` pulls its pattern criteria prompt dynamically from the registry.
- **No changes** to `fetcher/`, `trend.py`, `volume.py`, `rs_rank.py`, or data files.
