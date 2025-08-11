# AuraVest - Advanced Portfolio Analytics Platform

## Project Overview
AuraVest is a comprehensive financial portfolio management and analytics platform that allows users to:
- Add positions from any date since 2000
- Visualize current returns and performance
- Analyze risk metrics and correlations
- Run Monte Carlo simulations
- View future projections and scenarios

## Architecture
- Backend: FastAPI (Python) with JWT authentication
- Frontend: React with Material-UI and Chart.js
- Data: Yahoo Finance API for market data
- Analytics: Advanced risk models and quantitative analysis

## Development Guidelines

### Running the Application
```bash
# Backend
python main.py

# Frontend
cd frontend && npm start
```

### Environment Setup
- Python 3.10+ required
- Node.js 16+ for frontend
- Install dependencies: `pip install -r requirements.txt`
- Install frontend deps: `cd frontend && npm install`

### Demo Authentication
- Demo User: demo@auravest.com / demo123
- Admin User: admin@auravest.com / admin123

### API Endpoints
- `/auth/login` - User authentication
- `/auth/register` - User registration
- `/portfolios` - List user portfolios
- `/portfolio/{id}` - Portfolio details with analytics
- `/portfolio/{id}/holdings` - Add holdings to portfolio
- `/market/historical/{ticker}?date=YYYY-MM-DD` - Historical prices
- `/analysis/risk/*` - Risk analysis endpoints

### Frontend Routes
- `/dashboard` - Main dashboard
- `/portfolio/{id}` - Standard portfolio view
- `/portfolio/{id}/robinhood` - Robinhood-style view
- `/portfolio/{id}/analytics` - Advanced analytics dashboard
- `/portfolio/{id}/add-holding` - Add new positions

### Key Features
1. Historical Position Entry: Add positions from any date since 2000
2. Real-time Analytics: Current portfolio values and performance
3. Risk Analysis: Comprehensive risk metrics and visualizations
4. Multiple Views: Standard, Robinhood-style, and advanced analytics
5. Future Projections: Monte Carlo simulations and scenario analysis

## Testing
- Backend: `python -m pytest tests/` (when implemented)
- Frontend: `cd frontend && npm test`
- Integration: `python integration_test.py`

## License
This is a personal portfolio project for educational and demonstration purposes.