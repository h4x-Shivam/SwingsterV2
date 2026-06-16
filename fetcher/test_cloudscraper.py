import cloudscraper

def test_nse_cloudscraper():
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    try:
        r0 = scraper.get("https://www.nseindia.com", timeout=10)
        print("Main page status:", r0.status_code)
        
        r1 = scraper.get("https://www.nseindia.com/api/quote-equity?symbol=RELIANCE&section=trade_info", timeout=10)
        print("Trade info status:", r1.status_code)
        
        if r1.status_code == 200:
            data = r1.json()
            print("Delivery:", data.get("tradeInfo", {}).get("deliveryToTradedQuantity"))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_nse_cloudscraper()
