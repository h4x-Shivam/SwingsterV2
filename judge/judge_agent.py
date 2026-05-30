import json
import time
import logging
import os
from collections import Counter
from groq import Groq, RateLimitError
from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_MODEL_FALLBACK,
    GROQ_MAX_TOKENS,
    GROQ_TIMEOUT
)
from scanner.patterns.registry import get_patterns

client = Groq(api_key=GROQ_API_KEY)

def _build_system_prompt(mode: str) -> str:
    base = """You are a professional quantitative trader and technical
analyst specialising in NSE Indian equities. You use Minervini-style
momentum strategies: Stage 2 stocks, relative strength leaders,
volume-confirmed setups, tight bases, and clear risk/reward.

You receive pre-screened stock candidates that have already passed:
- Minervini Stage 2 trend filter
- Minimum liquidity filter (avg volume >= 50,000 shares)
- Minimum price filter (>= ₹20)
- Pattern detection algorithm
- Composite scoring (signal 40% + volume 25% + RR 20% + stage2 10% + rs 5%)

Your job is to act as a qualitative filter. Evaluate the quantitative setups,
discard any with critical flaws, and return ALL surviving setups that pass
your qualitative criteria with HIGH or MEDIUM conviction.

CRITICAL: Return ONLY a raw JSON array.
No explanation. No markdown. No code fences.
Start your response with [ and end with ]
Any text outside the JSON array will break the parser."""

    active_patterns = get_patterns(mode)
    if mode == "ALL":
        mode_context = "\n".join(p.judge_prompt for p in active_patterns)
        mode_context += "\n- Maximum 2 stocks from the same sector in the final top 10"
    else:
        mode_context = active_patterns[0].judge_prompt

    return base + "\n\n" + mode_context

def _build_user_prompt(candidates: list[dict], mode: str) -> str:
    return f"""
Here are {len(candidates)} pre-screened NSE stock candidates
for {mode} pattern setups. All have passed Stage 2, liquidity,
and pattern detection filters.

CANDIDATES:
{json.dumps(candidates, indent=2)}

YOUR TASK:
Evaluate all candidates. Discard any setups that have critical flaws.
Return ALL surviving candidates, assigning them a conviction level.

Apply ALL of the following criteria in order of importance:

1. ACTIONABILITY — distance_from_buy_pct between -5% and +1% is ideal.
   Penalise > 3% above buy point. Reject > 8% above buy point entirely.

2. SETUP MATURITY — prefer complete, mature patterns over early-forming.
   VCP: 3–4 contractions > 2 contractions.
   Cup & Handle: handle currently forming > stale handle.
   Flag: recent flag (< 15 candles) > old flag (> 20 candles).
   Breakout: price near resistance NOW > already extended.

3. SECTOR DIVERSIFICATION — maximum 2 stocks from the same NSE sector.
   Use your knowledge of NSE sector classification.
   If heavy concentration exists, rotate in best setup from other sectors.

4. VOLUME CONVICTION — Breakout: volume_score >= 75 required.
   All other patterns: prefer volume_score >= 65.
   Equal setups: pick higher volume one.

5. RISK/REWARD — never include rr_ratio < 1.5.
   Strongly prefer rr_ratio >= 2.5.
   Excellent RR (>= 3.5) can compensate for moderate signal (55–65).

6. TREND STRENGTH — strongly prefer stage2_score = 100.
   stage2_score = 80 acceptable.
   stage2_score = 60 only if setup is exceptional everywhere else.

7. RELATIVE STRENGTH — prefer rs_score >= 60 (beating Nifty 50).
   rs_score >= 80 = institutional accumulation — give it a bonus.
   rs_score < 40 needs signal_strength >= 80 to be included.

QUALITATIVE CHECKS before finalising:
- For each pick ask: "Would a Minervini-style trader take this trade today?"
  If answer is "maybe" — replace with next best candidate.
- Check sector concentration across your final picks before returning.

RETURN FORMAT — THIS IS CRITICAL FOR GROQ:
You MUST return ONLY a raw JSON array.
Do NOT write any text before the [
Do NOT write any text after the ]
Do NOT use markdown code fences (no ```)
Do NOT explain your choices outside the JSON

Remember: start with [ end with ] no text outside the array

Each object must have EXACTLY these fields (no extra fields, no missing fields):

[
  {
    "symbol": "SYMBOLNAME",
    "conviction": "HIGH",
    "judge_verdict": "2–3 sentences on what makes this setup compelling. Must mention pattern type, key strength, proximity to buy point.",
    "flags": "Warnings like earnings, sector pressure, needs confirmation. Use empty string if none."
  }
]

conviction must be: HIGH or MEDIUM
"""

