"""
AuraQuant Logging Utility
Centralized logging configuration
"""

import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = 'INFO', log_file: str = 'data/logs/auraquant.log') -> logging.Logger:
    """
    Setup centralized logging for AuraQuant
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Create AuraQuant main logger
    logger = logging.getLogger('auraquant')
    logger.setLevel(numeric_level)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f'auraquant.{name}')


class PerformanceLogger:
    """
    Specialized logger for performance metrics
    """
    
    def __init__(self, log_file: str = 'data/logs/performance.log'):
        self.log_file = log_file
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Setup performance logger
        self.logger = logging.getLogger('auraquant.performance')
        
        # Performance file handler
        perf_handler = logging.FileHandler(log_file)
        perf_formatter = logging.Formatter(
            '%(asctime)s,%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        perf_handler.setFormatter(perf_formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(perf_handler)
            self.logger.setLevel(logging.INFO)
        
        self.logger.propagate = False  # Don't send to root logger
    
    def log_trade(self, symbol: str, action: str, quantity: int, price: float, 
                  signal_strength: float, pnl: float = None):
        """Log trade execution"""
        trade_data = f"{symbol},{action},{quantity},{price:.4f},{signal_strength:.4f}"
        if pnl is not None:
            trade_data += f",{pnl:.4f}"
        
        self.logger.info(trade_data)
    
    def log_performance(self, sharpe_ratio: float, total_return: float, 
                       max_drawdown: float, win_rate: float):
        """Log performance metrics"""
        perf_data = f"PERFORMANCE,{sharpe_ratio:.4f},{total_return:.4f},{max_drawdown:.4f},{win_rate:.4f}"
        self.logger.info(perf_data)
    
    def log_risk_metrics(self, portfolio_risk: float, largest_position: float, 
                        num_positions: int, leverage: float):
        """Log risk metrics"""
        risk_data = f"RISK,{portfolio_risk:.4f},{largest_position:.4f},{num_positions},{leverage:.4f}"
        self.logger.info(risk_data) 