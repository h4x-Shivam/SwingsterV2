"""
db_writer.py — SQLite persistence layer for OHLCV data.

Handles:
  • Creating / migrating the ohlcv table and indexes.
  • Upserting rows via INSERT OR REPLACE (safe for delta fetches).
  • Reading OHLCV data back for a given symbol.
  • WAL journal mode for concurrent thread safety.
"""

import sqlite3
from typing import Optional

from config import DB_PATH


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS ohlcv (
    symbol  TEXT    NOT NULL,
    date    TEXT    NOT NULL,
    open    REAL    NOT NULL,
    high    REAL    NOT NULL,
    low     REAL    NOT NULL,
    close   REAL    NOT NULL,
    volume  INTEGER NOT NULL,
    PRIMARY KEY (symbol, date)
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol ON ohlcv (symbol);
"""


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Open (or create) the SQLite database and return a connection.

    Enables WAL journal mode for safe concurrent reads from scanner threads
    while the fetcher is writing.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """
    Create the ohlcv table and index if they don't already exist.

    Safe to call multiple times — uses IF NOT EXISTS.
    """
    conn = get_connection(db_path)
    try:
        conn.execute(_CREATE_TABLE)
        conn.execute(_CREATE_INDEX)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def write_ohlcv(
    rows: list[tuple[str, str, float, float, float, float, int]],
    db_path: str = DB_PATH,
) -> int:
    """
    Upsert a batch of OHLCV rows into the database.

    Each row is a tuple of (symbol, date, open, high, low, close, volume).
    Uses INSERT OR REPLACE so delta fetches never create duplicate rows.

    Returns the number of rows written.
    """
    if not rows:
        return 0

    conn = get_connection(db_path)
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO ohlcv (symbol, date, open, high, low, close, volume) "
            "VALUES (?, ?, ?, ?, ?, ?, ?);",
            rows,
        )
        conn.commit()
        return len(rows)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def read_ohlcv(
    symbol: str,
    db_path: str = DB_PATH,
    conn: Optional[sqlite3.Connection] = None,
) -> list[tuple[str, float, float, float, float, int]]:
    """
    Read all OHLCV rows for a single symbol, ordered by date ascending.

    Returns a list of (date, open, high, low, close, volume) tuples.
    """
    should_close = False
    if conn is None:
        conn = get_connection(db_path)
        should_close = True
    try:
        cursor = conn.execute(
            "SELECT date, open, high, low, close, volume "
            "FROM ohlcv WHERE symbol = ? ORDER BY date ASC;",
            (symbol,),
        )
        return cursor.fetchall()
    finally:
        if should_close:
            conn.close()


def get_all_symbols(db_path: str = DB_PATH) -> list[str]:
    """
    Return a sorted list of all distinct symbols stored in the database.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT DISTINCT symbol FROM ohlcv ORDER BY symbol;")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_eligible_symbols(db_path: str = DB_PATH) -> list[str]:
    """
    Get all eligible symbols based on four database-level filters:
    1. Minimum candle count >= 60
    2. Minimum average volume >= 50,000
    3. Latest close price >= 20.0
    4. Data freshness (last trade date within 7 days of UTC 'now')
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT symbol
            FROM ohlcv
            GROUP BY symbol
            HAVING COUNT(date) >= 60
               AND AVG(volume) >= 50000
               AND (SELECT close FROM ohlcv o2 WHERE o2.symbol = ohlcv.symbol ORDER BY o2.date DESC LIMIT 1) >= 20.0
               AND MAX(date) >= date('now', '-7 days')
            ORDER BY symbol;
            """
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_prefilter_counts(db_path: str = DB_PATH) -> dict:
    """
    Returns a dictionary of counts for the pre-filter summary log.
    We classify the skipped symbols hierarchically to ensure:
    total = eligible + skipped (short + illiquid + penny + stale)
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT 
                symbol, 
                COUNT(date) as cnt, 
                AVG(volume) as avg_vol, 
                MAX(date) as max_dt,
                (SELECT close FROM ohlcv o2 WHERE o2.symbol = ohlcv.symbol ORDER BY o2.date DESC LIMIT 1) as lat_close
            FROM ohlcv
            GROUP BY symbol;
            """
        )
        rows = cursor.fetchall()
        threshold_dt = conn.execute("SELECT date('now', '-7 days');").fetchone()[0]
    finally:
        conn.close()
        
    counts = {
        "total": len(rows),
        "eligible": 0,
        "short": 0,
        "illiquid": 0,
        "penny": 0,
        "stale": 0
    }
    
    for row in rows:
        symbol, cnt, avg_vol, max_dt, lat_close = row
        lat_close = lat_close if lat_close is not None else 0.0
        
        if cnt < 60:
            counts["short"] += 1
        elif avg_vol < 50000:
            counts["illiquid"] += 1
        elif lat_close < 20.0:
            counts["penny"] += 1
        elif max_dt < threshold_dt:
            counts["stale"] += 1
        else:
            counts["eligible"] += 1
            
    return counts



def get_row_count(db_path: str = DB_PATH) -> int:
    """
    Return the total number of OHLCV rows in the database.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM ohlcv;")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def get_latest_date(symbol: str, db_path: str = DB_PATH) -> Optional[str]:
    """
    Return the most recent date string stored for a given symbol, or None.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT MAX(date) FROM ohlcv WHERE symbol = ?;",
            (symbol,),
        )
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()
