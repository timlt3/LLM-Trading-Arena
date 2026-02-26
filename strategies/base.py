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
    pair: str
    current_price: float
    prices_1h: list[float]  # Last hour of prices (1-min intervals)
    prices_24h: list[float]  # Last 24h of prices (15-min intervals)
    news_headlines: list[str]  # Recent news headlines
    timestamp: str


@dataclass
class Decision:
    action: Action
    pair: str
    confidence: float  # 0-1
    reasoning: str
    strategy_name: str


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, name: str):
        self.name = name
        self.positions: dict[str, float] = {}  # pair -> position size (+ long, - short)
        self.pnl: float = 0.0
        self.trades: list[dict] = []
    
    @abstractmethod
    def decide(self, market_data: MarketData) -> Decision:
        """Make a trading decision based on market data."""
        pass
    
    def record_trade(self, pair: str, action: Action, price: float, size: float):
        """Record a trade for P&L tracking."""
        self.trades.append({
            "pair": pair,
            "action": action.value,
            "price": price,
            "size": size,
            "timestamp": None  # Will be set by tracker
        })
