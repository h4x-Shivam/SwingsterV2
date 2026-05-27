## Context

The SwingsterV2 scanning pipeline processes over 2,000 stocks in parallel and outputs the top 30 candidates ranked by a quantitative composite score. To elevate this from a simple mathematical filter to a professional trading portfolio selector, we need a qualitative layer (the Judge Agent). It will apply classic momentum trading rules (Minervini's Volatility Contraction Pattern principles, Cup & Handle handle structures, Flag & Pole impulses, sector diversification, and entry actionability) to select and rank the final top 10 setups.

To ensure this does not slow down nightly execution, we will leverage Groq's high-speed LPU inference with `llama-3.3-70b-versatile`, keeping latency under 3–5 seconds per run.

## Goals / Non-Goals

**Goals:**
- **Structured JSON Integration**: Call the Groq Chat Completion API to output a highly structured JSON array of exactly 10 candidates.
- **Strict Qualitative Gating**: Enforce strict momentum criteria: actionability (reject > 8% extension from buy point), sector limits (max 2 per sector in the top 10), and pattern maturity checks.
- **Fail-Safe Robustness**: Parse responses safely using array boundaries `[` and `]` to strip accidental LLM conversational prose, and implement a deterministic fallback ranking to ensure the system never crashes.
- **Calculated Field Integrity**: Protect calculated pricing data (`buy_point`, `stop_loss`, `target`, `rr_ratio`) by overwriting any hallucinated LLM values with original scan metrics.
- **Console Presentation**: Present a clean, readable ASCII console report of the top 10 setups with qualitative verdicts.

**Non-Goals:**
- **Re-running Pattern Detection**: The LLM will not run technical analysis algorithms. It relies on pre-screened chart pattern inputs.
- **Real-Time Interactive Chat**: This is a batch-processing qualitative filter, not a chat assistant.
- **Direct Order Execution**: Placing orders directly through brokers is out of scope.

## Decisions

### 1. Groq LPU Inference over Traditional APIs
- **Choice**: Groq Chat Completions API with the `llama-3.3-70b-versatile` model (fallback: `llama-3.1-8b-instant`).
- **Rationale**: Response times on standard APIs for a 70B model range from 15-20 seconds. Groq performs this in 1-3 seconds, fitting neatly in our nightly batch scan workflow.

### 2. High-Precision Gating with Low Temperature (0.1)
- **Choice**: Set temperature to 0.1, max tokens to 2000, and a connection timeout of 60 seconds.
- **Rationale**: Minimizes random generation (hallucinations) and guarantees adherence to structured JSON array instructions.

### 3. Fail-Safe Parsing and Fallback
- **Choice**: Extract JSON array utilizing `clean.find("[")` and `clean.rfind("]")`. If parsing fails, fall back to a deterministic `_fallback_ranking()` that sorts by composite score descending.
- **Rationale**: Prevents accidental LLM preambles or post-prose from breaking the parser, and guarantees 100% pipeline reliability even if API rate limits or outages occur.

### 4. Calculated Field Safeguard
- **Choice**: Compare and restore `buy_point`, `stop_loss`, `target`, and `rr_ratio` from the original scan results.
- **Rationale**: Prevents critical financial parameters from being hallucinated by LLM reasoning, maintaining quantitative truth.

### 5. Sector Diversification Capping
- **Choice**: Apply a sector capping constraint of maximum 2 symbols per sector in the final top 10 list.
- **Rationale**: Mimics prudent risk management, preventing sector concentration risk during volatile market phases.

## Risks / Trade-offs

- **[Risk] API Downtime or Rate Limits**  
  *Mitigation*: The `_fallback_ranking()` logic immediately intercepts errors, generating a valid top 10 portfolio solely on quantitative composite scoring, completely avoiding crashes.
  
- **[Risk] Missing or Incorrect Sector Data**  
  *Mitigation*: If the LLM returns an empty sector or omits it, the parser automatically restores the original candidate data fields or populates them with safe defaults.
  
- **[Risk] Accidental Markdown Formatting in LLM Output**  
  *Mitigation*: Stripping of typical markdown wrappers (` ```json `, ` ``` `, etc.) is hardcoded prior to JSON deserialization.
