import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Optional
import numpy as np

from strategies.base import MarketData
import config


def calculate_rsi(prices: list[float], period: int = 14) -> Optional[float]:
    """Calculate RSI indicator."""
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices[-period-1:])
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)


def calculate_sma(prices: list[float], period: int) -> Optional[float]:
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return None
    return float(np.mean(prices[-period:]))


def get_market_data(symbol: str) -> MarketData:
    """Fetch current market data for a stock symbol."""
    
    ticker = yf.Ticker(symbol)
    
    # Current price
    try:
        info = ticker.info
        current_price = info.get("regularMarketPrice") or info.get("currentPrice") or 0
    except:
        current_price = 0
    
    # Today's prices (5-min intervals)
    try:
        hist_1d = ticker.history(period="1d", interval="5m")
        prices_1d = hist_1d["Close"].tolist() if not hist_1d.empty else []
    except:
        prices_1d = []
    
    # Last 5 days prices (15-min intervals for intraday granularity)
    try:
        hist_5d = ticker.history(period="5d", interval="15m")
        prices_5d = hist_5d["Close"].tolist() if not hist_5d.empty else []
    except:
        prices_5d = []
    
    # Fallback current price from history
    if current_price == 0 and prices_1d:
        current_price = prices_1d[-1]
    elif current_price == 0 and prices_5d:
        current_price = prices_5d[-1]
    
    # Calculate technical indicators
    all_prices = prices_5d if prices_5d else prices_1d
    rsi_14 = calculate_rsi(all_prices, 14)
    sma_10 = calculate_sma(all_prices, 10)
    sma_50 = calculate_sma(all_prices, 50)
    
    # Get news headlines
    news_headlines = get_news_headlines(symbol)
    
    return MarketData(
        symbol=symbol,
        current_price=current_price,
        prices_1d=prices_1d,
        prices_5d=prices_5d,
        news_headlines=news_headlines,
        timestamp=datetime.now().isoformat(),
        rsi_14=rsi_14,
        sma_10=sma_10,
        sma_50=sma_50
    )


def get_news_headlines(symbol: str) -> list[str]:
    """Fetch recent news headlines for a stock."""
    
    # Try yfinance news first (free, no API key needed)
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if news:
            return [item.get("title", "") for item in news[:5]]
    except:
        pass
    
    # Fall back to NewsAPI if configured
    if config.NEWS_API_KEY:
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": symbol,
                "apiKey": config.NEWS_API_KEY,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "from": (datetime.now() - timedelta(days=1)).isoformat()
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                return [article["title"] for article in data.get("articles", [])]
        except:
            pass
    
    return []


def get_multiple_market_data(symbols: list[str]) -> dict[str, MarketData]:
    """Fetch market data for multiple symbols efficiently."""
    result = {}
    for symbol in symbols:
        try:
            result[symbol] = get_market_data(symbol)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    return result
