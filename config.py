# LLM Trading Arena Configuration

# Droplet LLM API
LLM_BASE_URL = "http://129.212.181.103:8000/v1"
LLM_MODEL = "meta-llama/Llama-3.1-70B-Instruct"

# IBKR Settings
IBKR_HOST = "127.0.0.1"
IBKR_PORT = 7497  # Paper trading port
IBKR_CLIENT_ID = 1

# Trading Settings - Equities
BENCHMARK_SYMBOL = "SPY"  # S&P 500 ETF for baseline strategies

# Top 20 S&P 500 stocks for LLM to pick from
LLM_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "BRK-B", "JPM", "V",
    "UNH", "XOM", "JNJ", "WMT", "MA",
    "PG", "HD", "CVX", "MRK", "ABBV"
]

DECISION_INTERVAL_MINUTES = 15
POSITION_SIZE_USD = 10000  # Dollar amount per trade

# Strategy Settings
STRATEGIES = ["llama", "buy_hold", "mean_reversion", "trend_following"]

# News API (free tier)
# Get a free key at https://newsapi.org/
NEWS_API_KEY = ""  # Optional - leave empty to skip news

# Market Hours (Eastern Time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0
