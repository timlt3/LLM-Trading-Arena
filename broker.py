from ib_insync import IB, Forex, MarketOrder
from typing import Optional
import time

from strategies.base import Action
import config


class Broker:
    """IBKR paper trading broker connection."""
    
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
            print(f"Connected to IBKR on port {config.IBKR_PORT}")
            return True
        except Exception as e:
            print(f"Failed to connect to IBKR: {e}")
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
        pair: str,
        action: Action,
        size: int,
        strategy_name: str
    ) -> Optional[dict]:
        """Execute a trade on IBKR."""
        
        if action == Action.HOLD:
            return None
        
        if not self.connected:
            print("Not connected to IBKR")
            return None
        
        # Convert pair to IBKR format (EUR/USD -> EURUSD)
        symbol = pair.replace("/", "")
        
        # Create forex contract
        contract = Forex(symbol)
        
        # Determine order direction
        order_action = "BUY" if action == Action.BUY else "SELL"
        
        # Create market order with strategy tag in reference
        order = MarketOrder(
            action=order_action,
            totalQuantity=size,
            orderRef=f"LLM-ARENA-{strategy_name}"  # Tag for tracking
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
                print(f"[{strategy_name}] {order_action} {size} {pair} @ {fill_price}")
                return {
                    "pair": pair,
                    "action": order_action,
                    "size": size,
                    "price": fill_price,
                    "strategy": strategy_name,
                    "order_id": trade.order.orderId
                }
            else:
                print(f"Order not filled: {trade.orderStatus.status}")
                return None
                
        except Exception as e:
            print(f"Trade execution error: {e}")
            return None
    
    def get_position(self, pair: str) -> float:
        """Get current position for a pair."""
        if not self.connected:
            return 0.0
        
        symbol = pair.replace("/", "")
        positions = self.ib.positions()
        
        for pos in positions:
            if pos.contract.symbol == symbol[:3]:  # Base currency
                return pos.position
        
        return 0.0
    
    def get_account_value(self) -> float:
        """Get total account value."""
        if not self.connected:
            return 0.0
        
        account_values = self.ib.accountValues()
        for av in account_values:
            if av.tag == "NetLiquidation" and av.currency == "USD":
                return float(av.value)
        
        return 0.0
