# 📚 AuraQuant API Documentation

## Overview

AuraQuant is a professional AI-powered portfolio management platform that follows modern financial technology best practices. This API provides comprehensive portfolio analysis, real-time market data, and AI-driven insights.

### Architecture

- **Backend**: FastAPI with Python 3.8+
- **Database**: PostgreSQL (simplified to file storage for MVP)
- **Market Data**: Yahoo Finance via yfinance (primary), Alpha Vantage (fallback)
- **AI/ML**: Ollama LLM with RAG (Retrieval-Augmented Generation)
- **Trading**: LimeTrader SDK integration
- **Security**: JWT authentication, HTTPS, encrypted data

### Base URL
```
Production: https://api.auraquant.com
Development: http://localhost:8000
```

## Authentication

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user_12345",
  "token": "jwt_token_here",
  "message": "User registered successfully"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com", 
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user_12345",
  "token": "jwt_token_here",
  "profile": {
    "email": "user@example.com",
    "risk_profile": "moderate",
    "portfolios": []
  }
}
```

## Portfolio Management

### Get Live Positions
Retrieve current portfolio positions from LimeTrader or demo data.

```http
GET /api/portfolio/positions
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "account_info": {
      "account_number": "ACC123456",
      "total_value": 100000.0,
      "cash": 50000.0,
      "buying_power": 100000.0,
      "is_demo": false
    },
    "positions": [
      {
        "symbol": "AAPL",
        "quantity": 10,
        "average_cost": 150.0,
        "current_price": 175.0,
        "market_value": 1750.0,
        "unrealized_pnl": 250.0,
        "unrealized_pnl_percent": 16.67,
        "percentage": 1.75
      }
    ],
    "summary": {
      "total_portfolio_value": 100000.0,
      "total_market_value": 50000.0,
      "cash_balance": 50000.0,
      "total_unrealized_pnl": 2500.0,
      "unrealized_pnl_percentage": 5.0,
      "position_count": 5,
      "concentration_risk": 25.0,
      "tech_exposure": 40.0
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Analyze Portfolio
Analyze a portfolio with AI insights.

```http
POST /api/portfolio/analyze
Authorization: Bearer {token}
Content-Type: application/json

{
  "holdings": [
    {
      "symbol": "AAPL",
      "quantity": 10,
      "purchase_price": 150.0,
      "purchase_date": "2024-01-01"
    },
    {
      "symbol": "GOOGL", 
      "quantity": 5,
      "purchase_price": 2500.0
    }
  ],
  "cash_balance": 10000.0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_analysis": {
      "total_value": 35000.0,
      "risk_score": 6.5,
      "sharpe_ratio": 1.2,
      "diversification_score": 7.0,
      "recommendations": [
        "Consider diversifying beyond technology sector",
        "Portfolio concentration in GOOGL is high at 35%"
      ]
    },
    "ai_insights": {
      "summary": "Your portfolio shows strong growth potential but lacks diversification...",
      "strengths": ["Strong tech exposure", "Quality companies"],
      "concerns": ["High concentration risk", "Sector overweight"],
      "recommendations": ["Add bonds or REITs", "Consider international exposure"]
    }
  }
}
```

### Risk Profile Assessment
Assess user risk tolerance through questionnaire.

```http
POST /api/portfolio/risk-profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "investment_goals": "Long-term growth",
  "time_horizon": 10,
  "risk_comfort": 4,
  "market_experience": "Intermediate",
  "reaction_to_loss": "Hold and wait for recovery"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "risk_profile": "Moderate",
    "risk_score": 0.65,
    "recommended_allocation": {
      "stocks": 60,
      "bonds": 35,
      "alternatives": 5
    },
    "explanation": "Based on your responses, you have a moderate risk profile..."
  }
}
```

## AI Chat Interface

### Chat with AI Advisor
Get AI-powered financial advice and portfolio insights.

```http
POST /api/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "Should I rebalance my portfolio given current market conditions?",
  "portfolio_context": {
    "total_value": 100000,
    "positions": [...]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ai_response": "Based on your current portfolio allocation and market conditions...",
    "intelligence_score": 85,
    "confidence_level": 0.8,
    "response_quality": "expert",
    "analysis_enhanced": true,
    "key_insights": [
      {
        "category": "Risk Management",
        "insight": "Your tech concentration is above recommended levels",
        "confidence": 90,
        "impact_level": "high"
      }
    ],
    "top_recommendations": [
      "Consider reducing tech exposure by 10-15%",
      "Add defensive sectors like utilities or consumer staples"
    ],
    "analyzed_stocks": ["AAPL", "GOOGL", "MSFT"],
    "market_outlook": "Current market shows elevated volatility..."
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Market Data

### Get Market Data
Retrieve comprehensive market data for specified symbols.

```http
POST /api/market/data
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbols": ["AAPL", "GOOGL", "SPY"],
  "include_news": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "market_data": {
      "AAPL": {
        "price": 175.50,
        "change": 2.50,
        "change_percent": 1.45,
        "volume": 50000000,
        "market_cap": 2800000000000,
        "pe_ratio": 28.5,
        "beta": 1.2
      }
    },
    "market_sentiment": {
      "vix_level": 18.5,
      "overall_sentiment": "neutral",
      "confidence_score": 0.7
    },
    "news_items": [
      {
        "title": "Apple Reports Strong Quarterly Earnings",
        "summary": "Apple Inc. reported better than expected...",
        "source": "Reuters",
        "published_date": "2024-01-15T09:00:00Z",
        "sentiment_score": 0.6,
        "sentiment_label": "positive"
      }
    ]
  }
}
```

### Get Market Indices
Retrieve major market indices data.

```http
GET /api/market/indices
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "SPY": {
      "name": "S&P 500",
      "price": 4150.25,
      "change": 35.20,
      "change_percent": 0.85
    },
    "QQQ": {
      "name": "NASDAQ",
      "price": 350.75,
      "change": 4.25,
      "change_percent": 1.23
    },
    "VIX": {
      "name": "Volatility Index",
      "price": 18.45,
      "change": -0.85,
      "change_percent": -4.41
    }
  }
}
```

## System Status

### Health Check
Check system health and service availability.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "limetrader": true,
    "ai_advisor": true,
    "market_data": true,
    "stock_analyzer": true
  },
  "capabilities": [
    "Portfolio Analysis",
    "AI-Powered Insights", 
    "Real-time Market Data",
    "Risk Assessment",
    "Natural Language Processing"
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### System Status
Get detailed system status information.

```http
GET /api/system-status
```

**Response:**
```json
{
  "status": "active",
  "ollama_status": "Active",
  "ai_enhanced": true,
  "services": {
    "limetrader": true,
    "ai_advisor": true,
    "market_data": true,
    "stock_analyzer": true
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Detailed error message",
  "error_code": "PORTFOLIO_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

- `INVALID_TOKEN`: Authentication token is invalid or expired
- `PORTFOLIO_NOT_FOUND`: Requested portfolio does not exist
- `MARKET_DATA_UNAVAILABLE`: Market data service is temporarily unavailable
- `AI_SERVICE_ERROR`: AI/LLM service encountered an error
- `RATE_LIMIT_EXCEEDED`: Too many requests, please slow down
- `VALIDATION_ERROR`: Request data validation failed

## Rate Limits

- **Free Tier**: 100 requests per hour
- **Premium**: 1000 requests per hour
- **Enterprise**: Custom limits

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## Data Sources & Compliance

### Market Data Sources
- **Primary**: Yahoo Finance (yfinance) - 15-minute delayed quotes
- **Fallback**: Alpha Vantage API (rate limited)
- **Real-time**: Available with premium subscription

### Disclaimers
- Market data is delayed and for informational purposes only
- AI recommendations are educational, not personalized investment advice
- Past performance does not guarantee future results
- Always consult qualified financial professionals for investment decisions

### Security & Privacy
- All data transmitted over HTTPS
- Sensitive data encrypted at rest
- User financial details kept private by default
- Optional pseudonymous sharing for community features
- GDPR and CCPA compliant data handling

## SDK & Client Libraries

### Python Client
```python
from auraquant import AuraQuantClient

client = AuraQuantClient(api_key="your_api_key")
portfolio = client.get_portfolio()
analysis = client.analyze_portfolio(holdings)
```

### JavaScript Client
```javascript
import { AuraQuantAPI } from '@auraquant/api-client';

const client = new AuraQuantAPI({ apiKey: 'your_api_key' });
const portfolio = await client.getPortfolio();
const analysis = await client.analyzePortfolio(holdings);
```

## Webhooks

Subscribe to portfolio events and market alerts:

```http
POST /api/webhooks/subscribe
{
  "url": "https://your-app.com/webhook",
  "events": ["portfolio.rebalance", "market.volatility_alert"]
}
```

## Testing

### Test Environment
```
Base URL: https://api-test.auraquant.com
Test API Key: test_key_12345
```

### Mock Data
All endpoints support mock data for testing:
```http
GET /api/portfolio/positions?mock=true
```

## Support

- **Documentation**: https://docs.auraquant.com
- **Support Email**: support@auraquant.com  
- **Discord Community**: https://discord.gg/auraquant
- **GitHub Issues**: https://github.com/auraquant/api/issues

---

*Last Updated: December 2024*  
*API Version: 3.0.0* 