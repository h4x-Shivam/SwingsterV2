import requests
import time

def test_nse():
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE",
        "Connection": "keep-alive"
    }
    s.headers.update(headers)
    
    try:
        r0 = s.get("https://www.nseindia.com", timeout=10)
        print("Main page status:", r0.status_code)
        time.sleep(1)
        
        r1 = s.get("https://www.nseindia.com/api/quote-equity?symbol=RELIANCE&section=trade_info", timeout=10)
        print("Trade info status:", r1.status_code)
        print(r1.text[:200])
        
        if r1.status_code == 200:
            data = r1.json()
            print("Delivery:", data.get("tradeInfo", {}).get("deliveryToTradedQuantity"))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_nse()
