## 1. Dependencies and Configuration

- [ ] 1.1 Add `groq>=0.9.0` to `requirements.txt`
- [ ] 1.2 Add Groq API parameters and constants to `config.py`: `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_MAX_TOKENS`, `GROQ_TIMEOUT`, and `GROQ_MODEL_FALLBACK`

## 2. Core Judge Module

- [ ] 2.1 Create empty `judge/__init__.py` to initialize the `judge` package
- [ ] 2.2 Create `judge/judge_agent.py` and implement Groq client initialization
- [ ] 2.3 Implement system prompt builder `_build_system_prompt(mode: str) -> str` supporting `VCP`, `FLAG_POLE`, `CUP_HANDLE`, `BREAKOUT`, and `ALL`
- [ ] 2.4 Implement user prompt builder `_build_user_prompt(candidates: list[dict], mode: str) -> str` containing momentum qualitative criteria
- [ ] 2.5 Implement core `run_judge(candidates: list[dict], mode: str = "ALL") -> list[dict]` executing chat completions at low temperature (0.1) and timeout (60s)
- [ ] 2.6 Implement response parser and validator `_parse_and_validate(raw_text: str, candidates: list[dict]) -> list[dict]`
- [ ] 2.7 Strip markdown code fences, and extract array boundary using `clean.find("[")` and `clean.rfind("]")`
- [ ] 2.8 Enforce a maximum sector limit of 2 stocks per sector in the final top 10 selections
- [ ] 2.9 Protect core calculated fields (`buy_point`, `stop_loss`, `target`, `rr_ratio`) by restoring original values from candidates
- [ ] 2.10 Implement fallback ranking `_fallback_ranking(candidates: list[dict]) -> list[dict]` sorting by `composite_score` descending
- [ ] 2.11 Implement output saver `save_top10(top10: list[dict], mode: str)` saving to `data/top10.json`

## 3. Pipeline Wiring and CLI

- [ ] 3.1 Import `run_judge` and `save_top10` in `main.py`
- [ ] 3.2 Update `main.py` orchestrator flow to feed scanned candidates list to `run_judge`
- [ ] 3.3 Add console printing routine in `main.py` displaying the top 10 setups, conviction levels, pricing levels, and judge verdicts

## 4. Verification and Testing

- [ ] 4.1 **V1 (VCP scan verify)**: Run `python main.py --mode VCP` to check the qualitative VCP ranking returns 10 candidates in under 5s
- [ ] 4.2 **V2 (CUP_HANDLE scan verify)**: Run `python main.py --mode CUP_HANDLE` to confirm handle characteristics and rejection of > 8% extension
- [ ] 4.3 **V3 (API Failure simulation)**: Pass a wrong/empty API key to simulate API failure and verify the pipeline falls back gracefully to `_fallback_ranking` without crashing
- [ ] 4.4 **V4 (Field Protection check)**: Assert that protected fields (`buy_point`, `stop_loss`, `target`, `rr_ratio`) in `data/top10.json` match the source fields in `data/results.json` exactly
- [ ] 4.5 **V5 (Sector Diversification verify)**: Validate that no single sector has more than 2 stocks in the top 10
- [ ] 4.6 **V6 (API speed check)**: Measure API latency to ensure it executes in under 5s on average due to Groq LPU speed advantage
- [ ] 4.7 **V7 (Structure Validation)**: Validate that `data/top10.json` matches the required structure (scan_mode, scan_time, total_picks, results) and contains exactly 10 candidates with 19 required fields
