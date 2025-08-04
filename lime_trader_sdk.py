"""
Mock LimeTrader SDK for development and testing
Replace this with the actual SDK once available from LimeTrader
"""

import time
import random
from typing import Dict, List, Optional


class Client:
    """Mock LimeTrader API Client"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.connected = True
        
        # Mock account data
        self.mock_account = {
            "account_id": "DEMO123456",
            "buying_power": 100000.0,
            "total_value": 100000.0,
            "cash": 50000.0
        }
        
        # Mock positions
        self.mock_positions = {}
        
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.api_key or self.api_key == "your_api_key":
            raise Exception("Invalid API credentials")
            
        return self.mock_account
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        positions = []
        for symbol, data in self.mock_positions.items():
            positions.append({
                "symbol": symbol,
                "quantity": data["quantity"],
                "market_value": data["quantity"] * data["avg_price"],
                "avg_price": data["avg_price"],
                "unrealized_pnl": data["quantity"] * (self._get_mock_price(symbol) - data["avg_price"])
            })
        return positions
    
    def place_order(self, symbol: str, side: str, quantity: int, 
                   type: str = "market", account_id: str = None) -> Dict:
        """Place an order"""
        order_id = f"ORD_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Mock order execution
        fill_price = self._get_mock_price(symbol)
        
        # Update mock positions
        if symbol not in self.mock_positions:
            self.mock_positions[symbol] = {"quantity": 0, "avg_price": fill_price}
        
        if side.lower() == "buy":
            old_qty = self.mock_positions[symbol]["quantity"]
            old_price = self.mock_positions[symbol]["avg_price"]
            new_qty = old_qty + quantity
            
            if new_qty != 0:
                self.mock_positions[symbol]["avg_price"] = (
                    (old_qty * old_price + quantity * fill_price) / new_qty
                )
            self.mock_positions[symbol]["quantity"] = new_qty
        else:  # sell
            self.mock_positions[symbol]["quantity"] -= quantity
            
        # Clean up zero positions
        if self.mock_positions[symbol]["quantity"] == 0:
            del self.mock_positions[symbol]
        
        return {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "type": type,
            "status": "filled",
            "fill_price": fill_price,
            "timestamp": time.time()
        }
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get market data for a symbol"""
        return {
            "symbol": symbol,
            "price": self._get_mock_price(symbol),
            "bid": self._get_mock_price(symbol) - 0.01,
            "ask": self._get_mock_price(symbol) + 0.01,
            "volume": random.randint(100000, 1000000),
            "timestamp": time.time()
        }
    
    def _get_mock_price(self, symbol: str) -> float:
        """Generate mock price data"""
        # Simple mock price generator
        base_prices = {
            "AAPL": 180.0,
            "MSFT": 350.0,
            "GOOGL": 140.0,
            "TSLA": 200.0,
            "NVDA": 450.0,
            "SPY": 450.0,
            "QQQ": 380.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        # Add some random variation (±2%)
        variation = random.uniform(-0.02, 0.02)
        return round(base_price * (1 + variation), 2) 