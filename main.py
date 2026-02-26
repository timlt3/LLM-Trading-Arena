import time
from datetime import datetime
import schedule

from strategies import LlamaStrategy, BuyHoldStrategy, MeanReversionStrategy, TrendFollowingStrategy
from strategies.base import Action
from broker import Broker
from tracker import Tracker
from data import get_market_data, get_multiple_market_data
import config


class TradingArena:
    """Main trading arena that runs all strategies."""
    
    def __init__(self):
        self.broker = Broker()
        self.tracker = Tracker()
        
        # Initialize strategies
        self.strategies = [
            LlamaStrategy(),
            BuyHoldStrategy(),
            MeanReversionStrategy(),
            TrendFollowingStrategy(),
        ]
        
        print(f"Initialized {len(self.strategies)} strategies:")
        for s in self.strategies:
            print(f"  - {s.name}")
    
    def run_cycle(self):
        """Run one decision cycle for all strategies."""
        print(f"\n{'='*60}")
        print(f"Trading Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Get SPY data for baseline strategies
        print(f"\n--- {config.BENCHMARK_SYMBOL} (Benchmark) ---")
        try:
            spy_data = get_market_data(config.BENCHMARK_SYMBOL)
            print(f"Price: ${spy_data.current_price:.2f}")
            if spy_data.rsi_14:
                print(f"RSI(14): {spy_data.rsi_14:.1f}")
            if spy_data.sma_10 and spy_data.sma_50:
                print(f"SMA(10): ${spy_data.sma_10:.2f}, SMA(50): ${spy_data.sma_50:.2f}")
        except Exception as e:
            print(f"Error fetching SPY data: {e}")
            spy_data = None
        
        # Run baseline strategies on SPY
        if spy_data:
            for strategy in self.strategies:
                if strategy.name != "Llama-70B":  # Baseline strategies
                    self._run_strategy(strategy, spy_data)
        
        # Run Llama on individual stocks
        print(f"\n--- Llama Stock Picks ---")
        llama_strategy = next(s for s in self.strategies if s.name == "Llama-70B")
        
        for symbol in config.LLM_UNIVERSE[:5]:  # Analyze top 5 stocks per cycle
            try:
                stock_data = get_market_data(symbol)
                print(f"\n[{symbol}] ${stock_data.current_price:.2f}")
                self._run_strategy(llama_strategy, stock_data)
            except Exception as e:
                print(f"Error with {symbol}: {e}")
        
        # Print leaderboard
        self._print_leaderboard()
    
    def _run_strategy(self, strategy, market_data):
        """Run a single strategy on market data."""
        try:
            decision = strategy.decide(market_data)
            
            action_emoji = "🟢" if decision.action == Action.BUY else "🔴" if decision.action == Action.SELL else "⚪"
            print(f"  [{strategy.name}] {action_emoji} {decision.action.value} "
                  f"(conf: {decision.confidence:.0%}) - {decision.reasoning[:60]}...")
            
            # Execute trade if not HOLD
            if decision.action != Action.HOLD and decision.quantity:
                fill = self.broker.execute_trade(
                    symbol=market_data.symbol,
                    action=decision.action,
                    quantity=decision.quantity,
                    strategy_name=strategy.name
                )
                
                if fill:
                    self.tracker.record_trade(
                        strategy=strategy.name,
                        symbol=market_data.symbol,
                        action=decision.action,
                        quantity=fill["quantity"],
                        price=fill["price"]
                    )
                    # Update strategy's internal position tracking
                    current = strategy.positions.get(market_data.symbol, 0)
                    if decision.action == Action.BUY:
                        strategy.positions[market_data.symbol] = current + fill["quantity"]
                    else:
                        strategy.positions[market_data.symbol] = current - fill["quantity"]
        
        except Exception as e:
            print(f"  [{strategy.name}] Error: {e}")
    
    def _print_leaderboard(self):
        """Print current leaderboard."""
        # Get current prices for unrealized P&L
        current_prices = {}
        current_prices[config.BENCHMARK_SYMBOL] = get_market_data(config.BENCHMARK_SYMBOL).current_price
        for symbol in config.LLM_UNIVERSE[:10]:
            try:
                current_prices[symbol] = get_market_data(symbol).current_price
            except:
                pass
        
        leaderboard = self.tracker.get_leaderboard(current_prices)
        
        print(f"\n{'='*60}")
        print("🏆 LEADERBOARD")
        print(f"{'='*60}")
        print(f"{'Rank':<6}{'Strategy':<20}{'Total P&L':>12}{'Trades':>8}")
        print("-" * 50)
        
        for i, entry in enumerate(leaderboard, 1):
            pnl = entry['total_pnl']
            pnl_str = f"${pnl:+,.2f}"
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{medal:<6}{entry['strategy']:<20}{pnl_str:>12}{entry['trades']:>8}")
    
    def start(self):
        """Start the trading arena."""
        print("\n" + "="*60)
        print("🤖 LLM TRADING ARENA - EQUITIES EDITION")
        print("="*60)
        print(f"Benchmark: {config.BENCHMARK_SYMBOL}")
        print(f"LLM Universe: {', '.join(config.LLM_UNIVERSE[:5])}...")
        print(f"Interval: {config.DECISION_INTERVAL_MINUTES} minutes")
        print(f"Position size: ${config.POSITION_SIZE_USD:,}")
        print("="*60 + "\n")
        
        # Connect to broker
        if not self.broker.connect():
            print("⚠️  WARNING: Running without broker connection (dry run mode)")
            print("    Trades will be simulated but not executed")
        
        # Run first cycle immediately
        self.run_cycle()
        
        # Schedule subsequent cycles
        schedule.every(config.DECISION_INTERVAL_MINUTES).minutes.do(self.run_cycle)
        
        print(f"\n⏰ Next cycle in {config.DECISION_INTERVAL_MINUTES} minutes...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping arena...")
            self.broker.disconnect()
            self._print_leaderboard()
            print("Arena stopped.")


def main():
    arena = TradingArena()
    arena.start()


if __name__ == "__main__":
    main()
