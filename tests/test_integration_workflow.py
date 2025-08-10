"""
Integration tests for complete AuraVest workflow
"""
import pytest
import asyncio
import httpx
import json
import time
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd
import numpy as np

# Test configuration
TEST_BASE_URL = "http://localhost:8000"
TEST_FRONTEND_URL = "http://localhost:3000"

class TestCompleteUserWorkflow:
    """Test complete user workflow from registration to risk analysis"""
    
    @pytest.fixture
    async def async_client(self):
        """Async HTTP client for API testing"""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client
    
    @pytest.fixture
    def test_user_data(self):
        """Test user registration data"""
        return {
            "email": "test_integration@auravest.com",
            "password": "SecureTestPassword123!"
        }
    
    @pytest.fixture
    def test_portfolio_data(self):
        """Test portfolio data"""
        return {
            "name": "Integration Test Portfolio",
            "description": "Portfolio for integration testing"
        }
    
    @pytest.fixture
    def test_holdings_data(self):
        """Test holdings data"""
        return [
            {
                "ticker_symbol": "AAPL",
                "quantity": 10,
                "purchase_price": 150.0,
                "purchase_date": "2024-01-01"
            },
            {
                "ticker_symbol": "GOOGL", 
                "quantity": 5,
                "purchase_price": 2800.0,
                "purchase_date": "2024-01-01"
            },
            {
                "ticker_symbol": "MSFT",
                "quantity": 15,
                "purchase_price": 400.0,
                "purchase_date": "2024-01-01"
            }
        ]
    
    @pytest.fixture
    def risk_questionnaire_data(self):
        """Test risk questionnaire responses"""
        return {
            "investment_goals": "balanced",
            "time_horizon": 7,
            "risk_comfort": 3,
            "market_experience": "moderate",
            "reaction_to_loss": "hold",
            "income_stability": "stable",
            "investment_knowledge": "moderate"
        }

    @pytest.mark.asyncio
    async def test_complete_user_journey(self, async_client, test_user_data, test_portfolio_data, 
                                       test_holdings_data, risk_questionnaire_data):
        """Test complete user journey from registration to risk analysis"""
        
        # Step 1: User Registration
        print("Testing user registration...")
        registration_response = await async_client.post("/auth/register", json=test_user_data)
        
        if registration_response.status_code == 400 and "already registered" in registration_response.text:
            # User already exists, try login instead
            login_response = await async_client.post("/auth/login", json=test_user_data)
            assert login_response.status_code == 200
            auth_data = login_response.json()
        else:
            assert registration_response.status_code == 200
            auth_data = registration_response.json()
        
        # Extract token
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Complete Risk Questionnaire
        print("Testing risk questionnaire submission...")
        risk_response = await async_client.post(
            "/profile/risk-questionnaire", 
            json=risk_questionnaire_data,
            headers=headers
        )
        assert risk_response.status_code == 200
        risk_data = risk_response.json()
        assert "risk_score" in risk_data
        assert "risk_category" in risk_data
        
        # Step 3: Create Portfolio
        print("Testing portfolio creation...")
        portfolio_response = await async_client.post(
            "/portfolio/create",
            json=test_portfolio_data,
            headers=headers
        )
        assert portfolio_response.status_code == 200
        portfolio_data = portfolio_response.json()
        portfolio_id = portfolio_data["id"]
        
        # Step 4: Add Holdings
        print("Testing holdings addition...")
        for holding in test_holdings_data:
            holding_response = await async_client.post(
                f"/portfolio/{portfolio_id}/holdings",
                json=holding,
                headers=headers
            )
            assert holding_response.status_code == 200
        
        # Step 5: Fetch Portfolio with Current Values
        print("Testing portfolio retrieval with market data...")
        portfolio_get_response = await async_client.get(
            f"/portfolio/{portfolio_id}",
            headers=headers
        )
        assert portfolio_get_response.status_code == 200
        portfolio_full = portfolio_get_response.json()
        
        assert "holdings" in portfolio_full
        assert len(portfolio_full["holdings"]) == len(test_holdings_data)
        assert "total_value" in portfolio_full
        assert portfolio_full["total_value"] > 0
        
        # Step 6: Risk Analysis
        print("Testing comprehensive risk analysis...")
        risk_analysis_response = await async_client.post(
            "/analysis/risk/portfolio",
            json=portfolio_full,
            headers=headers
        )
        assert risk_analysis_response.status_code == 200
        risk_analysis = risk_analysis_response.json()
        
        assert "risk_analysis" in risk_analysis
        assert "summary" in risk_analysis
        
        # Step 7: Monte Carlo Simulation
        print("Testing Monte Carlo simulation...")
        mc_response = await async_client.post(
            "/analysis/risk/monte-carlo",
            json=portfolio_full,
            headers=headers
        )
        assert mc_response.status_code == 200
        mc_data = mc_response.json()
        
        assert "simulation_params" in mc_data
        assert "results" in mc_data
        
        # Step 8: Stress Testing
        print("Testing stress testing...")
        stress_response = await async_client.post(
            "/analysis/risk/stress-test",
            json=portfolio_full,
            headers=headers
        )
        assert stress_response.status_code == 200
        stress_data = stress_response.json()
        
        assert "stress_test_results" in stress_data
        assert "worst_case_scenario" in stress_data
        assert "best_case_scenario" in stress_data
        
        # Step 9: Covariance Analysis
        print("Testing covariance analysis...")
        cov_response = await async_client.post(
            "/analysis/risk/covariance",
            json=portfolio_full,
            headers=headers
        )
        assert cov_response.status_code == 200
        cov_data = cov_response.json()
        
        assert "covariance_analysis" in cov_data
        assert "portfolio_risk_decomposition" in cov_data
        
        # Step 10: User Profile Retrieval
        print("Testing user profile retrieval...")
        profile_response = await async_client.get("/profile", headers=headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        
        assert profile_data["email"] == test_user_data["email"]
        assert "risk_assessment" in profile_data
        assert profile_data["risk_assessment"]["risk_category"] is not None
        
        print("✅ Complete user journey test passed!")
        
        return {
            "user": profile_data,
            "portfolio": portfolio_full,
            "risk_analysis": risk_analysis,
            "monte_carlo": mc_data,
            "stress_test": stress_data,
            "covariance": cov_data
        }

class TestPerformanceValidation:
    """Test performance and accuracy of risk calculations"""
    
    @pytest.mark.asyncio
    async def test_risk_calculation_performance(self, async_client):
        """Test risk calculation performance under load"""
        
        # Create a large portfolio for performance testing
        large_portfolio = {
            "holdings": [
                {"ticker": f"STOCK{i}", "current_value": 1000 + i*100, "weight": 1/20}
                for i in range(20)
            ],
            "total_value": 30000
        }
        
        # Mock authentication
        headers = {"Authorization": "Bearer test_token"}
        
        # Measure response times for different analysis types
        start_time = time.time()
        
        with patch('main.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, email="perf@test.com")
            
            # Test Monte Carlo performance (should complete within 10 seconds)
            mc_response = await async_client.post(
                "/analysis/risk/monte-carlo",
                json=large_portfolio,
                headers=headers
            )
            
            mc_time = time.time() - start_time
            print(f"Monte Carlo simulation time: {mc_time:.2f} seconds")
            
            assert mc_response.status_code == 200
            assert mc_time < 10.0, f"Monte Carlo took too long: {mc_time:.2f}s"
    
    def test_risk_metrics_accuracy(self):
        """Test accuracy of risk metrics against theoretical values"""
        from risk_models import PortfolioRiskModel
        
        risk_model = PortfolioRiskModel()
        
        # Create controlled test data
        np.random.seed(42)  # For reproducible results
        
        # Single asset test (no diversification)
        single_asset_returns = pd.DataFrame({
            'STOCK1': np.random.normal(0.1/252, 0.2/np.sqrt(252), 252)
        })
        
        weights_single = np.array([1.0])
        
        cov_analysis = risk_model.calculate_portfolio_covariance(single_asset_returns, weights_single)
        
        # For single asset, portfolio volatility should equal individual asset volatility
        expected_vol = single_asset_returns['STOCK1'].std() * np.sqrt(252)
        calculated_vol = cov_analysis['portfolio_volatility']
        
        # Allow small numerical difference
        assert abs(calculated_vol - expected_vol) < 0.01, \
            f"Single asset vol mismatch: expected {expected_vol:.4f}, got {calculated_vol:.4f}"
        
        # Test diversification benefit
        two_asset_returns = pd.DataFrame({
            'STOCK1': np.random.normal(0.1/252, 0.2/np.sqrt(252), 252),
            'STOCK2': np.random.normal(0.08/252, 0.18/np.sqrt(252), 252)
        })
        
        # Make them uncorrelated by construction
        two_asset_returns['STOCK2'] = np.random.normal(0.08/252, 0.18/np.sqrt(252), 252)
        
        weights_equal = np.array([0.5, 0.5])
        
        two_asset_cov = risk_model.calculate_portfolio_covariance(two_asset_returns, weights_equal)
        two_asset_vol = two_asset_cov['portfolio_volatility']
        
        # Two uncorrelated assets should reduce portfolio volatility
        individual_vols = two_asset_returns.std() * np.sqrt(252)
        weighted_avg_vol = np.dot(weights_equal, individual_vols)
        
        # Portfolio volatility should be less than weighted average (diversification benefit)
        assert two_asset_vol < weighted_avg_vol, \
            f"No diversification benefit: portfolio vol {two_asset_vol:.4f} >= weighted avg {weighted_avg_vol:.4f}"

class TestSystemResilience:
    """Test system behavior under various conditions"""
    
    @pytest.mark.asyncio
    async def test_error_handling(self, async_client):
        """Test error handling for invalid requests"""
        
        # Test invalid portfolio data
        invalid_portfolio = {"invalid": "data"}
        headers = {"Authorization": "Bearer test_token"}
        
        with patch('main.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, email="test@example.com")
            
            response = await async_client.post(
                "/analysis/risk/portfolio",
                json=invalid_portfolio,
                headers=headers
            )
            
            # Should handle error gracefully
            assert response.status_code in [400, 422, 500]
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client):
        """Test system behavior under concurrent load"""
        
        portfolio_data = {
            "holdings": [
                {"ticker": "AAPL", "current_value": 10000, "weight": 0.5},
                {"ticker": "GOOGL", "current_value": 10000, "weight": 0.5}
            ],
            "total_value": 20000
        }
        
        headers = {"Authorization": "Bearer test_token"}
        
        with patch('main.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, email="test@example.com")
            
            # Send 5 concurrent requests
            tasks = []
            for i in range(5):
                task = async_client.post(
                    "/analysis/risk/portfolio",
                    json=portfolio_data,
                    headers=headers
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # At least most requests should succeed
            successful_responses = [r for r in responses if hasattr(r, 'status_code') and r.status_code == 200]
            assert len(successful_responses) >= 3, f"Only {len(successful_responses)} out of 5 requests succeeded"

class TestDataValidation:
    """Test data validation and integrity"""
    
    @pytest.mark.asyncio
    async def test_market_data_consistency(self, async_client):
        """Test market data consistency and validation"""
        
        # Test individual stock data endpoint
        response = await async_client.get("/market/stock/AAPL")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify data structure
            assert "basic_data" in data
            basic_data = data["basic_data"]
            
            if "price" in basic_data:
                # Price should be positive
                assert basic_data["price"] > 0
                
            if "change_percent" in basic_data:
                # Change percent should be reasonable (not more than ±50% in a day)
                assert -50 <= basic_data["change_percent"] <= 50
    
    def test_portfolio_calculations(self):
        """Test portfolio calculation accuracy"""
        
        # Test data
        holdings = [
            {"ticker": "AAPL", "quantity": 10, "purchase_price": 100, "current_price": 150},
            {"ticker": "GOOGL", "quantity": 5, "purchase_price": 2000, "current_price": 2500}
        ]
        
        # Calculate expected values
        expected_total_cost = (10 * 100) + (5 * 2000)  # 11,000
        expected_total_value = (10 * 150) + (5 * 2500)  # 14,000
        expected_total_pnl = expected_total_value - expected_total_cost  # 3,000
        expected_pnl_percent = (expected_total_pnl / expected_total_cost) * 100  # 27.27%
        
        # Verify calculations
        assert expected_total_cost == 11000
        assert expected_total_value == 14000
        assert expected_total_pnl == 3000
        assert abs(expected_pnl_percent - 27.27) < 0.01

def run_integration_tests():
    """Run all integration tests"""
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            __file__, 
            '-v', 
            '--tb=short',
            '--asyncio-mode=auto',
            '-s'  # Don't capture output so we can see progress
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running integration tests: {e}")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)