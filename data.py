import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Optional

from strategies.base import MarketData
import config


# Yahoo Finance uses different symbols for FX
FX_SYMBOL_MAP = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
}


def get_market_data(pair: str) -> MarketData:
    """Fetch current market data for a currency pair."""
    
    symbol = FX_SYMBOL_MAP.get(pair, pair.replace("/", "") + "=X")
    
    # Get price data
    ticker = yf.Ticker(symbol)
    
    # Current price
    try:
        current_price = ticker.info.get("regularMarketPrice") or ticker.info.get("ask") or 0
    except:
        current_price = 0
    
    # Historical prices - last 24h
    try:
        hist_24h = ticker.history(period="1d", interval="15m")
        prices_24h = hist_24h["Close"].tolist() if not hist_24h.empty else []
    except:
        prices_24h = []
    
    # Historical prices - last hour (1-min intervals)
    try:
        hist_1h = ticker.history(period="1h", interval="1m")
        prices_1h = hist_1h["Close"].tolist() if not hist_1h.empty else []
    except:
        prices_1h = []
    
    # Fallback current price from history
    if current_price == 0 and prices_24h:
        current_price = prices_24h[-1]
    
    # Get news headlines
    news_headlines = get_news_headlines(pair)
    
    return MarketData(
        pair=pair,
        current_price=current_price,
        prices_1h=prices_1h,
        prices_24h=prices_24h,
        news_headlines=news_headlines,
        timestamp=datetime.now().isoformat()
    )


def get_news_headlines(pair: str) -> list[str]:
    """Fetch recent news headlines related to the currency pair."""
    
    if not config.NEWS_API_KEY:
        return _get_fallback_context(pair)
    
    # Map pairs to search terms
    search_terms = {
        "EUR/USD": "EUR USD euro dollar forex",
        "GBP/USD": "GBP USD pound sterling dollar forex",
        "USD/JPY": "USD JPY dollar yen forex",
    }
    
    query = search_terms.get(pair, pair.replace("/", " "))
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": config.NEWS_API_KEY,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "from": (datetime.now() - timedelta(days=1)).isoformat()
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "ok":
            return [article["title"] for article in data.get("articles", [])]
    
    except Exception as e:
        print(f"News API error: {e}")
    
    return _get_fallback_context(pair)


def _get_fallback_context(pair: str) -> list[str]:
    """Return basic context when news API isn't available."""
    # Could scrape free sources or return empty
    return []
