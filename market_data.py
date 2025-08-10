"""
Market Data Service for AuraVest
Enhanced with comprehensive stock data and options information
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import warnings
warnings.filterwarnings('ignore')

class MarketDataService:
    """Enhanced market data service with caching and comprehensive data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.last_update = {}
        
    def get_stock_price(self, ticker: str) -> float:
        """Get current stock price with caching"""
        cache_key = f"price_{ticker}"
        
        # Check cache
        if cache_key in self.cache:
            if time.time() - self.last_update.get(cache_key, 0) < self.cache_duration:
                return self.cache[cache_key]
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if 'regularMarketPrice' in info and info['regularMarketPrice']:
                price = info['regularMarketPrice']
            else:
                # Fallback to historical data
                hist = stock.history(period='1d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                else:
                    return 0.0
            
            # Update cache
            self.cache[cache_key] = price
            self.last_update[cache_key] = time.time()
            
            return price
            
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return 0.0
    
    def get_stock_data(self, ticker: str) -> Dict:
        """Get comprehensive stock data"""
        cache_key = f"data_{ticker}"
        
        # Check cache
        if cache_key in self.cache:
            if time.time() - self.last_update.get(cache_key, 0) < self.cache_duration:
                return self.cache[cache_key]
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get current price
            current_price = info.get('regularMarketPrice', 0)
            if not current_price:
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
            
            # Get historical data for calculations
            hist_data = stock.history(period='1y')
            
            # Calculate metrics
            if not hist_data.empty:
                returns = hist_data['Close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)
                avg_volume = hist_data['Volume'].mean()
                
                # Calculate moving averages
                ma_20 = hist_data['Close'].rolling(20).mean().iloc[-1]
                ma_50 = hist_data['Close'].rolling(50).mean().iloc[-1]
                ma_200 = hist_data['Close'].rolling(200).mean().iloc[-1]
                
                # Calculate RSI
                delta = hist_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                # Calculate MACD
                exp1 = hist_data['Close'].ewm(span=12).mean()
                exp2 = hist_data['Close'].ewm(span=26).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9).mean()
                macd_value = macd.iloc[-1]
                signal_value = signal.iloc[-1]
                
            else:
                volatility = 0
                avg_volume = 0
                ma_20 = ma_50 = ma_200 = current_price
                rsi = 50
                macd_value = signal_value = 0
            
            # Compile data
            stock_data = {
                "ticker": ticker,
                "price": current_price,
                "change": info.get('regularMarketChange', 0),
                "change_percent": info.get('regularMarketChangePercent', 0),
                "volume": info.get('volume', avg_volume),
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "pb_ratio": info.get('priceToBook', 0),
                "dividend_yield": info.get('dividendYield', 0),
                "beta": info.get('beta', 1.0),
                "volatility": volatility,
                "moving_averages": {
                    "ma_20": ma_20,
                    "ma_50": ma_50,
                    "ma_200": ma_200
                },
                "technical_indicators": {
                    "rsi": rsi,
                    "macd": macd_value,
                    "macd_signal": signal_value
                },
                "company_info": {
                    "name": info.get('longName', ticker),
                    "sector": info.get('sector', ''),
                    "industry": info.get('industry', ''),
                    "description": info.get('longBusinessSummary', '')
                }
            }
            
            # Update cache
            self.cache[cache_key] = stock_data
            self.last_update[cache_key] = time.time()
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return {
                "ticker": ticker,
                "price": 0,
                "error": str(e)
            }
    
    def get_multiple_stocks(self, tickers: List[str]) -> Dict[str, Dict]:
        """Get data for multiple stocks"""
        results = {}
        
        for ticker in tickers:
            results[ticker] = self.get_stock_data(ticker)
        
        return results
    
    def get_portfolio_value(self, holdings: List[Dict]) -> Dict:
        """Calculate portfolio value and metrics"""
        total_value = 0
        total_cost = 0
        holdings_data = []
        
        for holding in holdings:
            ticker = holding['ticker']
            quantity = holding['quantity']
            purchase_price = holding.get('purchase_price', 0)
            
            current_price = self.get_stock_price(ticker)
            current_value = quantity * current_price
            cost_basis = quantity * purchase_price
            
            total_value += current_value
            total_cost += cost_basis
            
            holdings_data.append({
                "ticker": ticker,
                "quantity": quantity,
                "purchase_price": purchase_price,
                "current_price": current_price,
                "current_value": current_value,
                "cost_basis": cost_basis,
                "unrealized_pnl": current_value - cost_basis,
                "unrealized_pnl_percent": ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
            })
        
        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_unrealized_pnl": total_value - total_cost,
            "total_unrealized_pnl_percent": ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            "holdings": holdings_data
        }
    
    def get_historical_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Get historical price data"""
        cache_key = f"hist_{ticker}_{period}"
        
        # Check cache
        if cache_key in self.cache:
            if time.time() - self.last_update.get(cache_key, 0) < self.cache_duration:
                return self.cache[cache_key]
        
        try:
            stock = yf.Ticker(ticker)
            hist_data = stock.history(period=period)
            
            if not hist_data.empty:
                # Add technical indicators
                hist_data['SMA_20'] = hist_data['Close'].rolling(20).mean()
                hist_data['SMA_50'] = hist_data['Close'].rolling(50).mean()
                hist_data['SMA_200'] = hist_data['Close'].rolling(200).mean()
                
                # Calculate RSI
                delta = hist_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                hist_data['RSI'] = 100 - (100 / (1 + rs))
                
                # Calculate MACD
                exp1 = hist_data['Close'].ewm(span=12).mean()
                exp2 = hist_data['Close'].ewm(span=26).mean()
                hist_data['MACD'] = exp1 - exp2
                hist_data['MACD_Signal'] = hist_data['MACD'].ewm(span=9).mean()
                
                # Calculate Bollinger Bands
                hist_data['BB_Middle'] = hist_data['Close'].rolling(20).mean()
                bb_std = hist_data['Close'].rolling(20).std()
                hist_data['BB_Upper'] = hist_data['BB_Middle'] + (bb_std * 2)
                hist_data['BB_Lower'] = hist_data['BB_Middle'] - (bb_std * 2)
                
                # Update cache
                self.cache[cache_key] = hist_data
                self.last_update[cache_key] = time.time()
            
            return hist_data
            
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_options_data(self, ticker: str, expiration_date: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Get options data for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            
            if not expiration_date:
                options = stock.options
                if options:
                    expiration_date = options[0]  # Use nearest expiration
            
            if expiration_date:
                opt = stock.option_chain(expiration_date)
                return opt.calls, opt.puts
            else:
                return None, None
                
        except Exception as e:
            print(f"Error fetching options data for {ticker}: {e}")
            return None, None
    
    def get_market_sentiment(self, ticker: str) -> Dict:
        """Get market sentiment indicators"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get institutional ownership and insider transactions
            institutional_ownership = info.get('heldPercentInstitutions', 0)
            insider_ownership = info.get('heldPercentInsiders', 0)
            
            # Get analyst recommendations
            recommendations = stock.recommendations
            if not recommendations.empty:
                recent_recommendations = recommendations.tail(10)
                buy_count = len(recent_recommendations[recent_recommendations['To Grade'].str.contains('Buy', na=False)])
                hold_count = len(recent_recommendations[recent_recommendations['To Grade'].str.contains('Hold', na=False)])
                sell_count = len(recent_recommendations[recent_recommendations['To Grade'].str.contains('Sell', na=False)])
                
                total_recommendations = buy_count + hold_count + sell_count
                if total_recommendations > 0:
                    buy_percentage = (buy_count / total_recommendations) * 100
                    sell_percentage = (sell_count / total_recommendations) * 100
                else:
                    buy_percentage = sell_percentage = 0
            else:
                buy_percentage = sell_percentage = 0
            
            return {
                "institutional_ownership": institutional_ownership,
                "insider_ownership": insider_ownership,
                "analyst_recommendations": {
                    "buy_percentage": buy_percentage,
                    "sell_percentage": sell_percentage
                }
            }
            
        except Exception as e:
            print(f"Error fetching sentiment for {ticker}: {e}")
            return {}
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.last_update.clear()

# Global instance
market_service = MarketDataService() 