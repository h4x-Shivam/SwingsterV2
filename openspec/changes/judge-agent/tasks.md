# SwingsterV2 — Judge Agent Implementation
# Final reviewed and corrected task spec

---

## 1. Dependencies and Configuration

- [x] 1.1 Add `groq>=0.9.0` to `requirements.txt`

- [x] 1.2 Add to `config.py`:
          ```python
          import os

          # Groq API — Judge Agent
          GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")
          GROQ_MODEL           = "llama-3.3-70b-versatile"
          GROQ_MODEL_FALLBACK  = "llama-3.1-8b-instant"
          GROQ_MAX_TOKENS      = 2000
          GROQ_TIMEOUT         = 60     # seconds
          ```

          Why llama-3.3-70b-versatile:
          Best JSON instruction-following on Groq free tier.
          Handles 30-candidate payload without truncating.

          Why llama-3.1-8b-instant as fallback:
          Faster, lower rate limit consumption.
          Less reliable on complex JSON — fallback only.

---

## 2. Core Judge Module

- [x] 2.1 Create empty `judge/__init__.py` to initialise the judge package

- [x] 2.2 Create `judge/judge_agent.py` with Groq client initialisation:
          ```python
          from groq import Groq
          from config import (
              GROQ_API_KEY, GROQ_MODEL, GROQ_MODEL_FALLBACK,
              GROQ_MAX_TOKENS, GROQ_TIMEOUT
          )
          client = Groq(api_key=GROQ_API_KEY)
          ```

- [x] 2.3 Implement `_build_system_prompt(mode: str) -> str`
          Base prompt explains the agent's role as a Minervini-style
          NSE quant trader reviewing pre-screened candidates.
          Must include this critical instruction in the base:
          ```
          CRITICAL: Return ONLY a raw JSON array.
          No explanation. No markdown. No code fences.
          Start your response with [ and end with ]
          Any text outside the JSON array will break the parser.
          ```
          Mode-specific sections must cover:
          - VCP     : prefer 3–4 contractions, tightest final base,
                      volume dry-up per contraction, within 5% of pivot
          - FLAG_POLE: pole >= 8% in <= 15 candles, flag retracement
                      <= 35%, flag slope downward/flat, recent flags
                      (< 15 candles) preferred over old ones (> 20)
          - CUP_HANDLE: U-shape required, right lip within 5% of left,
                        handle slope downward/flat only,
                        handle above cup midpoint,
                        handles > 25 candles are stale
          - BREAKOUT: 2+ resistance tests >= 10 days apart,
                      volume_score >= 75 required,
                      low volume breakout = fake, reject it
          - ALL     : cross-pattern comparison, sector max 2 per sector,
                      proximity to buy point beats higher score

- [x] 2.4 Implement `_build_user_prompt(candidates: list[dict], mode: str) -> str`
          Must include:
          - Full candidates JSON via `json.dumps(candidates, indent=2)`
          - All 7 qualitative criteria in order of importance:
            1. Actionability — distance_from_buy_pct -5% to +1% ideal,
               penalise > 3%, REJECT > 8% entirely
            2. Setup maturity — pattern-specific maturity checks
            3. Sector diversification — max 2 per sector, rotate if needed
            4. Volume conviction — breakout >= 75, others >= 65
            5. Risk/reward — reject rr_ratio < 1.5, prefer >= 2.5
            6. Trend strength — stage2_score 100 preferred, 60 minimum
            7. Relative strength — rs_score >= 60 preferred,
               rs_score < 40 needs signal_strength >= 80
          - Minervini trader test: "Would a Minervini trader take this today?"
          - Exact required output JSON schema with all 19 fields shown
            as an example object inside the prompt
          - Repeat JSON-only instruction at the END of the prompt:
            "Remember: start with [ end with ] no text outside the array"

- [x] 2.5 Implement `run_judge(candidates: list[dict], mode: str = "ALL") -> list[dict]`

          Primary call using GROQ_MODEL:
          ```python
          response = client.chat.completions.create(
              model       = GROQ_MODEL,
              messages    = [
                  {"role": "system", "content": system_prompt},
                  {"role": "user",   "content": user_prompt}
              ],
              max_tokens  = GROQ_MAX_TOKENS,
              temperature = 0.1,
              timeout     = GROQ_TIMEOUT,
          )
          ```
          temperature = 0.1 is mandatory — never set above 0.3.
          Low temperature prevents Groq/Llama from adding prose
          before or after the JSON array.

- [x] 2.5b Rate limit fallback — if primary call raises `RateLimitError`
           (HTTP 429), retry ONCE using `GROQ_MODEL_FALLBACK` with
           identical parameters before going to `_fallback_ranking()`.
           Any other exception goes straight to `_fallback_ranking()`.
           Never retry more than once total.
           ```python
           from groq import RateLimitError

           try:
               # primary call with GROQ_MODEL
               ...
           except RateLimitError:
               logger.warning("Rate limited on primary model, trying fallback model")
               try:
                   # retry with GROQ_MODEL_FALLBACK
                   ...
               except Exception as e:
                   logger.error(f"Fallback model also failed: {e}")
                   return _fallback_ranking(candidates)
           except Exception as e:
               logger.error(f"Judge failed: {e}")
               return _fallback_ranking(candidates)
           ```

