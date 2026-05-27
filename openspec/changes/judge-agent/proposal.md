## Why

The current SwingsterV2 scanner performs high-performance quantitative scanning across more than 2,000 tickers to produce a top 30 ranked candidate list based on a five-factor mathematical formula. However, it lacks the qualitative judgment of a professional trader (e.g., assessing the tightness of the final VCP contraction, verifying the shape of a Cup and Handle, ensuring strict sector diversification to mitigate systemic risk, and penalizing entries that are too far from the buy point). By integrating a fast, LPU-powered LLM judge using Groq's API and the `llama-3.3-70b-versatile` model, we can apply robust qualitative reasoning to the candidates in 1-3 seconds and output a final, highly curated, actionable top 10 list.

## What Changes

- **Dependency**: Add `groq>=0.9.0` to the project's dependencies to support API communications.
- **Configuration**: Add Groq API credentials, model configurations (primary and fallback), and connection parameters in `config.py`.
- **Core Judge Component**: Introduce a new module `judge/judge_agent.py` to handle Minervini-style quantitative-qualitative prompting, structured JSON output extraction, and automated fallback logic.
- **Pipeline Orchestration**: Wire the judge agent into the main execution entry point (`main.py`) to process scanned candidates and display the final ranked lists.
- **Persistent Output**: Persist the final top 10 candidates to a new JSON document at `data/top10.json`.

## Capabilities

### New Capabilities
- `judge-agent`: Performs qualitative technical analysis and ranks pre-screened stock candidates to select the final top 10 actionable setups using LLM reasoning.

### Modified Capabilities
- `scan-engine`: Extends the execution flow of the parallel batch scanner to orchestrate the judge pipeline, display a unified output banner, and save the final top 10 setups.

## Impact

- `requirements.txt`: Adds `groq>=0.9.0`.
- `config.py`: Adds constants `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_MAX_TOKENS`, and `GROQ_TIMEOUT`.
- `main.py`: Integrates `run_judge` and `save_top10` inside the main runtime pipeline.
- `data/top10.json`: New persistent output location for the curated portfolio candidates.
