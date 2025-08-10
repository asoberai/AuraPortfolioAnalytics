"""
Quantitative Models for AuraVest Portfolio Analysis
Advanced options pricing, volatility analysis, and portfolio optimization
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.optimize import minimize
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class OptionsPricingModel:
    """Black-Scholes and advanced options pricing models"""
    
    def __init__(self):
        self.risk_free_rate = 0.05  # 5% risk-free rate
        
    def black_scholes(self, S, K, T, r, sigma, option_type='call'):
        """
        Black-Scholes options pricing model
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        r: Risk-free rate
        sigma: Volatility
        option_type: 'call' or 'put'
        """
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        if option_type.lower() == 'call':
            price = S*stats.norm.cdf(d1) - K*np.exp(-r*T)*stats.norm.cdf(d2)
        else:  # put
            price = K*np.exp(-r*T)*stats.norm.cdf(-d2) - S*stats.norm.cdf(-d1)
            
        return price
    
    def implied_volatility(self, S, K, T, r, option_price, option_type='call', tolerance=1e-5, max_iter=100):
        """
        Calculate implied volatility using Newton-Raphson method
        """
        sigma = 0.5  # Initial guess
        
        for i in range(max_iter):
            price = self.black_scholes(S, K, T, r, sigma, option_type)
            diff = option_price - price
            
            if abs(diff) < tolerance:
                return sigma
                
            # Vega (derivative of price with respect to volatility)
            d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            vega = S * np.sqrt(T) * stats.norm.pdf(d1)
            
            sigma = sigma + diff / vega
            
            if sigma <= 0:
                sigma = 0.01
                
        return sigma
    
    def get_options_data(self, ticker, expiration_date=None):
        """
        Fetch options data for a given ticker
        """
        try:
            stock = yf.Ticker(ticker)
            
            if expiration_date:
                options = stock.options
                if expiration_date in options:
                    opt = stock.option_chain(expiration_date)
                    return opt.calls, opt.puts
                else:
                    # Use nearest expiration
                    expiration_date = options[0] if options else None
                    
            if not expiration_date:
                options = stock.options
                expiration_date = options[0] if options else None
                
            if expiration_date:
                opt = stock.option_chain(expiration_date)
                return opt.calls, opt.puts
            else:
                return None, None
                
        except Exception as e:
            print(f"Error fetching options data for {ticker}: {e}")
            return None, None

class VolatilityAnalyzer:
    """Advanced volatility analysis and forecasting"""
    
    def __init__(self):
        self.lookback_periods = [5, 10, 20, 30, 60, 252]  # Different timeframes
        
    def calculate_historical_volatility(self, prices, window=30):
        """
        Calculate historical volatility (standard deviation of returns)
        """
        returns = np.log(prices / prices.shift(1))
        return returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
    
    def calculate_implied_volatility_surface(self, ticker, expiration_dates=None):
        """
        Calculate implied volatility surface across different strikes and expirations
        """
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            if not expiration_dates:
                expiration_dates = stock.options[:3]  # First 3 expirations
                
            iv_surface = {}
            
            for exp_date in expiration_dates:
                opt = stock.option_chain(exp_date)
                calls = opt.calls
                puts = opt.puts
                
                # Calculate time to expiration
                exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                T = (exp_datetime - datetime.now()).days / 365
                
                if T <= 0:
                    continue
                    
                iv_data = []
                
                # Process calls
                for _, call in calls.iterrows():
                    if call['bid'] > 0 and call['ask'] > 0:
                        mid_price = (call['bid'] + call['ask']) / 2
                        iv = self._calculate_iv(current_price, call['strike'], T, mid_price, 'call')
                        if iv and 0.1 < iv < 2.0:  # Reasonable IV range
                            iv_data.append({
                                'strike': call['strike'],
                                'iv': iv,
                                'type': 'call',
                                'moneyness': call['strike'] / current_price
                            })
                
                # Process puts
                for _, put in puts.iterrows():
                    if put['bid'] > 0 and put['ask'] > 0:
                        mid_price = (put['bid'] + put['ask']) / 2
                        iv = self._calculate_iv(current_price, put['strike'], T, mid_price, 'put')
                        if iv and 0.1 < iv < 2.0:  # Reasonable IV range
                            iv_data.append({
                                'strike': put['strike'],
                                'iv': iv,
                                'type': 'put',
                                'moneyness': put['strike'] / current_price
                            })
                
                if iv_data:
                    iv_surface[exp_date] = pd.DataFrame(iv_data)
                    
            return iv_surface
            
        except Exception as e:
            print(f"Error calculating IV surface for {ticker}: {e}")
            return {}
    
    def _calculate_iv(self, S, K, T, option_price, option_type):
        """Helper method to calculate implied volatility"""
        try:
            # Use Newton-Raphson method
            sigma = 0.5
            for _ in range(50):
                d1 = (np.log(S/K) + (0.05 + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
                d2 = d1 - sigma*np.sqrt(T)
                
                if option_type == 'call':
                    price = S*stats.norm.cdf(d1) - K*np.exp(-0.05*T)*stats.norm.cdf(d2)
                else:
                    price = K*np.exp(-0.05*T)*stats.norm.cdf(-d2) - S*stats.norm.cdf(-d1)
                
                diff = option_price - price
                if abs(diff) < 1e-5:
                    return sigma
                
                vega = S * np.sqrt(T) * stats.norm.pdf(d1)
                sigma = sigma + diff / vega
                
                if sigma <= 0:
                    sigma = 0.01
                    
            return sigma if 0.1 < sigma < 2.0 else None
            
        except:
            return None
    
    def forecast_volatility(self, prices, method='garch', forecast_days=30):
        """
        Forecast volatility using various methods
        """
        returns = np.log(prices / prices.shift(1)).dropna()
        
        if method == 'garch':
            return self._garch_forecast(returns, forecast_days)
        elif method == 'ewma':
            return self._ewma_forecast(returns, forecast_days)
        elif method == 'historical':
            return self._historical_forecast(returns, forecast_days)
        else:
            return self._historical_forecast(returns, forecast_days)
    
    def _garch_forecast(self, returns, forecast_days):
        """GARCH(1,1) volatility forecast"""
        try:
            from arch import arch_model
            
            model = arch_model(returns, vol='Garch', p=1, q=1)
            results = model.fit(disp='off')
            
            forecast = results.forecast(horizon=forecast_days)
            return np.sqrt(forecast.variance.values[-1, :] * 252)  # Annualized
            
        except:
            return self._historical_forecast(returns, forecast_days)
    
    def _ewma_forecast(self, returns, forecast_days):
        """Exponentially Weighted Moving Average forecast"""
        lambda_param = 0.94
        ewma_var = returns.ewm(alpha=1-lambda_param).var().iloc[-1]
        
        # Simple mean reversion forecast
        forecast = []
        for i in range(forecast_days):
            forecast.append(ewma_var * (lambda_param ** i))
            
        return np.sqrt(np.array(forecast) * 252)
    
    def _historical_forecast(self, returns, forecast_days):
        """Simple historical volatility forecast"""
        hist_vol = returns.std() * np.sqrt(252)
        return np.full(forecast_days, hist_vol)

class PortfolioOptimizer:
    """Advanced portfolio optimization using Modern Portfolio Theory"""
    
    def __init__(self):
        self.risk_free_rate = 0.05
        
    def calculate_portfolio_metrics(self, returns, weights=None):
        """
        Calculate comprehensive portfolio metrics
        """
        if weights is None:
            weights = np.ones(len(returns.columns)) / len(returns.columns)
            
        portfolio_returns = (returns * weights).sum(axis=1)
        
        metrics = {
            'expected_return': portfolio_returns.mean() * 252,
            'volatility': portfolio_returns.std() * np.sqrt(252),
            'sharpe_ratio': (portfolio_returns.mean() * 252 - self.risk_free_rate) / (portfolio_returns.std() * np.sqrt(252)),
            'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
            'var_95': np.percentile(portfolio_returns, 5),
            'cvar_95': portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)].mean(),
            'skewness': stats.skew(portfolio_returns),
            'kurtosis': stats.kurtosis(portfolio_returns)
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, returns):
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def optimize_portfolio(self, returns, method='sharpe', constraints=None):
        """
        Optimize portfolio weights using various methods
        """
        n_assets = len(returns.columns)
        cov_matrix = returns.cov() * 252
        expected_returns = returns.mean() * 252
        
        if method == 'sharpe':
            return self._optimize_sharpe_ratio(expected_returns, cov_matrix, constraints)
        elif method == 'min_variance':
            return self._optimize_min_variance(cov_matrix, constraints)
        elif method == 'max_return':
            return self._optimize_max_return(expected_returns, constraints)
        else:
            return self._optimize_sharpe_ratio(expected_returns, cov_matrix, constraints)
    
    def _optimize_sharpe_ratio(self, expected_returns, cov_matrix, constraints=None):
        """Maximize Sharpe ratio"""
        n_assets = len(expected_returns)
        
        def objective(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe  # Minimize negative Sharpe ratio
        
        # Constraints
        bounds = [(0, 1) for _ in range(n_assets)]
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        if constraints:
            constraints_list.extend(constraints)
        
        # Initial guess
        initial_weights = np.ones(n_assets) / n_assets
        
        result = minimize(objective, initial_weights, method='SLSQP', 
                         bounds=bounds, constraints=constraints_list)
        
        return result.x if result.success else np.ones(n_assets) / n_assets
    
    def _optimize_min_variance(self, cov_matrix, constraints=None):
        """Minimize portfolio variance"""
        n_assets = len(cov_matrix)
        
        def objective(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        bounds = [(0, 1) for _ in range(n_assets)]
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        if constraints:
            constraints_list.extend(constraints)
        
        initial_weights = np.ones(n_assets) / n_assets
        
        result = minimize(objective, initial_weights, method='SLSQP', 
                         bounds=bounds, constraints=constraints_list)
        
        return result.x if result.success else np.ones(n_assets) / n_assets
    
    def _optimize_max_return(self, expected_returns, constraints=None):
        """Maximize expected return"""
        n_assets = len(expected_returns)
        
        def objective(weights):
            return -np.sum(weights * expected_returns)  # Minimize negative return
        
        bounds = [(0, 1) for _ in range(n_assets)]
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        if constraints:
            constraints_list.extend(constraints)
        
        initial_weights = np.ones(n_assets) / n_assets
        
        result = minimize(objective, initial_weights, method='SLSQP', 
                         bounds=bounds, constraints=constraints_list)
        
        return result.x if result.success else np.ones(n_assets) / n_assets

class PriceForecaster:
    """Advanced price forecasting using options data and quantitative models"""
    
    def __init__(self):
        self.options_model = OptionsPricingModel()
        self.vol_analyzer = VolatilityAnalyzer()
        
    def forecast_price_range(self, ticker, forecast_days=30, confidence_level=0.95):
        """
        Forecast price range using options implied volatility
        """
        try:
            # Get current stock data
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            if current_price == 0:
                return None
            
            # Get options data for volatility analysis
            options = stock.options
            if not options:
                return self._historical_forecast(stock, forecast_days, confidence_level)
            
            # Use nearest expiration for IV calculation
            nearest_exp = options[0]
            opt = stock.option_chain(nearest_exp)
            
            # Calculate average implied volatility
            iv_values = []
            for _, call in opt.calls.iterrows():
                if call['bid'] > 0 and call['ask'] > 0:
                    mid_price = (call['bid'] + call['ask']) / 2
                    iv = self.options_model.implied_volatility(
                        current_price, call['strike'], 
                        self._days_to_expiry(nearest_exp) / 365,
                        0.05, mid_price, 'call'
                    )
                    if iv and 0.1 < iv < 2.0:
                        iv_values.append(iv)
            
            for _, put in opt.puts.iterrows():
                if put['bid'] > 0 and put['ask'] > 0:
                    mid_price = (put['bid'] + put['ask']) / 2
                    iv = self.options_model.implied_volatility(
                        current_price, put['strike'], 
                        self._days_to_expiry(nearest_exp) / 365,
                        0.05, mid_price, 'put'
                    )
                    if iv and 0.1 < iv < 2.0:
                        iv_values.append(iv)
            
            if iv_values:
                avg_iv = np.mean(iv_values)
            else:
                # Fallback to historical volatility
                hist_data = stock.history(period='1y')
                returns = np.log(hist_data['Close'] / hist_data['Close'].shift(1))
                avg_iv = returns.std() * np.sqrt(252)
            
            # Calculate price range using log-normal distribution
            time_to_forecast = forecast_days / 365
            drift = 0.05 - 0.5 * avg_iv**2  # Risk-free rate minus volatility adjustment
            
            # Calculate confidence intervals
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            
            lower_bound = current_price * np.exp((drift - z_score * avg_iv) * time_to_forecast)
            upper_bound = current_price * np.exp((drift + z_score * avg_iv) * time_to_forecast)
            expected_price = current_price * np.exp(drift * time_to_forecast)
            
            return {
                'current_price': current_price,
                'expected_price': expected_price,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'confidence_level': confidence_level,
                'implied_volatility': avg_iv,
                'forecast_days': forecast_days
            }
            
        except Exception as e:
            print(f"Error forecasting price for {ticker}: {e}")
            return None
    
    def _days_to_expiry(self, expiration_date):
        """Calculate days to expiration"""
        exp_datetime = datetime.strptime(expiration_date, '%Y-%m-%d')
        return (exp_datetime - datetime.now()).days
    
    def _historical_forecast(self, stock, forecast_days, confidence_level):
        """Fallback to historical volatility forecast"""
        try:
            hist_data = stock.history(period='1y')
            current_price = hist_data['Close'].iloc[-1]
            
            returns = np.log(hist_data['Close'] / hist_data['Close'].shift(1))
            hist_vol = returns.std() * np.sqrt(252)
            
            time_to_forecast = forecast_days / 365
            drift = returns.mean() * 252
            
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            
            lower_bound = current_price * np.exp((drift - z_score * hist_vol) * time_to_forecast)
            upper_bound = current_price * np.exp((drift + z_score * hist_vol) * time_to_forecast)
            expected_price = current_price * np.exp(drift * time_to_forecast)
            
            return {
                'current_price': current_price,
                'expected_price': expected_price,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'confidence_level': confidence_level,
                'implied_volatility': hist_vol,
                'forecast_days': forecast_days,
                'method': 'historical'
            }
            
        except Exception as e:
            print(f"Error in historical forecast: {e}")
            return None

class QuantitativeAnalyzer:
    """Main quantitative analysis orchestrator"""
    
    def __init__(self):
        self.options_model = OptionsPricingModel()
        self.vol_analyzer = VolatilityAnalyzer()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.price_forecaster = PriceForecaster()
    
    def analyze_portfolio(self, holdings_data):
        """
        Comprehensive portfolio analysis
        """
        try:
            # Extract tickers and weights
            tickers = [holding['ticker'] for holding in holdings_data]
            weights = np.array([holding['weight'] for holding in holdings_data])
            
            # Get historical data
            returns_data = {}
            price_data = {}
            
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='1y')
                    if not hist.empty:
                        returns_data[ticker] = hist['Close'].pct_change().dropna()
                        price_data[ticker] = hist['Close']
                except:
                    continue
            
            if not returns_data:
                return None
            
            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data)
            
            # Calculate portfolio metrics
            portfolio_metrics = self.portfolio_optimizer.calculate_portfolio_metrics(returns_df, weights)
            
            # Calculate individual asset metrics
            asset_metrics = {}
            for ticker in returns_data.keys():
                asset_returns = returns_data[ticker]
                asset_metrics[ticker] = {
                    'volatility': asset_returns.std() * np.sqrt(252),
                    'sharpe_ratio': (asset_returns.mean() * 252 - 0.05) / (asset_returns.std() * np.sqrt(252)),
                    'max_drawdown': self.portfolio_optimizer._calculate_max_drawdown(asset_returns),
                    'var_95': np.percentile(asset_returns, 5),
                    'beta': self._calculate_beta(asset_returns, returns_df.mean(axis=1))
                }
            
            # Optimize portfolio
            optimal_weights = self.portfolio_optimizer.optimize_portfolio(returns_df, method='sharpe')
            optimal_metrics = self.portfolio_optimizer.calculate_portfolio_metrics(returns_df, optimal_weights)
            
            # Price forecasts
            price_forecasts = {}
            for ticker in tickers[:5]:  # Limit to first 5 for performance
                forecast = self.price_forecaster.forecast_price_range(ticker, forecast_days=30)
                if forecast:
                    price_forecasts[ticker] = forecast
            
            return {
                'portfolio_metrics': portfolio_metrics,
                'asset_metrics': asset_metrics,
                'optimal_weights': dict(zip(tickers, optimal_weights)),
                'optimal_metrics': optimal_metrics,
                'price_forecasts': price_forecasts,
                'correlation_matrix': returns_df.corr().to_dict(),
                'volatility_analysis': self._analyze_volatility(returns_df)
            }
            
        except Exception as e:
            print(f"Error in portfolio analysis: {e}")
            return None
    
    def _calculate_beta(self, asset_returns, market_returns):
        """Calculate beta relative to portfolio"""
        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        return covariance / market_variance if market_variance != 0 else 1.0
    
    def _analyze_volatility(self, returns_df):
        """Analyze volatility patterns"""
        vol_analysis = {}
        
        for column in returns_df.columns:
            returns = returns_df[column].dropna()
            vol_analysis[column] = {
                'current_vol': returns.tail(30).std() * np.sqrt(252),
                'historical_vol': returns.std() * np.sqrt(252),
                'vol_forecast_30d': self.vol_analyzer.forecast_volatility(
                    returns.index.to_series().map(lambda x: returns.loc[:x].iloc[-1] if x in returns.index else 0),
                    method='garch', forecast_days=30
                ).mean() if len(returns) > 30 else returns.std() * np.sqrt(252)
            }
        
        return vol_analysis
