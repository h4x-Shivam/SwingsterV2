## Why

The current SwingsterV2 UI is a basic, dark-mode Streamlit dashboard that lacks professional typography, information density, and the precise, minimal design required for high-frequency stock scanning. To provide a professional, Bloomberg-meets-Linear terminal experience, we need a custom light-mode, single-page UI tailored for rapid NSE/BSE technical pattern screening.

## What Changes

- Replace or build a new high-fidelity single-page light-mode dashboard for technical pattern screening.
- Implement a three-row scan configuration panel: pattern mode selector, stock universe selector, and scan action row.
- Create a highly dense results layout featuring summary stats, micro-charts (pattern, sector, score distributions), and detailed result cards with visual score bars (Signal, Volume, R/R).
- Add judge verdict integration showing STRONG BUY, WATCHLIST, and REJECT statuses, complete with LLM reasoning and custom entry/stop/target parameters.
- Support seamless transitions, collapsed config headers, score bar viewport viewport animations, and auto-dismissing toasts.
- Add minimal sector lookup table for NSE Nifty 50 constituents.

## Capabilities

### New Capabilities
- `pattern-screening-ui`: A professional, light-mode single-page interface for scanning and viewing BSE/NSE technical pattern matches.

### Modified Capabilities
<!-- None -->

## Impact

- `app.py`: Will be updated or completely redesigned to serve the new custom UI or render it.
- `scanner/engine.py` and `judge/judge_agent.py`: Serve as the backend scanner and evaluator, supplying scan data.
