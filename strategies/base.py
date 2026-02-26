from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class MarketData:
    symbol: str
    current_price: float
    prices_1d: list[float]  # Today's prices (1-min or 5-min intervals)
    prices_5d: list[float]  # Last 5 days of prices (15-min intervals)
    news_headlines: list[str]  # Recent news headlines
    timestamp: str
    
    # Technical indicators (pre-calculated)
    rsi_14: Optional[float] = None
    sma_10: Optional[float] = None
    sma_50: Optional[float] = None


@dataclass
class Decision:
    action: Action
    symbol: str
    confidence: float  # 0-1
    reasoning: str
    strategy_name: str
    quantity: Optional[int] = None  # Number of shares


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, name: str):
        self.name = name
        self.positions: dict[str, int] = {}  # symbol -> shares (+ long, - short)
        self.cash: float = 100000.0  # Starting cash for tracking
        self.trades: list[dict] = []
    
    @abstractmethod
    def decide(self, market_data: MarketData) -> Decision:
        """Make a trading decision based on market data."""
        pass
    
    def get_position(self, symbol: str) -> int:
        """Get current position for a symbol."""
        return self.positions.get(symbol, 0)
