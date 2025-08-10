#!/usr/bin/env python3
"""
AuraQuant FastAPI Backend Server
Connects frontend to Ollama-powered portfolio analyzer with LimeTrader integration
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from app.services.portfolio_service import get_portfolio_service
from core.execution_engine import ExecutionEngine
from utils.logger import get_logger

# Initialize FastAPI app
app = FastAPI(
    title="AuraQuant Portfolio Analyzer",
    description="Ollama-powered portfolio optimization with LimeTrader integration",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
logger = get_logger(__name__)
portfolio_service = None
execution_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global portfolio_service, execution_engine
    
    try:
        # Initialize Ollama-powered portfolio service
        portfolio_service = get_portfolio_service(enable_llm=True, enable_trading=True)
        logger.info("🤖 Ollama-powered portfolio service initialized")
        
        # Initialize LimeTrader connection
        try:
            execution_engine = ExecutionEngine()
            logger.info("🚀 LimeTrader connection established")
        except Exception as e:
            logger.warning(f"⚠️ LimeTrader unavailable: {str(e)}")
            execution_engine = None
        
        logger.info("✅ AuraQuant backend server ready")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise RuntimeError(f"Failed to initialize AuraQuant: {str(e)}")

# Request/Response Models
class UserRequestModel(BaseModel):
    user_input: str

class PortfolioAnalysisModel(BaseModel):
    portfolio_description: str
    target_return: Optional[float] = None
    time_horizon_months: Optional[int] = None

class ChatModel(BaseModel):
    question: str
    portfolio_context: Dict[str, Any]

class PortfolioModificationModel(BaseModel):
    action: str  # 'approve_all', 'modify_positions', 'reject_and_regenerate'
    modifications: Optional[list] = None
    new_requirements: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    portfolio_context: Dict[str, Any]

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AuraQuant Portfolio Analyzer",
        "ollama_available": portfolio_service is not None,
        "limetrader_available": execution_engine is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/parse-requirements")
async def parse_requirements(request: UserRequestModel):
    """Parse natural language portfolio requirements using Ollama"""
    try:
        if not portfolio_service:
            raise HTTPException(status_code=503, detail="Portfolio service not available")
        
        result = portfolio_service.parse_user_request(request.user_input)
        
        if result.success:
            return {
                "success": True,
                "data": {
                    "original_text": result.data.original_text,
                    "strategy_type": result.data.strategy_type.value if result.data.strategy_type else None,
                    "risk_tolerance": result.data.risk_tolerance,
                    "capital": result.data.capital,
                    "target_return": result.data.target_return,
                    "time_horizon": result.data.time_horizon,
                    "sectors_preferred": result.data.sectors_preferred,
                    "sectors_excluded": result.data.sectors_excluded,
                    "special_preferences": result.data.special_preferences
                },
                "metadata": result.metadata
            }
        else:
            raise HTTPException(status_code=400, detail=result.error)
            
    except Exception as e:
        logger.error(f"Parse requirements error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-portfolio")
async def analyze_portfolio(request: PortfolioAnalysisModel):
    """Analyze existing portfolio using Ollama-powered analysis"""
    try:
        if not portfolio_service:
            raise HTTPException(status_code=503, detail="Portfolio service not available")
        
        goals = None
        if request.target_return or request.time_horizon_months:
            goals = {
                'target_return': request.target_return,
                'time_horizon_months': request.time_horizon_months
            }
        
        result = portfolio_service.analyze_portfolio(request.portfolio_description, goals)
        
        if result.success:
            data = result.data
            return {
                "success": True,
                "data": {
                    "analysis": {
                        "total_value": data['analysis'].total_value,
                        "risk_score": data['analysis'].risk_score,
                        "risk_category": data['analysis'].risk_category.value,
                        "expected_return": data['analysis'].expected_return,
                        "volatility": data['analysis'].volatility,
                        "cash_percentage": data['analysis'].cash_percentage,
                        "positions": [
                            {
                                "symbol": pos.symbol,
                                "value": pos.value,
                                "weight": pos.weight,
                                "risk_score": pos.risk_score,
                                "sector": pos.sector,
                                "ytd_return": pos.ytd_return
                            }
                            for pos in data['analysis'].positions
                        ]
                    },
                    "recommendations": [
                        {
                            "action": rec.action,
                            "reason": rec.reason,
                            "priority": rec.priority,
                            "impact": rec.impact
                        }
                        for rec in data['recommendations']
                    ],
                    "goal_alignment": data.get('goal_alignment').__dict__ if data.get('goal_alignment') else None,
                    "rebalancing_needed": data['rebalancing_needed']
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result.error)
            
    except Exception as e:
        logger.error(f"Portfolio analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-portfolio")
async def generate_portfolio(request: UserRequestModel):
    """Generate optimized portfolio using Ollama and quantitative analysis"""
    try:
        if not portfolio_service:
            raise HTTPException(status_code=503, detail="Portfolio service not available")
        
        # First parse the requirements
        parsed_result = portfolio_service.parse_user_request(request.user_input)
        if not parsed_result.success:
            raise HTTPException(status_code=400, detail=parsed_result.error)
        
        # Generate portfolio
        portfolio_result = portfolio_service.generate_portfolio(parsed_result.data)
        
        if portfolio_result.success:
            portfolio = portfolio_result.data
            return {
                "success": True,
                "data": {
                    "strategy_name": portfolio.strategy_name,
                    "strategy_description": portfolio.strategy_description,
                    "expected_return": portfolio.expected_return,
                    "risk_level": portfolio.risk_level,
                    "positions": [
                        {
                            "symbol": pos.symbol,
                            "allocation_percentage": pos.weight,
                            "value": pos.value,
                            "risk_score": pos.risk_score,
                            "sector": pos.sector,
                            "momentum_score": pos.momentum_score
                        }
                        for pos in portfolio.positions
                    ],
                    "performance_metrics": portfolio.performance_metrics,
                    "requires_approval": portfolio.requires_approval
                },
                "metadata": portfolio_result.metadata
            }
        else:
            raise HTTPException(status_code=400, detail=portfolio_result.error)
            
    except Exception as e:
        logger.error(f"Portfolio generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Enhanced chat endpoint with comprehensive stock analysis"""
    try:
        result = portfolio_service.chat_about_portfolio(
            request.question, 
            request.portfolio_context
        )
        
        if result.success:
            # Extract the response data properly
            response_data = result.data
            
            return {
                "success": True,
                "data": {
                    "ai_response": response_data.get('ai_response', ''),
                    "suggestions": response_data.get('suggestions', []),
                    "analyzed_stocks": response_data.get('analyzed_stocks', []),
                    "analysis_enhanced": response_data.get('analysis_enhanced', False)
                }
            }
        else:
            raise HTTPException(status_code=400, detail=result.error)
            
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/live-positions")
async def get_live_positions():
    """Get live portfolio positions from LimeTrader API"""
    try:
        if not execution_engine:
            raise HTTPException(status_code=503, detail="LimeTrader connection not available")
        
        # Get comprehensive portfolio summary
        portfolio_summary = execution_engine.get_portfolio_summary()
        
        if 'error' in portfolio_summary:
            raise HTTPException(status_code=500, detail=portfolio_summary['error'])
        
        return {
            "success": True,
            "data": {
                "account_info": portfolio_summary['account_info'],
                "positions": portfolio_summary['positions'],
                "summary": portfolio_summary['summary']
            }
        }
        
    except Exception as e:
        logger.error(f"Live positions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-live-portfolio")
