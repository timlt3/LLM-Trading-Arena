import time
from datetime import datetime
import schedule

from strategies import LlamaStrategy, BuyHoldStrategy, RandomStrategy, MeanReversionStrategy
from strategies.base import Action
from broker import Broker
from tracker import Tracker
from data import get_market_data
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
            RandomStrategy(),
            MeanReversionStrategy(),
        ]
        
        print(f"Initialized {len(self.strategies)} strategies:")
        for s in self.strategies:
            print(f"  - {s.name}")
    
    def run_cycle(self):
        """Run one decision cycle for all strategies and pairs."""
        print(f"\n{'='*60}")
        print(f"Trading Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        for pair in config.TRADING_PAIRS:
            print(f"\n--- {pair} ---")
            
            # Fetch market data
            try:
                market_data = get_market_data(pair)
                print(f"Price: {market_data.current_price:.5f}")
            except Exception as e:
                print(f"Error fetching market data for {pair}: {e}")
                continue
            
            # Get decisions from all strategies
            for strategy in self.strategies:
                try:
                    decision = strategy.decide(market_data)
                    print(f"[{strategy.name}] {decision.action.value} "
                          f"(confidence: {decision.confidence:.1%}) - {decision.reasoning[:50]}...")
                    
                    # Execute trade if not HOLD
                    if decision.action != Action.HOLD:
                        fill = self.broker.execute_trade(
                            pair=pair,
                            action=decision.action,
                            size=config.POSITION_SIZE,
                            strategy_name=strategy.name
                        )
                        
                        if fill:
                            self.tracker.record_trade(
                                strategy=strategy.name,
                                pair=pair,
                                action=decision.action,
                                size=fill["size"],
                                price=fill["price"]
                            )
                
                except Exception as e:
                    print(f"[{strategy.name}] Error: {e}")
        
        # Print leaderboard
        self._print_leaderboard()
    
    def _print_leaderboard(self):
        """Print current leaderboard."""
        # Get current prices for unrealized P&L
        current_prices = {}
        for pair in config.TRADING_PAIRS:
            try:
                data = get_market_data(pair)
                current_prices[pair] = data.current_price
            except:
                pass
        
        leaderboard = self.tracker.get_leaderboard(current_prices)
        
        print(f"\n{'='*60}")
        print("LEADERBOARD")
        print(f"{'='*60}")
        print(f"{'Rank':<6}{'Strategy':<20}{'Total P&L':>12}{'Trades':>8}")
        print("-" * 50)
        
        for i, entry in enumerate(leaderboard, 1):
            pnl = entry['total_pnl']
            pnl_str = f"${pnl:+,.2f}" if abs(pnl) < 1000000 else f"${pnl/1000:+,.1f}K"
            print(f"{i:<6}{entry['strategy']:<20}{pnl_str:>12}{entry['trades']:>8}")
    
    def start(self):
        """Start the trading arena."""
        print("\n" + "="*60)
        print("LLM TRADING ARENA")
        print("="*60)
        print(f"Pairs: {', '.join(config.TRADING_PAIRS)}")
        print(f"Interval: {config.DECISION_INTERVAL_MINUTES} minutes")
        print(f"Position size: {config.POSITION_SIZE} units")
        print("="*60 + "\n")
        
        # Connect to broker
        if not self.broker.connect():
            print("WARNING: Running without broker connection (simulation mode)")
        
        # Run first cycle immediately
        self.run_cycle()
        
        # Schedule subsequent cycles
        schedule.every(config.DECISION_INTERVAL_MINUTES).minutes.do(self.run_cycle)
        
        print(f"\nNext cycle in {config.DECISION_INTERVAL_MINUTES} minutes...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping arena...")
            self.broker.disconnect()
            print("Arena stopped.")


def main():
    arena = TradingArena()
    arena.start()


if __name__ == "__main__":
    main()
