from ib_insync import IB, Stock, MarketOrder
from typing import Optional
import time

from strategies.base import Action
import config


class Broker:
    """IBKR paper trading broker connection for equities."""
    
    def __init__(self):
        self.ib = IB()
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to TWS/IB Gateway."""
        try:
            self.ib.connect(
                config.IBKR_HOST,
                config.IBKR_PORT,
                clientId=config.IBKR_CLIENT_ID
            )
            self.connected = True
            print(f"✅ Connected to IBKR on port {config.IBKR_PORT}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to IBKR: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from IBKR."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            print("Disconnected from IBKR")
    
    def execute_trade(
        self,
        symbol: str,
        action: Action,
        quantity: int,
        strategy_name: str
    ) -> Optional[dict]:
        """Execute a stock trade on IBKR."""
        
        if action == Action.HOLD:
            return None
        
        if not self.connected:
            print(f"    [DRY RUN] Would {action.value} {quantity} {symbol}")
            # Return simulated fill for dry run mode
            return {
                "symbol": symbol,
                "action": action.value,
                "quantity": quantity,
                "price": 0.0,  # Will be filled by tracker
                "strategy": strategy_name
            }
        
        # Create stock contract (US stocks on SMART routing)
        contract = Stock(symbol, "SMART", "USD")
        
        # Qualify the contract to get full details
        try:
            self.ib.qualifyContracts(contract)
        except Exception as e:
            print(f"    Failed to qualify contract for {symbol}: {e}")
            return None
        
        # Determine order direction
        order_action = "BUY" if action == Action.BUY else "SELL"
        
        # Create market order with strategy tag
        order = MarketOrder(
            action=order_action,
            totalQuantity=quantity,
            orderRef=f"LLM-ARENA-{strategy_name}"
        )
        
        try:
            # Place order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait for fill (with timeout)
            timeout = 30
            start = time.time()
            while not trade.isDone() and time.time() - start < timeout:
                self.ib.sleep(0.5)
            
            if trade.orderStatus.status == "Filled":
                fill_price = trade.orderStatus.avgFillPrice
                print(f"    ✅ [{strategy_name}] {order_action} {quantity} {symbol} @ ${fill_price:.2f}")
                return {
                    "symbol": symbol,
                    "action": order_action,
                    "quantity": quantity,
                    "price": fill_price,
                    "strategy": strategy_name,
                    "order_id": trade.order.orderId
                }
            else:
                print(f"    ⚠️ Order not filled: {trade.orderStatus.status}")
                return None
                
        except Exception as e:
            print(f"    ❌ Trade execution error: {e}")
            return None
    
    def get_position(self, symbol: str) -> int:
        """Get current position for a symbol."""
        if not self.connected:
            return 0
        
        positions = self.ib.positions()
        
        for pos in positions:
            if pos.contract.symbol == symbol:
                return int(pos.position)
        
        return 0
    
    def get_account_value(self) -> float:
        """Get total account value."""
        if not self.connected:
            return 0.0
        
        account_values = self.ib.accountValues()
        for av in account_values:
            if av.tag == "NetLiquidation" and av.currency == "USD":
                return float(av.value)
        
        return 0.0
