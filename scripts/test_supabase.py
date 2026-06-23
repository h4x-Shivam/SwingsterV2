import requests
import json
import os

supabase_url = "https://vlsiekhxmhflpfvckjwr.supabase.co"
anon_key = "sb_publishable_d5jFuMMWCKGOS00CK2HLdQ_iT-zpo2H"

headers = {
    "apikey": anon_key,
    "Authorization": f"Bearer {anon_key}",
    "Content-Type": "application/json"
}

# We don't have the user's password, but we can just check if the anon key is valid by making a public request
response = requests.get(f"{supabase_url}/auth/v1/settings", headers=headers)
print("Auth Settings Response:")
print(response.status_code)
print(response.text)
