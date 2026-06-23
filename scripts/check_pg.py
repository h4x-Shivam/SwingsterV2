import os
import psycopg2

DATABASE_URL="postgresql://postgres.vlsiekhxmhflpfvckjwr:Sjisbest%40%2312@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"

try:
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, mode, timestamp FROM scan_summary ORDER BY timestamp DESC LIMIT 5;")
        rows = cursor.fetchall()
        print("Rows in scan_summary via psycopg2 (superuser):")
        for r in rows:
            print(r)
except Exception as e:
    print("Error:", e)
