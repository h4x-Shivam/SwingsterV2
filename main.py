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
    
    # We are no longer saving full candidates to JSON for judge agent.
    # The judge agent gets them directly in memory.
    import datetime
    from fetcher.db_writer import get_connection
    import psycopg2.extras
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Insert scan summary and get ID
            cursor.execute("""
                INSERT INTO scan_summary (mode, total_scanned, pattern_match_count, rejected_by_rr)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (args.mode, total_scanned, count_pattern, rejected_rr_list))
            scan_summary_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Dynamic metrics saved to Supabase (Scan Summary ID: {scan_summary_id})")
    except Exception as e:
        print(f"Failed to save scan summary to Supabase: {e}")
        scan_summary_id = None
        if conn:
            conn.rollback()

    sys.stdout.flush()
    
    try:
        from fetcher.nse_fetcher import fetch_pledge_pct
        print(f"\nFetching Pledge % for {len(candidates_dict)} candidates before judge...")
        sys.stdout.flush()
        for c in candidates_dict:
            try:
                c["pledge_pct"] = fetch_pledge_pct(c["symbol"], timeout=3)
            except Exception:
                c["pledge_pct"] = None
    except ImportError as ie:
        print(f"  [WARN] fetch_pledge_pct not available — skipping ({ie})")
        for c in candidates_dict:
            c["pledge_pct"] = None

    # Wire judge
    print(f"\nSending {len(candidates_dict)} candidates to Groq judge...")
    sys.stdout.flush()
    final_picks = run_judge(candidates_dict, mode=args.mode)
            
    if scan_summary_id is not None and final_picks:
        try:
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO final_picks (
                    scan_summary_id, rank, symbol, pattern, scan_mode, composite_score, 
                    conviction, buy_point, stop_loss, target, rr_ratio, current_price, 
                    distance_from_buy_pct, signal_strength, volume_score, rr_score, 
                    stage2_score, rs_score, judge_verdict, flags, pledge_pct, sector, 
                    target2, pattern_age, trend
                ) VALUES %s
                """
                # Prepare rows
                rows = []
                for p in final_picks:
                    rows.append((
                        scan_summary_id,
                        p.get('rank', 0),
                        p.get('symbol', ''),
                        p.get('pattern', ''),
                        p.get('scan_mode', args.mode),
                        p.get('composite_score', 0.0),
                        p.get('conviction', 'MEDIUM'),
                        p.get('buy_point', 0.0),
                        p.get('stop_loss', 0.0),
                        p.get('target', 0.0),
                        p.get('rr_ratio', 0.0),
                        p.get('current_price', 0.0),
                        p.get('distance_from_buy_pct', 0.0),
                        p.get('signal_strength', 0.0),
                        p.get('volume_score', 0.0),
                        p.get('rr_score', 0.0),
                        p.get('stage2_score', 0.0),
                        p.get('rs_score', 0.0),
                        p.get('judge_verdict', ''),
                        p.get('flags', ''),
                        p.get('pledge_pct', None),
                        p.get('sector', None),
                        p.get('target2', None),
                        p.get('pattern_age', None),
                        p.get('trend', None)
                    ))
                psycopg2.extras.execute_values(cursor, insert_query, rows)
            conn.commit()
            print(f"Final {len(final_picks)} picks saved to Supabase -> final_picks table.")
        except Exception as e:
            print(f"Failed to save final picks to Supabase: {e}")
            conn.rollback()
    
    if conn:
        conn.close()

    # Print judge results
    print(f"\n{'-' * 55}")
    print(f"  FINAL PICKS - {args.mode} SETUPS")
    print(f"{'-' * 55}")
    for r in final_picks:
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