async def analyze_live_portfolio():
    """Analyze live portfolio from LimeTrader with AI insights"""
    try:
        if not execution_engine:
            raise HTTPException(status_code=503, detail="LimeTrader connection not available")
        
        # Get live portfolio data
        portfolio_summary = execution_engine.get_portfolio_summary()
        
        if 'error' in portfolio_summary:
            raise HTTPException(status_code=400, detail=portfolio_summary['error'])
        
        # Convert to format for AI analysis
        positions = portfolio_summary['positions']
        summary = portfolio_summary['summary']
        account_info = portfolio_summary['account_info']
        
        # Create portfolio description string for analysis
        portfolio_parts = []
        if summary.get('cash', 0) > 0:
            portfolio_parts.append(f"Cash: ${summary['cash']:,.0f}")
        
        for pos in positions:
            portfolio_parts.append(f"{pos['symbol']}: ${pos['market_value']:,.0f}")
        
        portfolio_description = ", ".join(portfolio_parts)
        
        # Get AI analysis using Ollama
        ai_analysis_prompt = f"""
        Analyze this live portfolio and provide risk-adjusted insights:
        
        Portfolio: {portfolio_description}
        Total Value: ${summary.get('total_portfolio_value', 0):,.0f}
        Cash Percentage: {summary.get('cash_percentage', 0):.1f}%
        Unrealized P&L: ${summary.get('total_unrealized_pnl', 0):,.0f} ({summary.get('unrealized_pnl_percentage', 0):.1f}%)
        Position Count: {summary.get('position_count', 0)}
        Largest Position: {summary.get('concentration_risk', 0):.1f}% of portfolio
        Tech Exposure: {summary.get('tech_exposure', 0):.1f}%
        
        Provide analysis covering:
        1. Overall risk assessment
        2. Portfolio diversification
        3. Cash allocation appropriateness  
        4. Concentration risk evaluation
        5. Specific recommendations for improvement
        
        Focus on actionable insights for risk-adjusted returns.
        """
        
        # Use portfolio service chat functionality for AI analysis
        chat_result = portfolio_service.chat_about_portfolio(
            ai_analysis_prompt, 
            {"portfolio_summary": portfolio_summary}
        )
        
        if chat_result.success:
            return {
                "success": True,
                "data": {
                    "portfolio_summary": portfolio_summary,
                    "ai_analysis": chat_result.data.ai_response,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "is_live_data": not summary.get('is_mock_data', False)
                }
            }
        else:
            raise HTTPException(status_code=400, detail=chat_result.error)
            
    except Exception as e:
        logger.error(f"Live portfolio analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approve-portfolio")
