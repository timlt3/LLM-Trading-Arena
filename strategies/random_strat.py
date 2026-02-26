import random
from strategies.base import BaseStrategy, MarketData, Decision, Action


class RandomStrategy(BaseStrategy):
    """Random strategy - coin flip decisions."""
    
    def __init__(self):
        super().__init__("Random")
    
    def decide(self, market_data: MarketData) -> Decision:
        # 40% buy, 40% sell, 20% hold
        roll = random.random()
        
        if roll < 0.4:
            action = Action.BUY
            reasoning = "Random: coin flip said buy"
        elif roll < 0.8:
            action = Action.SELL
            reasoning = "Random: coin flip said sell"
        else:
            action = Action.HOLD
            reasoning = "Random: coin flip said hold"
        
        return Decision(
            action=action,
            pair=market_data.pair,
            confidence=0.5,  # Random is never confident
            reasoning=reasoning,
            strategy_name=self.name
        )
