"""
AuraQuant Configuration Manager
Handles configuration loading and management
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    Configuration manager for AuraQuant
    Handles environment variables and configuration files
    """
    
    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file and environment"""
        # Load from .env file if it exists
        if os.path.exists(self.config_file):
            load_dotenv(self.config_file)
        
        # Load LimeTrader credentials
        self.config.update({
            'LIME_SDK_USERNAME': os.getenv('LIME_SDK_USERNAME'),
            'LIME_SDK_PASSWORD': os.getenv('LIME_SDK_PASSWORD'),
            'LIME_SDK_CLIENT_ID': os.getenv('LIME_SDK_CLIENT_ID'),
            'LIME_SDK_CLIENT_SECRET': os.getenv('LIME_SDK_CLIENT_SECRET'),
            'LIME_SDK_GRANT_TYPE': os.getenv('LIME_SDK_GRANT_TYPE', 'password'),
            'LIME_SDK_BASE_URL': os.getenv('LIME_SDK_BASE_URL', 'https://api.lime.co'),
            'LIME_SDK_AUTH_URL': os.getenv('LIME_SDK_AUTH_URL', 'https://auth.lime.co'),
        })
        
        # Load strategy parameters
        self.config.update({
            'STRATEGY_LOOKBACK_PERIOD': self._get_int('STRATEGY_LOOKBACK_PERIOD', 20),
            'STRATEGY_MOMENTUM_THRESHOLD': self._get_float('STRATEGY_MOMENTUM_THRESHOLD', 0.02),
            'STRATEGY_RISK_PER_TRADE': self._get_float('STRATEGY_RISK_PER_TRADE', 0.02),
            'STRATEGY_MAX_POSITION_SIZE': self._get_float('STRATEGY_MAX_POSITION_SIZE', 10000),
        })
        
        # Load logging configuration
        self.config.update({
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'data/logs/auraquant.log'),
        })
        
        # Load data directories
        self.config.update({
            'DATA_DIR': os.getenv('DATA_DIR', 'data'),
            'LOGS_DIR': os.getenv('LOGS_DIR', 'data/logs'),
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def _get_int(self, key: str, default: int) -> int:
        """Get integer configuration value"""
        try:
            value = os.getenv(key)
            return int(value) if value else default
        except (ValueError, TypeError):
            return default
    
    def _get_float(self, key: str, default: float) -> float:
        """Get float configuration value"""
        try:
            value = os.getenv(key)
            return float(value) if value else default
        except (ValueError, TypeError):
            return default
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean configuration value"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration"""
        validation_results = {}
        
        # Check required LimeTrader credentials
        required_lime_keys = [
            'LIME_SDK_USERNAME', 'LIME_SDK_PASSWORD', 
            'LIME_SDK_CLIENT_ID', 'LIME_SDK_CLIENT_SECRET'
        ]
        
        for key in required_lime_keys:
            value = self.config.get(key)
            validation_results[key] = bool(value and value != 'your_actual_password')
        
        # Check strategy parameters are reasonable
        lookback = self.config.get('STRATEGY_LOOKBACK_PERIOD', 0)
        validation_results['STRATEGY_LOOKBACK_PERIOD'] = 5 <= lookback <= 100
        
        momentum_threshold = self.config.get('STRATEGY_MOMENTUM_THRESHOLD', 0)
        validation_results['STRATEGY_MOMENTUM_THRESHOLD'] = 0.001 <= momentum_threshold <= 0.1
        
        risk_per_trade = self.config.get('STRATEGY_RISK_PER_TRADE', 0)
        validation_results['STRATEGY_RISK_PER_TRADE'] = 0.001 <= risk_per_trade <= 0.1
        
        return validation_results
    
    def get_credentials_dict(self) -> Dict[str, str]:
        """Get LimeTrader credentials as dictionary"""
        return {
            'username': self.config.get('LIME_SDK_USERNAME'),
            'password': self.config.get('LIME_SDK_PASSWORD'),
            'client_id': self.config.get('LIME_SDK_CLIENT_ID'),
            'client_secret': self.config.get('LIME_SDK_CLIENT_SECRET'),
            'grant_type': self.config.get('LIME_SDK_GRANT_TYPE'),
            'base_url': self.config.get('LIME_SDK_BASE_URL'),
            'auth_url': self.config.get('LIME_SDK_AUTH_URL'),
        }
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.config.get('DATA_DIR', 'data'),
            self.config.get('LOGS_DIR', 'data/logs'),
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save_config_template(self, file_path: str = ".env.template"):
        """Save configuration template"""
        template = '''# LimeTrader API Credentials
LIME_SDK_USERNAME=your_username
LIME_SDK_PASSWORD=your_password
LIME_SDK_CLIENT_ID=your_client_id
LIME_SDK_CLIENT_SECRET=your_client_secret
LIME_SDK_GRANT_TYPE=password
LIME_SDK_BASE_URL=https://api.lime.co
LIME_SDK_AUTH_URL=https://auth.lime.co

# Strategy Parameters
STRATEGY_LOOKBACK_PERIOD=20
STRATEGY_MOMENTUM_THRESHOLD=0.02
STRATEGY_RISK_PER_TRADE=0.02
STRATEGY_MAX_POSITION_SIZE=10000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=data/logs/auraquant.log

# Data Directories
DATA_DIR=data
LOGS_DIR=data/logs
'''
        
        with open(file_path, 'w') as f:
            f.write(template)
    
    def print_config_summary(self):
        """Print configuration summary"""
        print("📋 AuraQuant Configuration Summary:")
        print("=" * 40)
        
        # Credentials (masked)
        username = self.config.get('LIME_SDK_USERNAME', 'Not Set')
        client_id = self.config.get('LIME_SDK_CLIENT_ID', 'Not Set')
        password_set = bool(self.config.get('LIME_SDK_PASSWORD'))
        
        print(f"Username: {username}")
        print(f"Client ID: {client_id}")
        print(f"Password: {'✅ Set' if password_set else '❌ Not Set'}")
        
        # Strategy parameters
        print(f"\nStrategy Parameters:")
        print(f"Lookback Period: {self.config.get('STRATEGY_LOOKBACK_PERIOD')}")
        print(f"Momentum Threshold: {self.config.get('STRATEGY_MOMENTUM_THRESHOLD')}")
        print(f"Risk per Trade: {self.config.get('STRATEGY_RISK_PER_TRADE')}")
        print(f"Max Position Size: ${self.config.get('STRATEGY_MAX_POSITION_SIZE'):,.0f}")
        
        # Validation
        validation = self.validate_config()
        all_valid = all(validation.values())
        print(f"\nConfiguration Valid: {'✅ Yes' if all_valid else '❌ No'}")
        
        if not all_valid:
            print("Issues found:")
            for key, valid in validation.items():
                if not valid:
                    print(f"  ❌ {key}") 