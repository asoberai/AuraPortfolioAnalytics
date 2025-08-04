# AuraQuant - LimeTrader Sharpe Agent

AI-assisted trading bot designed for the LimeTrader challenge, specifically focused on maximizing the Sharpe ratio through intelligent signal generation and risk management.

## 🎯 Project Overview

AuraQuant combines momentum and mean reversion strategies to generate high-quality trading signals while maintaining optimal risk-adjusted returns. The system is built with modularity and performance monitoring at its core.

## 📁 Project Structure

```
auraquant/
├── .env                     # API credentials (create from template)
├── main.py                  # Entry point and orchestration
├── config.py                # Configuration and API key management
├── strategy.py              # Trading signal generation logic
├── execution.py             # Order execution and position management
├── data/
│   └── logs/                # Performance and trade logs
│       ├── daily_returns.csv    # Daily returns for Sharpe calculation
│       └── order_history.csv    # Trade execution history
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

1. Copy `.env` file and add your LimeTrader credentials:
```bash
LIME_API_KEY=your_actual_api_key
LIME_API_SECRET=your_actual_api_secret
LIME_ACCOUNT_ID=your_demo_account_id
```

2. Test connection:
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
- [x] API integration and testing
- [x] Basic strategy framework
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

---

**Disclaimer**: This is a trading bot for educational and competition purposes. Past performance does not guarantee future results. Always understand the risks involved in trading. 