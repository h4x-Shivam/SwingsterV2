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
- **Choice**: Groq Chat Completions API with the `llama-3.3-70b-versatile` model.
- **Rationale**: Response times on standard APIs for a 70B model range from 15-20 seconds. Groq performs this in 1-3 seconds, fitting neatly in our nightly batch scan workflow.

### 2. Primary and Fallback Models
- **Choice**: Primary: `llama-3.3-70b-versatile`. Fallback: `llama-3.1-8b-instant`.
- **Rationale**: If the primary model encounters a `RateLimitError` (HTTP 429), the agent retries exactly once using `GROQ_MODEL_FALLBACK` with identical parameters. Any other exception goes straight to the fail-safe `_fallback_ranking()`.

### 3. Temperature Gating
- **Choice**: Low temperature `0.1` mandatory (never set above `0.3`).
- **Rationale**: Low temperature guarantees highly consistent structured JSON outputs and prevents the LLM from adding verbose prose preambles or postscripts.

### 4. Precise 10-Stage Parsing & Validation Sequence
- **Step 1**: Strip markdown code fences (` ```json `, ` ```JSON `, ` ``` `).
- **Step 2**: Extract array boundaries by searching for first `[` and last `]`. Returns fallback if not found.
- **Step 3**: Parse JSON with `json.loads()`.
- **Step 4**: Validate list type and verify it is not empty.
- **Step 5**: Trim results to exactly 10 if the LLM returned more than 10.
- **Step 6**: Pad results if fewer than 10 by filling from original candidates sorted by `composite_score` descending (excluding symbols already in the list), using specific fallback fields.
- **Step 7**: Validate all 19 required fields per candidate. Fill missing values from original candidates (strings default to `""`, numbers to `0`).
- **Step 8**: Protect calculated fields (`buy_point`, `stop_loss`, `target`, `rr_ratio`) by overwriting them with original values from the scanner.
- **Step 9**: Sector concentration check: warn only (log warnings if sector count > 2) without removing items. Sector diversification is the prompt's responsibility; the validator only tracks and alerts.
- **Step 10**: Re-index ranks cleanly from 1 to 10.

### 5. Fallback Mechanism (`_fallback_ranking()`)
- **Choice**: Sort all original candidates by `composite_score` descending and take the top 10.
- **Rationale**: If the API call fails or the output is completely corrupted, the pipeline falls back gracefully to a high-quality quantitative ranking, preventing any crashes.

## Risks / Trade-offs

- **[Risk] API Downtime or Rate Limits**  
  *Mitigation*: The one-time rate-limit fallback retry combined with immediate fail-safe `_fallback_ranking()` ensures 100% execution robustness.
  
- **[Risk] Missing or Incorrect Sector Data**  
  *Mitigation*: Automated re-mapping of required fields using a `candidate_lookup` lookup dictionary guarantees all fields are populated correctly.
  
- **[Risk] Accidental Markdown Formatting in LLM Output**  
  *Mitigation*: Fenced formatting blocks are stripped and array search bounds are extracted prior to parsing.
