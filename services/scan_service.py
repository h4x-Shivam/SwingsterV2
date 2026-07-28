"""
scan_service.py — Top-level orchestrator for the SwingsterV2 scan pipeline.

Owns the full flow:
  1. Run the scan engine
  2. Fetch supplemental data (pledge %)
  3. Run the auto-judge
  4. Persist results to the database

Callers (main.py, api_server.py) become thin wrappers that only
handle CLI args / HTTP and delegate everything here.
"""

import logging
import sys
from dataclasses import dataclass, field
from typing import Optional

from scanner.engine import scan_all
from judge.judge_agent import run_judge
from services.result_repository import ResultRepository

logger = logging.getLogger(__name__)


@dataclass
class ScanRunResult:
    """Immutable result of a complete scan pipeline run."""

    mode: str
    total_scanned: int
    pattern_match_count: int
    rejected_rr_list: list[str]
    final_picks: list[dict] = field(default_factory=list)
    scan_summary_id: Optional[int] = None


class ScanService:
    """
    Orchestrates a complete scan run: scan → enrich → judge → persist.

    Usage::

        service = ScanService()
        result = service.run(mode="VCP")
    """

    def run(self, mode: str) -> ScanRunResult:
        """
        Execute the full pipeline and return the result.

        Never raises — errors in individual stages are logged and
        the pipeline continues with degraded data where possible.
        """
        # 1. Scan
        candidates, total_scanned, count_pattern, rejected_rr_list = scan_all(
            mode=mode
        )
        candidates_dict = [vars(c) for c in candidates]

        # 2. Enrich with pledge data
        self._enrich_pledge_data(candidates_dict)

        # 3. Judge
        logger.info("Evaluating %d candidates with Auto-Judge...", len(candidates_dict))
        sys.stdout.flush()
        final_picks = run_judge(candidates_dict, mode=mode)

        # 4. Persist
        repo = ResultRepository()
        try:
            scan_summary_id = repo.save_scan_summary(
                mode=mode,
                total_scanned=total_scanned,
                pattern_match_count=count_pattern,
                rejected_by_rr=rejected_rr_list,
            )

            if scan_summary_id is not None and final_picks:
                repo.save_final_picks(scan_summary_id, final_picks, mode)
        finally:
            repo.close()

        return ScanRunResult(
            mode=mode,
            total_scanned=total_scanned,
            pattern_match_count=count_pattern,
            rejected_rr_list=rejected_rr_list,
            final_picks=final_picks,
            scan_summary_id=scan_summary_id if scan_summary_id else None,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _enrich_pledge_data(candidates: list[dict]) -> None:
        """Fetch promoter pledge % for each candidate from NSE."""
        try:
            from fetcher.nse_fetcher import fetch_pledge_pct

            logger.info(
                "Fetching Pledge %% for %d candidates before judge...",
                len(candidates),
            )
            sys.stdout.flush()
            for c in candidates:
                try:
                    c["pledge_pct"] = fetch_pledge_pct(c["symbol"], timeout=3)
                except Exception:
                    c["pledge_pct"] = None
        except ImportError as ie:
            logger.warning("fetch_pledge_pct not available — skipping (%s)", ie)
            for c in candidates:
                c["pledge_pct"] = None
