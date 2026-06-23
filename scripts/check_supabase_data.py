import os
from supabase import create_client

supabase_url = "https://vlsiekhxmhflpfvckjwr.supabase.co"
anon_key = "sb_publishable_d5jFuMMWCKGOS00CK2HLdQ_iT-zpo2H"

supabase = create_client(supabase_url, anon_key)

try:
    response = supabase.table("scan_summary").select("*").order("timestamp", desc=True).limit(1).execute()
    print("Scan Summary:", response.data)
except Exception as e:
    print("Error:", e)
