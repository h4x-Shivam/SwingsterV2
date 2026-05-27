"""
Centralized configuration for SwingsterV2.

Every path, URL, threshold, and tunable constant lives here.
No other module should hardcode any of these values — always import from config.
"""

import os

# ---------------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

SYMBOLS_CSV = os.path.join(DATA_DIR, "symbols.csv")
DB_PATH = os.path.join(DATA_DIR, "ohlcv.db")
RESULTS_JSON = os.path.join(DATA_DIR, "results.json")

# ---------------------------------------------------------------------------
# Yahoo Finance API
# ---------------------------------------------------------------------------

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

# ---------------------------------------------------------------------------
# Fetcher Settings
# ---------------------------------------------------------------------------

FETCH_PERIOD = "1y"            # first-time full fetch (range param)
FETCH_DELTA_PERIOD = "5d"      # nightly delta fetch
FETCH_INTERVAL = "1d"          # daily candles

SEMAPHORE_LIMIT = 40           # max concurrent aiohttp requests (Windows safe)
RETRY_ATTEMPTS = 3             # retries per ticker on failure
RETRY_DELAY = 2                # base delay in seconds (exponential backoff)

# ---------------------------------------------------------------------------
# Symbol Filtering
# ---------------------------------------------------------------------------

MIN_PRICE = 20.0               # skip tickers whose close < this
VALID_SERIES = {"EQ", "BE"}    # keep only these SERIES values from symbols.csv
YAHOO_SUFFIX = ".NS"           # appended to NSE symbols for Yahoo Finance

# ---------------------------------------------------------------------------
# Scanner / Agent Settings
# ---------------------------------------------------------------------------

NUM_AGENTS = 5                 # parallel ThreadPoolExecutor workers
import os
WORKER_COUNT = max(1, min(NUM_AGENTS, (os.cpu_count() or 2) - 1))

# Pattern scan modes
SCAN_MODES = ["VCP", "FLAG_POLE", "CUP_HANDLE", "BREAKOUT", "ALL"]
SCAN_MODE  = "VCP"   # default mode — change per run

MIN_SIGNAL_SCORE = 55          # minimum pattern signal score to be a candidate
TOP_N_CANDIDATES = 30          # sent to the Groq judge
TOP_N_FINAL = 10               # final ranked output

# Groq API — Judge Agent
GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")
GROQ_MODEL           = "llama-3.3-70b-versatile"
GROQ_MODEL_FALLBACK  = "llama-3.1-8b-instant"
GROQ_MAX_TOKENS      = 2000
GROQ_TIMEOUT         = 60     # seconds


# ---------------------------------------------------------------------------
# Scoring Weights  (must sum to 1.0)
# ---------------------------------------------------------------------------

WEIGHT_SIGNAL = 0.40
WEIGHT_VOLUME = 0.25
WEIGHT_RR = 0.20
WEIGHT_STAGE2 = 0.10
WEIGHT_RS = 0.05

# ---------------------------------------------------------------------------
# Stage 2 & Liquidity Filters
# ---------------------------------------------------------------------------

STAGE2_MIN_SCORE = 60          # minimum stage2_score to proceed with scanning
MIN_AVG_VOLUME = 50_000        # avg daily volume below this → illiquid, skip

# ---------------------------------------------------------------------------
# HTTP Headers (for Yahoo Finance requests)
# ---------------------------------------------------------------------------

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
