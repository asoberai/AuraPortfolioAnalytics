"""
AuraQuant Trading Strategy Module
Implements momentum and mean reversion signals for Sharpe ratio optimization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class SharpeStrategy:
    """
    Trading strategy focused on maximizing Sharpe ratio
    Combines momentum and mean reversion signals
    """
    
    def __init__(self, lookback_period: int = 20, momentum_threshold: float = 0.02):
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
        self.position_history = []
        
    def calculate_momentum_signal(self, prices: pd.Series) -> float:
        """
        Calculate momentum signal based on price movement
        Returns: -1 (sell), 0 (hold), 1 (buy)
        """
        if len(prices) < self.lookback_period:
            return 0
            
        # Calculate momentum as percentage change over lookback period
        momentum = (prices.iloc[-1] - prices.iloc[-self.lookback_period]) / prices.iloc[-self.lookback_period]
        
        if momentum > self.momentum_threshold:
            return 1  # Buy signal
        elif momentum < -self.momentum_threshold:
            return -1  # Sell signal
        else:
            return 0  # Hold
    
    def calculate_mean_reversion_signal(self, prices: pd.Series) -> float:
        """
        Calculate mean reversion signal based on deviation from moving average
        Returns: -1 (sell), 0 (hold), 1 (buy)
        """
        if len(prices) < self.lookback_period:
            return 0
            
        # Calculate moving average and standard deviation
        ma = prices.rolling(window=self.lookback_period).mean().iloc[-1]
        std = prices.rolling(window=self.lookback_period).std().iloc[-1]
        current_price = prices.iloc[-1]
        
        # Z-score for mean reversion
        z_score = (current_price - ma) / std if std > 0 else 0
        
        if z_score > 2:
            return -1  # Overbought, sell signal
        elif z_score < -2:
            return 1  # Oversold, buy signal
        else:
            return 0  # Hold
    
    def generate_signal(self, symbol: str, prices: pd.Series) -> Dict:
        """
        Generate combined trading signal
        Returns: Dictionary with signal details
        """
        momentum_signal = self.calculate_momentum_signal(prices)
        mean_reversion_signal = self.calculate_mean_reversion_signal(prices)
        
        # Combine signals (simple average for now)
        combined_signal = (momentum_signal + mean_reversion_signal) / 2
        
        # Convert to discrete signal
        if combined_signal > 0.5:
            action = "BUY"
            strength = min(combined_signal, 1.0)
        elif combined_signal < -0.5:
            action = "SELL"
            strength = max(combined_signal, -1.0)
        else:
            action = "HOLD"
            strength = 0
        
        return {
            "symbol": symbol,
            "action": action,
            "strength": abs(strength),
            "momentum_signal": momentum_signal,
            "mean_reversion_signal": mean_reversion_signal,
            "current_price": prices.iloc[-1] if len(prices) > 0 else None,
            "timestamp": pd.Timestamp.now()
        }
    
    def calculate_position_size(self, signal_strength: float, account_balance: float, 
                              risk_per_trade: float = 0.02) -> float:
        """
        Calculate position size based on signal strength and risk management
        """
        max_risk_amount = account_balance * risk_per_trade
        position_size = max_risk_amount * signal_strength
        
        return position_size
    
    def update_performance_metrics(self, returns: List[float]) -> Dict:
        """
        Update and return current performance metrics
        """
        if not returns:
            return {"sharpe_ratio": 0, "total_return": 0, "volatility": 0}
        
        returns_array = np.array(returns)
        
        # Calculate metrics
        total_return = np.sum(returns_array)
        volatility = np.std(returns_array)
        sharpe_ratio = (np.mean(returns_array) / (volatility + 0.002)) * np.sqrt(252)
        
        return {
            "sharpe_ratio": sharpe_ratio,
            "total_return": total_return,
            "volatility": volatility,
            "num_trades": len(returns)
        } 