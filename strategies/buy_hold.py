from strategies.base import BaseStrategy, MarketData, Decision, Action


class BuyHoldStrategy(BaseStrategy):
    """Simple buy and hold strategy - buys once and holds."""
    
    def __init__(self):
        super().__init__("Buy & Hold")
        self.has_bought: dict[str, bool] = {}
    
    def decide(self, market_data: MarketData) -> Decision:
        pair = market_data.pair
        
        # If we haven't bought yet, buy. Otherwise hold.
        if not self.has_bought.get(pair, False):
            self.has_bought[pair] = True
            return Decision(
                action=Action.BUY,
                pair=pair,
                confidence=1.0,
                reasoning="Initial buy for buy-and-hold strategy",
                strategy_name=self.name
            )
        
        return Decision(
            action=Action.HOLD,
            pair=pair,
            confidence=1.0,
            reasoning="Holding position per buy-and-hold strategy",
            strategy_name=self.name
        )
