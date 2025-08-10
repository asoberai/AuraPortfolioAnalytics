#!/usr/bin/env python3
"""
AuraVest MVP Phase 1 - Comprehensive Test Suite
Tests all PRD-compliant functionality
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@auravest.com",
    "password": "testpassword123"
}

class AuraVestTester:
    def __init__(self):
        self.token = None
        self.portfolio_id = None
        self.session = requests.Session()
    
    def test_health_check(self):
        """Test basic health endpoint"""
        print("🩺 Testing health check...")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed - Phase: {data['phase']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        print("👤 Testing user registration...")
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                json=TEST_USER
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ User registration successful")
                return True
            else:
                print(f"❌ Registration failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_user_login(self):
        """Test user login (alternative to registration)"""
        print("🔐 Testing user login...")
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=TEST_USER
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ User login successful")
                return True
            else:
                print(f"❌ Login failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_risk_questionnaire(self):
        """Test risk profiling questionnaire"""
        print("📊 Testing risk questionnaire...")
        questionnaire = {
            "investment_goals": "Long-term growth",
            "time_horizon": 15,
            "risk_comfort": 4,
            "market_experience": "Experienced investor",
            "reaction_to_loss": "Hold and wait for recovery",
            "income_stability": "Very stable",
            "investment_knowledge": "Advanced"
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/profile/risk-questionnaire",
                json=questionnaire
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Risk profile: {data['risk_category']} (score: {data['risk_score']:.2f})")
                return True
            else:
                print(f"❌ Risk questionnaire failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Risk questionnaire error: {e}")
            return False
    
    def test_portfolio_creation(self):
        """Test portfolio creation"""
        print("📁 Testing portfolio creation...")
        try:
            response = self.session.post(
                f"{BASE_URL}/portfolio/create",
                params={"name": "Test Portfolio"}
            )
            if response.status_code == 200:
                data = response.json()
                self.portfolio_id = data["id"]
                print(f"✅ Portfolio created: {data['name']} (ID: {self.portfolio_id})")
                return True
            else:
                print(f"❌ Portfolio creation failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Portfolio creation error: {e}")
            return False
    
    def test_add_holdings(self):
        """Test adding holdings to portfolio"""
        print("📈 Testing add holdings...")
        holdings = [
            {"ticker_symbol": "AAPL", "quantity": 10, "purchase_price": 150.0},
            {"ticker_symbol": "GOOGL", "quantity": 5, "purchase_price": 2500.0},
            {"ticker_symbol": "TSLA", "quantity": 8, "purchase_price": 800.0}
        ]
        
        success_count = 0
        for holding in holdings:
            try:
                response = self.session.post(
                    f"{BASE_URL}/portfolio/{self.portfolio_id}/holdings",
                    json=holding
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Added {holding['quantity']} shares of {holding['ticker_symbol']}")
                    success_count += 1
                else:
                    print(f"❌ Failed to add {holding['ticker_symbol']}: {response.json()}")
            except Exception as e:
                print(f"❌ Error adding {holding['ticker_symbol']}: {e}")
        
        return success_count == len(holdings)
    
    def test_portfolio_valuation(self):
        """Test portfolio valuation with market data"""
        print("💰 Testing portfolio valuation...")
        try:
            response = self.session.get(f"{BASE_URL}/portfolio/{self.portfolio_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Portfolio '{data['name']}' valued at ${data['total_value']:,.2f}")
                
                for holding in data['holdings']:
                    if holding['current_price']:
                        print(f"   📊 {holding['ticker_symbol']}: {holding['quantity']} @ ${holding['current_price']:.2f} = ${holding['current_value']:,.2f} ({holding['change_percent']:+.2f}%)")
                    else:
                        print(f"   ⚠️ {holding['ticker_symbol']}: Market data unavailable")
                
                return data['total_value'] > 0
            else:
                print(f"❌ Portfolio valuation failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Portfolio valuation error: {e}")
            return False
    
    def test_market_data(self):
        """Test market data endpoints"""
        print("📊 Testing market data...")
        try:
            # Test single stock
            response = self.session.get(f"{BASE_URL}/market/stock/AAPL")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ AAPL: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
            
            # Test multiple stocks
            response = self.session.post(
                f"{BASE_URL}/market/stocks",
                json=["AAPL", "GOOGL", "MSFT"]
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved data for {len(data)} stocks")
                return True
            else:
                print(f"❌ Market data failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Market data error: {e}")
            return False
    
    def test_user_profile(self):
        """Test user profile endpoint"""
        print("👤 Testing user profile...")
        try:
            response = self.session.get(f"{BASE_URL}/profile")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Profile: {data['email']} - Risk: {data['risk_profile']}")
                return True
            else:
                print(f"❌ Profile failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Profile error: {e}")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 AuraVest MVP Phase 1 - Comprehensive Test Suite")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("Risk Questionnaire", self.test_risk_questionnaire),
            ("Portfolio Creation", self.test_portfolio_creation),
            ("Add Holdings", self.test_add_holdings),
            ("Portfolio Valuation", self.test_portfolio_valuation),
            ("Market Data", self.test_market_data),
            ("User Profile", self.test_user_profile)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
                    # Try login if registration failed
                    if test_name == "User Registration":
                        print("🔄 Trying login instead...")
                        if self.test_user_login():
                            passed += 1
                            failed -= 1
            except Exception as e:
                print(f"❌ Test crashed: {e}")
                failed += 1
            
            time.sleep(0.5)  # Brief pause between tests
        
        print("\n" + "=" * 60)
        print("🎯 TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed}/{len(tests)}")
        print(f"❌ Failed: {failed}/{len(tests)}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! PRD Phase 1 is fully functional!")
            print("✅ Ready for production deployment or Phase 2 development")
        else:
            print(f"\n⚠️ {failed} tests failed. System needs fixes before proceeding.")
        
        return failed == 0

def main():
    """Main test execution"""
    print("⏳ Starting test server check...")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first:")
            print("   docker-compose up  # or")
            print("   python main.py")
            return False
    except:
        print("❌ Server not running. Please start the server first:")
        print("   docker-compose up  # or")
        print("   python main.py")
        return False
    
    # Run tests
    tester = AuraVestTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 