"""
AuraQuant Risk Manager
Advanced risk management and position sizing
"""

import numpy as np
from typing import Dict, List, Optional
import logging


class RiskManager:
    """
    Advanced risk management for trading operations
    """
    
    def __init__(self, max_risk_per_trade: float = 0.02, max_portfolio_risk: float = 0.10,
                 max_correlation_exposure: float = 0.30, max_sector_exposure: float = 0.40):
        self.max_risk_per_trade = max_risk_per_trade  # 2% per trade
        self.max_portfolio_risk = max_portfolio_risk  # 10% total portfolio risk
        self.max_correlation_exposure = max_correlation_exposure  # 30% in correlated assets
        self.max_sector_exposure = max_sector_exposure  # 40% in single sector
        
        self.logger = logging.getLogger(__name__)
        
        # Risk tracking
        self.current_risk = 0.0
        self.sector_exposures = {}
        self.position_correlations = {}
        
    def validate_signal(self, signal: Dict, account_status: Dict) -> bool:
        """
        Validate trading signal against risk management rules
        """
        try:
            symbol = signal['symbol']
            action = signal['action']
            strength = signal['strength']
            
            if action == "HOLD":
                return True
            
            # 1. Check maximum risk per trade
            if not self._check_max_risk_per_trade(signal, account_status):
                self.logger.warning(f"Signal for {symbol} rejected: exceeds max risk per trade")
                return False
            
            # 2. Check portfolio risk limits
            if not self._check_portfolio_risk_limits(signal, account_status):
                self.logger.warning(f"Signal for {symbol} rejected: exceeds portfolio risk limits")
                return False
            
            # 3. Check position concentration
            if not self._check_position_concentration(signal, account_status):
                self.logger.warning(f"Signal for {symbol} rejected: position concentration too high")
                return False
            
            # 4. Check sector exposure limits
            if not self._check_sector_exposure(signal, account_status):
                self.logger.warning(f"Signal for {symbol} rejected: sector exposure too high")
                return False
            
            # 5. Check signal quality
            if not self._check_signal_quality(signal):
                self.logger.warning(f"Signal for {symbol} rejected: poor signal quality")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Risk validation failed for {symbol}: {e}")
            return False
    
    def _check_max_risk_per_trade(self, signal: Dict, account_status: Dict) -> bool:
        """Check if trade risk is within limits"""
        try:
            account_value = account_status['total_value']
            strength = signal['strength']
            
            # Calculate maximum position size based on risk
            max_risk_amount = account_value * self.max_risk_per_trade
            
            # Estimate position size (simplified)
            current_price = signal.get('current_price', 100)  # Default if not available
            estimated_position_size = (max_risk_amount / current_price) * strength
            
            # Check if position size is reasonable
            if estimated_position_size > account_value * 0.2:  # No single position > 20% of account
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking max risk per trade: {e}")
            return False
    
    def _check_portfolio_risk_limits(self, signal: Dict, account_status: Dict) -> bool:
        """Check portfolio-wide risk limits"""
        try:
            # Calculate current portfolio risk (simplified)
            positions_count = account_status.get('positions_count', 0)
            
            # Don't allow too many positions (diversification vs over-diversification)
            max_positions = 10
            if positions_count >= max_positions and signal['action'] in ['BUY', 'SELL']:
                return False
            
            # Check if we're not over-leveraged
            buying_power_used = (account_status['total_value'] - account_status['cash']) / account_status['total_value']
            if buying_power_used > 0.8:  # Don't use more than 80% of buying power
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking portfolio risk limits: {e}")
            return False
    
    def _check_position_concentration(self, signal: Dict, account_status: Dict) -> bool:
        """Check position size concentration"""
        try:
            symbol = signal['symbol']
            account_value = account_status['total_value']
            
            # Get current position in this symbol
            current_positions = account_status.get('positions', [])
            current_position_value = 0
            
            for pos in current_positions:
                if hasattr(pos, 'symbol') and pos.symbol == symbol:
                    current_position_value = abs(float(getattr(pos, 'market_value', 0)))
                    break
            
            # Don't allow any single position to exceed 15% of account
            max_position_value = account_value * 0.15
            
            if current_position_value > max_position_value:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking position concentration: {e}")
            return True  # Default to allow if check fails
    
    def _check_sector_exposure(self, signal: Dict, account_status: Dict) -> bool:
        """Check sector exposure limits"""
        try:
            symbol = signal['symbol']
            
            # Simplified sector mapping (in real implementation, use proper sector data)
            tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
            finance_stocks = ['JPM', 'BAC', 'WFC', 'GS']
            
            if symbol in tech_stocks:
                sector = 'technology'
            elif symbol in finance_stocks:
                sector = 'finance'
            else:
                sector = 'other'
            
            # Check sector exposure (simplified)
            current_sector_exposure = self.sector_exposures.get(sector, 0)
            if current_sector_exposure > self.max_sector_exposure:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking sector exposure: {e}")
            return True
    
    def _check_signal_quality(self, signal: Dict) -> bool:
        """Check signal quality and confidence"""
        try:
            strength = signal['strength']
            confidence = signal.get('confidence', 50)
            
            # Minimum signal strength threshold
            if strength < 0.3:
                return False
            
            # Minimum confidence threshold
            if confidence < 40:
                return False
            
            # Check for conflicting signals
            momentum_signal = signal.get('momentum_signal', 0)
            mean_reversion_signal = signal.get('mean_reversion_signal', 0)
            
            # If momentum and mean reversion strongly disagree, be cautious
            if abs(momentum_signal + mean_reversion_signal) < 0.1 and abs(momentum_signal) > 0.5:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking signal quality: {e}")
            return True
    
    def calculate_position_size(self, signal: Dict, account_status: Dict) -> int:
        """Calculate optimal position size with risk management"""
        try:
            account_value = account_status['total_value']
            strength = signal['strength']
            current_price = signal.get('current_price', 100)
            
            # Base position size on risk per trade
            risk_amount = account_value * self.max_risk_per_trade * strength
            
            # Adjust for volatility (if available)
            volatility_factor = signal.get('volatility_factor', 1.0)
            adjusted_risk_amount = risk_amount / volatility_factor
            
            # Calculate position size
            position_size = int(adjusted_risk_amount / current_price)
            
            # Apply maximum position limits
            max_position_value = account_value * 0.15  # 15% max per position
            max_position_size = int(max_position_value / current_price)
            
            final_position_size = min(position_size, max_position_size)
            
            return max(final_position_size, 0)
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0
    
    def update_risk_metrics(self, account_status: Dict):
        """Update current risk metrics"""
        try:
            # Update current portfolio risk
            total_value = account_status['total_value']
            cash = account_status['cash']
            
            self.current_risk = (total_value - cash) / total_value if total_value > 0 else 0
            
            # Update sector exposures (simplified)
            positions = account_status.get('positions', [])
            sector_values = {}
            
            for pos in positions:
                if hasattr(pos, 'symbol') and hasattr(pos, 'market_value'):
                    symbol = pos.symbol
                    value = abs(float(pos.market_value))
                    
                    # Simplified sector classification
                    if symbol in ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']:
                        sector = 'technology'
                    else:
                        sector = 'other'
                    
                    sector_values[sector] = sector_values.get(sector, 0) + value
            
            # Calculate sector exposures as percentage of total value
            self.sector_exposures = {
                sector: value / total_value for sector, value in sector_values.items()
            } if total_value > 0 else {}
            
        except Exception as e:
            self.logger.error(f"Error updating risk metrics: {e}")
    
    def get_risk_report(self) -> Dict:
        """Generate risk management report"""
        return {
            "current_portfolio_risk": self.current_risk,
            "max_risk_per_trade": self.max_risk_per_trade,
            "max_portfolio_risk": self.max_portfolio_risk,
            "sector_exposures": self.sector_exposures,
            "risk_utilization": self.current_risk / self.max_portfolio_risk if self.max_portfolio_risk > 0 else 0,
            "within_limits": self.current_risk <= self.max_portfolio_risk
        } 