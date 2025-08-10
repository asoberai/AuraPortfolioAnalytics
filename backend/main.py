#!/usr/bin/env python3
"""
AuraQuant FastAPI Backend Server
Clean API implementation following PRD specifications
- FastAPI backend with PostgreSQL (simplified to file storage for MVP)
- yfinance for market data (as specified in PRD)
- Ollama LLM integration with RAG
- LimeTrader SDK integration
- Security best practices
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Core imports
from core.execution_engine import ExecutionEngine
from core.market_data_service import get_market_data_service
from utils.logger import get_logger

# Try to import AI services
try:
    from analysis.ai_portfolio_advisor import AIPortfolioAdvisor
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from analysis.market_data_integrator import MarketDataIntegrator
    MARKET_INTEGRATOR_AVAILABLE = True
except ImportError:
    MARKET_INTEGRATOR_AVAILABLE = False

try:
    from analysis.enhanced_stock_analyzer import EnhancedStockAnalyzer
    STOCK_ANALYZER_AVAILABLE = True
except ImportError:
    STOCK_ANALYZER_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="AuraQuant - AI Portfolio Management Platform",
    description="Professional AI-powered portfolio optimization with real-time market data",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration (restrictive for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Global services
logger = get_logger(__name__)
execution_engine: Optional[ExecutionEngine] = None
ai_advisor: Optional[Any] = None
market_integrator: Optional[Any] = None
stock_analyzer: Optional[Any] = None
market_service = None

# Request/Response Models
class UserAuthRequest(BaseModel):
    """User authentication request"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")

class PortfolioHolding(BaseModel):
    """Manual portfolio holding input"""
    symbol: str = Field(..., description="Stock ticker symbol")
    quantity: float = Field(..., description="Number of shares")
    purchase_price: Optional[float] = Field(None, description="Purchase price per share")
    purchase_date: Optional[str] = Field(None, description="Purchase date (YYYY-MM-DD)")

class PortfolioInput(BaseModel):
    """Portfolio input for analysis"""
    holdings: List[PortfolioHolding] = Field(..., description="List of portfolio holdings")
    cash_balance: float = Field(default=0, description="Cash balance")

class ChatRequest(BaseModel):
    """AI chat request"""
    question: str = Field(..., description="User question")
    portfolio_context: Optional[Dict[str, Any]] = Field(None, description="Portfolio context for personalized responses")

class RiskProfileRequest(BaseModel):
    """Risk tolerance questionnaire"""
    investment_goals: str = Field(..., description="Primary investment goals")
    time_horizon: int = Field(..., description="Investment time horizon in years")
    risk_comfort: int = Field(..., ge=1, le=5, description="Risk comfort level (1-5)")
    market_experience: str = Field(..., description="Investment experience level")
    reaction_to_loss: str = Field(..., description="Reaction to portfolio losses")

class MarketDataRequest(BaseModel):
    """Market data request"""
    symbols: List[str] = Field(..., description="List of symbols to fetch")
    include_news: bool = Field(default=True, description="Include news and sentiment")

# Startup/Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    global execution_engine, ai_advisor, market_integrator, stock_analyzer, market_service
    
    logger.info("🚀 Starting AuraQuant API Server")
    
    try:
        # Initialize Market Data Service
        try:
            market_service = get_market_data_service()
            logger.info("✅ Market Data Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Market data service limited: {str(e)}")
        
        # Initialize LimeTrader connection
        try:
            execution_engine = ExecutionEngine()
            logger.info("✅ Execution Engine initialized")
        except Exception as e:
            logger.warning(f"⚠️ Execution Engine in demo mode: {str(e)}")
            execution_engine = ExecutionEngine(demo_mode=True)
        
        # Initialize AI Advisor (if available)
        if AI_AVAILABLE:
            try:
                ai_advisor = AIPortfolioAdvisor()
                logger.info("✅ AI Portfolio Advisor initialized")
            except Exception as e:
                logger.warning(f"⚠️ AI Advisor unavailable: {str(e)}")
                ai_advisor = None
        else:
            logger.warning("⚠️ AI Portfolio Advisor not available")
        
        # Initialize Market Data Integrator (if available)
        if MARKET_INTEGRATOR_AVAILABLE:
            try:
                market_integrator = MarketDataIntegrator()
                logger.info("✅ Market Data Integrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ Market Data Integrator limited: {str(e)}")
        
        # Initialize Stock Analyzer (if available)
        if STOCK_ANALYZER_AVAILABLE:
            try:
                stock_analyzer = EnhancedStockAnalyzer()
                logger.info("✅ Enhanced Stock Analyzer initialized")
            except Exception as e:
                logger.warning(f"⚠️ Stock Analyzer limited: {str(e)}")
        
        logger.info("🎉 AuraQuant API Server ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down AuraQuant API Server")

# Authentication Dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple auth dependency (expand for production)"""
    # For MVP, we'll skip complex auth but keep the structure
    # In production, validate JWT tokens here
    return {"user_id": "demo_user", "email": "demo@auraquant.com"}

