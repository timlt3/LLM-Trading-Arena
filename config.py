# LLM Trading Arena Configuration

# Droplet LLM API
LLM_BASE_URL = "http://129.212.181.103:8000/v1"
LLM_MODEL = "meta-llama/Llama-3.1-70B-Instruct"

# IBKR Settings
IBKR_HOST = "127.0.0.1"
IBKR_PORT = 7497  # Paper trading port
IBKR_CLIENT_ID = 1

# Trading Settings
TRADING_PAIRS = ["EUR/USD", "GBP/USD"]
DECISION_INTERVAL_MINUTES = 15
POSITION_SIZE = 10000  # Units per trade

# Strategy Settings
STRATEGIES = ["llama", "buy_hold", "random", "mean_reversion"]

# News API (free tier)
# Get a free key at https://newsapi.org/
NEWS_API_KEY = ""  # Optional - leave empty to skip news
