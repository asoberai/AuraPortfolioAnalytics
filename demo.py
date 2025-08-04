"""
Demo script for AuraQuant - LimeTrader Sharpe Agent
Shows Sharpe ratio calculation with mock data
"""

import os
from dotenv import load_dotenv
try:
    from lime_trader import LimeClient
    OFFICIAL_SDK_AVAILABLE = True
except ImportError:
    OFFICIAL_SDK_AVAILABLE = False
    print("⚠️  Official LimeTrader SDK not available - using fallback for demo")

from strategy import SharpeStrategy
from execution import OrderExecutor
import pandas as pd
import numpy as np

# Load environment variables
load_dotenv()


class MockClient:
    """Simple mock client for demo purposes"""
    def __init__(self):
        self.account_data = {
            'buying_power': 100000.0,
            'total_value': 100000.0,
            'cash': 50000.0
        }
    
    def get_account_info(self):
        return self.account_data
    
    # Add mock account property for new SDK compatibility
    @property 
    def account(self):
        return self
    
    def get(self):
        return self.account_data
    
    def positions(self):
        return []


def create_mock_client():
    """Create a mock client for demo purposes"""
    return MockClient()


def demo_with_mock_credentials():
    """Demo with mock credentials to show functionality"""
    print("🚀 AuraQuant Demo - LimeTrader Sharpe Agent")
    print("=" * 50)
    
    # Set up mock credentials for demo
    os.environ["LIME_SDK_USERNAME"] = "demo_user"
    os.environ["LIME_SDK_PASSWORD"] = "demo_pass"
    os.environ["LIME_SDK_CLIENT_ID"] = "demo_client_id"
    os.environ["LIME_SDK_CLIENT_SECRET"] = "demo_client_secret"
    os.environ["LIME_SDK_GRANT_TYPE"] = "password"
    os.environ["LIME_SDK_BASE_URL"] = "https://api.lime.co"
    os.environ["LIME_SDK_AUTH_URL"] = "https://auth.lime.co"
    
    # Initialize client - try official SDK first, then fallback to mock
    if OFFICIAL_SDK_AVAILABLE:
        try:
            client = LimeClient.from_env()
            print("✅ Using official LimeTrader SDK")
        except Exception as e:
            print(f"⚠️  Official SDK failed ({e}), using mock for demo")
            # Create a simple mock client
            client = create_mock_client()
    else:
        print("⚠️  Using mock client for demo (official SDK not installed)")
        client = create_mock_client()
    
    try:
        # Test connection
        try:
            account_info = client.account.get()
        except AttributeError:
            # Fallback for mock client
            account_info = client.get_account_info()
        print("✅ Connection successful!")
        print(f"Account Balance: ${account_info['buying_power']:,.2f}")
        
        # Initialize strategy and executor
        strategy = SharpeStrategy()
        executor = OrderExecutor(client)
        
        # Generate mock price data for AAPL
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        prices = pd.Series(
            180 + np.cumsum(np.random.normal(0, 2, 50)),
            index=dates
        )
        
        print(f"\n📈 Generated {len(prices)} days of mock AAPL price data")
        print(f"Price range: ${prices.min():.2f} - ${prices.max():.2f}")
        
        # Generate trading signal
        signal = strategy.generate_signal("AAPL", prices)
        print(f"\n🎯 Trading Signal Generated:")
        print(f"   Symbol: {signal['symbol']}")
        print(f"   Action: {signal['action']}")
        print(f"   Strength: {signal['strength']:.2f}")
        print(f"   Current Price: ${signal['current_price']:.2f}")
        
        # Test order execution (mock)
        if signal['action'] != "HOLD":
            success = executor.execute_signal(signal)
            if success:
                print(f"✅ Order executed successfully")
            else:
                print(f"❌ Order execution failed")
        
        # Calculate Sharpe ratio from existing log
        print(f"\n📊 Sharpe Ratio Calculation:")
        df = pd.read_csv("data/logs/daily_returns.csv")
        mean_return = df['return'].mean()
        std_return = df['return'].std()
        sharpe = (mean_return / (std_return + 0.002)) * np.sqrt(252)
        
        print(f"   Mean Daily Return: {mean_return:.4f}")
        print(f"   Daily Volatility: {std_return:.4f}")
        print(f"   Sharpe Ratio: {sharpe:.4f}")
        
        # Performance metrics
        returns = df['return'].tolist()
        metrics = strategy.update_performance_metrics(returns)
        print(f"\n📈 Performance Metrics:")
        print(f"   Total Return: {metrics['total_return']:.4f}")
        print(f"   Volatility: {metrics['volatility']:.4f}")
        print(f"   Number of Trades: {metrics['num_trades']}")
        
        # Risk metrics
        risk_metrics = executor.get_risk_metrics()
        print(f"\n🛡️  Risk Metrics:")
        print(f"   Account Balance: ${risk_metrics['account_balance']:,.2f}")
        print(f"   Total Exposure: ${risk_metrics['total_exposure']:,.2f}")
        print(f"   Leverage: {risk_metrics['leverage']:.2f}x")
        
        print(f"\n✅ Demo completed successfully!")
        print(f"🔧 Next steps:")
        print(f"   1. Add real LimeTrader API credentials to .env")
        print(f"   2. Replace lime_trader_sdk.py with official SDK")
        print(f"   3. Implement advanced strategy logic")
        print(f"   4. Add real-time market data integration")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    demo_with_mock_credentials() 