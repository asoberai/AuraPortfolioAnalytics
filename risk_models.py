"""
Advanced Risk Models for AuraVest
Probability density functions, portfolio covariance analysis, and Monte Carlo simulations
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.optimize import minimize
from scipy.integrate import quad
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PortfolioRiskModel:
    """Advanced portfolio risk modeling with covariance and probability distributions"""
    
    def __init__(self):
        self.risk_free_rate = 0.05
        self.confidence_levels = [0.90, 0.95, 0.99]
        
    def calculate_portfolio_covariance(self, returns_df: pd.DataFrame, weights: np.ndarray) -> Dict:
        """
        Calculate portfolio covariance matrix and risk metrics
        """
        # Calculate covariance matrix
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Portfolio variance
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Individual asset contributions to portfolio risk
        marginal_contributions = np.dot(cov_matrix, weights) / portfolio_volatility
        component_var = weights * marginal_contributions
        
        # Correlation matrix
        correlation_matrix = returns_df.corr()
        
        return {
            'covariance_matrix': cov_matrix.to_dict(),
            'correlation_matrix': correlation_matrix.to_dict(),
            'portfolio_variance': portfolio_variance,
            'portfolio_volatility': portfolio_volatility,
            'marginal_contributions': dict(zip(returns_df.columns, marginal_contributions)),
            'component_var': dict(zip(returns_df.columns, component_var)),
            'risk_contributions': dict(zip(returns_df.columns, component_var / portfolio_volatility))
        }
    
    def monte_carlo_portfolio_simulation(self, 
                                       returns_df: pd.DataFrame, 
                                       weights: np.ndarray, 
                                       n_simulations: int = 10000,
                                       time_horizon: int = 252) -> Dict:
        """
        Monte Carlo simulation for portfolio value distribution
        """
        # Calculate parameters
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        # Generate correlated random returns
        np.random.seed(42)  # For reproducibility
        correlated_returns = np.random.multivariate_normal(
            mean_returns.values, 
            cov_matrix.values, 
            size=(time_horizon, n_simulations)
        )
        
        # Calculate portfolio returns for each simulation
        portfolio_returns = np.dot(correlated_returns, weights)
        
        # Calculate cumulative portfolio values (starting with $100,000)
        initial_value = 100000
        portfolio_values = initial_value * np.exp(np.cumsum(portfolio_returns, axis=0))
        
        # Calculate risk metrics
        final_values = portfolio_values[-1, :]
        
        # Probability density function parameters
        mu = np.mean(final_values)
        sigma = np.std(final_values)
        
        # Calculate VaR and CVaR at different confidence levels
        var_metrics = {}
        cvar_metrics = {}
        
        for confidence in self.confidence_levels:
            alpha = 1 - confidence
            var = np.percentile(final_values, alpha * 100)
            cvar = np.mean(final_values[final_values <= var])
            
            var_metrics[f'var_{int(confidence*100)}'] = var
            cvar_metrics[f'cvar_{int(confidence*100)}'] = cvar
        
        # Calculate probability of loss
        prob_loss = np.mean(final_values < initial_value)
        
        # Calculate expected shortfall
        expected_shortfall = np.mean(final_values[final_values < initial_value])
        
        return {
            'simulation_results': {
                'final_values': final_values.tolist(),
                'portfolio_values': portfolio_values.tolist(),
                'portfolio_returns': portfolio_returns.tolist()
            },
            'risk_metrics': {
                'mean_final_value': mu,
                'std_final_value': sigma,
                'var_metrics': var_metrics,
                'cvar_metrics': cvar_metrics,
                'probability_of_loss': prob_loss,
                'expected_shortfall': expected_shortfall,
                'max_drawdown': self._calculate_max_drawdown(portfolio_values)
            },
            'distribution_params': {
                'mu': mu,
                'sigma': sigma,
                'skewness': stats.skew(final_values),
                'kurtosis': stats.kurtosis(final_values)
            }
        }
    
    def _calculate_max_drawdown(self, portfolio_values: np.ndarray) -> float:
        """Calculate maximum drawdown from portfolio values"""
        peak = np.maximum.accumulate(portfolio_values, axis=0)
        drawdown = (portfolio_values - peak) / peak
        return np.min(drawdown)
    
    def price_probability_density(self, 
                                current_price: float, 
                                volatility: float, 
                                time_horizon: int = 30,
                                n_points: int = 1000) -> Dict:
        """
        Calculate probability density function for future stock prices
        Using log-normal distribution (Black-Scholes assumption)
        """
        # Parameters for log-normal distribution
        drift = 0.05 - 0.5 * volatility**2  # Risk-free rate minus volatility adjustment
        time_to_horizon = time_horizon / 365
        
        # Calculate distribution parameters
        mu = np.log(current_price) + drift * time_to_horizon
        sigma = volatility * np.sqrt(time_to_horizon)
        
        # Generate price range
        min_price = current_price * np.exp(-3 * sigma)
        max_price = current_price * np.exp(3 * sigma)
        price_range = np.linspace(min_price, max_price, n_points)
        
        # Calculate probability density
        pdf_values = stats.lognorm.pdf(price_range, sigma, scale=np.exp(mu))
        
        # Calculate cumulative distribution
        cdf_values = stats.lognorm.cdf(price_range, sigma, scale=np.exp(mu))
        
        # Calculate confidence intervals
        confidence_intervals = {}
        for confidence in self.confidence_levels:
            alpha = 1 - confidence
            lower_bound = stats.lognorm.ppf(alpha/2, sigma, scale=np.exp(mu))
            upper_bound = stats.lognorm.ppf(1-alpha/2, sigma, scale=np.exp(mu))
            confidence_intervals[f'{int(confidence*100)}%'] = {
                'lower': lower_bound,
                'upper': upper_bound
            }
        
        # Calculate expected value and variance
        expected_price = np.exp(mu + 0.5 * sigma**2)
        variance = (np.exp(sigma**2) - 1) * np.exp(2*mu + sigma**2)
        
        return {
            'price_range': price_range.tolist(),
            'pdf_values': pdf_values.tolist(),
            'cdf_values': cdf_values.tolist(),
            'confidence_intervals': confidence_intervals,
            'distribution_params': {
                'mu': mu,
                'sigma': sigma,
                'expected_price': expected_price,
                'variance': variance,
                'volatility': np.sqrt(variance)
            },
            'probabilities': {
                'prob_above_current': 1 - stats.lognorm.cdf(current_price, sigma, scale=np.exp(mu)),
                'prob_below_current': stats.lognorm.cdf(current_price, sigma, scale=np.exp(mu)),
                'prob_positive_return': 1 - stats.lognorm.cdf(current_price, sigma, scale=np.exp(mu))
            }
        }
    
    def portfolio_probability_density(self, 
                                    portfolio_data: Dict,
                                    time_horizon: int = 30) -> Dict:
        """
        Calculate probability density function for entire portfolio
        Considering covariance between assets
        """
        # Extract data
        holdings = portfolio_data['holdings']
        total_value = portfolio_data['total_value']
        
        # Calculate individual asset PDFs
        asset_pdfs = {}
        portfolio_components = []
        
        for holding in holdings:
            ticker = holding['ticker']
            current_price = holding.get('current_price', 100.0)  # Default price if not provided
            quantity = holding.get('quantity', 1)  # Default quantity if not provided
            current_value = holding['current_value']
            
            # Get volatility (simplified - in practice would use historical or implied)
            volatility = 0.25  # Default 25% volatility
            
            # Calculate individual asset PDF
            asset_pdf = self.price_probability_density(current_price, volatility, time_horizon)
            asset_pdfs[ticker] = asset_pdf
            
            # Store portfolio component
            portfolio_components.append({
                'ticker': ticker,
                'weight': current_value / total_value,
                'quantity': quantity,
                'current_price': current_price,
                'current_value': current_value,
                'pdf': asset_pdf
            })
        
        # Calculate portfolio-level metrics
        portfolio_expected_value = 0
        portfolio_variance = 0
        
        for component in portfolio_components:
            weight = component['weight']
            expected_price = component['pdf']['distribution_params']['expected_price']
            variance = component['pdf']['distribution_params']['variance']
            
            portfolio_expected_value += weight * expected_price * component['quantity']
            portfolio_variance += (weight * component['quantity'])**2 * variance
        
        # Add covariance terms (simplified - would need correlation matrix)
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        return {
            'asset_pdfs': asset_pdfs,
            'portfolio_components': portfolio_components,
            'portfolio_metrics': {
                'current_value': total_value,
                'expected_value': portfolio_expected_value,
                'expected_return': (portfolio_expected_value - total_value) / total_value,
                'volatility': portfolio_volatility,
                'sharpe_ratio': ((portfolio_expected_value - total_value) / total_value - self.risk_free_rate * time_horizon/365) / portfolio_volatility
            },
            'risk_analysis': {
                'var_95': total_value * (1 - 1.645 * portfolio_volatility),
                'var_99': total_value * (1 - 2.326 * portfolio_volatility),
                'probability_of_loss': stats.norm.cdf(0, portfolio_expected_value - total_value, portfolio_volatility)
            }
        }
    
    def stress_test_portfolio(self, 
                            portfolio_data: Dict,
                            scenarios: List[Dict]) -> Dict:
        """
        Stress test portfolio under various market scenarios
        """
        results = {}
        
        for scenario in scenarios:
            scenario_name = scenario['name']
            market_shock = scenario['market_shock']  # e.g., -0.20 for 20% market drop
            volatility_multiplier = scenario.get('volatility_multiplier', 1.5)
            
            # Calculate scenario impact
            holdings = portfolio_data['holdings']
            scenario_value = 0
            
            for holding in holdings:
                current_value = holding['current_value']
                # Apply market shock (simplified - would use beta in practice)
                scenario_value += current_value * (1 + market_shock)
            
            # Calculate risk metrics under stress
            stress_volatility = portfolio_data.get('volatility', 0.15) * volatility_multiplier
            stress_var = scenario_value * (1 - 1.645 * stress_volatility)
            
            results[scenario_name] = {
                'scenario_value': scenario_value,
                'value_change': scenario_value - portfolio_data['total_value'],
                'value_change_percent': (scenario_value - portfolio_data['total_value']) / portfolio_data['total_value'],
                'stress_volatility': stress_volatility,
                'stress_var_95': stress_var,
                'stress_probability_of_loss': stats.norm.cdf(0, scenario_value - portfolio_data['total_value'], stress_volatility)
            }
        
        return results
    
    def calculate_copula_dependencies(self, returns_df: pd.DataFrame) -> Dict:
        """
        Calculate copula-based dependencies between assets
        """
        # Calculate rank correlations (Spearman's rho)
        spearman_corr = returns_df.corr(method='spearman')
        
        # Calculate Kendall's tau
        kendall_corr = returns_df.corr(method='kendall')
        
        # Calculate tail dependencies (simplified)
        tail_dependencies = {}
        
        for col1 in returns_df.columns:
            for col2 in returns_df.columns:
                if col1 != col2:
                    # Calculate lower tail dependence
                    threshold = 0.1
                    lower_tail = np.mean((returns_df[col1] < np.quantile(returns_df[col1], threshold)) & 
                                       (returns_df[col2] < np.quantile(returns_df[col2], threshold)))
                    
                    # Calculate upper tail dependence
                    upper_tail = np.mean((returns_df[col1] > np.quantile(returns_df[col1], 1-threshold)) & 
                                       (returns_df[col2] > np.quantile(returns_df[col2], 1-threshold)))
                    
                    tail_dependencies[f'{col1}_{col2}'] = {
                        'lower_tail': lower_tail / threshold,
                        'upper_tail': upper_tail / threshold
                    }
        
        return {
            'spearman_correlation': spearman_corr.to_dict(),
            'kendall_correlation': kendall_corr.to_dict(),
            'tail_dependencies': tail_dependencies
        }

class RiskVisualizer:
    """Advanced risk visualization for portfolio analysis"""
    
    def __init__(self):
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
    def create_risk_dashboard_data(self, 
                                 portfolio_data: Dict,
                                 risk_model: PortfolioRiskModel) -> Dict:
        """
        Create comprehensive risk dashboard data
        """
        # Calculate all risk metrics
        holdings = portfolio_data['holdings']
        
        # Individual asset risk metrics
        asset_risks = []
        for holding in holdings:
            ticker = holding['ticker']
            current_price = holding.get('current_price', 100.0)  # Default price if not provided
            current_value = holding['current_value']
            weight = current_value / portfolio_data['total_value']
            
            # Calculate individual asset PDF
            volatility = 0.25  # Would get from historical data
            pdf_data = risk_model.price_probability_density(current_price, volatility)
            
            asset_risks.append({
                'ticker': ticker,
                'weight': weight,
                'current_value': current_value,
                'volatility': volatility,
                'var_95': current_value * (1 - 1.645 * volatility),
                'expected_return': pdf_data['distribution_params']['expected_price'] / current_price - 1,
                'probability_of_loss': pdf_data['probabilities']['prob_below_current']
            })
        
        # Portfolio-level Monte Carlo simulation
        if len(holdings) > 1:
            # Create returns DataFrame for simulation
            returns_data = {}
            for holding in holdings:
                # Simplified - would use actual historical returns
                returns_data[holding['ticker']] = np.random.normal(0.08, 0.25, 252)
            
            returns_df = pd.DataFrame(returns_data)
            weights = np.array([h['current_value'] / portfolio_data['total_value'] for h in holdings])
            
            # Run Monte Carlo simulation
            mc_results = risk_model.monte_carlo_portfolio_simulation(returns_df, weights)
            
            # Calculate covariance analysis
            cov_analysis = risk_model.calculate_portfolio_covariance(returns_df, weights)
        else:
            mc_results = None
            cov_analysis = None
        
        # Stress test scenarios
        scenarios = [
            {'name': 'Market Crash (-20%)', 'market_shock': -0.20, 'volatility_multiplier': 2.0},
            {'name': 'Recession (-10%)', 'market_shock': -0.10, 'volatility_multiplier': 1.5},
            {'name': 'Volatility Spike', 'market_shock': 0.0, 'volatility_multiplier': 2.5},
            {'name': 'Bull Market (+15%)', 'market_shock': 0.15, 'volatility_multiplier': 0.8}
        ]
        
        stress_results = risk_model.stress_test_portfolio(portfolio_data, scenarios)
        
        return {
            'portfolio_summary': {
                'total_value': portfolio_data['total_value'],
                'number_of_holdings': len(holdings),
                'largest_position': max(holdings, key=lambda x: x['current_value'])['ticker'],
                'largest_weight': max(holdings, key=lambda x: x['current_value'])['current_value'] / portfolio_data['total_value']
            },
            'asset_risks': asset_risks,
            'monte_carlo_results': mc_results,
            'covariance_analysis': cov_analysis,
            'stress_test_results': stress_results,
            'risk_metrics': {
                'total_var_95': sum(asset['var_95'] for asset in asset_risks),
                'weighted_volatility': sum(asset['weight'] * asset['volatility'] for asset in asset_risks),
                'concentration_risk': max(asset['weight'] for asset in asset_risks),
                'diversification_benefit': 1 - (sum(asset['weight'] * asset['volatility'] for asset in asset_risks) / 
                                               max(asset['volatility'] for asset in asset_risks))
            }
        }
    
    def generate_risk_charts(self, dashboard_data: Dict) -> Dict:
        """
        Generate chart data for risk visualization
        """
        charts = {}
        
        # Asset allocation pie chart
        asset_risks = dashboard_data['asset_risks']
        charts['allocation'] = {
            'labels': [asset['ticker'] for asset in asset_risks],
            'values': [asset['current_value'] for asset in asset_risks],
            'weights': [asset['weight'] for asset in asset_risks]
        }
        
        # Risk contribution bar chart
        charts['risk_contribution'] = {
            'labels': [asset['ticker'] for asset in asset_risks],
            'values': [asset['weight'] * asset['volatility'] for asset in asset_risks],
            'colors': self.colors[:len(asset_risks)]
        }
        
        # Monte Carlo distribution
        if dashboard_data['monte_carlo_results']:
            mc_data = dashboard_data['monte_carlo_results']['simulation_results']['final_values']
            charts['monte_carlo_distribution'] = {
                'values': mc_data,
                'mean': dashboard_data['monte_carlo_results']['risk_metrics']['mean_final_value'],
                'var_95': dashboard_data['monte_carlo_results']['risk_metrics']['var_metrics']['var_95'],
                'var_99': dashboard_data['monte_carlo_results']['risk_metrics']['var_metrics']['var_99']
            }
        
        # Stress test results
        stress_results = dashboard_data['stress_test_results']
        charts['stress_test'] = {
            'scenarios': list(stress_results.keys()),
            'values': [stress_results[scenario]['value_change_percent'] for scenario in stress_results.keys()],
            'colors': ['red' if v < 0 else 'green' for v in [stress_results[scenario]['value_change_percent'] for scenario in stress_results.keys()]]
        }
        
        # Correlation heatmap
        if dashboard_data['covariance_analysis']:
            corr_matrix = dashboard_data['covariance_analysis']['correlation_matrix']
            charts['correlation_heatmap'] = {
                'data': corr_matrix,
                'tickers': list(corr_matrix.keys())
            }
        
        return charts
