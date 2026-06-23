import psycopg2
DATABASE_URL="postgresql://postgres.vlsiekhxmhflpfvckjwr:Sjisbest%40%2312@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"
try:
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM ohlcv;")
        rows = cursor.fetchone()
        print(f"Total rows in ohlcv: {rows[0]}")
except Exception as e:
    print("Error:", e)
