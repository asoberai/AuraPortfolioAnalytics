# AuraQuant - LimeTrader Sharpe Agent

AI-assisted trading bot designed for the LimeTrader challenge, specifically focused on maximizing the Sharpe ratio through intelligent signal generation and risk management.

## 🎯 Project Overview

AuraQuant combines momentum and mean reversion strategies to generate high-quality trading signals while maintaining optimal risk-adjusted returns. The system is built with modularity and performance monitoring at its core.

## 📁 Project Structure

```
auraquant/
├── .env                     # Your LimeTrader credentials (add password)
├── main.py                  # Entry point and connection testing
├── config.py                # Configuration loading
├── strategy.py              # Trading strategy (momentum + mean reversion)
├── execution.py             # Order execution and risk management  
├── demo.py                  # Demo with mock data (always works)
├── real_lime_example.py     # SDK usage examples
├── data/
│   └── logs/                # Performance logs
│       └── daily_returns.csv    # For Sharpe ratio calculation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python3 -m venv lime_env
source lime_env/bin/activate  # On Windows: lime_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. API Configuration

**Simple setup - just add your password:**

1. Copy the example file: `cp .env.example .env`
2. Edit `.env` and replace `your_actual_password` with your real LimeTrader password
3. Your credentials are already configured:
   - Username: `armaan0oberai@gmail.com`
   - Client ID: `trading-app-dmo-c383`
   - Client Secret: `4aa00156c97b4ba3952e81fa3e3d7159`

**Test connection:**
```bash
python main.py
```

### 3. Strategy Components

#### **strategy.py**
- **Momentum Signals**: Identifies trending movements
- **Mean Reversion Signals**: Captures oversold/overbought conditions
- **Combined Logic**: Weighted signal generation
- **Position Sizing**: Risk-adjusted position calculation

#### **execution.py**
- **Order Management**: Automated order placement
- **Risk Controls**: Position size limits and exposure management
- **Performance Logging**: Real-time P&L tracking
- **Sharpe Monitoring**: Continuous ratio calculation

#### **main.py**
- **Orchestration**: Coordinates strategy and execution
- **Connection Testing**: API health checks
- **Performance Reporting**: Daily Sharpe ratio updates

## 📊 Sharpe Ratio Calculation

The system continuously monitors performance through daily return logging:

```python
# Automatic calculation from logged returns
df = pd.read_csv("data/logs/daily_returns.csv")
sharpe = (df['return'].mean() / (df['return'].std() + 0.002)) * np.sqrt(252)
```

**Target Metrics:**
- Sharpe Ratio: > 1.5
- Maximum Drawdown: < 10%
- Win Rate: > 55%

## 🛡️ Risk Management

- **Position Sizing**: Max 2% risk per trade
- **Exposure Limits**: Total exposure capped at account size
- **Stop Losses**: Automatic risk controls
- **Diversification**: Multi-symbol trading capability

## 📈 Performance Monitoring

### Real-time Metrics
- Live Sharpe ratio calculation
- Daily/weekly performance summaries
- Risk exposure monitoring
- Trade execution analytics

### Log Files
- `daily_returns.csv`: Daily P&L for Sharpe calculation
- `order_history.csv`: Complete trade execution log

## 🔧 Development Roadmap

- [x] Core infrastructure setup
- [x] Official LimeTrader SDK integration
- [x] Multiple credential configuration methods
- [x] Basic strategy framework
- [x] Comprehensive examples and documentation
- [ ] Advanced signal optimization
- [ ] Machine learning integration
- [ ] Real-time dashboard
- [ ] Backtesting framework

## 🚨 Important Notes

- **Demo Account**: Always test with demo account first
- **Risk Management**: Never risk more than you can afford to lose
- **API Limits**: Respect LimeTrader rate limits
- **Monitoring**: Always monitor positions during market hours

## 📞 Support

For questions or issues:
1. Check API documentation
2. Review log files in `data/logs/`
3. Verify `.env` configuration
4. Test connection with `python main.py`

## 🚀 Quick Start Commands
```bash
# Test the setup with demo/fallback
python demo.py

# Run with real credentials (after updating .env or credentials.json)
python main.py

# Try official SDK examples
python real_lime_example.py

# Check Sharpe ratio calculation
python -c "from main import calculate_sharpe_ratio; calculate_sharpe_ratio()"
```

## 📚 Official Documentation

This project now uses the official **LimeTrader SDK** based on their documentation:
- [Getting Started](https://docs.lime.co/lime-trader-sdk/getting_started.html)
- [Configuration Guide](https://docs.lime.co/lime-trader-sdk/configuring_client.html)
- [Trading Examples](https://docs.lime.co/lime-trader-sdk/examples.html)

The project is ready for the LimeTrader challenge with official SDK integration and **Sharpe ratio optimization** focus! 🚀

---

**Disclaimer**: This is a trading bot for educational and competition purposes. Past performance does not guarantee future results. Always understand the risks involved in trading. 