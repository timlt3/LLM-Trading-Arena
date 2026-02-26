from strategies.base import BaseStrategy, MarketData, Decision, Action
import config


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using RSI on SPY."""
    
    def __init__(self, oversold: float = 30.0, overbought: float = 70.0):
        super().__init__("Mean Reversion")
        self.oversold = oversold
        self.overbought = overbought
    
    def decide(self, market_data: MarketData) -> Decision:
        # Only trade SPY
        if market_data.symbol != config.BENCHMARK_SYMBOL:
            return Decision(
                action=Action.HOLD,
                symbol=market_data.symbol,
                confidence=0.0,
                reasoning="Mean Reversion only trades SPY",
                strategy_name=self.name
            )
        
        rsi = market_data.rsi_14
        
        if rsi is None:
            return Decision(
                action=Action.HOLD,
                symbol=market_data.symbol,
                confidence=0.0,
                reasoning="Not enough price history to calculate RSI",
                strategy_name=self.name
            )
        
        current_position = self.get_position(market_data.symbol)
        shares = int(config.POSITION_SIZE_USD / market_data.current_price)
        
        if rsi < self.oversold:
            # Oversold - buy signal
            if current_position <= 0:
                return Decision(
                    action=Action.BUY,
                    symbol=market_data.symbol,
                    confidence=min((self.oversold - rsi) / self.oversold, 1.0),
                    reasoning=f"RSI({rsi:.1f}) below {self.oversold} - oversold, expecting bounce",
                    strategy_name=self.name,
                    quantity=shares
                )
        
        elif rsi > self.overbought:
            # Overbought - sell signal
            if current_position > 0:
                return Decision(
                    action=Action.SELL,
                    symbol=market_data.symbol,
                    confidence=min((rsi - self.overbought) / (100 - self.overbought), 1.0),
                    reasoning=f"RSI({rsi:.1f}) above {self.overbought} - overbought, expecting pullback",
                    strategy_name=self.name,
                    quantity=current_position  # Sell entire position
                )
        
        return Decision(
            action=Action.HOLD,
            symbol=market_data.symbol,
            confidence=0.5,
            reasoning=f"RSI({rsi:.1f}) in neutral zone ({self.oversold}-{self.overbought})",
            strategy_name=self.name
        )
