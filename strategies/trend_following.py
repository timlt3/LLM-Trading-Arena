from strategies.base import BaseStrategy, MarketData, Decision, Action
import config


class TrendFollowingStrategy(BaseStrategy):
    """Trend following strategy using SMA crossover on SPY."""
    
    def __init__(self):
        super().__init__("Trend Following")
        self.was_bullish = None  # Track previous state to avoid constant trading
    
    def decide(self, market_data: MarketData) -> Decision:
        # Only trade SPY
        if market_data.symbol != config.BENCHMARK_SYMBOL:
            return Decision(
                action=Action.HOLD,
                symbol=market_data.symbol,
                confidence=0.0,
                reasoning="Trend Following only trades SPY",
                strategy_name=self.name
            )
        
        sma_10 = market_data.sma_10
        sma_50 = market_data.sma_50
        
        if sma_10 is None or sma_50 is None:
            return Decision(
                action=Action.HOLD,
                symbol=market_data.symbol,
                confidence=0.0,
                reasoning="Not enough price history for SMA calculation",
                strategy_name=self.name
            )
        
        current_position = self.get_position(market_data.symbol)
        shares = int(config.POSITION_SIZE_USD / market_data.current_price)
        
        is_bullish = sma_10 > sma_50
        
        # Only trade on crossover (state change)
        if is_bullish and self.was_bullish == False:
            # Bullish crossover - go long
            self.was_bullish = True
            if current_position <= 0:
                return Decision(
                    action=Action.BUY,
                    symbol=market_data.symbol,
                    confidence=0.8,
                    reasoning=f"Bullish crossover: SMA(10)={sma_10:.2f} crossed above SMA(50)={sma_50:.2f}",
                    strategy_name=self.name,
                    quantity=shares
                )
        
        elif not is_bullish and self.was_bullish == True:
            # Bearish crossover - exit long
            self.was_bullish = False
            if current_position > 0:
                return Decision(
                    action=Action.SELL,
                    symbol=market_data.symbol,
                    confidence=0.8,
                    reasoning=f"Bearish crossover: SMA(10)={sma_10:.2f} crossed below SMA(50)={sma_50:.2f}",
                    strategy_name=self.name,
                    quantity=current_position
                )
        
        # Initialize state on first run
        if self.was_bullish is None:
            self.was_bullish = is_bullish
            # Enter position if already bullish
            if is_bullish and current_position <= 0:
                return Decision(
                    action=Action.BUY,
                    symbol=market_data.symbol,
                    confidence=0.6,
                    reasoning=f"Initial entry: SMA(10)={sma_10:.2f} > SMA(50)={sma_50:.2f}, trend is bullish",
                    strategy_name=self.name,
                    quantity=shares
                )
        
        trend = "bullish" if is_bullish else "bearish"
        return Decision(
            action=Action.HOLD,
            symbol=market_data.symbol,
            confidence=0.5,
            reasoning=f"No crossover - maintaining {trend} stance. SMA(10)={sma_10:.2f}, SMA(50)={sma_50:.2f}",
            strategy_name=self.name
        )
