# SwingsterV2 — Pattern Registry Architecture Refactor
# Production-grade, scalable, future-proof
# Based on repo: https://github.com/h4x-Shivam/SwingsterV2

---

## What this task does and why

### The problem with current architecture

Every pattern (VCP, Flag & Pole, Cup & Handle, Breakout) currently
shares the same thresholds, the same scoring weights, the same
candidate pool size, and the same filtering pipeline — all defined
in a single flat config.py and implemented across a handful of
monolithic files.

This creates four- [x] **Step 30 — Run verification V7: Adding a new pattern requires zero changes to existing files** and risking
   breakage of all other patterns in the process

2. Debugging a VCP issue = scrolling past Flag, Cup, Breakout code
   with no isolation

3. Changing one pattern's thresholds = hoping it doesn't cascade
   into another pattern's behavior

4. Scoring a Breakout the same way as a VCP is wrong — Breakout
   needs high volume (expansion), VCP needs low volume (contraction).
   One formula for everything produces incorrect rankings.

### The solution — Pattern Registry

Each pattern becomes a fully self-contained module with its own:
- Detection algorithm
- Thresholds and constants
- Scoring weights
- Candidate pool settings
- Judge agent prompt
- UI metadata (color, icon, description)

A central registry maps mode keys to pattern instances.
The engine, judge, and UI consume the registry — they never
know or care what patterns exist. Adding a new pattern in
future means creating one new folder and registering one
new line. Zero changes to engine, judge, or UI.

---

## Current file structure (what exists now)

```
SwingsterV2/
├── config.py                    ← global constants only, NO pattern thresholds
├── main.py                      ← unchanged externally, minor internal update
├── scanner/
│   ├── __init__.py              ← unchanged
│   ├── models.py                ← add PatternConfig dataclass, keep all else
│   ├── engine.py                ← consumes registry, score-based pool
│   ├── trend.py                 ← unchanged
│   ├── volume.py                ← unchanged
│   ├── risk_reward.py     - [x] **Step 27 — Run verification V4: Inverted stop loss fixed**bug, loosen RR
│   ├── scoring.py               ← delegates to pattern-specific weights
│   └── patterns/                ← NEW — replaces monolithic patterns.py
│       ├── __init__.py          ← NEW — empty package init
│       ├── base.py              ← NEW — BasePattern ABC + PatternConfig
│       ├── registry.py          ← NEW — PATTERN_REGISTRY dict
│       ├── pivots.py            ← NEW — find_swing_pivots() moved here
│       ├── vcp/
│       │   ├── __init__.py      ← NEW — empty
│       │   ├── config.py        ← NEW — VCP-only thresholds + weights + meta
│       │   └── detector.py      ← NEW — VCPPattern(BasePattern)
│       ├── flag_pole/
│       │   ├── __init__.py      ← NEW — empty
│       │   ├── config.py        ← NEW — Flag-only thresholds + weights + meta
│       │   └── detector.py      ← NEW — FlagPolePattern(BasePattern)
│       ├── cup_handle/
│       │   ├── __init__.py      ← NEW — empty
│       │   ├── config.py        ← NEW — Cup-only thresholds + weights + meta
│       │   └── detector.py      ← NEW — CupHandlePattern(BasePattern)
│       └── breakout/
│           ├── __init__.py      ← NEW — empty
│           ├── config.py        ← NEW — Breakout-only thresholds + weights + meta
│           └── detector.py      ← NEW — BreakoutPattern(BasePattern)
├── judge/
│   ├── __init__.py              ← unchanged
│   └── judge_agent.py           ← read judge_prompt from registry
├── fetcher/                     ← entirely unchanged
└── data/                        ← entirely unchanged
```

---

## Build Tasks

