"""
result_repository.py — Persistence layer for scan results.

Owns all scan-result database operations that were previously
inlined in main.py. Provides a clean interface for:
  • Saving scan summaries
  • Saving final picks
  • Querying latest results
"""

import logging
from typing import Optional

import psycopg2.extras

from fetcher.db_writer import get_connection

logger = logging.getLogger(__name__)


class ResultRepository:
    """
    Repository for persisting and querying scan results in PostgreSQL.

    Manages its own connection lifecycle — callers don't need to
    worry about connection handling.
    """

    def __init__(self, conn=None):
        self._conn = conn
        self._owns_conn = conn is None

    def _get_conn(self):
        if self._conn is None:
            self._conn = get_connection()
            self._owns_conn = True
        return self._conn

    def close(self):
        """Close the connection if we own it."""
        if self._owns_conn and self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    # ------------------------------------------------------------------
    # Scan Summary
    # ------------------------------------------------------------------

    def save_scan_summary(
        self,
        mode: str,
        total_scanned: int,
        pattern_match_count: int,
        rejected_by_rr: list[str],
    ) -> Optional[int]:
        """
        Insert a scan summary row and return its ID.

        Returns None if the insert fails (logged, never raises).
        """
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO scan_summary (mode, total_scanned, pattern_match_count, rejected_by_rr)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (mode, total_scanned, pattern_match_count, rejected_by_rr),
                )
                scan_summary_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(
                "Scan summary saved (ID: %d, mode: %s, scanned: %d, matches: %d)",
                scan_summary_id, mode, total_scanned, pattern_match_count,
            )
            return scan_summary_id
        except Exception as e:
            logger.error("Failed to save scan summary: %s", e)
            if conn:
                conn.rollback()
            return None

    # ------------------------------------------------------------------
    # Final Picks
    # ------------------------------------------------------------------

    def save_final_picks(
        self,
        scan_summary_id: int,
        picks: list[dict],
        mode: str,
    ) -> bool:
        """
        Bulk-insert final picks linked to a scan summary.

        Returns True on success, False on failure (logged, never raises).
        """
        if not picks:
            logger.warning("No picks to save")
            return False

        conn = self._get_conn()
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
                rows = [
                    (
                        scan_summary_id,
                        p.get("rank", 0),
                        p.get("symbol", ""),
                        p.get("pattern", ""),
                        p.get("scan_mode", mode),
                        p.get("composite_score", 0.0),
                        p.get("conviction", "MEDIUM"),
                        p.get("buy_point", 0.0),
                        p.get("stop_loss", 0.0),
                        p.get("target", 0.0),
                        p.get("rr_ratio", 0.0),
                        p.get("current_price", 0.0),
                        p.get("distance_from_buy_pct", 0.0),
                        p.get("signal_strength", 0.0),
                        p.get("volume_score", 0.0),
                        p.get("rr_score", 0.0),
                        p.get("stage2_score", 0.0),
                        p.get("rs_score", 0.0),
                        p.get("judge_verdict", ""),
                        p.get("flags", ""),
                        p.get("pledge_pct"),
                        p.get("sector"),
                        p.get("target2"),
                        p.get("pattern_age"),
                        p.get("trend"),
                    )
                    for p in picks
                ]
                psycopg2.extras.execute_values(cursor, insert_query, rows)
            conn.commit()
            logger.info(
                "Saved %d final picks to Supabase (scan_summary_id: %d)",
                len(picks), scan_summary_id,
            )
            return True
        except Exception as e:
            logger.error("Failed to save final picks: %s", e)
            conn.rollback()
            return False
