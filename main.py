import argparse
import json
import sys
import os
from config import SCAN_MODE, SCAN_MODES
from scanner.engine import scan_all
from judge.judge_agent import run_judge, save_final_picks

def _validate_registry():
    from scanner.patterns.registry import PATTERN_REGISTRY
    registry_keys = set(PATTERN_REGISTRY.keys())
    modes = set(SCAN_MODES) - {"ALL"}
    if registry_keys != modes:
        raise RuntimeError(
            f"Config/Registry mismatch!\n"
            f"SCAN_MODES (sans ALL): {modes}\n"
            f"PATTERN_REGISTRY keys: {registry_keys}"
        )

if __name__ == "__main__":
    _validate_registry()
    parser = argparse.ArgumentParser(description="SwingsterV2 Scanner")
    parser.add_argument(
        "--mode",
        choices=SCAN_MODES,
        default=SCAN_MODE,
        help=f"Pattern to scan for. Options: {SCAN_MODES}"
    )
    args = parser.parse_args()
    
    # 4.2 Startup banner (ASCII safe)
    print(f"\n{'-' * 50}")
    print(f"  SwingsterV2 - Pattern Mode: {args.mode}")
    print(f"{'-' * 50}\n")
    sys.stdout.flush()
    
    # 4.3 Call scan_all inside __main__ guard
    candidates, total_scanned, count_pattern, rejected_rr_list = scan_all(mode=args.mode)
    
    candidates_dict = [vars(c) for c in candidates]
    
    # Save full candidates to data/results.json for judge agent
    os.makedirs("data", exist_ok=True)
    with open("data/results.json", "w") as f:
        json.dump(candidates_dict, f, indent=2)
    print(f"\nFull {len(candidates)} candidates saved -> data/results.json")
    
    import datetime
    summary_data = {
        "mode": args.mode,
        "total_scanned": total_scanned,
        "vcp_found_count": count_pattern,
        "rejected_by_rr": rejected_rr_list,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    with open("data/scan_summary.json", "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"Dynamic metrics saved -> data/scan_summary.json")
    
    sys.stdout.flush()
    
    # Wire judge
    print(f"\nSending {len(candidates_dict)} candidates to Groq judge...")
    sys.stdout.flush()
    final_picks = run_judge(candidates_dict, mode=args.mode)
    
    print(f"\nFetching NSE fundamental data for {len(final_picks)} final picks...")
    sys.stdout.flush()

    _yf_fetch = None
    try:
        from fetcher.nse_fetcher import _yf_fetch
    except ImportError as ie:
        print(f"  [WARN] yfinance not available — skipping fundamentals ({ie})")

    def format_mcap(val):
        if not val: return "N/A"
        try:
            v = float(val)
            if v >= 1e12: return f"Rs {v/1e12:.1f}T"
            if v >= 1e9: return f"Rs {v/1e9:.1f}B"
            if v >= 1e6: return f"Rs {v/1e6:.1f}M"
            return f"Rs {v:.0f}"
        except: return "N/A"

    def format_pct(val):
        if not val: return "N/A"
        try: return f"{float(val)*100:.1f}%"
        except: return "N/A"

    def format_ratio(val):
        if not val: return "N/A"
        try: return f"{float(val):.2f}"
        except: return "N/A"

    for r in final_picks:
        symbol = r['symbol']
        if _yf_fetch is None:
            r["fundamentals"] = {
                "market_cap": "N/A", "pe_ratio": "N/A", "roe": "N/A", "debt_to_equity": "N/A"
            }
            continue
        try:
            yf_data = _yf_fetch(f"{symbol}.NS")
            r["fundamentals"] = {
                "market_cap": format_mcap(yf_data.get("market_cap")),
                "pe_ratio": format_ratio(yf_data.get("trailing_pe")),
                "roe": format_pct(yf_data.get("return_on_equity")),
                "debt_to_equity": format_ratio(yf_data.get("debt_to_equity"))
            }
        except Exception as e:
            r["fundamentals"] = {
                "market_cap": "N/A", "pe_ratio": "N/A", "roe": "N/A", "debt_to_equity": "N/A"
            }
            print(f"  [!] Failed to fetch fundamentals for {symbol}: {e}")
            
    save_final_picks(final_picks, mode=args.mode)
    
    # Print judge results
    print(f"\n{'-' * 55}")
    print(f"  FINAL PICKS - {args.mode} SETUPS")
    print(f"{'-' * 55}")
    for r in final_picks:
        print(f"\n  #{r['rank']}  {r['symbol']:<12} "
              f"[{r['pattern'].upper():<12}] "
              f"Score: {r['composite_score']:.1f}  "
              f"Conviction: {r['conviction']}")
        print(f"      Buy:  Rs {r['buy_point']:.2f}  "
              f"Stop: Rs {r['stop_loss']:.2f}  "
              f"Target: Rs {r['target']:.2f}  "
              f"R:R {r['rr_ratio']:.1f}x")
        print(f"      {r['judge_verdict']}")
        if r['flags']:
            print(f"      WARNING: {r['flags']}")
    print(f"\n{'-' * 55}")
    print(f"Full results -> data/final_picks.json")
    sys.stdout.flush()