# Health Check Endpoints
@app.get("/")
async def root():
    """Root health check"""
    return {
        "service": "AuraQuant API",
        "version": "3.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/api/docs",
            "health": "/api/health",
            "chat": "/api/chat",
            "portfolio": "/api/portfolio",
            "market": "/api/market"
        }
    }

@app.get("/api/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "services": {
            "execution_engine": execution_engine is not None,
            "market_service": market_service is not None,
            "ai_advisor": ai_advisor is not None,
            "market_integrator": market_integrator is not None,
            "stock_analyzer": stock_analyzer is not None
        },
        "capabilities": [
            "Portfolio Analysis",
            "Real-time Market Data",
            "Risk Assessment",
            "AI-Powered Insights" if ai_advisor else "Basic Analysis"
        ],
        "timestamp": datetime.now().isoformat()
    }

# User Management Endpoints (MVP - simplified)
@app.post("/api/auth/register")
async def register_user(request: UserAuthRequest):
    """Register new user (MVP implementation)"""
    # For MVP, we'll simulate user registration
    # In production, hash passwords and store in database
    return {
        "success": True,
        "message": "User registered successfully",
        "user_id": f"user_{datetime.now().timestamp()}",
        "token": "demo_token_123"  # In production, generate JWT
    }

@app.post("/api/auth/login")
async def login_user(request: UserAuthRequest):
    """User login (MVP implementation)"""
    # For MVP, accept any credentials
    # In production, validate against database
    return {
        "success": True,
        "message": "Login successful",
        "user_id": "demo_user",
        "token": "demo_token_123",
        "profile": {
            "email": request.email,
            "risk_profile": None,
            "portfolios": []
        }
    }

