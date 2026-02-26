from strategies.base import BaseStrategy, MarketData, Decision, Action
import config


class BuyHoldStrategy(BaseStrategy):
    """Buy and hold SPY - the Boglehead benchmark."""
    
    def __init__(self):
        super().__init__("Buy & Hold SPY")
        self.has_bought = False
    
    def decide(self, market_data: MarketData) -> Decision:
        # Only trade SPY
        if market_data.symbol != config.BENCHMARK_SYMBOL:
            return Decision(
                action=Action.HOLD,
                symbol=market_data.symbol,
                confidence=1.0,
                reasoning="Buy & Hold only trades SPY",
                strategy_name=self.name
            )
        
        # If we haven't bought yet, buy. Otherwise hold.
        if not self.has_bought:
            self.has_bought = True
            # Calculate shares based on position size
            shares = int(config.POSITION_SIZE_USD / market_data.current_price)
            return Decision(
                action=Action.BUY,
                symbol=market_data.symbol,
                confidence=1.0,
                reasoning="Initial buy for buy-and-hold strategy",
                strategy_name=self.name,
                quantity=shares
            )
        
        return Decision(
            action=Action.HOLD,
            symbol=market_data.symbol,
            confidence=1.0,
            reasoning="Holding position per buy-and-hold strategy",
            strategy_name=self.name
        )
