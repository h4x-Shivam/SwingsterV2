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

Your job is to apply qualitative judgment on top of quantitative
scores and select the final top 10 setups worth acting on.

CRITICAL: Return ONLY a raw JSON array.
No explanation. No markdown. No code fences.
Start your response with [ and end with ]
Any text outside the JSON array will break the parser."""

    mode_context = {
        "VCP": """
You are evaluating ONLY Volatility Contraction Pattern (VCP) setups.
VCP criteria you must apply:
- Prefer 3–4 contractions over 2 (more mature, more reliable base)
- Final contraction must be the tightest of all contractions
- Volume must dry up significantly in each successive contraction
- Stock must be sitting close to its pivot point (within 5%)
- The tighter and quieter the final base, the higher you rank it""",

        "FLAG_POLE": """
You are evaluating ONLY Flag & Pole setups.
Flag & Pole criteria you must apply:
- Pole must be a sharp impulsive move (strong, not gradual drift up)
- Flag must be tight and orderly — NOT a deep correction
- Flag retracement should be 20–35% of pole, never more
- Volume must dry up inside the flag vs the pole
- Flags older than 20 candles lose momentum — rank them lower
- Prefer flags that formed recently (last 10–15 candles)""",

        "CUP_HANDLE": """
You are evaluating ONLY Cup & Handle setups.
Cup & Handle criteria you must apply:
- Cup must have a proper U-shape — V-shapes are lower quality
- Right lip must be within 5% of left lip (symmetry matters)
- Handle must slope downward or sideways — upward handle = invalid
- Handle must form in upper half of the cup
- Volume must dry up in the handle
- Prefer handles that are currently forming (5–15 candles old)
- Handles older than 25 candles are stale — rank lower""",

        "BREAKOUT": """
You are evaluating ONLY Horizontal Breakout setups.
Breakout criteria you must apply:
- Resistance must have been tested multiple times (2+ touches)
- Each resistance test must be separated by at least 10 days
- Volume on the breakout candle is critical — must be above average
- Low volume breakout = fake breakout — rank it last or exclude
- Prefer stocks sitting just below resistance (within 3%)
- Stocks already extended past breakout are not actionable""",

        "ALL": """
You are evaluating a MIXED set of VCP, Flag & Pole, Cup & Handle,
and Breakout setups.
Cross-pattern criteria you must apply:
- A setup near its buy point beats a higher-scored setup that is extended
- Prefer the more mature/complete setup when scores are similar
- Apply pattern-specific quality checks for each pattern type
- Maximum 2 stocks from the same sector in the final top 10"""
    }

    return base + mode_context.get(mode, mode_context["ALL"])

def _build_user_prompt(candidates: list[dict], mode: str) -> str:
    return f"""
Here are {len(candidates)} pre-screened NSE stock candidates
for {mode} pattern setups. All have passed Stage 2, liquidity,
and pattern detection filters.

CANDIDATES:
{json.dumps(candidates, indent=2)}

YOUR TASK:
Select and rank the TOP 10 best setups from these candidates.

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
- Check sector concentration across your final 10 before returning.