def run_judge(candidates: list[dict], mode: str = "ALL") -> list[dict]:
    logger = logging.getLogger(__name__)

    if not candidates:
        logger.warning("Judge received empty candidates list")
        return []

    logger.info(f"Judge agent starting — {len(candidates)} candidates | mode: {mode}")
    start = time.perf_counter()

    system_prompt = _build_system_prompt(mode)
    user_prompt = _build_user_prompt(candidates, mode)

    try:
        # Primary call using GROQ_MODEL
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=GROQ_MAX_TOKENS,
            temperature=0.1,
            timeout=GROQ_TIMEOUT,
        )
        elapsed = time.perf_counter() - start
        logger.info(
            f"Groq call complete in {elapsed:.2f}s | "
            f"model: {response.model} | "
            f"tokens used: {response.usage.total_tokens}"
        )
        raw_text = response.choices[0].message.content.strip()
        return _parse_and_validate(raw_text, candidates)

    except RateLimitError:
        logger.warning("Rate limited on primary model, trying fallback model")
        fallback_start = time.perf_counter()
        try:
            # Retry ONCE using GROQ_MODEL_FALLBACK
            response = client.chat.completions.create(
                model=GROQ_MODEL_FALLBACK,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.1,
                timeout=GROQ_TIMEOUT,
            )
            elapsed = time.perf_counter() - fallback_start
            logger.info(
                f"Groq fallback call complete in {elapsed:.2f}s | "
                f"model: {response.model} | "
                f"tokens used: {response.usage.total_tokens}"
            )
            raw_text = response.choices[0].message.content.strip()
            return _parse_and_validate(raw_text, candidates)
        except Exception as e:
            logger.error(f"Fallback model also failed: {e}")
            return _fallback_ranking(candidates)

    except Exception as e:
        elapsed = time.perf_counter() - start
        logger.error(f"Judge failed after {elapsed:.2f}s: {e}")
        return _fallback_ranking(candidates)

def _parse_and_validate(raw_text: str, candidates: list[dict]) -> list[dict]:
    logger = logging.getLogger(__name__)

    # Step 1 — strip markdown fences
    clean = raw_text
    for fence in ["```json", "```JSON", "```"]:
        clean = clean.replace(fence, "")
    clean = clean.strip()

    # Step 2 — extract JSON array boundaries
    start_idx = clean.find("[")
    end_idx = clean.rfind("]")
    if start_idx == -1 or end_idx == -1:
        logger.error("No JSON array found in response")
        logger.error(f"Raw response was: {raw_text}")
        return _fallback_ranking(candidates)
    clean = clean[start_idx : end_idx + 1]

    # Step 3 — parse JSON
    try:
        results = json.loads(clean)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e}")
        return _fallback_ranking(candidates)

    # Step 4 — validate list type and non-empty
    if not isinstance(results, list) or len(results) == 0:
        logger.error("Response is not a valid non-empty JSON array")
        return _fallback_ranking(candidates)

    # Step 5 — Map candidates back and restore missing fields
    candidate_lookup = {c.get("symbol"): c for c in candidates}
    
    final_results = []
    for item in results:
        sym = item.get("symbol", "")
        if sym not in candidate_lookup:
            logger.warning(f"Judge returned unknown symbol: {sym}")
            continue # LLM hallucinated a symbol
        
        merged = dict(candidate_lookup[sym]) # start with original quantitative data
        merged["conviction"] = item.get("conviction", "MEDIUM").upper()
        if merged["conviction"] not in ("HIGH", "MEDIUM"):
            merged["conviction"] = "MEDIUM"
        merged["judge_verdict"] = item.get("judge_verdict", "")
        merged["flags"] = item.get("flags", "")
        
        final_results.append(merged)
        
    # Step 6 — Sort by Conviction (HIGH > MEDIUM) then Composite Score (desc)
    def sort_key(x):
        c = 2 if x.get("conviction") == "HIGH" else 1
        return (c, x.get("composite_score", 0.0))
        
    final_results.sort(key=sort_key, reverse=True)
    
    # Step 7 — Assign ranks cleanly
    for i, item in enumerate(final_results):
        item["rank"] = i + 1
        
    # Step 8 — Sector check (log only)
    sector_counts = Counter(r.get("sector", "") for r in final_results)
    for sector, count in sector_counts.items():
        if sector and count > 2:
            logger.warning(
                f"Sector concentration: {sector} appears {count} times "
                f"in final picks"
            )
            
    return final_results

def _fallback_ranking(candidates: list[dict]) -> list[dict]:
    logger = logging.getLogger(__name__)
    logger.warning("Using fallback ranking — returning all candidates sorted by composite_score")

    candidates_sorted = sorted(
        candidates,
        key=lambda x: x.get("composite_score", 0),
        reverse=True
    )

    results = []
    for i, item in enumerate(candidates_sorted):
        fallback_item = dict(item)
        fallback_item["rank"] = i + 1
        fallback_item["conviction"] = "MEDIUM"
        fallback_item["judge_verdict"] = (
            "Auto-ranked by composite score. "
            "Groq judge unavailable for this run."
        )
        fallback_item["flags"] = "Judge unavailable — manual review recommended."
        results.append(fallback_item)

    return results

def save_final_picks(picks: list[dict], mode: str):
    output = {
        "scan_mode": mode,
        "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_picks": len(picks),
        "results": picks
    }
    os.makedirs("data", exist_ok=True)
    with open("data/final_picks.json", "w") as f:
        json.dump(output, f, indent=2)

    logging.getLogger(__name__).info(
        f"Final {len(picks)} picks saved → data/final_picks.json (mode: {mode})"
    )
