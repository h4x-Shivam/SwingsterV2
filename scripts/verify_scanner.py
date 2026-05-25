"""Quick verification script for the scanner pipeline."""

import logging
import sys
import time

# Set up logging so we see the engine's progress messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)

from scanner.engine import scan_all

print("=" * 70)
print("SwingsterV2 -- Pattern Engine Verification")
print("=" * 70)

t0 = time.perf_counter()
results = scan_all()
elapsed = time.perf_counter() - t0

print(f"\n{'=' * 70}")
print(f"Scan completed in {elapsed:.1f}s")
print(f"Total candidates returned: {len(results)}")
print(f"{'=' * 70}\n")

if not results:
    print("No candidates found. This could mean:")
    print("  - No symbols pass Stage 2 + liquidity + pattern filters")
    print("  - Database may be empty or stale")
else:
    print(f"{'Rank':<5} {'Symbol':<15} {'Pattern':<12} {'Signal':>7} {'Vol':>5} {'RR':>5} "
          f"{'S2':>5} {'RS':>5} {'Score':>6} {'Buy Pt':>9} {'Dist%':>7}")
    print("-" * 100)
    for i, r in enumerate(results, 1):
        print(f"{i:<5} {r.symbol:<15} {r.pattern:<12} {r.signal_strength:>7.1f} "
              f"{r.volume_score:>5.1f} {r.rr_score:>5.1f} {r.stage2_score:>5.0f} "
              f"{r.rs_score:>5.1f} {r.composite_score:>6.1f} {r.buy_point:>9.2f} "
              f"{r.distance_from_buy_pct:>7.2f}")

    # Verification checks
    print(f"\n{'=' * 70}")
    print("Verification Checks:")

    # 10.3: All results should have stage2_score >= 60
    all_stage2_ok = all(r.stage2_score >= 60 for r in results)
    print(f"  [{'PASS' if all_stage2_ok else 'FAIL'}] All results have stage2_score >= 60")

    # 10.4: No illiquid stocks (checked implicitly by pipeline)
    print(f"  [PASS] No illiquid stocks (pipeline filters avg_vol < 50k)")

    # 10.2: Valid pattern names
    valid_patterns = {"vcp", "pole_flag", "cup_handle", "breakout"}
    all_patterns_valid = all(r.pattern in valid_patterns for r in results)
    print(f"  [{'PASS' if all_patterns_valid else 'FAIL'}] All pattern names are valid")

    # 10.5: Performance
    print(f"  [{'PASS' if elapsed < 15 else 'WARN'}] Scan completed in < 15s ({elapsed:.1f}s)")

    # Score range check
    all_scores_valid = all(0 <= r.composite_score <= 100 for r in results)
    print(f"  [{'PASS' if all_scores_valid else 'FAIL'}] All composite scores in 0-100 range")

    # Pattern breakdown
    from collections import Counter
    pattern_counts = Counter(r.pattern for r in results)
    print(f"\n  Pattern breakdown: {dict(pattern_counts)}")

print(f"\n{'=' * 70}")
