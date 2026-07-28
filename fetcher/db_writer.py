"""
db_writer.py — PostgreSQL persistence layer for OHLCV data.

Handles:
  • Connection pooling via ThreadedConnectionPool.
  • Creating / migrating the ohlcv table and indexes.
  • Upserting rows via INSERT ON CONFLICT (safe for delta fetches).
  • Reading OHLCV data back for a given symbol.
"""

import logging
import os
import time
from contextlib import contextmanager
from typing import Optional

import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool

from config import DATABASE_URL

logger = logging.getLogger(__name__)

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
# Connection Pool
# ---------------------------------------------------------------------------

_pool: Optional[ThreadedConnectionPool] = None


def _get_pool(db_url: str = DATABASE_URL) -> ThreadedConnectionPool:
    """
    Lazily initialize and return the global connection pool.

    minconn=1  — one connection kept warm at all times.
    maxconn=10 — enough for ProcessPool workers + main thread.
    """
    global _pool
    if _pool is None or _pool.closed:
        if not db_url:
            raise ValueError("DATABASE_URL is not set. Please configure it in .env.")
        _pool = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=db_url)
        logger.debug("Connection pool created (min=1, max=10)")
    return _pool


def get_connection(db_url: str = DATABASE_URL):
    """
    Get a connection from the pool.

    For backward compatibility, callers that manage their own connection
    lifecycle can still use this directly. Prefer ``db_connection()``
    context manager for new code.
    """
    return _get_pool(db_url).getconn()


def release_connection(conn) -> None:
    """Return a connection to the pool."""
    try:
        pool = _get_pool()
        pool.putconn(conn)
    except Exception:
        # If pool is closed or conn is bad, just try to close it
        try:
            conn.close()
        except Exception:
            pass


@contextmanager
def db_connection(db_url: str = DATABASE_URL):
    """
    Context manager for safe connection handling.

    Automatically returns the connection to the pool on exit.
    Usage::

        with db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ...")
    """
    conn = get_connection(db_url)
    try:
        yield conn
    finally:
        release_connection(conn)


def close_pool() -> None:
    """
    Close all connections in the pool.

    Call this at application shutdown for clean teardown.
    """
    global _pool
    if _pool is not None and not _pool.closed:
        _pool.closeall()
        logger.debug("Connection pool closed")
    _pool = None


# ---------------------------------------------------------------------------
# Schema initialization
# ---------------------------------------------------------------------------

def init_db(db_url: str = DATABASE_URL) -> None:
    """
    Create the ohlcv table and index if they don't already exist.
    """
    with db_connection(db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(_CREATE_TABLE)
            cursor.execute(_CREATE_INDEX)
        conn.commit()


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def write_ohlcv(
    rows: list[tuple[str, str, float, float, float, float, int]],
    db_url: str = DATABASE_URL,
    conn=None,
) -> int:
    """
    Upsert a batch of OHLCV rows into the database.

    Each row is a tuple of (symbol, date, open, high, low, close, volume).
    Uses INSERT ON CONFLICT DO UPDATE so delta fetches never create duplicate rows.

    Returns the number of rows written.
    """
    if not rows:
        return 0

    # Support callers that pass their own connection (e.g. fetch_all batching)
    owns_conn = conn is None
    if owns_conn:
        conn = get_connection(db_url)

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
        if owns_conn:
            release_connection(conn)


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def read_ohlcv(
    symbol: str,
    db_url: str = DATABASE_URL,
    conn=None,
) -> list[tuple[str, float, float, float, float, int]]:
    """
    Read all OHLCV rows for a single symbol, ordered by date ascending.

    Returns a list of (date, open, high, low, close, volume) tuples.
    """
    owns_conn = conn is None
    if owns_conn:
        conn = get_connection(db_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT date, open, high, low, close, volume "
                "FROM ohlcv WHERE symbol = %s ORDER BY date ASC;",
                (symbol,),
            )
            return cursor.fetchall()
    finally:
        if owns_conn:
            release_connection(conn)


def read_ohlcv_batch(
    symbols: list[str],
    db_url: str = DATABASE_URL,
    conn=None,
) -> dict[str, list[tuple[str, float, float, float, float, int]]]:
    """
    Read all OHLCV rows for a batch of symbols, ordered by symbol and date ascending.
    
    Returns a dictionary mapping each symbol to its list of (date, open, high, low, close, volume) tuples.
    """
    if not symbols:
        return {}

    owns_conn = conn is None
    if owns_conn:
        conn = get_connection(db_url)
        
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
                logger.warning(
                    "[%d] Database OperationalError on batch %d: %s. Retrying %d more times...",
                    os.getpid(), i, e, retries - 1,
                )
                retries -= 1
                time.sleep(2)
                if retries == 0:
                    raise
                    
    if owns_conn:
        release_connection(conn)
    return result


def get_all_symbols(db_url: str = DATABASE_URL) -> list[str]:
    """
    Return a sorted list of all distinct symbols stored in the database.
    """
    with db_connection(db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT symbol FROM ohlcv ORDER BY symbol;")
            return [row[0] for row in cursor.fetchall()]


def get_eligible_symbols(db_url: str = DATABASE_URL) -> list[str]:
    """
    Get all eligible symbols based on four database-level filters:
    1. Minimum candle count >= 60
    2. Minimum average volume >= 50,000
    3. Latest close price >= 20.0
    4. Data freshness (last trade date within 7 days of UTC 'now')
    """
    with db_connection(db_url) as conn:
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


def get_prefilter_counts(db_url: str = DATABASE_URL) -> dict:
    """
    Returns a dictionary of counts for the pre-filter summary log.
    """
    with db_connection(db_url) as conn:
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
    with db_connection(db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ohlcv;")
            return cursor.fetchone()[0]


def get_latest_date(symbol: str, db_url: str = DATABASE_URL) -> Optional[str]:
    """
    Return the most recent date string stored for a given symbol, or None.
    """
    with db_connection(db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT MAX(date) FROM ohlcv WHERE symbol = %s;",
                (symbol,),
            )
            result = cursor.fetchone()
            return result[0] if result else None
