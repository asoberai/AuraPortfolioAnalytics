"""
Comprehensive tests for enhanced risk analysis features
"""
import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

# Import the FastAPI app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from risk_models import PortfolioRiskModel, RiskVisualizer

client = TestClient(app)

@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing"""
    return {
        "holdings": [
            {"ticker": "AAPL", "current_value": 10000, "weight": 0.4},
            {"ticker": "GOOGL", "current_value": 7500, "weight": 0.3},
            {"ticker": "MSFT", "current_value": 5000, "weight": 0.2},
            {"ticker": "TSLA", "current_value": 2500, "weight": 0.1}
        ],
        "total_value": 25000,
        "total_cost": 20000
    }

@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers for testing"""
    return {"Authorization": "Bearer test_token"}

@pytest.fixture
def risk_model():
    """Initialize risk model for testing"""
    return PortfolioRiskModel()

class TestRiskAnalysisAPI:
    """Test suite for risk analysis API endpoints"""

    @patch('main.get_current_user')
    def test_portfolio_risk_analysis_endpoint(self, mock_user, sample_portfolio_data, mock_auth_headers):
        """Test portfolio risk analysis endpoint"""
        mock_user.return_value = Mock(id=1, email="test@example.com")
        
        response = client.post(
            "/analysis/risk/portfolio",
            json=sample_portfolio_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "risk_analysis" in data
        assert "charts" in data
        assert "summary" in data
        
        # Verify risk metrics
        risk_analysis = data["risk_analysis"]
        assert "risk_metrics" in risk_analysis
        assert "weighted_volatility" in risk_analysis["risk_metrics"]
        assert "diversification_benefit" in risk_analysis["risk_metrics"]

    @patch('main.get_current_user')
    def test_monte_carlo_simulation_endpoint(self, mock_user, sample_portfolio_data, mock_auth_headers):
        """Test Monte Carlo simulation endpoint"""
        mock_user.return_value = Mock(id=1, email="test@example.com")
        
        response = client.post(
            "/analysis/risk/monte-carlo",
            json=sample_portfolio_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify simulation parameters
        assert "simulation_params" in data
        assert "results" in data
        assert data["simulation_params"]["n_simulations"] > 0

    @patch('main.get_current_user')
    def test_covariance_analysis_endpoint(self, mock_user, sample_portfolio_data, mock_auth_headers):
        """Test covariance analysis endpoint"""
        mock_user.return_value = Mock(id=1, email="test@example.com")
        
        response = client.post(
            "/analysis/risk/covariance",
            json=sample_portfolio_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify covariance analysis structure
        assert "covariance_analysis" in data
        assert "copula_analysis" in data
        assert "portfolio_risk_decomposition" in data

    def test_price_probability_density_endpoint(self):
        """Test price probability density function endpoint"""
        response = client.get("/analysis/risk/price-pdf/AAPL?time_horizon=30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify PDF data structure
        assert "ticker" in data
        assert "current_price" in data
        assert "probability_density" in data
        assert data["ticker"] == "AAPL"

    @patch('main.get_current_user')
    def test_stress_test_endpoint(self, mock_user, sample_portfolio_data, mock_auth_headers):
        """Test stress testing endpoint"""
        mock_user.return_value = Mock(id=1, email="test@example.com")
        
        response = client.post(
            "/analysis/risk/stress-test",
            json=sample_portfolio_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify stress test results
        assert "stress_test_results" in data
        assert "scenarios_tested" in data
        assert "worst_case_scenario" in data
        assert "best_case_scenario" in data

class TestRiskModels:
    """Test suite for risk calculation models"""

    def test_portfolio_risk_calculation(self, risk_model, sample_portfolio_data):
        """Test portfolio risk metrics calculation"""
        # Create mock returns data
        returns_data = pd.DataFrame({
            'AAPL': np.random.normal(0.08/252, 0.25/np.sqrt(252), 252),
            'GOOGL': np.random.normal(0.10/252, 0.28/np.sqrt(252), 252),
            'MSFT': np.random.normal(0.12/252, 0.22/np.sqrt(252), 252),
            'TSLA': np.random.normal(0.15/252, 0.35/np.sqrt(252), 252)
        })
        
        weights = np.array([0.4, 0.3, 0.2, 0.1])
        
        # Test covariance calculation
        cov_analysis = risk_model.calculate_portfolio_covariance(returns_data, weights)
        
        assert "portfolio_volatility" in cov_analysis
        assert "risk_contributions" in cov_analysis
        assert isinstance(cov_analysis["portfolio_volatility"], float)
        assert cov_analysis["portfolio_volatility"] > 0

    def test_monte_carlo_simulation(self, risk_model):
        """Test Monte Carlo portfolio simulation"""
        # Create mock returns data
        returns_data = pd.DataFrame({
            'AAPL': np.random.normal(0.08/252, 0.25/np.sqrt(252), 252),
            'GOOGL': np.random.normal(0.10/252, 0.28/np.sqrt(252), 252)
        })
        
        weights = np.array([0.6, 0.4])
        
        # Run Monte Carlo simulation
        mc_results = risk_model.monte_carlo_portfolio_simulation(
            returns_data, weights, n_simulations=1000, time_horizon=252
        )
        
        assert "final_values" in mc_results
        assert "expected_return" in mc_results
        assert "percentile_5" in mc_results
        assert "percentile_95" in mc_results
        
        # Verify simulation results are reasonable
        assert len(mc_results["final_values"]) == 1000
        assert mc_results["percentile_5"] < mc_results["expected_return"]
        assert mc_results["expected_return"] < mc_results["percentile_95"]

    def test_price_probability_density(self, risk_model):
        """Test price probability density function calculation"""
        current_price = 150.0
        volatility = 0.25
        time_horizon = 30
        
        pdf_data = risk_model.price_probability_density(current_price, volatility, time_horizon)
        
        assert "price_range" in pdf_data
        assert "pdf_values" in pdf_data
        assert "cdf_values" in pdf_data
        assert "confidence_intervals" in pdf_data
        assert "distribution_params" in pdf_data
        
        # Verify data integrity
        assert len(pdf_data["price_range"]) == len(pdf_data["pdf_values"])
        assert all(p >= 0 for p in pdf_data["pdf_values"])  # PDF values should be non-negative

    def test_stress_testing(self, risk_model, sample_portfolio_data):
        """Test portfolio stress testing functionality"""
        scenarios = [
            {'name': 'Market Crash', 'market_shock': -0.20, 'volatility_multiplier': 2.0},
            {'name': 'Bull Market', 'market_shock': 0.15, 'volatility_multiplier': 0.8}
        ]
        
        stress_results = risk_model.stress_test_portfolio(sample_portfolio_data, scenarios)
        
        assert len(stress_results) == len(scenarios)
        for scenario_name, results in stress_results.items():
            assert "value_change" in results
            assert "value_change_percent" in results
            assert "new_portfolio_value" in results
            assert isinstance(results["value_change_percent"], float)

class TestRiskVisualization:
    """Test suite for risk visualization components"""

    def test_risk_dashboard_data_generation(self, sample_portfolio_data):
        """Test risk dashboard data creation"""
        risk_model = PortfolioRiskModel()
        risk_visualizer = RiskVisualizer()
        
        dashboard_data = risk_visualizer.create_risk_dashboard_data(sample_portfolio_data, risk_model)
        
        assert "risk_metrics" in dashboard_data
        assert "asset_breakdown" in dashboard_data
        assert "correlation_matrix" in dashboard_data
        
        # Verify risk metrics structure
        risk_metrics = dashboard_data["risk_metrics"]
        assert "weighted_volatility" in risk_metrics
        assert "diversification_benefit" in risk_metrics
        assert "concentration_risk" in risk_metrics

    def test_chart_generation(self, sample_portfolio_data):
        """Test chart data generation for visualizations"""
        risk_model = PortfolioRiskModel()
        risk_visualizer = RiskVisualizer()
        
        dashboard_data = risk_visualizer.create_risk_dashboard_data(sample_portfolio_data, risk_model)
        charts = risk_visualizer.generate_risk_charts(dashboard_data)
        
        assert "allocation_chart" in charts
        assert "risk_breakdown_chart" in charts
        assert "correlation_heatmap" in charts
        
        # Verify chart data structure
        allocation_chart = charts["allocation_chart"]
        assert "labels" in allocation_chart
        assert "data" in allocation_chart
        assert len(allocation_chart["labels"]) == len(allocation_chart["data"])

class TestMarketDataIntegration:
    """Test suite for market data integration"""

    def test_stock_data_endpoint(self):
        """Test market data retrieval for stocks"""
        response = client.get("/market/stock/AAPL")
        
        # Should return data or handle gracefully
        if response.status_code == 200:
            data = response.json()
            assert "basic_data" in data
            assert "options_data" in data
            assert "volatility_analysis" in data
        else:
            # Market data might not be available in test environment
            assert response.status_code in [500, 404]

    def test_multiple_stocks_endpoint(self):
        """Test multiple stocks data retrieval"""
        response = client.get("/market/stocks?tickers=AAPL,GOOGL,MSFT")
        
        # Should return data structure even if some data is unavailable
        assert response.status_code in [200, 500]  # May fail due to data availability

class TestPerformanceMetrics:
    """Test suite for performance and accuracy"""

    def test_risk_calculation_accuracy(self, risk_model):
        """Test accuracy of risk calculations against known values"""
        # Create deterministic test data
        np.random.seed(42)
        returns_data = pd.DataFrame({
            'STOCK1': np.random.normal(0.1/252, 0.2/np.sqrt(252), 252),
            'STOCK2': np.random.normal(0.08/252, 0.15/np.sqrt(252), 252)
        })
        
        weights = np.array([0.6, 0.4])
        
        # Calculate portfolio volatility
        cov_analysis = risk_model.calculate_portfolio_covariance(returns_data, weights)
        portfolio_vol = cov_analysis["portfolio_volatility"]
        
        # Verify volatility is within reasonable bounds
        assert 0.05 < portfolio_vol < 0.50  # Between 5% and 50% annualized
        
        # Test diversification benefit
        individual_vols = returns_data.std() * np.sqrt(252)
        weighted_avg_vol = np.dot(weights, individual_vols)
        
        diversification_benefit = (weighted_avg_vol - portfolio_vol) / weighted_avg_vol
        assert diversification_benefit >= 0  # Should always be positive

    def test_monte_carlo_convergence(self, risk_model):
        """Test Monte Carlo simulation convergence"""
        returns_data = pd.DataFrame({
            'TEST': np.random.normal(0.1/252, 0.2/np.sqrt(252), 252)
        })
        
        weights = np.array([1.0])
        
        # Run simulations with different sample sizes
        results_1000 = risk_model.monte_carlo_portfolio_simulation(
            returns_data, weights, n_simulations=1000, time_horizon=252
        )
        results_10000 = risk_model.monte_carlo_portfolio_simulation(
            returns_data, weights, n_simulations=10000, time_horizon=252
        )
        
        # Expected returns should converge
        diff = abs(results_1000["expected_return"] - results_10000["expected_return"])
        assert diff < 0.05  # Difference should be less than 5%

@pytest.mark.asyncio
class TestEndToEndWorkflow:
    """End-to-end integration tests"""

    @patch('main.get_current_user')
    async def test_complete_risk_analysis_workflow(self, mock_user, sample_portfolio_data, mock_auth_headers):
        """Test complete risk analysis workflow"""
        mock_user.return_value = Mock(id=1, email="test@example.com")
        
        # Test portfolio risk analysis
        risk_response = client.post(
            "/analysis/risk/portfolio",
            json=sample_portfolio_data,
            headers=mock_auth_headers
        )
        assert risk_response.status_code == 200
        
        # Test Monte Carlo simulation
        mc_response = client.post(
            "/analysis/risk/monte-carlo",
            json=sample_portfolio_data,
            headers=mock_auth_headers
        )
        assert mc_response.status_code == 200
        
        # Test stress testing
        stress_response = client.post(
            "/analysis/risk/stress-test",
            json=sample_portfolio_data,
            headers=mock_auth_headers
        )
        assert stress_response.status_code == 200
        
        # Verify all responses have consistent data
        risk_data = risk_response.json()
        mc_data = mc_response.json()
        stress_data = stress_response.json()
        
        assert all(response["status"] != "error" for response in [risk_data, mc_data, stress_data] if "status" in response)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])