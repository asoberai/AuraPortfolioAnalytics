#!/usr/bin/env python3
"""
AuraQuant Market Data Service
Implements PRD requirements for market data ingestion using yfinance
- Primary data source: Yahoo Finance via yfinance (free, 15-min delayed)
- Fallback: Alpha Vantage (free tier, limited)
- Caching for performance
- Alternative data integration (news, sentiment)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import time
from dataclasses import dataclass, asdict
import concurrent.futures

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Core imports
import yfinance as yf
import pandas as pd
import numpy as np

# Optional imports for enhanced features
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False

try:
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

from utils.logger import get_logger

@dataclass
class MarketDataPoint:
    """Market data for a single symbol"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    beta: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    timestamp: datetime

@dataclass
class NewsItem:
    """News item with sentiment analysis"""
    title: str
    summary: str
    source: str
    url: str
    published_date: datetime
    sentiment_score: float
    sentiment_label: str

@dataclass
class MarketSentiment:
    """Overall market sentiment indicators"""
    vix_level: Optional[float]
    fear_greed_index: Optional[float]
    overall_sentiment: str  # bullish, bearish, neutral
    confidence_score: float

class MarketDataService:
    """
    Market Data Service implementing PRD specifications
    - Primary: yfinance for stock/ETF prices (free, delayed)
    - Caching for performance optimization
    - Alternative data: news headlines, basic sentiment
    - Error handling and fallbacks
    """
    
    def __init__(self, enable_caching: bool = True, cache_ttl: int = 300):
        self.logger = get_logger(__name__)
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl  # 5 minutes default
        
        # Data cache
        self.price_cache = {}
        self.news_cache = {}
        self.last_update = {}
        
        # Initialize sentiment analyzer if available
        self.sentiment_analyzer = None
        if SENTIMENT_AVAILABLE:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Alpha Vantage API key (optional fallback)
        self.alpha_vantage_key = None  # Set from environment if needed
        
        self.logger.info("📊 Market Data Service initialized")
        self.logger.info(f"   Primary: Yahoo Finance (yfinance)")
        self.logger.info(f"   Caching: {'Enabled' if enable_caching else 'Disabled'}")
        self.logger.info(f"   Sentiment: {'Available' if SENTIMENT_AVAILABLE else 'Limited'}")
    
    def get_stock_data(self, symbol: str, include_fundamentals: bool = True) -> Optional[MarketDataPoint]:
        """
        Get comprehensive stock data for a single symbol
        Following PRD: Use yfinance for stock prices and basic data
        """
        try:
            # Check cache first
            if self._is_cached(symbol):
                return self.price_cache[symbol]
            
            # Fetch from yfinance
            ticker = yf.Ticker(symbol)
            
            # Get current price data
            hist = ticker.history(period="2d")  # Get 2 days for change calculation
            if hist.empty:
                self.logger.warning(f"No price data available for {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            
            # Get additional data if requested
            info = {}
            if include_fundamentals:
                try:
                    info = ticker.info
                except:
                    self.logger.warning(f"Could not fetch fundamentals for {symbol}")
            
            # Create data point
            data_point = MarketDataPoint(
                symbol=symbol,
                price=float(current_price),
                change=float(change),
                change_percent=float(change_percent),
                volume=int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                beta=info.get('beta'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow'),
                timestamp=datetime.now()
            )
            
            # Cache the result
            if self.enable_caching:
                self.price_cache[symbol] = data_point
                self.last_update[symbol] = datetime.now()
            
            self.logger.info(f"📈 {symbol}: ${current_price:.2f} ({change_percent:+.2f}%)")
            return data_point
            
        except Exception as e:
            self.logger.error(f"Failed to get data for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str], max_workers: int = 5) -> Dict[str, MarketDataPoint]:
        """
        Get data for multiple stocks efficiently using threading
        """
        results = {}
        
        if not symbols:
            return results
        
        # Use ThreadPoolExecutor for parallel requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_symbol = {
                executor.submit(self.get_stock_data, symbol): symbol 
                for symbol in symbols
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data_point = future.result()
                    if data_point:
                        results[symbol] = data_point
                except Exception as e:
                    self.logger.error(f"Failed to process {symbol}: {str(e)}")
        
        self.logger.info(f"📊 Retrieved data for {len(results)}/{len(symbols)} symbols")
        return results
    
    def get_market_indices(self) -> Dict[str, MarketDataPoint]:
        """
        Get major market indices data
        Following PRD: Track major indices for market context
        """
        indices = {
            '^GSPC': 'S&P 500',  # S&P 500
            '^IXIC': 'NASDAQ',   # NASDAQ Composite
            '^DJI': 'Dow Jones', # Dow Jones Industrial Average
            '^VIX': 'VIX'        # Volatility Index
        }
        
        results = {}
        
        for symbol, name in indices.items():
            try:
                data_point = self.get_stock_data(symbol, include_fundamentals=False)
                if data_point:
                    # Update symbol to friendly name
                    data_point.symbol = name
                    results[name] = data_point
            except Exception as e:
                self.logger.warning(f"Failed to get {name}: {str(e)}")
        
        return results
    
    def get_sector_performance(self) -> Dict[str, float]:
        """
        Get sector ETF performance for sector analysis
        Following PRD: Track sector rotation and performance
        """
        sector_etfs = {
            'XLK': 'Technology',
            'XLF': 'Financial',
            'XLV': 'Healthcare',
            'XLE': 'Energy',
            'XLI': 'Industrial',
            'XLY': 'Consumer Discretionary',
            'XLP': 'Consumer Staples',
            'XLU': 'Utilities',
            'XLB': 'Materials',
            'XLRE': 'Real Estate'
        }
        
        sector_performance = {}
        
        for etf_symbol, sector_name in sector_etfs.items():
            try:
                data_point = self.get_stock_data(etf_symbol, include_fundamentals=False)
                if data_point:
                    sector_performance[sector_name] = data_point.change_percent
            except Exception as e:
                self.logger.warning(f"Failed to get sector data for {sector_name}: {str(e)}")
        
        return sector_performance
    
    def get_news_sentiment(self, symbol: str, max_articles: int = 5) -> List[NewsItem]:
        """
        Get news and sentiment for a symbol
        Following PRD: Basic alternative data integration
        """
        news_items = []
        
        if not SENTIMENT_AVAILABLE:
            self.logger.warning("Sentiment analysis not available - install textblob and vaderSentiment")
            return news_items
        
        try:
            # Check cache
            cache_key = f"{symbol}_news"
            if self._is_cached(cache_key, cache_type='news'):
                return self.news_cache[cache_key]
            
            # Get news from yfinance
            ticker = yf.Ticker(symbol)
            
            # Try to get news (this feature may not always be available)
            try:
                news = ticker.news[:max_articles] if hasattr(ticker, 'news') else []
            except:
                news = []
            
            for article in news:
                try:
                    title = article.get('title', '')
                    summary = article.get('summary', title)
                    
                    if title:
                        # Analyze sentiment
                        sentiment = self.sentiment_analyzer.polarity_scores(title + " " + summary)
                        
                        news_item = NewsItem(
                            title=title,
                            summary=summary[:200] + "..." if len(summary) > 200 else summary,
                            source=article.get('publisher', 'Unknown'),
                            url=article.get('link', ''),
                            published_date=datetime.fromtimestamp(
                                article.get('providerPublishTime', time.time())
                            ),
                            sentiment_score=sentiment['compound'],
                            sentiment_label=self._classify_sentiment(sentiment['compound'])
                        )
                        
                        news_items.append(news_item)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to process news item: {str(e)}")
                    continue
            
            # Cache results
            if self.enable_caching:
                self.news_cache[cache_key] = news_items
                self.last_update[cache_key] = datetime.now()
            
            self.logger.info(f"📰 Retrieved {len(news_items)} news items for {symbol}")
            return news_items
            
        except Exception as e:
            self.logger.error(f"Failed to get news for {symbol}: {str(e)}")
            return news_items
    
    def get_market_sentiment(self) -> MarketSentiment:
        """
        Get overall market sentiment indicators
        Following PRD: Basic market sentiment analysis
        """
        try:
            # Get VIX level
            vix_data = self.get_stock_data('^VIX', include_fundamentals=False)
            vix_level = vix_data.price if vix_data else None
            
            # Determine overall sentiment based on VIX
            if vix_level:
                if vix_level < 20:
                    overall_sentiment = "bullish"
                    confidence = 0.7
                elif vix_level > 30:
                    overall_sentiment = "bearish"
                    confidence = 0.8
                else:
                    overall_sentiment = "neutral"
                    confidence = 0.6
            else:
                overall_sentiment = "neutral"
                confidence = 0.3
            
            return MarketSentiment(
                vix_level=vix_level,
                fear_greed_index=None,  # Would require external API
                overall_sentiment=overall_sentiment,
                confidence_score=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get market sentiment: {str(e)}")
            return MarketSentiment(
                vix_level=None,
                fear_greed_index=None,
                overall_sentiment="neutral",
                confidence_score=0.3
            )
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Get historical price data
        Following PRD: Historical data for performance calculations
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                self.logger.warning(f"No historical data for {symbol}")
                return None
            
            self.logger.info(f"📈 Retrieved {len(hist)} days of historical data for {symbol}")
            return hist
            
        except Exception as e:
            self.logger.error(f"Failed to get historical data for {symbol}: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        self.price_cache.clear()
        self.news_cache.clear()
        self.last_update.clear()
        self.logger.info("🗑️ Cache cleared")
    
    def _is_cached(self, key: str, cache_type: str = 'price') -> bool:
        """Check if data is cached and still valid"""
        if not self.enable_caching:
            return False
        
        cache = self.price_cache if cache_type == 'price' else self.news_cache
        
        if key not in cache or key not in self.last_update:
            return False
        
        # Check if cache is still valid
        cache_age = (datetime.now() - self.last_update[key]).total_seconds()
        return cache_age < self.cache_ttl
    
    def _classify_sentiment(self, compound_score: float) -> str:
        """Classify sentiment score into label"""
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    # Alpha Vantage fallback (for future use)
    def _get_alpha_vantage_data(self, symbol: str) -> Optional[Dict]:
        """
        Fallback to Alpha Vantage API (requires API key)
        Following PRD: Backup data source with rate limits
        """
        if not self.alpha_vantage_key:
            return None
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': quote.get('01. symbol'),
                    'price': float(quote.get('05. price', 0)),
                    'change_percent': float(quote.get('10. change percent', '0%').rstrip('%'))
                }
        
        except Exception as e:
            self.logger.warning(f"Alpha Vantage fallback failed for {symbol}: {str(e)}")
        
        return None

# Singleton instance
_market_data_service = None

def get_market_data_service() -> MarketDataService:
    """Get singleton market data service instance"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service

# Testing
if __name__ == "__main__":
    print("📊 Testing AuraQuant Market Data Service")
    print("=" * 50)
    
    service = MarketDataService()
    
    # Test single stock
    print("Testing single stock data...")
    aapl_data = service.get_stock_data("AAPL")
    if aapl_data:
        print(f"✅ AAPL: ${aapl_data.price:.2f} ({aapl_data.change_percent:+.2f}%)")
    
    # Test multiple stocks
    print("\nTesting multiple stocks...")
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    multi_data = service.get_multiple_stocks(symbols)
    for symbol, data in multi_data.items():
        print(f"✅ {symbol}: ${data.price:.2f} ({data.change_percent:+.2f}%)")
    
    # Test market indices
    print("\nTesting market indices...")
    indices = service.get_market_indices()
    for name, data in indices.items():
        print(f"✅ {name}: {data.price:.2f} ({data.change_percent:+.2f}%)")
    
    # Test sector performance
    print("\nTesting sector performance...")
    sectors = service.get_sector_performance()
    for sector, performance in sectors.items():
        print(f"✅ {sector}: {performance:+.2f}%")
    
    print("\n🎉 Market Data Service test complete!") 