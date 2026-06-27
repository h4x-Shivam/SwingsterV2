"""
db_writer.py — PostgreSQL persistence layer for OHLCV data.

Handles:
  • Creating / migrating the ohlcv table and indexes.
  • Upserting rows via INSERT ON CONFLICT (safe for delta fetches).
  • Reading OHLCV data back for a given symbol.
"""

import os
import psycopg2
from psycopg2.extras import execute_values
from typing import Optional

from config import DATABASE_URL

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
    volume  BIGINT  NOT NULL,
    PRIMARY KEY (symbol, date)
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol ON ohlcv (symbol);
"""


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def get_connection(db_url: str = DATABASE_URL):
    """
    Open the PostgreSQL database and return a connection.
    """
    if not db_url:
        raise ValueError("DATABASE_URL is not set. Please configure it in .env.")
    return psycopg2.connect(db_url)


def init_db(db_url: str = DATABASE_URL) -> None:
    """
    Create the ohlcv table and index if they don't already exist.
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(_CREATE_TABLE)
            cursor.execute(_CREATE_INDEX)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def write_ohlcv(
    rows: list[tuple[str, str, float, float, float, float, int]],
    db_url: str = DATABASE_URL,
    conn = None
) -> int:
    """
    Upsert a batch of OHLCV rows into the database.

    Each row is a tuple of (symbol, date, open, high, low, close, volume).
    Uses INSERT ON CONFLICT DO UPDATE so delta fetches never create duplicate rows.

    Returns the number of rows written.
    """
    if not rows:
        return 0

    should_close = False
    if conn is None:
        conn = get_connection(db_url)
        should_close = True
        
    try:
        with conn.cursor() as cursor:
            query = """
            INSERT INTO ohlcv (symbol, date, open, high, low, close, volume) 
            VALUES %s
            ON CONFLICT (symbol, date) DO UPDATE SET 
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
            """
            execute_values(cursor, query, rows)
        conn.commit()
        return len(rows)
    finally:
        if should_close:
            conn.close()


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def read_ohlcv(
    symbol: str,
    db_url: str = DATABASE_URL,
    conn = None,
) -> list[tuple[str, float, float, float, float, int]]:
    """
    Read all OHLCV rows for a single symbol, ordered by date ascending.

    Returns a list of (date, open, high, low, close, volume) tuples.
    """
    should_close = False
    if conn is None:
        conn = get_connection(db_url)
        should_close = True
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT date, open, high, low, close, volume "
                "FROM ohlcv WHERE symbol = %s ORDER BY date ASC;",
                (symbol,),
            )
            return cursor.fetchall()
    finally:
        if should_close:
            conn.close()


def read_ohlcv_batch(
    symbols: list[str],
    db_url: str = DATABASE_URL,
    conn = None,
) -> dict[str, list[tuple[str, float, float, float, float, int]]]:
    """
    Read all OHLCV rows for a batch of symbols, ordered by symbol and date ascending.
    
    Returns a dictionary mapping each symbol to its list of (date, open, high, low, close, volume) tuples.
    """
    if not symbols:
        return {}

    should_close = False
    if conn is None:
        conn = get_connection(db_url)
        should_close = True
        
    result = {sym: [] for sym in symbols}
    
    chunk_size = 500
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i+chunk_size]
        placeholders = ', '.join(['%s'] * len(chunk))
        
        max_retries = 3
        retries = max_retries
        while retries > 0:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT symbol, date, open, high, low, close, volume "
                        f"FROM ohlcv WHERE symbol IN ({placeholders}) "
                        "ORDER BY symbol, date ASC;",
                        chunk
                    )
                    rows = cursor.fetchall()
                    conn.commit()
                    for row in rows:
                        sym = row[0]
                        if sym in result:
                            result[sym].append((row[1], row[2], row[3], row[4], row[5], row[6]))
                break
            except psycopg2.OperationalError as e:
                conn.rollback()
                print(f"[{os.getpid()}] Database OperationalError on batch {i}: {e}. Retrying {retries-1} more times...")
                retries -= 1
                import time
                time.sleep(2)
                if retries == 0:
                    raise e
                    
    if should_close:
        conn.close()
    return result


def get_all_symbols(db_url: str = DATABASE_URL) -> list[str]:
    """
    Return a sorted list of all distinct symbols stored in the database.
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT symbol FROM ohlcv ORDER BY symbol;")
            return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_eligible_symbols(db_url: str = DATABASE_URL) -> list[str]:
    """
    Get all eligible symbols based on four database-level filters:
    1. Minimum candle count >= 60
    2. Minimum average volume >= 50,000
    3. Latest close price >= 20.0
    4. Data freshness (last trade date within 7 days of UTC 'now')
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT symbol
                FROM ohlcv
                GROUP BY symbol
                HAVING COUNT(date) >= 60
                   AND AVG(volume) >= 50000
                   AND (SELECT close FROM ohlcv o2 WHERE o2.symbol = ohlcv.symbol ORDER BY o2.date DESC LIMIT 1) >= 20.0
                   AND MAX(date) >= TO_CHAR(NOW() - INTERVAL '7 days', 'YYYY-MM-DD')
                ORDER BY symbol;
                """
            )
            return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_prefilter_counts(db_url: str = DATABASE_URL) -> dict:
    """
    Returns a dictionary of counts for the pre-filter summary log.
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
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
            
            cursor.execute("SELECT TO_CHAR(NOW() - INTERVAL '7 days', 'YYYY-MM-DD');")
            threshold_dt = cursor.fetchone()[0]
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


def get_row_count(db_url: str = DATABASE_URL) -> int:
    """
    Return the total number of OHLCV rows in the database.
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ohlcv;")
            return cursor.fetchone()[0]
    finally:
        conn.close()


def get_latest_date(symbol: str, db_url: str = DATABASE_URL) -> Optional[str]:
    """
    Return the most recent date string stored for a given symbol, or None.
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT MAX(date) FROM ohlcv WHERE symbol = %s;",
                (symbol,),
            )
            result = cursor.fetchone()
            return result[0] if result else None
    finally:
        conn.close()
