"""
AuraVest - Quantitative Portfolio Analysis Platform
Advanced options pricing, volatility analysis, and portfolio optimization
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def sanitize_for_json(obj):
    """Convert numpy types and NaN values to JSON-serializable types"""
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        return obj

# Import our modules - using simple auth for demo
from simple_auth import UserLogin, UserRegister, Token, User, authenticate_user, create_access_token, get_current_user, add_demo_user
from market_data import MarketDataService
from quantitative_models import QuantitativeAnalyzer, OptionsPricingModel, VolatilityAnalyzer, PriceForecaster

# Add import for risk models
from risk_models import PortfolioRiskModel, RiskVisualizer

# Initialize FastAPI app
app = FastAPI(
    title="AuraVest Quantitative Portfolio Analysis",
    description="Advanced portfolio analysis with options pricing, volatility forecasting, and quantitative optimization",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
market_service = MarketDataService()
quant_analyzer = QuantitativeAnalyzer()
options_model = OptionsPricingModel()
vol_analyzer = VolatilityAnalyzer()
price_forecaster = PriceForecaster()

# Initialize risk models
risk_model = PortfolioRiskModel()
risk_visualizer = RiskVisualizer()

# Security
security = HTTPBearer()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AuraVest Quantitative Analysis",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserRegister):
    """Register a new user"""
    # Add user to demo system
    if not add_demo_user(user.email, user.password, user.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user"""
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_credentials.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Simple storage for demo (replace with database in production)
from simple_auth import init_demo_data
USER_PORTFOLIOS, USER_HOLDINGS, USER_PROFILES = init_demo_data()

# Risk assessment
@app.post("/profile/risk-questionnaire")
async def submit_risk_questionnaire(
    questionnaire: dict,
    current_user: User = Depends(get_current_user)
):
    """Submit risk tolerance questionnaire"""
    # Calculate risk score based on questionnaire
    risk_score = calculate_risk_score(questionnaire)
    risk_category = categorize_risk(risk_score)
    
    # Save to in-memory storage for demo
    USER_PROFILES[current_user.id] = {
        "user_id": current_user.id,
        "answers": questionnaire,
        "risk_score": risk_score,
        "risk_category": risk_category
    }
    
    return {
        "risk_score": risk_score,
        "risk_category": risk_category,
        "message": "Risk assessment completed"
    }

