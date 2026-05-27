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

### Files to create or modify
- `requirements.txt`: Add `groq>=0.9.0`.
- `config.py`: Add Groq API parameters and constants (`GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_MODEL_FALLBACK`, `GROQ_MAX_TOKENS`, and `GROQ_TIMEOUT`).
- `judge/__init__.py`: Create empty package initialization file.
- `judge/judge_agent.py`: Create Core Judge Module containing prompts, client initialization, fallback logic, validation parser, and file persistence.
- `main.py`: Import `run_judge` and `save_top10`, feed scanned candidates, and format console stdout output.

### Files to NOT touch
- `scanner/` (all files): Scanner is complete.
- `fetcher/` (all files): Fetcher is complete.
- `scanner/models.py`: Dataclass models are complete.
