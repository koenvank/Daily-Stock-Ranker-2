import os

# Lookback window in hours
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "24"))

# Base URLs
PUSHSHIFT_BASE_URL = os.getenv("PUSHSHIFT_BASE_URL", "https://api.pushshift.io/reddit/search")
STOCKTWITS_BASE_URL = os.getenv("STOCKTWITS_BASE_URL", "https://api.stocktwits.com/api/2")

# Subreddits to scan
SUBREDDITS = [
    "stocks",
    "investing",
    "stockmarket",
    "wallstreetbets",
    "options",
]

# Weighting factors
SOURCE_WEIGHTS = {
    "pushshift": 1.0,
    "stocktwits": 0.8,
}

SUBREDDIT_WEIGHTS = {
    "stocks": 1.0,
    "investing": 1.0,
    "stockmarket": 0.9,
    "wallstreetbets": 0.8,
    "options": 0.9,
}

# Collection limits
PUSHSHIFT_SIZE = 200
STOCKTWITS_TRENDING_LIMIT = 15
STOCKTWITS_STREAM_LIMIT = 30

# Filtering
FILTER_MODE = os.getenv("FILTER_MODE", "balanced")  # strict | balanced
DENYLIST_TICKERS = {"KOLD", "BOIL"}
DENYLIST_KEYWORDS = [
    "2x",
    "3x",
    "ultra",
    "leveraged",
    "inverse",
    "short",
    "bear",
    "bull",
]

# Heuristic thresholds
PUMP_LOW_AUTHORS_MAX = 2
PUMP_LOW_MENTIONS_MAX = 3
PUMP_HIGH_MOMENTUM_MIN = 85

# Output paths
DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "reddit.db")
REPORT_DIR = os.path.join(DATA_DIR, "reports")
DOCS_DIR = "docs"
DOCS_DATA_DIR = os.path.join(DOCS_DIR, "data")