- [x] **Step 31 — Run verification V8: Full end-to-end scan**ner/models.py`**
  Add the `PatternConfig` dataclass (with `__post_init__` weight validation) to `scanner/models.py`. Do NOT remove any existing dataclasses. Only add.

  ```python
  from dataclasses import dataclass, field
  from typing import Dict, Any

  @dataclass
  class PatternConfig:
      # Identity
      name:         str
      full_name:    str
      version:      str

      # UI metadata
      color:        str
      icon:         str
      description:  str
      timeframe:    str

      # Candle requirements
      min_candles:  int

      # Filtering thresholds
      min_signal_score:          int
      min_candidate_score:       float
      max_candidates:            int
      rr_hard_minimum:           float

      # Volume direction
      vol_contraction_required:  bool

      # Scoring weights — must sum to 1.0
      weight_signal:  float
      weight_volume:  float
      weight_rr:      float
      weight_stage2:  float
      weight_rs:      float

      # Pattern-specific extras
      extras: Dict[str, Any] = field(default_factory=dict)

      def __post_init__(self):
          total = (self.weight_signal + self.weight_volume +
                   self.weight_rr + self.weight_stage2 + self.weight_rs)
          if abs(total - 1.0) > 0.001:
              raise ValueError(
                  f"{self.name}: scoring weights must sum to 1.0, got {total:.3f}"
              )
  ```

- [x] **Step 2 — Create `scanner/patterns/pivots.py`**
  Move `find_swing_pivots()` from the old `scanner/patterns.py` into this dedicated module verbatim. Do not change the algorithm — only move it.

  ```python
  # scanner/patterns/pivots.py

  def find_swing_pivots(candles: list, n: int = 3) -> tuple:
      """
      Identify swing highs and swing lows from candle list.
      n = number of neighbors on each side that must be lower/higher.
      Returns (swing_highs, swing_lows) — both are lists of (index, price).
      Only considers last 252 candles (1 year max lookback).
      """
      # copy existing implementation from patterns.py verbatim
      ...
  ```

- [x] **Step 3 — Create `scanner/patterns/base.py`**
  Create the `BasePattern` ABC with abstract methods `detect()`, `score()`, and `judge_prompt`, plus concrete helpers `is_eligible()` and `get_meta()`.

  ```python
  # scanner/patterns/base.py
  from abc import ABC, abstractmethod
  from scanner.models import PatternConfig, PatternSignal, Candle

  class BasePattern(ABC):
      config: PatternConfig

      @abstractmethod
      def detect(self, candles: list, pivots: tuple) -> "PatternSignal | None": ...

      @abstractmethod
      def score(
          self,
          signal_strength: float,
          volume_score:    float,
          rr_score:        float,
          stage2_score:    float,
          rs_score:        float,
      ) -> float: ...

      def is_eligible(self, candles: list) -> bool:
          return len(candles) >= self.config.min_candles

      def get_meta(self) -> dict:
          return {
              "name":        self.config.name,
              "full_name":   self.config.full_name,
              "color":       self.config.color,
              "icon":        self.config.icon,
              "description": self.config.description,
              "timeframe":   self.config.timeframe,
              "version":     self.config.version,
          }

      @property
      @abstractmethod
      def judge_prompt(self) -> str: ...
  ```

- [x] **Step 4 — Create `scanner/patterns/__init__.py`** (empty package init)

- [x] **Step 5 — Create `scanner/patterns/vcp/__init__.py`** (empty)

- [x] **Step 29 — Run verification V6: Registry/config sync check**

  ```python
  from scanner.models import PatternConfig

  VCP_CONFIG = PatternConfig(
      name         = "VCP",
      full_name    = "Volatility Contraction Pattern",
      version      = "1.0.0",
      color        = "#00f5c4",
      icon         = "📉",
      description  = "Minervini-style successive contractions with volume dry-up",
      timeframe    = "Swing trade — 3 to 8 weeks",
      min_candles  = 60,
      min_signal_score     = 60,
      min_candidate_score  = 62.0,
      max_candidates       = 50,
      rr_hard_minimum      = 0.8,
      vol_contraction_required = True,
      weight_signal  = 0.45,
      weight_volume  = 0.30,
      weight_rr      = 0.10,
      weight_stage2  = 0.10,
      weight_rs      = 0.05,
      extras = {
          "min_contractions":      2,
          "max_contractions":      4,
          "contraction_factor":    0.85,
          "tight_zone_pct":        0.08,
          "vol_dry_up_factor":     0.75,
          "near_pivot_max_pct":    0.05,
      }
  )
  ```

- [x] **Step 7 — Create `scanner/patterns/vcp/detector.py`**
  Move VCP detection algorithm verbatim from `scanner/patterns.py` into `VCPPattern(BasePattern)`. All threshold values must be read from `self.config.extras["key"]` — no hardcoded numbers inside `detect()`.

- [x] **Step 8 — Create `scanner/patterns/flag_pole/__init__.py`** (empty)

- [x] **Step 9 — Create `scanner/patterns/flag_pole/config.py`**

  ```python
  from scanner.models import PatternConfig

  FLAG_POLE_CONFIG = PatternConfig(
      name         = "FLAG_POLE",
      full_name    = "Flag & Pole",
      version      = "1.0.0",
      color        = "#f59e0b",
      icon         = "🚩",
      description  = "Impulsive pole followed by tight orderly consolidation",
      timeframe    = "Short swing — 1 to 4 weeks",
      min_candles  = 30,
      min_signal_score     = 55,
      min_candidate_score  = 57.0,
      max_candidates       = 50,
      rr_hard_minimum      = 0.8,
      vol_contraction_required = True,
      weight_signal  = 0.40,
      weight_volume  = 0.35,
      weight_rr      = 0.10,
      weight_stage2  = 0.10,
      weight_rs      = 0.05,
      extras = {
          "min_pole_gain_pct":       0.08,
          "max_pole_candles":        15,
          "max_flag_retracement":    0.35,
          "max_flag_candles":        20,
          "min_flag_candles":        5,
          "max_flag_slope_per_day":  0.001,
          "vol_flag_factor":         0.60,
      }
  )
  ```

- [x] **Step 10 — Create `scanner/patterns/flag_pole/detector.py`**
  Move Flag & Pole detection algorithm verbatim from `scanner/patterns.py` into `FlagPolePattern(BasePattern)`. All threshold values must be read from `self.config.extras["key"]`.

- [x] **Step 11 — Create `scanner/patterns/cup_handle/__init__.py`** (empty)

- [x] **Step 12 — Create `scanner/patterns/cup_handle/config.py`**

  ```python
  from scanner.models import PatternConfig

  CUP_HANDLE_CONFIG = PatternConfig(
      name         = "CUP_HANDLE",
      full_name    = "Cup & Handle",
      version      = "1.0.0",
      color        = "#a78bfa",
      icon         = "☕",
      description  = "U-shaped base with shallow handle consolidation",
      timeframe    = "Swing to position — 4 to 16 weeks",
      min_candles  = 100,
      min_signal_score     = 60,
      min_candidate_score  = 62.0,
      max_candidates       = 50,
      rr_hard_minimum      = 0.8,
      vol_contraction_required = True,
      weight_signal  = 0.40,
      weight_volume  = 0.25,
      weight_rr      = 0.20,
      weight_stage2  = 0.10,
      weight_rs      = 0.05,
      extras = {
          "min_cup_depth_pct":      0.12,
          "max_cup_depth_pct":      0.33,
          "min_cup_candles":        30,
          "max_cup_candles":        150,
          "lip_tolerance_pct":      0.05,
          "min_handle_candles":     5,
          "max_handle_candles":     25,
          "max_handle_drop_pct":    0.12,
          "handle_above_midpoint":  True,
      }
  )
  ```

- [x] **Step 13 — Create `scanner/patterns/cup_handle/detector.py`**
  Move Cup & Handle detection algorithm verbatim from `scanner/patterns.py` into `CupHandlePattern(BasePattern)`. All threshold values must be read from `self.config.extras["key"]`.

- [x] **Step 14 — Create `scanner/patterns/breakout/__init__.py`** (empty)

- [x] **Step 15 — Create `scanner/patterns/breakout/config.py`**

  ```python
  from scanner.models import PatternConfig

  BREAKOUT_CONFIG = PatternConfig(
      name         = "BREAKOUT",
      full_name    = "Horizontal Breakout",
      version      = "1.0.0",
      color        = "#f43f5e",
      icon         = "🚀",
      description  = "Price breaking through tested horizontal resistance",
      timeframe    = "Momentum — days to weeks",
      min_candles  = 30,
      min_signal_score     = 50,
      min_candidate_score  = 52.0,
      max_candidates       = 30,
      rr_hard_minimum      = 0.8,
      vol_contraction_required = False,
      weight_signal  = 0.30,
      weight_volume  = 0.40,
      weight_rr      = 0.15,
      weight_stage2  = 0.10,
      weight_rs      = 0.05,
      extras = {
          "resistance_tolerance_pct": 0.025,
          "min_resistance_tests":     2,
          "min_test_spacing_days":    10,
          "proximity_to_resistance":  0.03,
          "breakout_vol_multiplier":  1.5,
      }
  )
  ```

- [x] **Step 26 — Run verification V3: No hardcoded thresholds in detector files**
  Move Breakout detection algorithm verbatim from `scanner/patterns.py` into `BreakoutPattern(BasePattern)`. All threshold values must be read from `self.config.extras["key"]`.

- [x] **Step 28 — Run verification V5: Per-pattern scoring weights are different**

  ```python
  # scanner/patterns/registry.py
  from scanner.patterns.vcp.detector        import VCPPattern
  from scanner.patterns.flag_pole.detector  import FlagPolePattern
  from scanner.patterns.cup_handle.detector import CupHandlePattern
  from scanner.patterns.breakout.detector   import BreakoutPattern
  from scanner.patterns.base                import BasePattern

  PATTERN_REGISTRY: dict[str, BasePattern] = {
      "VCP":        VCPPattern(),
      "FLAG_POLE":  FlagPolePattern(),
      "CUP_HANDLE": CupHandlePattern(),
      "BREAKOUT":   BreakoutPattern(),
  }

  def get_patterns(mode: str) -> list[BasePattern]:
      if mode == "ALL":
          return list(PATTERN_REGISTRY.values())
      if mode not in PATTERN_REGISTRY:
          valid = list(PATTERN_REGISTRY.keys()) + ["ALL"]
          raise ValueError(f"Unknown mode '{mode}'. Valid: {valid}")
      return [PATTERN_REGISTRY[mode]]

  def get_all_metadata() -> list[dict]:
      return [p.get_meta() for p in PATTERN_REGISTRY.values()]

  def get_pattern_config(mode: str):
      if mode == "ALL":
          raise ValueError("get_pattern_config() not valid for ALL mode.")
      return get_patterns(mode)[0].config
  ```

- [x] **Step 20 — Update `scanner/scoring.py`**
  Make `scoring.py` a thin wrapper that delegates to `pattern.score()`. Remove the single shared formula. The per-pattern `score()` method on each `BasePattern` subclass now owns the calculation.

- [x] **Step 24 — Run verification V1: Registry loads cleanly**
  Remove all pattern-specific thresholds (`MIN_SIGNAL_SCORE`, `TOP_N_CANDIDATES`). Add two new global constants for ALL mode only. Keep `TOP_N_FINAL = 10`. Keep `SCAN_MODES` hardcoded (registry sync validated at startup by main.py).

  ```python
  # Candidate pool for ALL mode (individual modes use their own PatternConfig)
  MIN_CANDIDATE_SCORE = 55.0
  MAX_CANDIDATES      = 50

  SCAN_MODES = ["VCP", "FLAG_POLE", "CUP_HANDLE", "BREAKOUT", "ALL"]
  ```

- [x] **Step 22 — Update `judge/judge_agent.py`**
  Remove the hardcoded `mode_context` dict from `_build_system_prompt()`. Read the mode-specific prompt section from the registry instead.

  ```python
  from scanner.patterns.registry import get_patterns

  def _build_system_prompt(mode: str) -> str:
      base = """..."""  # base prompt unchanged

      if mode == "ALL":
          mode_section = """
          You are evaluating a MIXED set of patterns.
          Apply cross-pattern comparison criteria...
          """
      else:
          patterns = get_patterns(mode)
          mode_section = patterns[0].judge_prompt

      return base + mode_section
  ```

- [x] **Step 25 — Run verification V2: Weight validation works**egistry()` startup check to ensure `SCAN_MODES` in `config.py` and `PATTERN_REGISTRY` keys stay in sync. Call it before argparse in `__main__`.

  ```python
  from scanner.patterns.registry import PATTERN_REGISTRY

  def _validate_registry():
      config_modes  = set(SCAN_MODES) - {"ALL"}
      registry_keys = set(PATTERN_REGISTRY.keys())
      if config_modes != registry_keys:
          missing = config_modes - registry_keys
          extra   = registry_keys - config_modes
          raise RuntimeError(
              f"SCAN_MODES / registry mismatch.\n"
              f"In config but not registry: {missing}\n"
              f"In registry but not config: {extra}"
          )

  if __name__ == "__main__":
      _validate_registry()
      # ... rest unchanged ...
  ```

5. `find_swing_pivots()` lives in `scanner/patterns/pivots.py` only. All detectors import it from there. Never duplicate it.

6. The registry is the single source of truth for what patterns exist. Nothing else in the codebase should maintain its own list of pattern names.

7.- [x] **Step 32 — Delete `scanner/patterns.py`** (only after V1–V8 all pass). Keep it as fallback until migration is fully verified.

8. Commit only after V8 passes — one clean atomic commit for the entire refactor.