RETURN FORMAT — THIS IS CRITICAL FOR GROQ:
You MUST return ONLY a raw JSON array.
Do NOT write any text before the [
Do NOT write any text after the ]
Do NOT use markdown code fences (no ```)
Do NOT explain your choices outside the JSON

Remember: start with [ end with ] no text outside the array

Each of the 10 objects must have EXACTLY these fields
(no extra fields, no missing fields):

[
  {{
    "rank": 1,
    "symbol": "SYMBOLNAME",
    "pattern": "vcp",
    "signal_strength": 79,
    "volume_score": 85,
    "rr_ratio": 2.8,
    "stage2_score": 100,
    "rs_score": 72,
    "composite_score": 81.5,
    "current_price": 2810.50,
    "buy_point": 2847.50,
    "stop_loss": 2710.00,
    "target": 3100.00,
    "distance_from_buy_pct": 1.32,
    "conviction": "HIGH",
    "sector": "Energy",
    "judge_verdict": "2–3 sentences on what makes this setup compelling. Must mention pattern type, key strength, proximity to buy point.",
    "why_ranked_here": "1 sentence on why this rank vs others.",
    "flags": ""
  }}
]

conviction must be: HIGH or MEDIUM or LOW
flags: warnings like earnings, sector pressure, needs confirmation.
       Use empty string "" if no flags.
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

    # Step 5 — trim if more than 10
    if len(results) > 10:
        logger.warning(f"Trimming {len(results)} → 10")
        results = results[:10]

    # Step 6 — pad if fewer than 10
    if len(results) < 10:
        logger.warning(f"Padding results from {len(results)} → 10")
        existing = {r.get("symbol") for r in results if r.get("symbol")}
        pool = sorted(
            [c for c in candidates if c.get("symbol") not in existing],
            key=lambda x: x.get("composite_score", 0),
            reverse=True
        )
        for i, extra in enumerate(pool[:10 - len(results)]):
            padded_item = dict(extra)
            padded_item["rank"] = len(results) + i + 1
            padded_item["judge_verdict"] = "Auto-added: judge returned fewer than 10."
            padded_item["why_ranked_here"] = "Padded by composite score fallback."
            padded_item["flags"] = ""
            padded_item["sector"] = ""
            padded_item["conviction"] = padded_item.get("conviction", "LOW")
            results.append(padded_item)

    # Step 7 — validate all 19 required fields per item
    required_fields = [
        "rank", "symbol", "pattern", "signal_strength", "volume_score",
        "rr_ratio", "stage2_score", "rs_score", "composite_score",
        "current_price", "buy_point", "stop_loss", "target",
        "distance_from_buy_pct", "conviction", "sector",
        "judge_verdict", "why_ranked_here", "flags"
    ]

    candidate_lookup = {c.get("symbol"): c for c in candidates}

    for item in results:
        sym = item.get("symbol", "")
        original = candidate_lookup.get(sym, {})
        for field in required_fields:
            if field not in item or item[field] is None:
                if field in ("sector", "judge_verdict", "why_ranked_here", "flags"):
                    item[field] = original.get(field, "")
                elif field == "conviction":
                    item[field] = original.get(field, "LOW")
                elif field in ("symbol", "pattern"):
                    item[field] = original.get(field, "")
                else:
                    item[field] = original.get(field, 0)

        # Step 8 — restore protected fields (judge must never override)
        protected_fields = ["buy_point", "stop_loss", "target", "rr_ratio"]
        if sym in candidate_lookup:
            for field in protected_fields:
                item[field] = candidate_lookup[sym].get(field, item[field])

    # Step 9 — sector check (log only, do NOT remove items)
    sector_counts = Counter(r.get("sector", "") for r in results)
    for sector, count in sector_counts.items():
        if sector and count > 2:
            logger.warning(
                f"Sector concentration: {sector} appears {count} times "
                f"in top 10 — judge did not diversify"
            )

    # Step 10 — re-index ranks cleanly 1–10
    for i, item in enumerate(results):
        item["rank"] = i + 1

    return results

def _fallback_ranking(candidates: list[dict]) -> list[dict]:
    logger = logging.getLogger(__name__)
    logger.warning("Using fallback ranking — sorted by composite_score")

    top10 = sorted(
        candidates,
        key=lambda x: x.get("composite_score", 0),
        reverse=True
    )[:10]

    results = []
    for i, item in enumerate(top10):
        fallback_item = dict(item)
        fallback_item["rank"] = i + 1
        fallback_item["conviction"] = fallback_item.get("conviction", "LOW")
        fallback_item["sector"] = fallback_item.get("sector", "")
        fallback_item["judge_verdict"] = (
            "Auto-ranked by composite score. "
            "Groq judge unavailable for this run."
        )
        fallback_item["why_ranked_here"] = f"Ranked #{i+1} by composite score fallback."
        fallback_item["flags"] = "Judge unavailable — manual review recommended."
        results.append(fallback_item)

    return results

def save_top10(top10: list[dict], mode: str):
    output = {
        "scan_mode": mode,
        "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_picks": len(top10),
        "results": top10
    }
    os.makedirs("data", exist_ok=True)
    with open("data/top10.json", "w") as f:
        json.dump(output, f, indent=2)

    logging.getLogger(__name__).info(
        f"Top 10 saved → data/top10.json (mode: {mode})"
    )
