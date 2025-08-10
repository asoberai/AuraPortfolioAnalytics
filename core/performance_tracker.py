"""
AuraQuant Performance Tracker
Comprehensive performance monitoring and Sharpe ratio calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os
import csv
import logging


class PerformanceTracker:
    """
    Tracks and analyzes trading performance with focus on Sharpe ratio optimization
    """
    
    def __init__(self, data_file: str = "data/logs/daily_returns.csv"):
        self.data_file = data_file
        self.logger = logging.getLogger(__name__)
        
        # Performance data
        self.daily_returns = []
        self.trade_history = []
        self.equity_curve = []
        
        # Metrics cache
        self._cached_metrics = {}
        self._cache_timestamp = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        # Load existing data
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical performance data"""
        try:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file)
                self.daily_returns = df['return'].tolist()
                self.logger.info(f"Loaded {len(self.daily_returns)} historical returns")
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            self.daily_returns = []
    
    def log_cycle(self, signals: List[Dict], account_status: Dict):
        """Log a complete strategy cycle"""
        try:
            # Calculate portfolio return for this cycle
            portfolio_return = self._calculate_portfolio_return(account_status)
            
            # Log the return
            self.log_daily_return(portfolio_return)
            
            # Store signal information
            cycle_data = {
                'timestamp': datetime.now(),
                'signals': signals,
                'account_status': account_status,
                'portfolio_return': portfolio_return
            }
            
            self.trade_history.append(cycle_data)
            
            # Update equity curve
            if self.equity_curve:
                new_equity = self.equity_curve[-1] * (1 + portfolio_return)
            else:
                new_equity = account_status.get('total_value', 100000)
            
            self.equity_curve.append(new_equity)
            
        except Exception as e:
            self.logger.error(f"Error logging cycle: {e}")
    
    def log_daily_return(self, daily_return: float):
        """Log daily return"""
        try:
            # Add to in-memory list
            self.daily_returns.append(daily_return)
            
            # Log to CSV file
            log_entry = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "symbol": "PORTFOLIO",
                "return": daily_return
            }
            
            file_exists = os.path.exists(self.data_file)
            with open(self.data_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(log_entry)
            
            # Clear cache when new data is added
            self._cached_metrics = {}
            self._cache_timestamp = None
            
        except Exception as e:
            self.logger.error(f"Error logging daily return: {e}")
    
    def _calculate_portfolio_return(self, account_status: Dict) -> float:
        """Calculate portfolio return for current cycle"""
        try:
            # This is a simplified calculation
            # In a real implementation, you'd track position-level P&L
            
            # For now, use a mock calculation based on positions
            positions_count = account_status.get('positions_count', 0)
            
            if positions_count == 0:
                return 0.0
            
            # Generate a small random return as placeholder
            # In reality, this would be calculated from actual position P&L
            base_return = np.random.normal(0.0005, 0.015)  # ~0.05% mean, 1.5% std
            
            return base_return
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio return: {e}")
            return 0.0
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> Optional[float]:
        """Calculate annualized Sharpe ratio"""
        if len(self.daily_returns) < 30:  # Need at least 30 days
            return None
        
        try:
            returns_array = np.array(self.daily_returns)
            
            # Calculate excess returns
            daily_rf_rate = risk_free_rate / 252  # Convert annual to daily
            excess_returns = returns_array - daily_rf_rate
            
            # Calculate Sharpe ratio
            mean_excess_return = np.mean(excess_returns)
            std_excess_return = np.std(excess_returns)
            
            if std_excess_return == 0:
                return 0
            
            # Annualize
            sharpe_ratio = (mean_excess_return / std_excess_return) * np.sqrt(252)
            
            return sharpe_ratio
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {e}")
            return None
    
    def calculate_comprehensive_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        # Use cache if recent
        if (self._cached_metrics and self._cache_timestamp and 
            datetime.now() - self._cache_timestamp < timedelta(minutes=5)):
            return self._cached_metrics
        
        if not self.daily_returns:
            return self._get_empty_metrics()
        
        try:
            returns_array = np.array(self.daily_returns)
            
            # Basic metrics
            total_return = np.sum(returns_array)
            mean_return = np.mean(returns_array)
            volatility = np.std(returns_array)
            
            # Risk-adjusted metrics
            sharpe_ratio = self.calculate_sharpe_ratio()
            sortino_ratio = self._calculate_sortino_ratio(returns_array)
            
            # Drawdown analysis
            max_drawdown, current_drawdown = self._calculate_drawdowns(returns_array)
            
            # Win/Loss analysis
            winning_days = len([r for r in returns_array if r > 0])
            losing_days = len([r for r in returns_array if r < 0])
            win_rate = winning_days / len(returns_array) if len(returns_array) > 0 else 0
            
            # Average win/loss
            wins = [r for r in returns_array if r > 0]
            losses = [r for r in returns_array if r < 0]
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            
            # Profit factor
            total_wins = sum(wins)
            total_losses = abs(sum(losses))
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
            
            # Calmar ratio (annual return / max drawdown)
            annual_return = mean_return * 252
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Value at Risk (95% confidence)
            var_95 = np.percentile(returns_array, 5)
            
            metrics = {
                # Return metrics
                'total_return': total_return,
                'annual_return': annual_return,
                'mean_daily_return': mean_return,
                'volatility_daily': volatility,
                'volatility_annual': volatility * np.sqrt(252),
                
                # Risk-adjusted metrics
                'sharpe_ratio': sharpe_ratio or 0,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio,
                
                # Drawdown metrics
                'max_drawdown': max_drawdown,
                'current_drawdown': current_drawdown,
                
                # Win/Loss metrics
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'best_day': np.max(returns_array),
                'worst_day': np.min(returns_array),
                
                # Risk metrics
                'var_95': var_95,
                'skewness': self._calculate_skewness(returns_array),
                'kurtosis': self._calculate_kurtosis(returns_array),
                
                # General metrics
                'num_trading_days': len(returns_array),
                'winning_days': winning_days,
                'losing_days': losing_days,
            }
            
            # Cache results
            self._cached_metrics = metrics
            self._cache_timestamp = datetime.now()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive metrics: {e}")
            return self._get_empty_metrics()
    
    def _calculate_sortino_ratio(self, returns: np.ndarray) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        try:
            mean_return = np.mean(returns)
            downside_returns = returns[returns < 0]
            downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
            
            if downside_std == 0:
                return 0
            
            return (mean_return / downside_std) * np.sqrt(252)
        except:
            return 0
    
    def _calculate_drawdowns(self, returns: np.ndarray) -> tuple:
        """Calculate maximum drawdown and current drawdown"""
        try:
            cumulative = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            
            max_drawdown = np.min(drawdown)
            current_drawdown = drawdown[-1]
            
            return max_drawdown, current_drawdown
        except:
            return 0, 0
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calculate skewness of returns"""
        try:
            from scipy import stats
            return stats.skew(returns)
        except:
            return 0
    
    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calculate kurtosis of returns"""
        try:
            from scipy import stats
            return stats.kurtosis(returns)
        except:
            return 0
    
    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics dict"""
        return {key: 0 for key in [
            'total_return', 'annual_return', 'mean_daily_return',
            'volatility_daily', 'volatility_annual', 'sharpe_ratio',
            'sortino_ratio', 'calmar_ratio', 'max_drawdown',
            'current_drawdown', 'win_rate', 'profit_factor',
            'avg_win', 'avg_loss', 'best_day', 'worst_day',
            'var_95', 'skewness', 'kurtosis', 'num_trading_days',
            'winning_days', 'losing_days'
        ]}
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report"""
        metrics = self.calculate_comprehensive_metrics()
        
        report = f"""
📊 AuraQuant Performance Report
{'=' * 50}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📈 Trading Days: {metrics['num_trading_days']}

🎯 KEY METRICS:
   Sharpe Ratio: {metrics['sharpe_ratio']:.4f}
   Total Return: {metrics['total_return']:.2%}
   Annual Return: {metrics['annual_return']:.2%}
   Max Drawdown: {metrics['max_drawdown']:.2%}

📊 RISK METRICS:
   Daily Volatility: {metrics['volatility_daily']:.2%}
   Annual Volatility: {metrics['volatility_annual']:.2%}
   Sortino Ratio: {metrics['sortino_ratio']:.4f}
   Calmar Ratio: {metrics['calmar_ratio']:.4f}
   VaR (95%): {metrics['var_95']:.2%}

🏆 WIN/LOSS ANALYSIS:
   Win Rate: {metrics['win_rate']:.1%}
   Profit Factor: {metrics['profit_factor']:.2f}
   Average Win: {metrics['avg_win']:.2%}
   Average Loss: {metrics['avg_loss']:.2%}
   Best Day: {metrics['best_day']:.2%}
   Worst Day: {metrics['worst_day']:.2%}

📈 DISTRIBUTION:
   Skewness: {metrics['skewness']:.4f}
   Kurtosis: {metrics['kurtosis']:.4f}
   
🎯 PERFORMANCE GRADE:
   {'🔥 EXCELLENT' if metrics['sharpe_ratio'] > 2.0 else
    '✅ GOOD' if metrics['sharpe_ratio'] > 1.0 else
    '⚠️  NEEDS IMPROVEMENT' if metrics['sharpe_ratio'] > 0.5 else
    '❌ POOR'}
"""
        
        return report
    
    def export_to_csv(self, filename: str = None):
        """Export performance data to CSV"""
        if not filename:
            filename = f"data/logs/performance_export_{datetime.now().strftime('%Y%m%d')}.csv"
        
        try:
            # Create DataFrame with all available data
            data = []
            for i, ret in enumerate(self.daily_returns):
                data.append({
                    'date': (datetime.now() - timedelta(days=len(self.daily_returns)-i-1)).strftime('%Y-%m-%d'),
                    'daily_return': ret,
                    'cumulative_return': np.sum(self.daily_returns[:i+1]),
                    'equity_value': self.equity_curve[i] if i < len(self.equity_curve) else None
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            
            self.logger.info(f"Performance data exported to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}") 