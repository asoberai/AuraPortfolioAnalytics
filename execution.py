"""
AuraQuant Order Execution Module
Handles order placement, management, and risk controls
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import os
import csv


class OrderExecutor:
    """
    Handles order execution and position management for LimeTrader
    """
    
    def __init__(self, client, account_id: str, max_position_size: float = 10000):
        self.client = client
        self.account_id = account_id
        self.max_position_size = max_position_size
        self.positions = {}
        self.order_history = []
        self.daily_returns = []
        
    def get_account_balance(self) -> float:
        """Get current account balance"""
        try:
            account_info = self.client.get_account_info()
            return float(account_info.get('buying_power', 0))
        except Exception as e:
            print(f"❌ Error getting account balance: {e}")
            return 0
    
    def get_current_positions(self) -> Dict:
        """Get current positions"""
        try:
            positions = self.client.get_positions()
            return {pos['symbol']: pos for pos in positions}
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return {}
    
    def place_order(self, symbol: str, action: str, quantity: int, 
                   order_type: str = "market") -> Optional[Dict]:
        """
        Place an order through LimeTrader API
        """
        try:
            order_data = {
                "symbol": symbol,
                "side": action.lower(),  # "buy" or "sell"
                "quantity": abs(quantity),
                "type": order_type,
                "account_id": self.account_id
            }
            
            # Place order through client
            order_response = self.client.place_order(**order_data)
            
            # Log the order
            self.log_order(symbol, action, quantity, order_response)
            
            print(f"✅ Order placed: {action} {quantity} {symbol}")
            return order_response
            
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return None
    
    def execute_signal(self, signal: Dict) -> bool:
        """
        Execute a trading signal
        """
        symbol = signal['symbol']
        action = signal['action']
        strength = signal['strength']
        
        if action == "HOLD":
            return True
        
        # Get account balance and calculate position size
        balance = self.get_account_balance()
        if balance <= 0:
            print("❌ Insufficient account balance")
            return False
        
        # Calculate position size based on signal strength and risk management
        position_value = min(balance * 0.1 * strength, self.max_position_size)
        
        # Get current price to calculate quantity
        current_price = signal.get('current_price')
        if not current_price:
            print(f"❌ No current price for {symbol}")
            return False
        
        quantity = int(position_value / current_price)
        
        if quantity == 0:
            print(f"⚠️  Position size too small for {symbol}")
            return False
        
        # Check current position
        current_positions = self.get_current_positions()
        current_qty = current_positions.get(symbol, {}).get('quantity', 0)
        
        # Determine order quantity based on current position
        if action == "BUY":
            order_qty = quantity - current_qty
        else:  # SELL
            order_qty = -(quantity + current_qty)
        
        if abs(order_qty) < 1:
            print(f"⚠️  No significant position change needed for {symbol}")
            return True
        
        # Place the order
        order_result = self.place_order(symbol, 
                                      "buy" if order_qty > 0 else "sell", 
                                      abs(order_qty))
        
        return order_result is not None
    
    def log_order(self, symbol: str, action: str, quantity: int, order_response: Dict):
        """Log order details"""
        order_log = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "order_id": order_response.get('order_id', 'N/A'),
            "status": order_response.get('status', 'unknown')
        }
        
        self.order_history.append(order_log)
        
        # Save to CSV
        log_file = "data/logs/order_history.csv"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_exists = os.path.exists(log_file)
        with open(log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=order_log.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(order_log)
    
    def calculate_daily_return(self) -> float:
        """Calculate daily return based on current positions"""
        try:
            current_positions = self.get_current_positions()
            total_value = 0
            
            for symbol, position in current_positions.items():
                quantity = float(position.get('quantity', 0))
                current_price = float(position.get('market_value', 0)) / quantity if quantity != 0 else 0
                position_value = quantity * current_price
                total_value += position_value
            
            # Calculate return (simplified - would need previous day's value for actual calculation)
            # For now, return a placeholder
            daily_return = np.random.normal(0.001, 0.02)  # Placeholder
            
            return daily_return
            
        except Exception as e:
            print(f"❌ Error calculating daily return: {e}")
            return 0
    
    def log_daily_return(self, symbol: str, daily_return: float):
        """Log daily return for Sharpe ratio calculation"""
        log_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "symbol": symbol,
            "return": daily_return
        }
        
        self.daily_returns.append(log_entry)
        
        # Save to CSV
        log_file = "data/logs/daily_returns.csv"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_exists = os.path.exists(log_file)
        with open(log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
    
    def get_risk_metrics(self) -> Dict:
        """Calculate current risk metrics"""
        positions = self.get_current_positions()
        total_exposure = sum(abs(float(pos.get('market_value', 0))) for pos in positions.values())
        account_balance = self.get_account_balance()
        
        return {
            "total_exposure": total_exposure,
            "account_balance": account_balance,
            "leverage": total_exposure / account_balance if account_balance > 0 else 0,
            "num_positions": len(positions)
        } 