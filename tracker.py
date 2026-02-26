import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

from strategies.base import Action


@dataclass
class Trade:
    timestamp: str
    strategy: str
    symbol: str
    action: str
    quantity: int
    price: float
    pnl: Optional[float] = None  # Realized P&L when position closed


class Tracker:
    """Track trades and P&L for all strategies."""
    
    def __init__(self, data_file: str = "arena_data.json"):
        self.data_file = Path(data_file)
        self.trades: list[Trade] = []
        self.positions: dict[str, dict[str, int]] = {}  # strategy -> symbol -> shares
        self.entry_prices: dict[str, dict[str, float]] = {}  # strategy -> symbol -> avg price
        self.realized_pnl: dict[str, float] = {}  # strategy -> total realized P&L
        self.load()
    
    def load(self):
        """Load existing data from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.trades = [Trade(**t) for t in data.get("trades", [])]
                    self.positions = data.get("positions", {})
                    self.entry_prices = data.get("entry_prices", {})
                    self.realized_pnl = data.get("realized_pnl", {})
                    print(f"📂 Loaded {len(self.trades)} trades from {self.data_file}")
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def save(self):
        """Save data to file."""
        data = {
            "trades": [asdict(t) for t in self.trades],
            "positions": self.positions,
            "entry_prices": self.entry_prices,
            "realized_pnl": self.realized_pnl,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def record_trade(
        self,
        strategy: str,
        symbol: str,
        action: Action,
        quantity: int,
        price: float
    ):
        """Record a trade and update positions."""
        
        # Initialize strategy tracking if needed
        if strategy not in self.positions:
            self.positions[strategy] = {}
            self.entry_prices[strategy] = {}
            self.realized_pnl[strategy] = 0.0
        
        if symbol not in self.positions[strategy]:
            self.positions[strategy][symbol] = 0
            self.entry_prices[strategy][symbol] = 0.0
        
        current_pos = self.positions[strategy][symbol]
        entry_price = self.entry_prices[strategy][symbol]
        
        # Calculate P&L if closing/reducing position
        pnl = None
        if action == Action.BUY and current_pos < 0:
            # Closing short
            close_qty = min(quantity, abs(current_pos))
            pnl = close_qty * (entry_price - price)
            self.realized_pnl[strategy] += pnl
        elif action == Action.SELL and current_pos > 0:
            # Closing long
            close_qty = min(quantity, current_pos)
            pnl = close_qty * (price - entry_price)
            self.realized_pnl[strategy] += pnl
        
        # Update position
        if action == Action.BUY:
            new_pos = current_pos + quantity
        else:  # SELL
            new_pos = current_pos - quantity
        
        # Update entry price (weighted average for adding to position)
        if new_pos != 0:
            if current_pos * new_pos > 0 and current_pos != 0:
                # Same direction, average the entry
                total_cost = abs(current_pos) * entry_price + quantity * price
                self.entry_prices[strategy][symbol] = total_cost / (abs(current_pos) + quantity)
            else:
                # New position or flipped direction
                self.entry_prices[strategy][symbol] = price
        
        self.positions[strategy][symbol] = new_pos
        
        # Record trade
        trade = Trade(
            timestamp=datetime.now().isoformat(),
            strategy=strategy,
            symbol=symbol,
            action=action.value,
            quantity=quantity,
            price=price,
            pnl=pnl
        )
        self.trades.append(trade)
        self.save()
        
        return trade
    
    def get_unrealized_pnl(self, strategy: str, current_prices: dict[str, float]) -> float:
        """Calculate unrealized P&L for a strategy."""
        if strategy not in self.positions:
            return 0.0
        
        unrealized = 0.0
        for symbol, position in self.positions[strategy].items():
            if position != 0 and symbol in current_prices:
                entry = self.entry_prices[strategy].get(symbol, current_prices[symbol])
                current = current_prices[symbol]
                if position > 0:  # Long
                    unrealized += position * (current - entry)
                else:  # Short
                    unrealized += abs(position) * (entry - current)
        
        return unrealized
    
    def get_total_pnl(self, strategy: str, current_prices: dict[str, float]) -> float:
        """Get total P&L (realized + unrealized) for a strategy."""
        realized = self.realized_pnl.get(strategy, 0.0)
        unrealized = self.get_unrealized_pnl(strategy, current_prices)
        return realized + unrealized
    
    def get_leaderboard(self, current_prices: dict[str, float]) -> list[dict]:
        """Get sorted leaderboard of all strategies."""
        leaderboard = []
        
        for strategy in set(self.realized_pnl.keys()) | set(self.positions.keys()):
            total_pnl = self.get_total_pnl(strategy, current_prices)
            realized = self.realized_pnl.get(strategy, 0.0)
            unrealized = self.get_unrealized_pnl(strategy, current_prices)
            
            # Count trades
            trade_count = len([t for t in self.trades if t.strategy == strategy])
            
            leaderboard.append({
                "strategy": strategy,
                "total_pnl": total_pnl,
                "realized_pnl": realized,
                "unrealized_pnl": unrealized,
                "trades": trade_count,
                "positions": self.positions.get(strategy, {})
            })
        
        # Sort by total P&L descending
        leaderboard.sort(key=lambda x: x["total_pnl"], reverse=True)
        return leaderboard
