"""
AuraVest Database Configuration
PostgreSQL setup as specified in PRD Phase 1
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/auravest"
)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models (PRD Phase 1 Schema)

class User(Base):
    """User table - PRD Phase 1: Basic user system with secure auth"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Risk Profile (PRD: risk tolerance questionnaire)
    risk_profile = Column(String)  # Conservative, Moderate, Aggressive
    risk_score = Column(Float)     # 0.0 to 1.0
    
    # Privacy Settings (PRD: privacy by design)
    share_portfolio_performance = Column(Boolean, default=False)
    enable_profile_view = Column(Boolean, default=False)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="owner")

class Portfolio(Base):
    """Portfolio table - PRD Phase 1: Manual portfolio input"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, default="My Portfolio")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")

class Holding(Base):
    """Holdings table - PRD Phase 1: Assets by ticker, quantity, purchase info"""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    # Asset Information
    ticker_symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float)
    purchase_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")

class RiskQuestionnaire(Base):
    """Risk questionnaire responses - PRD Phase 1: 5-10 questions for risk profiling"""
    __tablename__ = "risk_questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Questionnaire Responses (PRD: investment goals, market reactions, etc.)
    investment_goals = Column(String)
    time_horizon = Column(Integer)  # years
    risk_comfort = Column(Integer)  # 1-5 scale
    market_experience = Column(String)
    reaction_to_loss = Column(String)
    income_stability = Column(String)
    investment_knowledge = Column(String)
    
    # Calculated Results
    risk_score = Column(Float)
    risk_category = Column(String)
    
    completed_at = Column(DateTime, default=datetime.utcnow)

# Database Functions

def get_database():
    """Get database session - dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def init_database():
    """Initialize database with tables"""
    print("🗄️ Initializing PostgreSQL database...")
    try:
        create_tables()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False 