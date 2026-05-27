import argparse
import json
import sys
from config import SCAN_MODE, SCAN_MODES
from scanner.engine import scan_all

if __name__ == "__main__":
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
    candidates = scan_all(mode=args.mode)
    
    # 4.4 Temporary output placeholder
    print(f"\nTop 10 - {args.mode} setups:\n")
    top10 = sorted(candidates, key=lambda x: x.composite_score, reverse=True)[:10]
    for i, r in enumerate(top10, 1):
        print(f"  #{i:>2}  {r.symbol:<12} "
              f"score={r.composite_score:.1f}  "
              f"pattern={r.pattern:<12} "
              f"buy=Rs {r.buy_point:.2f}  "
              f"rr={r.rr_ratio:.1f}x")
    sys.stdout.flush()
    
    # Save full candidates to data/results.json for judge agent
    with open("data/results.json", "w") as f:
        json.dump([vars(c) for c in candidates], f, indent=2)
    print(f"\nFull {len(candidates)} candidates saved -> data/results.json")
    sys.stdout.flush()