- [x] 2.5c Log token usage after every successful API call:
           ```python
           logger.info(
               f"Groq call complete in {elapsed:.2f}s | "
               f"model: {response.model} | "
               f"tokens used: {response.usage.total_tokens}"
           )
           ```
           This monitors free tier consumption.
           Groq free tier limit is ~14,400 tokens/min on 70B model.

- [x] 2.6 Implement `_parse_and_validate(raw_text: str, candidates: list[dict]) -> list[dict]`

          In this exact order:

          Step 1 — strip markdown fences:
          ```python
          for fence in ["```json", "```JSON", "```"]:
              clean = clean.replace(fence, "")
          clean = clean.strip()
          ```

          Step 2 — extract JSON array boundaries:
          ```python
          start_idx = clean.find("[")
          end_idx   = clean.rfind("]")
          if start_idx == -1 or end_idx == -1:
              logger.error("No JSON array found in response")
              return _fallback_ranking(candidates)
          clean = clean[start_idx : end_idx + 1]
          ```
          This handles Groq adding prose before/after the array
          despite instructions — extract only the array content.

          Step 3 — parse JSON:
          ```python
          try:
              results = json.loads(clean)
          except json.JSONDecodeError as e:
              logger.error(f"JSON parse failed: {e}")
              return _fallback_ranking(candidates)
          ```

          Step 4 — validate list type and non-empty:
          ```python
          if not isinstance(results, list) or len(results) == 0:
              logger.error("Response is not a valid non-empty JSON array")
              return _fallback_ranking(candidates)
          ```

          Step 5 — trim if more than 10:
          ```python
          if len(results) > 10:
              logger.warning(f"Trimming {len(results)} → 10")
              results = results[:10]
          ```

          Step 6 — pad if fewer than 10:
          Fill missing slots from candidates sorted by composite_score,
          excluding symbols already in results.
          Auto-generated fields for padded items:
          ```python
          extra["judge_verdict"]   = "Auto-added: judge returned fewer than 10."
          extra["why_ranked_here"] = "Padded by composite score fallback."
          extra["flags"]           = ""
          extra["sector"]          = ""
          extra["conviction"]      = extra.get("conviction", "LOW")
          ```

          Step 7 — validate all 19 required fields per item:
          Fill any missing field from the original candidate dict.
          Use empty string "" for string fields, 0 for numeric fields.
          Build candidate_lookup = {symbol: candidate} for O(1) access.

          Step 8 — restore protected fields (judge must never override):
          ```python
          protected = ["buy_point", "stop_loss", "target", "rr_ratio"]
          for item in results:
              sym = item.get("symbol", "")
              if sym in candidate_lookup:
                  for field in protected:
                      item[field] = candidate_lookup[sym].get(
                          field, item[field]
                      )
          ```

          Step 9 — sector check (log only, do NOT remove items):
          ```python
          from collections import Counter
          sector_counts = Counter(r.get("sector", "") for r in results)
          for sector, count in sector_counts.items():
              if sector and count > 2:
                  logger.warning(
                      f"Sector concentration: {sector} appears {count} times "
                      f"in top 10 — judge did not diversify"
                  )
          ```
          Do NOT remove or replace items here.
          Sector enforcement is the judge's responsibility via the prompt.
          The validator only checks and warns.

          Step 10 — re-index ranks cleanly 1–10:
          ```python
          for i, item in enumerate(results):
              item["rank"] = i + 1
          ```

- [x] 2.7 Implement `_fallback_ranking(candidates: list[dict]) -> list[dict]`
          Sort by composite_score descending, take top 10.
          Set these fields on every fallback item:
          ```python
          item["rank"]            = i + 1
          item["conviction"]      = item.get("conviction", "LOW")
          item["sector"]          = item.get("sector", "")
          item["judge_verdict"]   = (
              "Auto-ranked by composite score. "
              "Groq judge unavailable for this run."
          )
          item["why_ranked_here"] = f"Ranked #{i+1} by composite score fallback."
          item["flags"]           = "Judge unavailable — manual review recommended."
          ```
          Fallback must always return exactly 10 items.
          Zero results from run_judge() is never acceptable.

- [x] 2.8 Implement `save_top10(top10: list[dict], mode: str)`
          Save to `data/top10.json` with this wrapper structure:
          ```python
          output = {
              "scan_mode"  : mode,
              "scan_time"  : time.strftime("%Y-%m-%d %H:%M:%S"),
              "total_picks": len(top10),
              "results"    : top10
          }
          ```
          Create `data/` directory if it doesn't exist.
          Log: `"Top 10 saved → data/top10.json (mode: {mode})"`

---

## 3. Pipeline Wiring in main.py

- [x] 3.1 Import at top of `main.py`:
          ```python
          from judge.judge_agent import run_judge, save_top10
          ```

- [x] 3.2 After `scan_all()` returns candidates, wire judge:
          ```python
          print(f"\nSending {len(candidates)} candidates to Groq judge...")
          top10 = run_judge(candidates, mode=args.mode)
          save_top10(top10, mode=args.mode)
          ```

- [x] 3.3 Console display after judge completes:
          ```python
          print(f"\n{'─' * 55}")
          print(f"  TOP 10 — {args.mode} SETUPS")
          print(f"{'─' * 55}")
          for r in top10:
              print(f"\n  #{r['rank']}  {r['symbol']:<12} "
                    f"[{r['pattern'].upper():<12}] "
                    f"Score: {r['composite_score']:.1f}  "
                    f"Conviction: {r['conviction']}")
              print(f"      Buy:  ₹{r['buy_point']:.2f}  "
                    f"Stop: ₹{r['stop_loss']:.2f}  "
                    f"Target: ₹{r['target']:.2f}  "
                    f"R:R {r['rr_ratio']:.1f}x")
              print(f"      {r['judge_verdict']}")
              if r['flags']:
                  print(f"      ⚠️  {r['flags']}")
          print(f"\n{'─' * 55}")
          print(f"Full results → data/top10.json")
          ```

---

## 4. Files to create or modify

| File | Action |
|---|---|
| `requirements.txt` | Add groq>=0.9.0 |
| `config.py` | Add 5 Groq constants |
| `judge/__init__.py` | Create empty |
| `judge/judge_agent.py` | Create — full implementation |
| `main.py` | Wire judge into pipeline |

## 5. Files to NOT touch

| File | Reason |
|---|---|
| `scanner/` (all files) | Scanner is complete — no changes |
| `fetcher/` (all files) | Fetcher is complete — no changes |
| `scanner/models.py` | Models are complete — no changes |

---

## 6. Verification

- [x] V1 Run `python main.py --mode VCP`
       PASS: exactly 10 results returned
       PASS: all have judge_verdict, why_ranked_here, sector, flags
       PASS: data/top10.json created
       PASS: completes in under 5 seconds (Groq LPU speed)
       FAIL: crash, missing fields, > 10 seconds

- [x] V2 Run `python main.py --mode CUP_HANDLE`
       PASS: all results have pattern == "cup_handle"
       PASS: no result has distance_from_buy_pct > 8%
       PASS: judge_verdict references cup/handle characteristics

- [x] V3a Simulate auth failure — set GROQ_API_KEY = "wrong_key"
        PASS: AuthenticationError caught, fallback runs, 10 results returned
        PASS: judge_verdict says "Groq judge unavailable"
        PASS: no crash, pipeline completes
        Restore correct key after test

- [x] V3b Simulate timeout — set GROQ_TIMEOUT = 0.001
        PASS: TimeoutError caught, fallback runs, 10 results returned
        PASS: no crash
        Restore correct timeout after test

- [x] V4 Verify protected fields not overridden:
       For 3 symbols, compare buy_point, stop_loss, target, rr_ratio
       between data/top10.json and data/results.json
       PASS: values are byte-for-byte identical
       FAIL: any value differs

- [x] V5 Verify sector diversification:
       Count sector occurrences in data/top10.json results
       PASS: no sector appears more than twice
       FAIL: any sector appears 3+ times
       Note: if FAIL, check logs for the sector warning from validator

- [x] V6 Verify Groq response speed:
       PASS: API call completes in under 5 seconds
       PASS: token usage logged correctly
       FAIL: > 10 seconds (check model name in config, may be wrong)

- [x] V7 Verify data/top10.json structure:
       PASS: contains scan_mode, scan_time, total_picks, results
       PASS: results array has exactly 10 items
       PASS: each item has all 19 required fields:
             rank, symbol, pattern, signal_strength, volume_score,
             rr_ratio, stage2_score, rs_score, composite_score,
             current_price, buy_point, stop_loss, target,
             distance_from_buy_pct, conviction, sector,
             judge_verdict, why_ranked_here, flags

- [x] V8 Verify token usage is logged:
       PASS: every successful run prints token count to logs
       PASS: total_tokens value is non-zero and reasonable (500–1500)
       FAIL: token count missing or zero

---

## 7. Hard rules

1. Use Groq client only — never import Anthropic in judge_agent.py
2. temperature = 0.1 always — never higher than 0.3
3. JSON extraction must use find("[") and rfind("]") —
   Groq adds prose before/after arrays despite instructions,
   extraction handles this safely
4. Exactly one primary API call per run_judge() invocation —
   one retry allowed ONLY on RateLimitError using fallback model
5. Fallback must always return exactly 10 results —
   zero results from run_judge() is never acceptable
6. Import all keys from config.py only — never hardcode
7. Protected fields (buy_point, stop_loss, target, rr_ratio)
   must be restored from original candidate data after parsing —
   judge is never allowed to change calculated values
8. Sector enforcement is the prompt's job —
   validator only warns, never removes items