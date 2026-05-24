## Context

SwingsterV2 is a multi-agent NSE swing trade screener. Phase 1 populated the ticker master list (`data/symbols.csv`, 2,364 tickers). Phase 2 built the async OHLCV fetcher that downloads 1 year of daily candle data into `data/ohlcv.db` via SQLite with WAL mode. Phase 3 is the core analysis brain: a pattern engine that reads OHLCV data per symbol, applies a multi-stage funnel (Stage 2 trend → liquidity → chart patterns → RS rank → risk-reward → composite scoring), and produces a ranked candidate list.

The scanner detects 4 chart patterns: **VCP** (Volatility Contraction Pattern), **Pole & Flag**, **Cup & Handle**, and **Breakout**. These are multi-week/month price structure patterns requiring analysis of swing pivots, volume contraction, and slope validation across 30–200+ candles.

Before pattern detection, every symbol passes through a **Minervini Stage 2 trend filter** (5 MA conditions) and a **liquidity filter** (avg volume ≥ 50k). After pattern detection, a **Relative Strength rank** against Nifty 50 is computed. The composite score uses 5 weighted factors instead of 3.

The config uses: `NUM_AGENTS=5`, `MIN_SIGNAL_SCORE=55`, `TOP_N_CANDIDATES=30`, `TOP_N_FINAL=10`, and updated scoring weights: signal 0.40, volume 0.25, RR 0.20, stage2 0.10, RS 0.05.

## Goals / Non-Goals

**Goals:**
- Filter stocks to Stage 2 uptrend (Minervini) before any pattern detection — eliminate 60–70% of false signals.
- Detect 4 chart patterns (VCP, Pole & Flag, Cup & Handle, Breakout) with corrected, quant-reviewed thresholds.
- Compute volume metrics with a minimum liquidity filter (avg volume < 50k → skip).
- Compute Relative Strength rank against Nifty 50 benchmark.
- Calculate buy points per pattern with distance-from-buy percentage.
- Produce a 5-factor composite score (0–100) per symbol.
- Scan all ~2,300 symbols in <15 seconds using 5 `ThreadPoolExecutor` workers.
- Use typed dataclasses for all intermediate data structures.

**Non-Goals:**
- Candlestick patterns (engulfing, hammer, doji) — not in scope.
- Bearish patterns — this screener finds buy candidates only.
- Intraday or multi-timeframe analysis — daily candles only.
- Machine learning or trainable models — pure rule-based detection.
- Backtesting or paper trading — scoring only, no order execution.

## Decisions

### 1. Stage 2 trend filter: FIRST gate before patterns

**Rationale:** A chart pattern on a downtrending stock is worthless. Mark Minervini's Stage 2 criteria (price > 150 MA, price > 200 MA, 150 MA > 200 MA, 200 MA trending up, within 25% of 52-week high) eliminate stocks not in a confirmed uptrend. This filter alone removes 60–70% of the universe, dramatically reducing false signals and computation time.

The engine skips symbols with `stage2_score < 60` (allows partial Stage 2 to catch early-stage breakouts). Symbols with `is_stage2 = False` (not all 5 conditions met) get their final composite score capped at 50 regardless of pattern quality.

**Alternatives considered:**
- Simple 200 MA filter only — too crude, doesn't confirm uptrend structure.
- ADX trend strength — requires additional indicator computation, and Stage 2 is more aligned with swing trading methodology.

### 2. Pattern selection: VCP, Pole & Flag, Cup & Handle, Breakout (corrected thresholds)

**Rationale:** These 4 patterns are the bread-and-butter of swing trading, popularized by Mark Minervini (VCP), William O'Neil (Cup & Handle), and classical TA (Pole & Flag, Breakout). Key threshold corrections from quant review:

**VCP (Volatility Contraction Pattern):**
- 2–4 successive contractions, each base range ≤ 85% of previous.
- **Volume contraction required**: avg volume in each base < 75% of previous (was missing entirely).
- **Final tight zone ≤ 8%** of current price (was 15% — too wide, produces false signals).
- Buy point: highest high of last contraction + ₹0.10 buffer.

**Pole & Flag:**
- Pole: ≥ **8%** gain in ≤ **15** candles (was 15% in 10 — too aggressive for NSE).
- Flag retracement: ≤ **35%** (was 50% — 50% is a correction, not a flag).
- **Flag slope validation added**: upward-sloping flag = invalid.
- **Volume dry-up required**: flag volume < 60% of pole volume.
- Buy point: highest high of flag + ₹0.10 buffer.

**Cup & Handle:**
- Cup depth: **12–33%** (added minimum 12% — was missing, prevents shallow fake cups).
- **Handle slope validation added**: upward-sloping handle = invalid.
- **Handle volume dry-up**: < 70% of cup volume.
- Handle depth: ≤ 12% pullback from right lip.
- Buy point: highest high of handle + ₹0.10 buffer.

