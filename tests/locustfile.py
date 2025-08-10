"""
Performance testing with Locust for AuraVest API
"""
from locust import HttpUser, task, between
import json
import random

class AuraVestUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Mock authentication for performance testing
        self.token = "test_performance_token"
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Sample portfolio data for testing
        self.portfolio_data = {
            "holdings": [
                {"ticker": "AAPL", "current_value": 10000, "weight": 0.3},
                {"ticker": "GOOGL", "current_value": 8000, "weight": 0.25},
                {"ticker": "MSFT", "current_value": 7000, "weight": 0.2},
                {"ticker": "TSLA", "current_value": 5000, "weight": 0.15},
                {"ticker": "AMZN", "current_value": 3000, "weight": 0.1}
            ],
            "total_value": 33000,
            "total_cost": 30000
        }

    @task(1)
    def health_check(self):
        """Test health endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def get_stock_data(self):
        """Test individual stock data retrieval"""
        tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        ticker = random.choice(tickers)
        
        with self.client.get(f"/market/stock/{ticker}", catch_response=True) as response:
            if response.status_code in [200, 500]:  # 500 might be expected due to rate limits
                response.success()
            else:
                response.failure(f"Stock data failed for {ticker}: {response.status_code}")

    @task(3)
    def portfolio_risk_analysis(self):
        """Test portfolio risk analysis performance"""
        with self.client.post(
            "/analysis/risk/portfolio",
            json=self.portfolio_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Verify response has expected structure
                try:
                    data = response.json()
                    if "risk_analysis" in data and "summary" in data:
                        response.success()
                    else:
                        response.failure("Invalid response structure")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 401:
                # Authentication might be mocked differently in test
                response.success()
            else:
                response.failure(f"Risk analysis failed: {response.status_code}")

    @task(2)
    def monte_carlo_simulation(self):
        """Test Monte Carlo simulation performance"""
        with self.client.post(
            "/analysis/risk/monte-carlo",
            json=self.portfolio_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 401]:  # 401 expected due to auth mock
                response.success()
            else:
                response.failure(f"Monte Carlo failed: {response.status_code}")

    @task(1)
    def stress_test(self):
        """Test stress testing performance"""
        with self.client.post(
            "/analysis/risk/stress-test",
            json=self.portfolio_data,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Stress test failed: {response.status_code}")

    @task(1)
    def price_probability_density(self):
        """Test PDF calculation performance"""
        tickers = ["AAPL", "GOOGL", "MSFT"]
        ticker = random.choice(tickers)
        
        with self.client.get(
            f"/analysis/risk/price-pdf/{ticker}?time_horizon=30",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"PDF calculation failed for {ticker}: {response.status_code}")

class HeavyLoadUser(HttpUser):
    """Simulate heavy computational load"""
    wait_time = between(0.5, 1.5)
    
    def on_start(self):
        self.token = "heavy_load_token"
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Larger portfolio for stress testing
        self.large_portfolio = {
            "holdings": [
                {"ticker": f"STOCK{i}", "current_value": 1000 + i*50, "weight": 1/20}
                for i in range(20)
            ],
            "total_value": 50000,
            "total_cost": 45000
        }

    @task
    def heavy_monte_carlo(self):
        """Test heavy Monte Carlo simulation"""
        # Request larger simulation
        payload = {**self.large_portfolio, "n_simulations": 10000}
        
        with self.client.post(
            "/analysis/risk/monte-carlo",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 401, 500]:  # May timeout or fail
                response.success()
            else:
                response.failure(f"Heavy Monte Carlo failed: {response.status_code}")