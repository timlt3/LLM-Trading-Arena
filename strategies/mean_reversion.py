from strategies.base import BaseStrategy, MarketData, Decision, Action


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy - buy when below average, sell when above."""
    
    def __init__(self, lookback_periods: int = 20, threshold: float = 0.002):
        super().__init__("Mean Reversion")
        self.lookback_periods = lookback_periods
        self.threshold = threshold  # 0.2% deviation threshold
    
    def decide(self, market_data: MarketData) -> Decision:
        prices = market_data.prices_24h
        
        if len(prices) < self.lookback_periods:
            return Decision(
                action=Action.HOLD,
                pair=market_data.pair,
                confidence=0.0,
                reasoning="Not enough price history for mean reversion",
                strategy_name=self.name
            )
        
        # Calculate simple moving average
        recent_prices = prices[-self.lookback_periods:]
        sma = sum(recent_prices) / len(recent_prices)
        current = market_data.current_price
        
        # Calculate deviation from mean
        deviation = (current - sma) / sma
        
        if deviation < -self.threshold:
            # Price is below mean - expect reversion up, so buy
            return Decision(
                action=Action.BUY,
                pair=market_data.pair,
                confidence=min(abs(deviation) / self.threshold * 0.5, 1.0),
                reasoning=f"Price {deviation*100:.3f}% below SMA({self.lookback_periods}), expecting reversion up",
                strategy_name=self.name
            )
        
        elif deviation > self.threshold:
            # Price is above mean - expect reversion down, so sell
            return Decision(
                action=Action.SELL,
                pair=market_data.pair,
                confidence=min(abs(deviation) / self.threshold * 0.5, 1.0),
                reasoning=f"Price {deviation*100:.3f}% above SMA({self.lookback_periods}), expecting reversion down",
                strategy_name=self.name
            )
        
        return Decision(
            action=Action.HOLD,
            pair=market_data.pair,
            confidence=0.5,
            reasoning=f"Price within {self.threshold*100:.1f}% of SMA, no clear signal",
            strategy_name=self.name
        )