**Breakout:**
- Resistance tolerance: **2.5%** (was 1.5% — too tight for NSE spreads).
- **Minimum test spacing: ≥ 10 trading days** apart (prevents double-top false triggers).
- **Breakout volume required**: ≥ 1.5× the 20-day average (was missing — low volume breakout = fake).
- Buy point: resistance level + ₹0.10 buffer.

### 3. Relative Strength Rank: 12-month return vs Nifty 50

**Rationale:** Stocks outperforming Nifty 50 have institutional backing. A perfect VCP on an underperforming stock is a trap. RS rank computes 12-month return for both the symbol and `^NSEI`, then scores by outperformance magnitude (outperform by 20%+ → 100, in line → 50, underperform by 20%+ → 0).

Requires `^NSEI` OHLCV data in the database — fetched alongside regular symbols.

**Alternatives considered:**
- IBD-style RS percentile ranking across all stocks — requires ranking all 2,300 stocks before scoring any, adds complexity.
- Shorter-term RS (3-month) — less reliable for identifying institutional flows.

### 4. Module decomposition: 9 files in `scanner/` package

**Rationale:** Each analysis concern gets its own module. Added `trend.py` for Stage 2 and `rs_rank.py` for RS ranking alongside the existing pattern/volume/RR/scoring/engine split.

Files: `__init__.py`, `models.py`, `patterns.py`, `trend.py`, `rs_rank.py`, `volume.py`, `risk_reward.py`, `scoring.py`, `engine.py`.

### 5. Scoring: 5-factor weighted composite

**Rationale:** Updated from 3-factor to 5-factor:
- `signal × 0.40 + volume × 0.25 + rr × 0.20 + stage2 × 0.10 + rs × 0.05`

Signal still gets the highest weight. Stage 2 gets 10% because it's primarily a gate (pass/fail), not a gradient. RS gets 5% because it's a tiebreaker between otherwise similar setups.

**Hard cap rule:** If `is_stage2 = False`, composite score is capped at 50 regardless of how strong the pattern/volume/RR scores are. This prevents non-trending stocks from appearing in top candidates.

### 6. Liquidity filter: avg volume < 50k → skip

**Rationale:** Illiquid stocks with < 50,000 shares average daily volume are untradeable for practical swing trading — slippage eats profits, and exiting positions is difficult. The volume analysis module flags these and the engine skips them entirely.

### 7. Buy point calculation per pattern

**Rationale:** Each pattern has a specific buy point (breakout trigger level + ₹0.10 buffer). The `PatternSignal` carries `buy_point` and `distance_from_buy_pct` so downstream consumers know exactly where to enter and how far the stock is from actionable.

### 8. Concurrency: ThreadPoolExecutor(5) for batch scanning

**Rationale:** SQLite with WAL mode supports concurrent readers. Stage 2 filtering eliminates 60–70% of symbols before expensive pattern detection runs, keeping total scan time under 15 seconds. Each thread reads from the same database without contention.

### 9. Data structures: Dataclasses with expanded fields

**Rationale:** Added `TrendStatus` and `RSRank` dataclasses. `PatternSignal` expanded with `buy_point`, `distance_from_buy_pct`, `contraction_count`. `ScanResult` carries all sub-scores for full transparency.

## Risks / Trade-offs

- **Stage 2 filter may exclude early-stage breakouts** → Mitigation: Using `stage2_score ≥ 60` threshold (not requiring all 5 conditions), catching stocks entering Stage 2. Hard cap at 50 for non-Stage-2 stocks still surfaces them, just ranked lower.
- **VCP volume contraction rule may be too strict** → Mitigation: Using 75% threshold (not 50%). If the rule filters too aggressively, it can be tuned in config without code changes.
- **Nifty 50 data required in DB** → Mitigation: `^NSEI` will be added to the fetch pipeline. If data is missing, RS score defaults to 50 (neutral).
- **Chart pattern detection is more CPU-intensive (~2-5ms per symbol)** → Mitigation: Stage 2 filter eliminates 60–70% of symbols before pattern detection. Net effect: ~700 symbols × 5ms ÷ 5 threads ≈ 0.7 seconds for pattern phase.
- **Tighter thresholds may reduce candidate count** → Mitigation: The goal is quality over quantity. MIN_SIGNAL_SCORE of 55 and TOP_N_CANDIDATES of 30 are generous enough. Thresholds are configurable.
- **Slope validation on flags/handles may miss valid patterns** → Mitigation: Allows flat slope (not just downward). Only rejects clearly upward-sloping consolidations which are continuation patterns, not reversal setups.