async def approve_portfolio_changes(request: PortfolioModificationModel):
    """Handle user approval/modification of portfolio recommendations"""
    try:
        # For now, just return the approval status
        # In production, this would trigger actual trades via execution_engine
        
        response_data = {
            "action_taken": request.action,
            "timestamp": datetime.now().isoformat()
        }
        
        if request.action == "approve_all":
            response_data["message"] = "Portfolio approved for implementation"
            response_data["next_step"] = "Ready for trade execution"
            
        elif request.action == "modify_positions":
            response_data["message"] = "Portfolio modifications noted"
            response_data["modifications"] = request.modifications
            response_data["next_step"] = "Generate updated portfolio"
            
        elif request.action == "reject_and_regenerate":
            response_data["message"] = "Portfolio rejected, regenerating with new requirements"
            response_data["new_requirements"] = request.new_requirements
            response_data["next_step"] = "Generate new portfolio"
        
        return {
            "success": True,
            "data": response_data
        }
        
    except Exception as e:
        logger.error(f"Portfolio approval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system-status")
async def get_system_status():
    """Get comprehensive system status"""
    return {
        "ollama_available": portfolio_service is not None,
        "limetrader_available": execution_engine is not None,
        "services": {
            "portfolio_analyzer": "✅ Active" if portfolio_service else "❌ Unavailable",
            "live_trading": "✅ Connected" if execution_engine else "❌ Disconnected",
            "ollama_llm": "🤖 Active" if portfolio_service else "❌ Required"
        },
        "capabilities": [
            "Natural language portfolio analysis",
            "Ollama-powered chat interface", 
            "Live portfolio data from LimeTrader",
            "Sharpe ratio optimization",
            "Risk assessment and scoring",
            "Interactive portfolio modifications"
        ]
    }

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/app", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend application"""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found. Please build the frontend first.</h1>")

if __name__ == "__main__":
    print("🚀 Starting AuraQuant FastAPI Server")
    print("🤖 Ollama-powered portfolio analyzer with LimeTrader integration")
    print("=" * 60)
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 