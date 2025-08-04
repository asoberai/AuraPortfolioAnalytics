"""
AuraQuant - LimeTrader Sharpe Agent
Main entry point for the trading bot
"""

try:
    from lime_trader import LimeClient
    OFFICIAL_SDK_AVAILABLE = True
except ImportError:
    OFFICIAL_SDK_AVAILABLE = False
    print("⚠️  Official LimeTrader SDK not available")

from config import (LIME_USERNAME, LIME_PASSWORD, LIME_CLIENT_ID, 
                   LIME_CLIENT_SECRET, LIME_GRANT_TYPE, LIME_BASE_URL, LIME_AUTH_URL)
import pandas as pd
import numpy as np
import os


def test_connection():
    """Test connection to LimeTrader API"""
    if not OFFICIAL_SDK_AVAILABLE:
        print("❌ Official LimeTrader SDK not installed")
        print("💡 Install the official SDK or use demo.py for testing")
        print("   pip install lime-trader-sdk  # (when available)")
        return None
        
    try:
        # Initialize client using official SDK method
        client = LimeClient.from_env()
        
        # Test with account info
        account_info = client.account.get()
        print("✅ Connection successful!")
        print(f"Account Info: {account_info}")
        return client
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure to set all required environment variables:")
        print("   LIME_SDK_USERNAME, LIME_SDK_PASSWORD, LIME_SDK_CLIENT_ID,")
        print("   LIME_SDK_CLIENT_SECRET, LIME_SDK_BASE_URL, LIME_SDK_AUTH_URL")
        return None


def calculate_sharpe_ratio():
    """Calculate Sharpe ratio from daily returns log"""
    log_file = "data/logs/daily_returns.csv"
    
    if not os.path.exists(log_file):
        print(f"⚠️  Log file not found: {log_file}")
        return None
    
    try:
        df = pd.read_csv(log_file)
        if 'return' not in df.columns:
            print("❌ 'return' column not found in log file")
            return None
            
        # Calculate Sharpe ratio (assuming 252 trading days per year)
        mean_return = df['return'].mean()
        std_return = df['return'].std()
        
        # Add small epsilon to avoid division by zero
        sharpe = (mean_return / (std_return + 0.002)) * np.sqrt(252)
        
        print(f"📊 Sharpe Ratio: {sharpe:.4f}")
        print(f"📈 Mean Return: {mean_return:.6f}")
        print(f"📉 Std Deviation: {std_return:.6f}")
        
        return sharpe
    except Exception as e:
        print(f"❌ Error calculating Sharpe ratio: {e}")
        return None


def main():
    """Main execution function"""
    print("🚀 AuraQuant - LimeTrader Sharpe Agent")
    print("=" * 40)
    
    # Test API connection
    client = test_connection()
    
    if client:
        # Calculate current Sharpe ratio if logs exist
        calculate_sharpe_ratio()
        
        # TODO: Add strategy execution logic here
        print("\n📋 Next steps:")
        print("1. Implement strategy.py")
        print("2. Implement execution.py")
        print("3. Start trading loop")
    else:
        print("\n❌ Please check your API credentials in .env file")


if __name__ == "__main__":
    main() 