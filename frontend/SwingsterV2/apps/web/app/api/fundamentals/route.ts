import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

// Shareholding cache: symbol -> { data, expiry }
const shareholdingCache = new Map<string, { data: any, expiry: number }>();
const CACHE_TTL = 60 * 60 * 24; // 24 hours in seconds

const NSE_HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "Accept": "application/json",
  "Accept-Language": "en-US,en;q=0.9",
  "Referer": "https://www.nseindia.com/",
  "Connection": "keep-alive"
};

function cleanSymbol(symbol: string) {
  return symbol.replace(/\.NS$/i, "").replace(/\.NSE$/i, "").toUpperCase().trim();
}

async function fetchPythonFallback(symbol: string) {
  return new Promise<any>((resolve) => {
    const backendRoot = path.resolve(process.cwd(), "../../../../");
    const script = `
import json, sys
sys.path.append('.')
try:
    from fetcher.nse_fetcher import fetch_fundamentals_with_fallback
    print(json.dumps(fetch_fundamentals_with_fallback('${symbol}')))
except Exception as e:
    print(json.dumps({}))
`;
    const child = spawn("python", ["-c", script], { cwd: backendRoot });
    let stdout = "";
    child.stdout.on("data", (data) => { stdout += data.toString(); });
    child.on("close", () => {
      try {
        resolve(JSON.parse(stdout));
      } catch {
        resolve({});
      }
    });
    child.on("error", () => {
      resolve({});
    });
  });
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  let symbol = searchParams.get("symbol");
  
  if (!symbol) {
    return NextResponse.json({ error: "Symbol required" }, { status: 400 });
  }

  symbol = cleanSymbol(symbol);

  try {
    // 1. Establish session cookies
    const sessionRes = await fetch("https://www.nseindia.com", { headers: NSE_HEADERS });
    const cookies = sessionRes.headers.get("set-cookie");
    
    if (!cookies) {
      throw new Error("No cookies returned from NSE");
    }

    const authHeaders = { ...NSE_HEADERS, Cookie: cookies };

    // 2. Fetch Quote Equity
    const quoteRes = await fetch(
      `https://www.nseindia.com/api/quote-equity?symbol=${encodeURIComponent(symbol)}`,
      { headers: authHeaders }
    );
    
    if (!quoteRes.ok) throw new Error("Quote equity fetch failed");
    const quote = await quoteRes.json();

    // 3. Fetch Trade Info for Delivery Vol
    const tradeRes = await fetch(
      `https://www.nseindia.com/api/quote-equity?symbol=${encodeURIComponent(symbol)}&section=trade_info`,
      { headers: authHeaders }
    );
    
    if (!tradeRes.ok) throw new Error("Trade info fetch failed");
    const trade = await tradeRes.json();

    // 4. Fetch Shareholding (with cache)
    let shData = null;
    const now = Date.now();
    const cached = shareholdingCache.get(symbol);
    
    if (cached && cached.expiry > now) {
      shData = cached.data;
    } else {
      const shRes = await fetch(
        `https://www.nseindia.com/api/shareholding-patterns?symbol=${encodeURIComponent(symbol)}`,
        { headers: authHeaders }
      );
      if (shRes.ok) {
        shData = await shRes.json();
        shareholdingCache.set(symbol, {
          data: shData,
          expiry: now + (CACHE_TTL * 1000)
        });
      }
    }

    // Process data
    let market_cap = null;
    let pe_ratio = null;
    let delivery_vol_pct = null;
    let promoter_holding_pct = null;
    let fii_holding_pct = null;
    let pledge_pct = null;

    try { market_cap = quote?.priceInfo?.totalMarketCap || quote?.metadata?.pdSymbolPe?.symbolMarketCap; } catch {}
    try { pe_ratio = quote?.metadata?.pdSymbolPe?.symbolPe; } catch {}
    try { delivery_vol_pct = trade?.tradeInfo?.deliveryToTradedQuantity; } catch {}

    if (shData && shData.data && shData.data.length > 0) {
      const latest = shData.data[0];
      promoter_holding_pct = latest.promoterAndPromoterGroup;
      fii_holding_pct = latest.foreignInstInvestors;
      pledge_pct = latest.pledgedEncumbered;
    }

    // If primary fetch fails to get market cap, trigger fallback
    if (!market_cap) {
      throw new Error("Missing market cap, triggering fallback");
    }

    return NextResponse.json({
      market_cap,
      pe_ratio,
      roe: null, // Usually not available in standard quote
      debt_to_equity: null, // Usually not available in standard quote
      delivery_vol_pct,
      promoter_holding_pct,
      fii_holding_pct,
      pledge_pct
    });

  } catch (error) {
    console.error(`[NSE Node Fetch Error] ${symbol}:`, error);
    // Trigger Tier 2/3 Fallback
    const fallbackData = await fetchPythonFallback(symbol);
    return NextResponse.json(fallbackData);
  }
}
