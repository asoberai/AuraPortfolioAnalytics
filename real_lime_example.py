"""
Real LimeTrader SDK Example
Based on official documentation: https://docs.lime.co/lime-trader-sdk/getting_started.html
"""

from lime_trader import LimeClient
from strategy import SharpeStrategy
from execution import OrderExecutor
import pandas as pd
import numpy as np


def example_with_credentials_json():
    """Example using credentials.json file"""
    print("🚀 Real LimeTrader SDK Example")
    print("=" * 40)
    
    try:
        # Method 1: Load from credentials.json file
        client = LimeClient.from_file("credentials.json")
        
        # Test connection
        account_info = client.account.get()
        print("✅ Connection successful!")
        print(f"Account: {account_info}")
        
        # Get market data example
        market_data = client.market_data.quotes("AAPL")
        print(f"📊 AAPL Market Data: {market_data}")
        
        # Initialize trading components
        strategy = SharpeStrategy()
        executor = OrderExecutor(client)
        
        # Get account balance
        balance = executor.get_account_balance()
        print(f"💰 Account Balance: ${balance:,.2f}")
        
        # Get current positions
        positions = executor.get_current_positions()
        print(f"📈 Current Positions: {len(positions)}")
        
        # Example trading signal (you would get real price data)
        mock_prices = pd.Series([180.0, 181.5, 179.2, 182.1, 183.0])
        signal = strategy.generate_signal("AAPL", mock_prices)
        print(f"🎯 Trading Signal: {signal['action']} {signal['symbol']}")
        
        return client
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Setup Instructions:")
        print("1. Update credentials.json with your actual LimeTrader credentials")
        print("2. Or set environment variables (see .env template)")
        print("3. Make sure you have access to LimeTrader API")
        return None


def example_with_environment_variables():
    """Example using environment variables"""
    print("\n🔧 Environment Variables Example")
    print("=" * 40)
    
    try:
        # Method 2: Load from environment variables
        client = LimeClient.from_env()
        
        # Test connection
        account_info = client.account.get()
        print("✅ Connection successful via environment variables!")
        
        return client
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure all LIME_SDK_* environment variables are set")
        return None


def example_with_env_file():
    """Example using .env file"""
    print("\n📁 .env File Example")
    print("=" * 40)
    
    try:
        # Method 3: Load from .env file
        client = LimeClient.from_env_file(".env")
        
        # Test connection
        account_info = client.account.get()
        print("✅ Connection successful via .env file!")
        
        return client
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure .env file has all required LIME_SDK_* variables")
        return None


def trading_example(client):
    """Example of actual trading operations"""
    if not client:
        return
        
    print("\n📊 Trading Operations Example")
    print("=" * 40)
    
    try:
        # Get account info
        account = client.account.get()
        print(f"Account ID: {account.get('account_id', 'N/A')}")
        print(f"Buying Power: ${account.get('buying_power', 0):,.2f}")
        
        # Get positions
        positions = client.account.positions()
        print(f"Current Positions: {len(positions)}")
        
        # Get market data
        quotes = client.market_data.quotes("AAPL")
        print(f"AAPL Quote: {quotes}")
        
        # Example order (commented out for safety)
        print("\n⚠️  Order example (commented out for safety):")
        print("# order = client.trading.new_order()")
        print("#     symbol='AAPL',")
        print("#     quantity=1,")
        print("#     side='buy',")
        print("#     type='market'")
        print("# )")
        
    except Exception as e:
        print(f"❌ Trading operations error: {e}")


if __name__ == "__main__":
    # Try different credential methods
    client = None
    
    # Try credentials.json first
    client = example_with_credentials_json()
    
    # If that fails, try environment variables
    if not client:
        client = example_with_environment_variables()
    
    # If that fails, try .env file
    if not client:
        client = example_with_env_file()
    
    # Run trading example if we have a client
    if client:
        trading_example(client)
    else:
        print("\n❌ Could not establish connection with any credential method")
        print("\n📚 Refer to: https://docs.lime.co/lime-trader-sdk/getting_started.html") 