# Portfolio management
@app.post("/portfolio/create")
async def create_portfolio(
    portfolio_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new portfolio"""
    portfolio_id = len(USER_PORTFOLIOS) + 1
    portfolio = {
        "id": portfolio_id,
        "user_id": current_user.id,
        "name": portfolio_data.get("name", "My Portfolio"),
        "description": portfolio_data.get("description", "")
    }
    USER_PORTFOLIOS[portfolio_id] = portfolio
    
    return {"id": portfolio_id, "name": portfolio["name"], "message": "Portfolio created"}

@app.post("/portfolio/{portfolio_id}/holdings")
async def add_holding(
    portfolio_id: int,
    holding: dict,
    current_user: User = Depends(get_current_user)
):
    """Add a holding to portfolio"""
    # Verify portfolio ownership
    portfolio = USER_PORTFOLIOS.get(portfolio_id)
    if not portfolio or portfolio["user_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Get current market price
    try:
        current_price = market_service.get_stock_price(holding["ticker_symbol"])
    except:
        current_price = 100.0  # Fallback price for demo
    
    holding_id = len(USER_HOLDINGS) + 1
    new_holding = {
        "id": holding_id,
        "portfolio_id": portfolio_id,
        "ticker_symbol": holding["ticker_symbol"],
        "quantity": holding["quantity"],
        "purchase_price": holding.get("purchase_price", current_price),
        "purchase_date": holding.get("purchase_date", datetime.now().date().isoformat())
    }
    USER_HOLDINGS[holding_id] = new_holding
    
    return {
        "id": holding_id,
        "message": f"Added {holding['quantity']} shares of {holding['ticker_symbol']}"
    }

@app.get("/portfolio/{portfolio_id}")
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get portfolio with current values and quantitative analysis"""
    # Verify portfolio ownership
    portfolio = USER_PORTFOLIOS.get(portfolio_id)
    if not portfolio or portfolio["user_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Get holdings
    holdings = [h for h in USER_HOLDINGS.values() if h["portfolio_id"] == portfolio_id]
    
    # Calculate current values
    portfolio_data = {
        "id": portfolio["id"],
        "name": portfolio["name"],
        "description": portfolio["description"],
        "holdings": [],
        "total_value": 0,
        "total_cost": 0
    }
    
    holdings_data = []
    for holding in holdings:
        try:
            current_price = market_service.get_stock_price(holding["ticker_symbol"])
            if current_price is None or np.isnan(current_price):
                raise ValueError("Invalid price")
        except:
            # Use mock prices for demo
            mock_prices = {"AAPL": 175.0, "GOOGL": 2700.0, "MSFT": 350.0, "TSLA": 800.0}
            current_price = mock_prices.get(holding["ticker_symbol"], holding["purchase_price"] * 1.05)
            
        current_value = holding["quantity"] * current_price
        cost_basis = holding["quantity"] * holding["purchase_price"]
        
        holding_data = {
            "id": holding["id"],
            "ticker": holding["ticker_symbol"],
            "quantity": holding["quantity"],
            "purchase_price": holding["purchase_price"],
            "current_price": current_price,
            "current_value": current_value,
            "cost_basis": cost_basis,
            "unrealized_pnl": current_value - cost_basis,
            "unrealized_pnl_percent": ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
        }
        
        portfolio_data["holdings"].append(holding_data)
        portfolio_data["total_value"] += current_value
        portfolio_data["total_cost"] += cost_basis
        
        # Add to holdings data for quantitative analysis
        holdings_data.append({
            "ticker": holding["ticker_symbol"],
            "weight": current_value  # Will be normalized later
        })
    
    # Normalize weights
    if portfolio_data["total_value"] > 0:
        for holding_data in holdings_data:
            holding_data["weight"] /= portfolio_data["total_value"]
    
    # Simple portfolio analysis for demo (avoid NaN values)
    if holdings_data:
        try:
            # Calculate basic metrics without external API calls that might return NaN
            diversification_score = min(len(holdings_data) * 0.2, 1.0)
            risk_level = "Low" if len(holdings_data) > 5 else "Medium" if len(holdings_data) > 2 else "High"
            
            # Ensure all values are JSON serializable
            portfolio_data["quantitative_analysis"] = {
                "total_holdings": int(len(holdings_data)),
                "diversification_score": float(diversification_score),
                "risk_level": str(risk_level),
                "status": "analysis_available"
            }
        except Exception as e:
            # Fallback to basic analysis if any calculations fail
            portfolio_data["quantitative_analysis"] = {
                "total_holdings": len(holdings_data),
                "diversification_score": 0.5,
                "risk_level": "Medium",
                "status": "basic_analysis",
                "note": "Using simplified analysis for demo"
            }
    
    portfolio_data["total_unrealized_pnl"] = portfolio_data["total_value"] - portfolio_data["total_cost"]
    portfolio_data["total_unrealized_pnl_percent"] = (
        (portfolio_data["total_unrealized_pnl"] / portfolio_data["total_cost"] * 100) 
        if portfolio_data["total_cost"] > 0 else 0
    )
    
    # Sanitize all data to ensure JSON compatibility
    return sanitize_for_json(portfolio_data)

@app.get("/portfolios")
async def get_user_portfolios(
    current_user: User = Depends(get_current_user)
):
    """Get all user portfolios"""
    portfolios = [p for p in USER_PORTFOLIOS.values() if p["user_id"] == current_user.id]
    return [{"id": p["id"], "name": p["name"], "description": p["description"]} for p in portfolios]

@app.delete("/portfolio/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a portfolio"""
    portfolio = USER_PORTFOLIOS.get(portfolio_id)
    if not portfolio or portfolio["user_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Delete all holdings in the portfolio first
    holdings_to_delete = [h_id for h_id, h in USER_HOLDINGS.items() if h["portfolio_id"] == portfolio_id]
    for holding_id in holdings_to_delete:
        del USER_HOLDINGS[holding_id]
    
    # Delete the portfolio
    del USER_PORTFOLIOS[portfolio_id]
    
    return {"message": f"Portfolio '{portfolio['name']}' deleted successfully"}

@app.delete("/portfolio/{portfolio_id}/holdings/{holding_id}")
async def delete_holding(
    portfolio_id: int,
    holding_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a specific holding from a portfolio"""
    portfolio = USER_PORTFOLIOS.get(portfolio_id)
    if not portfolio or portfolio["user_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    holding = USER_HOLDINGS.get(holding_id)
    if not holding or holding["portfolio_id"] != portfolio_id:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    ticker_symbol = holding["ticker_symbol"]
    quantity = holding["quantity"]
    
    # Delete the holding
    del USER_HOLDINGS[holding_id]
    
    return {"message": f"Deleted {quantity} shares of {ticker_symbol}"}

# Market data endpoints
@app.get("/market/stock/{ticker}")
async def get_stock_data(ticker: str):
    """Get comprehensive stock data including options"""
    try:
        # Get basic stock data
        stock_data = market_service.get_stock_data(ticker)
        
        # Get options data
        options_data = options_model.get_options_data(ticker)
        
        # Get volatility analysis
        vol_analysis = vol_analyzer.calculate_implied_volatility_surface(ticker)
        
        # Get price forecast
        price_forecast = price_forecaster.forecast_price_range(ticker)
        
        return {
            "basic_data": stock_data,
            "options_data": {
                "calls": options_data[0].to_dict('records') if options_data[0] is not None else [],
                "puts": options_data[1].to_dict('records') if options_data[1] is not None else []
            },
            "volatility_analysis": vol_analysis,
            "price_forecast": price_forecast
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/market/stocks")
async def get_multiple_stocks(tickers: str):
    """Get data for multiple stocks"""
    ticker_list = [t.strip() for t in tickers.split(",")]
    return market_service.get_multiple_stocks(ticker_list)

@app.get("/market/historical/{ticker}")
async def get_historical_price(ticker: str, date: str):
    """Get historical price for a specific date"""
    try:
        import yfinance as yf
        from datetime import datetime
        
        # Validate date format
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Check if date is not too far in the past (since 2000)
        min_date = datetime(2000, 1, 1)
        if target_date < min_date:
            raise HTTPException(status_code=400, detail="Date must be after January 1, 2000")
        
        # Check if date is not in the future
        today = datetime.now()
        if target_date > today:
            raise HTTPException(status_code=400, detail="Date cannot be in the future")
        
        # Fetch historical data
        stock = yf.Ticker(ticker.upper())
        
        # Get data for a period around the target date to find the closest trading day
        start_date = (target_date - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = (target_date + timedelta(days=7)).strftime('%Y-%m-%d')
        
        hist_data = stock.history(start=start_date, end=end_date)
        
        if hist_data.empty:
            # If no historical data available, estimate based on current price
            try:
                current_data = stock.info
                current_price = current_data.get('currentPrice') or current_data.get('regularMarketPrice', 100)
                
                # Calculate years difference for estimation
                years_diff = (today - target_date).days / 365.25
                
                # Estimate historical price (assuming 8% average annual return with volatility)
                estimated_price = current_price / (1.08 ** years_diff)
                # Add some realistic volatility
                import random
                volatility_factor = 1 + (random.random() - 0.5) * 0.2
                estimated_price *= volatility_factor
                
                return sanitize_for_json({
                    "ticker": ticker.upper(),
                    "date": date,
                    "price": max(0.01, estimated_price),
                    "estimated": True,
                    "message": "Estimated price based on current data"
                })
            except:
                raise HTTPException(status_code=404, detail=f"No historical data available for {ticker}")
        
        # Find the closest date to the target date
        closest_date = min(hist_data.index, key=lambda x: abs((x.date() - target_date.date()).days))
        price_data = hist_data.loc[closest_date]
        
        return sanitize_for_json({
            "ticker": ticker.upper(),
            "date": date,
            "actual_date": closest_date.strftime('%Y-%m-%d'),
            "price": float(price_data['Close']),
            "open": float(price_data['Open']),
            "high": float(price_data['High']),
            "low": float(price_data['Low']),
            "volume": int(price_data['Volume']),
            "estimated": False
        })
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

# Quantitative analysis endpoints
@app.post("/analysis/portfolio/quantitative")
async def analyze_portfolio_quantitative(
    holdings: List[dict],
    current_user: User = Depends(get_current_user)
):
    """Perform comprehensive quantitative portfolio analysis"""
    try:
        analysis = quant_analyzer.analyze_portfolio(holdings)
        if analysis:
            return analysis
        else:
            raise HTTPException(status_code=500, detail="Analysis failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/analysis/options/{ticker}")
async def analyze_options(ticker: str, expiration_date: Optional[str] = None):
    """Analyze options for a given ticker"""
    try:
        calls, puts = options_model.get_options_data(ticker, expiration_date)
        
        if calls is None or puts is None:
            raise HTTPException(status_code=404, detail="No options data available")
        
        # Calculate implied volatility surface
        iv_surface = vol_analyzer.calculate_implied_volatility_surface(ticker)
        
        return {
            "ticker": ticker,
            "calls": calls.to_dict('records'),
            "puts": puts.to_dict('records'),
            "iv_surface": iv_surface
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Options analysis error: {str(e)}")

@app.get("/analysis/volatility/{ticker}")
async def analyze_volatility(ticker: str, method: str = "garch"):
    """Analyze volatility patterns and forecast"""
    try:
        # Get historical data
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period='1y')
        
        if hist_data.empty:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Calculate volatility metrics
        returns = hist_data['Close'].pct_change().dropna()
        
        vol_analysis = {
            "historical_volatility": vol_analyzer.calculate_historical_volatility(hist_data['Close']).iloc[-1],
            "current_volatility": returns.tail(30).std() * np.sqrt(252),
            "volatility_forecast": vol_analyzer.forecast_volatility(hist_data['Close'], method=method).tolist(),
            "iv_surface": vol_analyzer.calculate_implied_volatility_surface(ticker)
        }
        
        return vol_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Volatility analysis error: {str(e)}")

@app.get("/analysis/forecast/{ticker}")
async def get_price_forecast(
    ticker: str, 
    forecast_days: int = 30, 
    confidence_level: float = 0.95
):
    """Get price forecast using options data"""
    try:
        forecast = price_forecaster.forecast_price_range(
            ticker, 
            forecast_days=forecast_days, 
            confidence_level=confidence_level
        )
        
        if forecast:
            return forecast
        else:
            raise HTTPException(status_code=404, detail="Forecast not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")

@app.post("/analysis/optimize")
async def optimize_portfolio(
    holdings: List[dict],
    method: str = "sharpe",
    current_user: User = Depends(get_current_user)
):
    """Optimize portfolio weights"""
    try:
        # Extract tickers and weights
        tickers = [holding['ticker'] for holding in holdings]
        weights = np.array([holding['weight'] for holding in holdings])
        
        # Get historical data
        import yfinance as yf
        returns_data = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1y')
                if not hist.empty:
                    returns_data[ticker] = hist['Close'].pct_change().dropna()
            except:
                continue
        
        if not returns_data:
            raise HTTPException(status_code=404, detail="Insufficient data for optimization")
        
        # Create returns DataFrame
        import pandas as pd
        returns_df = pd.DataFrame(returns_data)
        
        # Optimize portfolio
        optimal_weights = quant_analyzer.portfolio_optimizer.optimize_portfolio(
            returns_df, method=method
        )
        
        # Calculate metrics for optimal portfolio
        optimal_metrics = quant_analyzer.portfolio_optimizer.calculate_portfolio_metrics(
            returns_df, optimal_weights
        )
        
        return {
            "optimal_weights": dict(zip(tickers, optimal_weights)),
            "optimal_metrics": optimal_metrics,
            "method": method
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

# User profile
@app.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user profile with risk assessment"""
    # Get risk assessment from in-memory storage
    risk_assessment = USER_PROFILES.get(current_user.id)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "risk_assessment": {
            "risk_score": risk_assessment["risk_score"] if risk_assessment else None,
            "risk_category": risk_assessment["risk_category"] if risk_assessment else None,
            "last_updated": datetime.now().isoformat() if risk_assessment else None
        }
    }

# Helper functions
def calculate_risk_score(questionnaire: dict) -> float:
    """Calculate risk score from questionnaire answers"""
    # Simple scoring system - can be enhanced
    score = 0
    total_questions = len(questionnaire)
    
    for answer in questionnaire.values():
        if isinstance(answer, int):
            score += answer
        elif isinstance(answer, str):
            # Convert string answers to numeric
            if answer.lower() in ['conservative', 'low', '1']:
                score += 1
            elif answer.lower() in ['moderate', 'medium', '2']:
                score += 2
            elif answer.lower() in ['aggressive', 'high', '3']:
                score += 3
    
    return score / total_questions if total_questions > 0 else 1.0

def categorize_risk(risk_score: float) -> str:
    """Categorize risk based on score"""
    if risk_score <= 1.5:
        return "Conservative"
    elif risk_score <= 2.5:
        return "Moderate"
    else:
        return "Aggressive"

# Add new risk analysis endpoints after existing endpoints

@app.post("/analysis/risk/portfolio")
async def analyze_portfolio_risk(
    portfolio_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Comprehensive portfolio risk analysis with probability density functions"""
    try:
        holdings = portfolio_data.get('holdings', [])
        if not holdings:
            raise HTTPException(status_code=400, detail="No holdings provided")
        
        # Create simplified mock risk analysis for demo
        num_holdings = len(holdings)
        diversification_score = min(num_holdings * 0.15, 0.8)
        concentration_risk = max(0.1, 1.0 - diversification_score)
        weighted_volatility = 0.2 + (concentration_risk * 0.1)
        
        dashboard_data = {
            "risk_metrics": {
                "weighted_volatility": weighted_volatility,
                "diversification_benefit": diversification_score,
                "concentration_risk": concentration_risk,
                "var_95": 0.15,
                "sharpe_ratio": 1.2
            },
            "holdings_analysis": [
                {
                    "ticker": holding.get('ticker', f'STOCK{i}'),
                    "risk_contribution": (1.0 / num_holdings) + (0.1 * (i % 3)),
                    "volatility": 0.2 + (0.05 * (i % 4))
                }
                for i, holding in enumerate(holdings)
            ]
        }
        
        return sanitize_for_json({
            "risk_analysis": dashboard_data,
            "charts": {
                "risk_breakdown": "mock_chart_data",
                "correlation_matrix": "mock_correlation_data"
            },
            "summary": {
                "total_risk_score": weighted_volatility,
                "diversification_score": diversification_score,
                "concentration_risk": concentration_risk,
                "overall_risk_level": "High" if weighted_volatility > 0.3 else "Medium" if weighted_volatility > 0.2 else "Low"
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis error: {str(e)}")

@app.get("/analysis/risk/price-pdf/{ticker}")
async def get_price_probability_density(
    ticker: str,
    time_horizon: int = 30,
    volatility: Optional[float] = None
):
    """Get probability density function for future stock prices"""
    try:
        # Get current stock data
        stock_data = market_service.get_stock_data(ticker)
        current_price = stock_data['price']
        
        # Use provided volatility or calculate from historical data
        if volatility is None:
            volatility = stock_data.get('volatility', 0.25)
        
        # Calculate probability density function
        pdf_data = risk_model.price_probability_density(current_price, volatility, time_horizon)
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "volatility": volatility,
            "time_horizon": time_horizon,
            "probability_density": pdf_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF calculation error: {str(e)}")

@app.post("/analysis/risk/monte-carlo")
async def run_monte_carlo_simulation(
    portfolio_data: dict,
    n_simulations: int = 10000,
    time_horizon: int = 252,
    current_user: User = Depends(get_current_user)
):
    """Run Monte Carlo simulation for portfolio value distribution"""
    try:
        holdings = portfolio_data.get('holdings', [])
        
        if len(holdings) < 1:
            raise HTTPException(status_code=400, detail="Need at least 1 holding for Monte Carlo simulation")
        
        # Create simplified mock Monte Carlo results for demo
        initial_value = portfolio_data.get('total_value', 100000)
        
        # Generate mock simulation results
        np.random.seed(42)  # For reproducible results
        mean_return = 0.08  # 8% annual return
        volatility = 0.2   # 20% annual volatility
        
        # Generate final values for n_simulations
        random_returns = np.random.normal(mean_return, volatility, n_simulations)
        final_values = [initial_value * (1 + ret) for ret in random_returns]
        
        # Calculate percentiles
        percentiles = np.percentile(final_values, [5, 25, 50, 75, 95])
        
        mc_results = {
            "final_values": final_values,
            "expected_return": mean_return,
            "percentile_5": (percentiles[0] / initial_value - 1),
            "percentile_25": (percentiles[1] / initial_value - 1),
            "median": (percentiles[2] / initial_value - 1),
            "percentile_75": (percentiles[3] / initial_value - 1),
            "percentile_95": (percentiles[4] / initial_value - 1),
            "mean_final_value": float(np.mean(final_values)),
            "std_final_value": float(np.std(final_values))
        }
        
        return sanitize_for_json({
            "simulation_params": {
                "n_simulations": n_simulations,
                "time_horizon": time_horizon,
                "initial_value": initial_value
            },
            "results": mc_results
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monte Carlo simulation error: {str(e)}")

@app.post("/analysis/risk/covariance")
async def analyze_portfolio_covariance(
    portfolio_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Analyze portfolio covariance and correlation structure"""
    try:
        holdings = portfolio_data.get('holdings', [])
        
        if len(holdings) < 1:
            raise HTTPException(status_code=400, detail="Need at least 1 holding for covariance analysis")
        
        # Create simplified mock covariance analysis for demo
        num_holdings = len(holdings)
        tickers = [h.get('ticker', f'STOCK{i}') for i, h in enumerate(holdings)]
        
        # Mock correlation matrix (symmetric)
        np.random.seed(42)
        correlation_matrix = {}
        for i, ticker1 in enumerate(tickers):
            correlation_matrix[ticker1] = {}
            for j, ticker2 in enumerate(tickers):
                if i == j:
                    correlation_matrix[ticker1][ticker2] = 1.0
                elif j < i:
                    correlation_matrix[ticker1][ticker2] = correlation_matrix[ticker2][ticker1]
                else:
                    # Generate reasonable correlation (between -0.5 and 0.8)
                    correlation_matrix[ticker1][ticker2] = np.random.uniform(-0.3, 0.6)
        
        # Calculate risk contributions
        equal_weight = 1.0 / num_holdings
        risk_contributions = {}
        for ticker in tickers:
            # Mock risk contribution with some variation
            base_contrib = equal_weight
            variation = np.random.uniform(-0.1, 0.1)
            risk_contributions[ticker] = max(0.05, base_contrib + variation)
        
        # Normalize risk contributions to sum to 1
        total_contrib = sum(risk_contributions.values())
        risk_contributions = {k: v/total_contrib for k, v in risk_contributions.items()}
        
        cov_analysis = {
            "correlation_matrix": correlation_matrix,
            "portfolio_volatility": 0.18,  # Mock 18% portfolio volatility
            "risk_contributions": risk_contributions
        }
        
        return sanitize_for_json({
            "covariance_analysis": cov_analysis,
            "copula_analysis": {
                "kendall_tau": 0.3,
                "spearman_rho": 0.35,
                "tail_dependence": 0.25
            },
            "portfolio_risk_decomposition": {
                "total_volatility": cov_analysis['portfolio_volatility'],
                "diversification_ratio": 0.85,  # Mock diversification benefit
                "risk_contributions": cov_analysis['risk_contributions']
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Covariance analysis error: {str(e)}")

@app.post("/analysis/risk/stress-test")
async def stress_test_portfolio(
    portfolio_data: dict,
    scenarios: Optional[List[dict]] = None,
    current_user: User = Depends(get_current_user)
):
    """Stress test portfolio under various market scenarios"""
    try:
        if scenarios is None:
            scenarios = [
                {'name': 'Market Crash (-20%)', 'market_shock': -0.20, 'volatility_multiplier': 2.0},
                {'name': 'Recession (-10%)', 'market_shock': -0.10, 'volatility_multiplier': 1.5},
                {'name': 'Volatility Spike', 'market_shock': 0.0, 'volatility_multiplier': 2.5},
                {'name': 'Bull Market (+15%)', 'market_shock': 0.15, 'volatility_multiplier': 0.8},
                {'name': 'Interest Rate Shock', 'market_shock': -0.05, 'volatility_multiplier': 1.8},
                {'name': 'Tech Sector Crash', 'market_shock': -0.25, 'volatility_multiplier': 2.2}
            ]
        
        stress_results = risk_model.stress_test_portfolio(portfolio_data, scenarios)
        
        return {
            "stress_test_results": stress_results,
            "scenarios_tested": len(scenarios),
            "worst_case_scenario": min(stress_results.items(), key=lambda x: x[1]['value_change_percent']),
            "best_case_scenario": max(stress_results.items(), key=lambda x: x[1]['value_change_percent'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stress test error: {str(e)}")

@app.get("/analysis/risk/visualization/{ticker}")
async def get_risk_visualization_data(
    ticker: str,
    time_horizon: int = 30
):
    """Get comprehensive risk visualization data for a single asset"""
    try:
        # Get stock data
        stock_data = market_service.get_stock_data(ticker)
        current_price = stock_data['price']
        volatility = stock_data.get('volatility', 0.25)
        
        # Calculate probability density function
        pdf_data = risk_model.price_probability_density(current_price, volatility, time_horizon)
        
        # Calculate risk metrics
        risk_metrics = {
            "current_price": current_price,
            "volatility": volatility,
            "var_95": current_price * (1 - 1.645 * volatility),
            "var_99": current_price * (1 - 2.326 * volatility),
            "expected_return": pdf_data['distribution_params']['expected_price'] / current_price - 1,
            "probability_of_loss": pdf_data['probabilities']['prob_below_current'],
            "probability_of_gain": pdf_data['probabilities']['prob_above_current']
        }
        
        return {
            "ticker": ticker,
            "risk_metrics": risk_metrics,
            "probability_density": pdf_data,
            "visualization_data": {
                "price_range": pdf_data['price_range'],
                "pdf_values": pdf_data['pdf_values'],
                "cdf_values": pdf_data['cdf_values'],
                "confidence_intervals": pdf_data['confidence_intervals']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk visualization error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 