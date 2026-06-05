import requests
import time
import yfinance as yf

def _nse_fetch(symbol: str) -> dict:
    symbol = symbol.upper().strip()
    try:
        from jugaad_data.nse import NSELive
        nse   = NSELive()
        quote = nse.stock_quote(symbol)
        trade = nse.trade_info(symbol)
        return _parse_nse_response(symbol, quote, trade, source="jugaad-data")
    except ImportError:
        pass
    except Exception as e:
        print(f"[NSE/jugaad] {symbol}: {e}")
    return _nse_direct(symbol)


def _nse_direct(symbol: str) -> dict:
    BASE = "https://www.nseindia.com"
    headers = {
        "Host":             "www.nseindia.com",
        "Referer":          f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent":       (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        ),
        "Accept":           "*/*",
        "Accept-Language":  "en-GB,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding":  "gzip, deflate",
        "Cache-Control":    "no-cache",
        "Connection":       "keep-alive",
        "sec-fetch-dest":   "empty",
        "sec-fetch-mode":   "cors",
        "sec-fetch-site":   "same-origin",
    }
    s = requests.Session()
    s.headers.update(headers)
    try:
        s.get(f"{BASE}/get-quotes/equity?symbol={symbol}", timeout=12)
        time.sleep(0.5)
        r1    = s.get(f"{BASE}/api/quote-equity", params={"symbol": symbol}, timeout=14)
        quote = r1.json() if r1.status_code == 200 else {}
        r2    = s.get(f"{BASE}/api/quote-equity",
                      params={"symbol": symbol, "section": "trade_info"}, timeout=14)
        trade = r2.json() if r2.status_code == 200 else {}
    except Exception as e:
        return {"ok": False, "_error": str(e)}
    if not quote:
        return {"ok": False, "_error": "NSE returned empty response"}
    return _parse_nse_response(symbol, quote, trade, source="NSE direct")


def _safe_get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return default
    return d if d is not None else default


def _parse_nse_response(symbol: str, quote: dict, trade: dict, source: str = "NSE") -> dict:
    pi   = quote.get("priceInfo", {})
    meta = quote.get("metadata", {})
    si   = quote.get("securityInfo", {})
    ii   = quote.get("industryInfo", {})
    ti   = _safe_get(trade, "tradeInfo") or {}

    cur  = _safe_get(pi, "lastPrice") or _safe_get(pi, "close")
    w52h = _safe_get(pi, "weekHighLow", "max")
    w52l = _safe_get(pi, "weekHighLow", "min")

    position = "N/A"
    if cur and w52l and w52h and (w52h - w52l) > 0:
        pct      = round((cur - w52l) / (w52h - w52l) * 100, 1)
        position = f"{pct}% of 52-week range"

    return {
        "ok":            True,
        "data_source":   source,
        "symbol":        symbol,
        "company_name":  meta.get("companyName", symbol),
        "isin":          meta.get("isin", ""),
        "series":        meta.get("series", "EQ"),
        "listing_date":  meta.get("listingDate", ""),
        "face_value":    si.get("faceValue"),
        "sector":        ii.get("sector", ""),
        "industry":      ii.get("industry", ""),
        "current_price": cur,
        "prev_close":    _safe_get(pi, "previousClose"),
        "day_high":      _safe_get(pi, "intraDayHighLow", "max"),
        "day_low":       _safe_get(pi, "intraDayHighLow", "min"),
        "week52_high":   w52h,
        "week52_low":    w52l,
        "vwap":          _safe_get(pi, "vwap"),
        "change":        _safe_get(pi, "change", default=0),
        "pchange":       _safe_get(pi, "pChange", default=0),
        "momentum":      position,
        "total_vol":     _safe_get(ti, "totalTradedVolume"),
        "total_val":     _safe_get(ti, "totalTradedValue"),
        "delivery_qty":  _safe_get(ti, "deliveryQuantity"),
        "delivery_pct":  _safe_get(ti, "deliveryToTradedQuantity"),
    }


def _yf_fetch(ticker_ns: str) -> dict:
    try:
        stk  = yf.Ticker(ticker_ns)
        info = stk.info
        hist = stk.history(period="6mo")
        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )
        prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
        return {
            "ok":               True,
            "current_price":    price,
            "prev_close":       prev,
            "market_cap":       info.get("marketCap"),
            "trailing_pe":      info.get("trailingPE"),
            "forward_pe":       info.get("forwardPE"),
            "trailing_eps":     info.get("trailingEps"),
            "forward_eps":      info.get("forwardEps"),
            "pb_ratio":         info.get("priceToBook"),
            "profit_margins":   info.get("profitMargins"),
            "gross_margins":    info.get("grossMargins"),
            "ebitda_margins":   info.get("ebitdaMargins"),
            "revenue_growth":   info.get("revenueGrowth") or info.get("earningsGrowth"),
            "total_revenue":    info.get("totalRevenue"),
            "net_income":       info.get("netIncomeToCommon"),
            "free_cash_flow":   info.get("freeCashflow"),
            "debt_to_equity":   info.get("debtToEquity"),
            "current_ratio":    info.get("currentRatio"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
            "dividend_yield":   info.get("dividendYield"),
            "beta":             info.get("beta"),
            "recommendation":   info.get("recommendationKey"),
            "target_price":     info.get("targetMeanPrice"),
            "n_analysts":       info.get("numberOfAnalystOpinions"),
            "long_name":        info.get("longName"),
            "short_name":       info.get("shortName"),
            "sector":           info.get("sector", ""),
            "industry":         info.get("industry", ""),
            "hist":             hist,
            "_raw_info":        info,
        }
    except Exception as e:
        return {"ok": False, "_yf_error": str(e), "hist": None}


def _jugaad_extras(symbol: str) -> dict:
    try:
        from jugaad_data.nse import live_stock_data
        live = live_stock_data(symbol)
        return {
            "jugaad_pe":        live.get("pe"),
            "jugaad_pb":        live.get("pb"),
            "jugaad_div_yield": live.get("dividendYield"),
        }
    except Exception:
        return {}
