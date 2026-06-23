import json
import time
import logging
import os
from collections import Counter

def _auto_judge_candidate(item: dict) -> dict:
    """Generate a deterministic verdict and conviction based on scores."""
    result = dict(item)
    
    comp_score = item.get("composite_score", 0.0)
    sig_strength = item.get("signal_strength", 0.0)
    vol_score = item.get("volume_score", 0.0)
    pattern = item.get("pattern", "SETUP").upper()
    
    # 1. Conviction
    if comp_score >= 85 or sig_strength >= 90:
        result["conviction"] = "HIGH"
    else:
        result["conviction"] = "MEDIUM"
        
    # 2. Verdict Template
    if pattern == "VCP":
        if sig_strength >= 85:
            base = "Exceptional strict contraction with massive volume dry-up."
        else:
            base = "Solid price contraction preparing for a breakout."
    elif pattern == "CUP_HANDLE":
        base = "Classic Cup and Handle base forming a strong pivot."
    elif pattern == "FLAG_POLE":
        if sig_strength >= 85:
            base = "High-tight momentum flag. Explosive setup."
        else:
            base = "Healthy consolidation following a strong momentum thrust."
    else:
        base = f"Strong {pattern} technical setup."
        
    vol_text = " Excellent volume footprint." if vol_score >= 80 else ""
    result["judge_verdict"] = base + vol_text
    
    # 3. Flags (Warnings)
    flags = []
    pledge = item.get("pledge_pct")
    if pledge is not None and pledge > 20.0:
        flags.append(f"HIGH RISK: Promoter pledge is {pledge}%")
        
    if item.get("distance_from_buy_pct", 0) > 4.0:
        flags.append("Slightly extended past ideal buy point.")
        
    result["flags"] = " | ".join(flags) if flags else ""
    
    return result

def run_judge(candidates: list[dict], mode: str = "ALL") -> list[dict]:
    logger = logging.getLogger(__name__)

    if not candidates:
        logger.warning("Auto-Judge received empty candidates list")
        return []

    logger.info(f"Auto-Judge starting — {len(candidates)} candidates | mode: {mode}")
    start = time.perf_counter()

    all_results = []
    for item in candidates:
        evaluated = _auto_judge_candidate(item)
        all_results.append(evaluated)

    # Sort by Conviction (HIGH > MEDIUM) then Composite Score (desc)
    def sort_key(x):
        c = 2 if x.get("conviction") == "HIGH" else 1
        return (c, x.get("composite_score", 0.0))

    all_results.sort(key=sort_key, reverse=True)

    # Assign ranks cleanly
    for i, item in enumerate(all_results):
        item["rank"] = i + 1

    # Sector check (log only)
    sector_counts = Counter(r.get("sector", "") for r in all_results)
    for sector, count in sector_counts.items():
        if sector and count > 2:
            logger.info(
                f"Sector concentration: {sector} appears {count} times "
                f"in final picks"
            )

    elapsed = time.perf_counter() - start
    logger.info(f"Auto-Judge finished in {elapsed:.3f}s | Returned {len(all_results)} picks")
    print(f"Auto-Judge complete — {len(all_results)} picks in {elapsed:.3f}s")
    
    return all_results

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
