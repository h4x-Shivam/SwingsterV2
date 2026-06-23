import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
import time

DATABASE_URL = "postgresql://postgres.vlsiekhxmhflpfvckjwr:Sjisbest%40%2312@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"
SQLITE_DB = "data/ohlcv.db"

def migrate():
    print(f"Connecting to SQLite: {SQLITE_DB}")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    
    sqlite_cursor.execute("SELECT symbol, date, open, high, low, close, volume FROM ohlcv")
    rows = sqlite_cursor.fetchall()
    
    print(f"Loaded {len(rows)} rows from SQLite.")
    if not rows:
        print("SQLite db is empty.")
        return
        
    print(f"Connecting to Postgres: {DATABASE_URL.split('@')[1]}")
    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_cursor = pg_conn.cursor()
    
    # Create table if not exists (just in case)
    pg_cursor.execute("""
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
    """)
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol ON ohlcv (symbol);")
    pg_conn.commit()

    print("Inserting data into Postgres in batches...")
    
    query = """
    INSERT INTO ohlcv (symbol, date, open, high, low, close, volume) 
    VALUES %s
    ON CONFLICT (symbol, date) DO NOTHING;
    """
    
    batch_size = 50000
    t0 = time.time()
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        execute_values(pg_cursor, query, batch)
        pg_conn.commit()
        print(f"Inserted {i+len(batch)} / {len(rows)} rows...")
        
    pg_conn.close()
    sqlite_conn.close()
    
    t1 = time.time()
    print(f"Migration complete in {t1-t0:.1f} seconds!")

if __name__ == "__main__":
    migrate()
