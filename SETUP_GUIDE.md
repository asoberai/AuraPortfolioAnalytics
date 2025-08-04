# AuraQuant Setup Guide

## 🚀 Complete Setup for LimeTrader Sharpe Agent

This guide helps you set up **AuraQuant**, a trading bot designed for the LimeTrader challenge focused on **Sharpe ratio optimization**.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **LimeTrader account** with API access
3. **Network connectivity** to LimeTrader data centers (VPN/cross-connect)

## 🛠️ Installation Steps

### Step 1: Environment Setup
```bash
# Clone/navigate to project directory
cd finance

# Create virtual environment (recommended)
python3 -m venv lime_env
source lime_env/bin/activate  # On Windows: lime_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: LimeTrader SDK Installation

**Currently**: The official `lime-trader-sdk` package is not yet available on PyPI.

**When Available**: Run `pip install lime-trader-sdk`

**For Now**: The project includes fallback support for development and testing.

## 🔑 Credential Configuration

Based on [LimeTrader SDK Documentation](https://docs.lime.co/lime-trader-sdk/getting_started.html), you have **3 options**:

### Option 1: Environment Variables (.env file) - **Recommended**

Create/update `.env` file with your actual credentials:
```bash
LIME_SDK_USERNAME=armaan0oberai@gmail.com
LIME_SDK_PASSWORD=your_actual_password
LIME_SDK_CLIENT_ID=trading-app-dmo-c383
LIME_SDK_CLIENT_SECRET=4aa00156c97b4ba3952e81fa3e3d7159
LIME_SDK_GRANT_TYPE=password
LIME_SDK_BASE_URL=https://api.lime.co
LIME_SDK_AUTH_URL=https://auth.lime.co
```

**⚠️ Important**: Replace `your_actual_password` with your real LimeTrader password!

### Option 2: JSON Credentials File

Your `credentials.json` is already configured with your credentials:
```json
{
    "username": "armaan0oberai@gmail.com",
    "password": "<your_password>",
    "client_id": "trading-app-dmo-c383",
    "client_secret": "4aa00156c97b4ba3952e81fa3e3d7159",
    "grant_type": "password",
    "base_url": "https://api.lime.co",
    "auth_url": "https://auth.lime.co"
}
```

**⚠️ Important**: Update the `password` field with your actual LimeTrader password!

### Option 3: Environment Variables (System-wide)

Set these environment variables with your actual values:
```bash
export LIME_SDK_USERNAME=armaan0oberai@gmail.com
export LIME_SDK_PASSWORD=your_actual_password
export LIME_SDK_CLIENT_ID=trading-app-dmo-c383
export LIME_SDK_CLIENT_SECRET=4aa00156c97b4ba3952e81fa3e3d7159
export LIME_SDK_GRANT_TYPE=password
export LIME_SDK_BASE_URL=https://api.lime.co
export LIME_SDK_AUTH_URL=https://auth.lime.co
```

**⚠️ Important**: Replace `your_actual_password` with your real password!

## 🧪 Testing Your Setup

### Test 1: Credential Setup (Interactive)
```bash
python setup_credentials.py
```
Interactive script to configure your credentials with all methods.

### Test 2: Demo Mode (Always Works)
```bash
python demo.py
```
This runs with mock data and shows all features working.

### Test 3: Real Connection (Requires Password)
```bash
python main.py
```
Tests actual LimeTrader API connection with your credentials.

### Test 4: Official SDK Examples
```bash
python real_lime_example.py
```
Shows all credential methods and SDK usage patterns with your actual credentials.

## 📊 Understanding the Output

**Expected Demo Output:**
```
🚀 AuraQuant Demo - LimeTrader Sharpe Agent
==================================================
✅ Connection successful!
Account Balance: $100,000.00

📈 Generated 50 days of mock AAPL price data
Price range: $180.00 - $185.50

🎯 Trading Signal Generated:
   Symbol: AAPL
   Action: BUY/SELL/HOLD
   Strength: 0.75

📊 Sharpe Ratio Calculation:
   Mean Daily Return: 0.0064
   Daily Volatility: 0.0120
   Sharpe Ratio: 7.3017

✅ Demo completed successfully!
```

## 🎯 Strategy Overview

**AuraQuant** implements:

1. **Momentum Signals**: Identifies trending price movements
2. **Mean Reversion Signals**: Captures oversold/overbought conditions
3. **Combined Logic**: Weighted signal generation for optimal Sharpe ratio
4. **Risk Management**: Position sizing with 2% max risk per trade
5. **Performance Tracking**: Real-time Sharpe ratio calculation

## 📁 Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point, connection testing |
| `strategy.py` | Trading signal generation |
| `execution.py` | Order placement and management |
| `demo.py` | Working demonstration with fallback |
| `real_lime_example.py` | Official SDK usage examples |
| `config.py` | Credential management |
| `data/logs/daily_returns.csv` | Returns for Sharpe calculation |

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'lime_trader'"
- **Solution**: The official SDK isn't installed yet. Use `python demo.py` for testing.

### "Connection failed: Invalid credentials"
- **Solution**: Update your credentials in `.env` or `credentials.json`
- **Check**: Ensure all required fields are filled
- **Verify**: Your LimeTrader account has API access

### "Network connectivity issues"
- **Solution**: Ensure VPN connection to LimeTrader data centers
- **Check**: Contact LimeTrader for network setup requirements

### Missing log files
- **Solution**: Run the demo/main script once to generate sample logs
- **Files created**: `data/logs/daily_returns.csv`, `data/logs/order_history.csv`

## 🔄 Migration from Mock to Real SDK

When the official SDK becomes available:

1. **Install**: `pip install lime-trader-sdk`
2. **Update**: No code changes needed - automatic fallback handling
3. **Test**: Run `python main.py` to verify real connection
4. **Deploy**: Ready for live trading

## 📈 Next Steps

1. **Configure Real Credentials**: Update `.env` with your LimeTrader API credentials
2. **Test Connection**: Verify API connectivity with `python main.py`
3. **Customize Strategy**: Modify parameters in `strategy.py`
4. **Monitor Performance**: Watch Sharpe ratio in real-time
5. **Scale Up**: Add more symbols and advanced strategies

## 📚 References

- [LimeTrader SDK Documentation](https://docs.lime.co/lime-trader-sdk/getting_started.html)
- [Configuration Guide](https://docs.lime.co/lime-trader-sdk/configuring_client.html)
- [Trading API Documentation](https://docs.lime.co/trader/)

## 🆘 Support

**For SDK Issues**: Refer to [LimeTrader Documentation](https://docs.lime.co/)
**For AuraQuant Issues**: Check `data/logs/` files and error messages
**For Credential Issues**: Verify all required fields in your credential configuration

---

**Ready to trade with optimal Sharpe ratios!** 🚀📊 