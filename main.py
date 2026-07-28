"""
main.py — CLI entry point for SwingsterV2.

Thin wrapper: parses args, delegates to ScanService, prints results.
All orchestration, persistence, and business logic lives in services/.
"""

import argparse
import sys

from config import DEFAULT_SCAN_MODE, SCAN_MODES
from log import setup_logging
from services.scan_service import ScanService


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


def _print_results(result) -> None:
    """Pretty-print the final picks to stdout."""
    print(f"\n{'-' * 55}")
    print(f"  FINAL PICKS - {result.mode} SETUPS")
    print(f"{'-' * 55}")
    for r in result.final_picks:
        print(f"\n  #{r.get('rank')}  {r.get('symbol'):<12} "
              f"[{r.get('pattern', '').upper():<12}] "
              f"Score: {r.get('composite_score', 0):.1f}  "
              f"Conviction: {r.get('conviction')}")
        print(f"      Buy:  Rs {r.get('buy_point', 0):.2f}  "
              f"Stop: Rs {r.get('stop_loss', 0):.2f}  "
              f"Target: Rs {r.get('target', 0):.2f}  "
              f"R:R {r.get('rr_ratio', 0):.1f}x")
        print(f"      {r.get('judge_verdict')}")
        if r.get('flags'):
            print(f"      WARNING: {r.get('flags')}")
    print(f"\n{'-' * 55}")
    sys.stdout.flush()


if __name__ == "__main__":
    _validate_registry()

    parser = argparse.ArgumentParser(description="SwingsterV2 Scanner")
    parser.add_argument(
        "--mode",
        choices=SCAN_MODES,
        default=DEFAULT_SCAN_MODE,
        help=f"Pattern to scan for. Options: {SCAN_MODES}",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity level (default: INFO)",
    )
    args = parser.parse_args()

    # Initialize structured logging
    setup_logging(level=args.log_level)

    # Startup banner
    print(f"\n{'-' * 50}")
    print(f"  SwingsterV2 - Pattern Mode: {args.mode}")
    print(f"{'-' * 50}\n")
    sys.stdout.flush()

    # Run the full pipeline
    service = ScanService()
    result = service.run(mode=args.mode)

    # Display results
    _print_results(result)