# Portfolio Management Endpoints
@app.get("/api/portfolio/positions")
async def get_live_positions(user = Depends(get_current_user)):
    """Get live portfolio positions"""
    try:
        if not execution_engine:
            raise HTTPException(status_code=503, detail="Execution engine unavailable")
        
        portfolio_data = execution_engine.get_portfolio_summary()
        
        return {
            "success": True,
            "data": portfolio_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio/analyze")
async def analyze_portfolio(request: PortfolioInput, user = Depends(get_current_user)):
    """Analyze portfolio with available tools"""
    try:
        # Convert request to portfolio data
        portfolio_data = {
            "positions": [
                {
                    "symbol": holding.symbol,
                    "quantity": holding.quantity,
                    "purchase_price": holding.purchase_price,
                    "purchase_date": holding.purchase_date
                }
                for holding in request.holdings
            ],
            "cash_balance": request.cash_balance
        }
        
        # Basic analysis using market service
        analysis = {"basic_analysis": "Portfolio analysis completed"}
        
        if ai_advisor:
            try:
                # Use AI advisor if available
                ai_analysis = await ai_advisor.analyze_portfolio_comprehensive(portfolio_data)
                analysis.update(ai_analysis)
            except Exception as e:
                logger.warning(f"AI analysis failed: {str(e)}")
        
        return {
            "success": True,
            "data": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio/risk-profile")
async def assess_risk_profile(request: RiskProfileRequest, user = Depends(get_current_user)):
    """Assess user risk tolerance"""
    try:
        # Calculate risk score based on questionnaire
        risk_factors = {
            "time_horizon": min(request.time_horizon / 10, 1.0),  # Normalize to 0-1
            "risk_comfort": request.risk_comfort / 5.0,  # Normalize to 0-1
            "experience_weight": 0.8 if "experienced" in request.market_experience.lower() else 0.3,
            "loss_tolerance": 0.9 if "hold" in request.reaction_to_loss.lower() else 0.2
        }
        
        # Weighted risk score
        risk_score = (
            risk_factors["time_horizon"] * 0.3 +
            risk_factors["risk_comfort"] * 0.4 +
            risk_factors["experience_weight"] * 0.2 +
            risk_factors["loss_tolerance"] * 0.1
        )
        
        # Categorize risk profile
        if risk_score >= 0.7:
            profile = "Aggressive"
            allocation = {"stocks": 80, "bonds": 15, "alternatives": 5}
        elif risk_score >= 0.4:
            profile = "Moderate"
            allocation = {"stocks": 60, "bonds": 35, "alternatives": 5}
        else:
            profile = "Conservative"
            allocation = {"stocks": 30, "bonds": 65, "alternatives": 5}
        
        return {
            "success": True,
            "data": {
                "risk_profile": profile,
                "risk_score": round(risk_score, 2),
                "recommended_allocation": allocation,
                "explanation": f"Based on your responses, you have a {profile.lower()} risk profile with a score of {risk_score:.2f}/1.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Error assessing risk profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Chat Endpoints
@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest, user = Depends(get_current_user)):
    """Chat with AI financial advisor or provide basic responses"""
    try:
        # Get portfolio context if not provided
        portfolio_context = request.portfolio_context
        if not portfolio_context and execution_engine:
            try:
                portfolio_context = execution_engine.get_portfolio_summary()
            except:
                portfolio_context = {}
        
        if ai_advisor:
            # Use AI advisor if available
            try:
                response = await ai_advisor.handle_llm_chat(request.question, portfolio_context or {})
                return {
                    "success": True,
                    "data": response,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.warning(f"AI chat failed: {str(e)}")
        
        # Fallback to basic responses
        basic_response = {
            "ai_response": f"I received your question: '{request.question}'. The AI advisor is currently unavailable, but I can provide basic portfolio information.",
            "intelligence_score": 50,
            "confidence_level": 0.5,
            "response_quality": "basic",
            "suggestions": ["Check your portfolio positions", "Review risk profile", "Consider diversification"],
            "analyzed_stocks": []
        }
        
        return {
            "success": True,
            "data": basic_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Data Endpoints
@app.post("/api/market/data")
async def get_market_data(request: MarketDataRequest, user = Depends(get_current_user)):
    """Get comprehensive market data"""
    try:
        if not market_service:
            raise HTTPException(status_code=503, detail="Market data service unavailable")
        
        # Get market data for requested symbols
        market_data = market_service.get_multiple_stocks(request.symbols)
        
        # Convert to response format
        response_data = {}
        for symbol, data_point in market_data.items():
            response_data[symbol] = {
                "price": data_point.price,
                "change": data_point.change,
                "change_percent": data_point.change_percent,
                "volume": data_point.volume,
                "market_cap": data_point.market_cap,
                "pe_ratio": data_point.pe_ratio
            }
        
        return {
            "success": True,
            "data": {
                "market_data": response_data,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/indices")
async def get_market_indices():
    """Get major market indices"""
    try:
        if not market_service:
            raise HTTPException(status_code=503, detail="Market data service unavailable")
        
        indices_data = market_service.get_market_indices()
        
        # Convert to response format
        response_data = {}
        for name, data_point in indices_data.items():
            response_data[name] = {
                "name": name,
                "price": data_point.price,
                "change": data_point.change,
                "change_percent": data_point.change_percent
            }
        
        return {
            "success": True,
            "data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System Status
@app.get("/api/system-status")
async def get_system_status():
    """Get detailed system status"""
    return {
        "status": "active",
        "ai_enhanced": ai_advisor is not None,
        "services": {
            "execution_engine": execution_engine is not None,
            "market_service": market_service is not None,
            "ai_advisor": ai_advisor is not None,
            "market_integrator": market_integrator is not None,
            "stock_analyzer": stock_analyzer is not None
        },
        "timestamp": datetime.now().isoformat()
    }

# Static Files and Frontend (only mount if directory exists)
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    
    @app.get("/app", response_class=HTMLResponse)
    async def serve_frontend():
        """Serve the frontend application"""
        try:
            index_path = frontend_path / "index.html"
            if index_path.exists():
                return HTMLResponse(content=index_path.read_text())
            else:
                return HTMLResponse(
                    content="""
                    <html>
                        <head><title>AuraQuant</title></head>
                        <body>
                            <h1>AuraQuant API Server</h1>
                            <p>Frontend index.html not found. API is running at <a href="/api/docs">/api/docs</a></p>
                        </body>
                    </html>
                    """,
                    status_code=404
                )
        except Exception as e:
            logger.error(f"Error serving frontend: {str(e)}")
            return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)
else:
    @app.get("/app", response_class=HTMLResponse)
    async def serve_frontend_fallback():
        """Fallback when frontend directory doesn't exist"""
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <title>AuraQuant API Server</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                        .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        h1 {{ color: #2563eb; }}
                        .status {{ background: #10b981; color: white; padding: 10px; border-radius: 5px; }}
                        .links {{ margin: 20px 0; }}
                        .links a {{ display: inline-block; margin: 5px 10px; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🚀 AuraQuant API Server</h1>
                        <div class="status">✅ Server Running Successfully</div>
                        <p>The AuraQuant API server is running and ready to serve requests.</p>
                        <div class="links">
                            <a href="/api/docs">📚 API Documentation</a>
                            <a href="/api/health">🩺 Health Check</a>
                            <a href="/api/system-status">📊 System Status</a>
                        </div>
                        <h3>Available Services:</h3>
                        <ul>
                            <li>Portfolio Management</li>
                            <li>Market Data Integration</li>
                            <li>Risk Assessment</li>
                            <li>{"AI-Powered Analysis" if ai_advisor else "Basic Analysis"}</li>
                        </ul>
                        <p><em>Frontend directory not found. API endpoints are fully functional.</em></p>
                    </div>
                </body>
            </html>
            """
        )

# Development server
if __name__ == "__main__":
    print("🚀 AuraQuant API Server")
    print("📊 Professional AI Portfolio Management Platform")
    print("=" * 50)
    print("🔗 API Documentation: http://localhost:8000/api/docs")
    print("🌐 Frontend App: http://localhost:8000/app")
    print("💡 Health Check: http://localhost:8000/api/health")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 