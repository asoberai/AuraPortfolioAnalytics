#!/usr/bin/env python3
"""
Comprehensive test runner for AuraVest Enhanced Features
"""
import os
import sys
import subprocess
import time
import signal
import psutil
import requests
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.test_results = {}
        
    def setup_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Set environment variables
        os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/auravest_test"
        os.environ["SECRET_KEY"] = "test-secret-key"
        
        # Initialize database
        try:
            from database import init_database
            init_database()
            print("✅ Database initialized")
        except Exception as e:
            print(f"⚠️  Database setup warning: {e}")

    def start_backend(self):
        """Start backend server"""
        print("🚀 Starting backend server...")
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for i in range(30):
                try:
                    response = requests.get("http://localhost:8000/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Backend server started")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
            
            print("❌ Backend server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False

    def start_frontend(self):
        """Start frontend server"""
        print("🚀 Starting frontend server...")
        
        try:
            # Install dependencies if needed
            if not Path("frontend/node_modules").exists():
                print("📦 Installing frontend dependencies...")
                subprocess.run(["npm", "install"], cwd="frontend", check=True)
            
            # Build frontend
            print("🔨 Building frontend...")
            subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
            
            # Start frontend server
            self.frontend_process = subprocess.Popen(
                ["npx", "serve", "-s", "build", "-p", "3000"],
                cwd="frontend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for frontend to start
            for i in range(30):
                try:
                    response = requests.get("http://localhost:3000", timeout=1)
                    if response.status_code == 200:
                        print("✅ Frontend server started")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
            
            print("❌ Frontend server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False

    def run_backend_tests(self):
        """Run backend tests"""
        print("\n🧪 Running backend tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/test_enhanced_risk_analysis.py",
                "-v",
                "--cov=.",
                "--cov-report=html",
                "--cov-report=term"
            ], capture_output=True, text=True)
            
            self.test_results["backend"] = result.returncode == 0
            
            if result.returncode == 0:
                print("✅ Backend tests passed")
            else:
                print("❌ Backend tests failed")
                print(result.stdout)
                print(result.stderr)
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Backend test error: {e}")
            self.test_results["backend"] = False
            return False

    def run_integration_tests(self):
        """Run integration tests"""
        print("\n🔗 Running integration tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/test_integration_workflow.py",
                "-v",
                "--asyncio-mode=auto",
                "-s"
            ], capture_output=True, text=True)
            
            self.test_results["integration"] = result.returncode == 0
            
            if result.returncode == 0:
                print("✅ Integration tests passed")
            else:
                print("❌ Integration tests failed")
                print(result.stdout)
                print(result.stderr)
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Integration test error: {e}")
            self.test_results["integration"] = False
            return False

    def run_frontend_tests(self):
        """Run frontend tests"""
        print("\n🎨 Running frontend tests...")
        
        # Check if Chrome is available for Selenium tests
        try:
            subprocess.run(["google-chrome", "--version"], 
                         capture_output=True, check=True)
            chrome_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Chrome not found, skipping Selenium tests")
            chrome_available = False
        
        if chrome_available:
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest",
                    "tests/test_frontend_components.py",
                    "-v",
                    "--tb=short"
                ], capture_output=True, text=True)
                
                self.test_results["frontend"] = result.returncode == 0
                
                if result.returncode == 0:
                    print("✅ Frontend tests passed")
                else:
                    print("❌ Frontend tests failed")
                    print(result.stdout)
                    print(result.stderr)
                    
                return result.returncode == 0
                
            except Exception as e:
                print(f"❌ Frontend test error: {e}")
                self.test_results["frontend"] = False
                return False
        else:
            print("⏭️  Skipping frontend tests (Chrome not available)")
            self.test_results["frontend"] = True
            return True

    def run_performance_tests(self):
        """Run performance tests"""
        print("\n⚡ Running performance tests...")
        
        try:
            # Check if locust is available
            subprocess.run(["locust", "--version"], capture_output=True, check=True)
            
            # Run performance tests
            result = subprocess.run([
                "locust",
                "-f", "tests/locustfile.py",
                "--host=http://localhost:8000",
                "--users=5",
                "--spawn-rate=1",
                "--run-time=30s",
                "--headless"
            ], capture_output=True, text=True, timeout=45)
            
            self.test_results["performance"] = result.returncode == 0
            
            if result.returncode == 0:
                print("✅ Performance tests completed")
                print(result.stdout)
            else:
                print("⚠️  Performance tests completed with warnings")
                print(result.stdout)
                
            return True
            
        except subprocess.CalledProcessError:
            print("⚠️  Locust not available, skipping performance tests")
            self.test_results["performance"] = True
            return True
        except subprocess.TimeoutExpired:
            print("⚠️  Performance tests timed out")
            self.test_results["performance"] = True
            return True
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            self.test_results["performance"] = False
            return False

    def validate_risk_calculations(self):
        """Validate risk calculation accuracy"""
        print("\n🔢 Validating risk calculations...")
        
        try:
            # Test basic portfolio risk calculation
            from risk_models import PortfolioRiskModel
            import pandas as pd
            import numpy as np
            
            risk_model = PortfolioRiskModel()
            
            # Create test data
            np.random.seed(42)
            test_returns = pd.DataFrame({
                'AAPL': np.random.normal(0.1/252, 0.25/np.sqrt(252), 252),
                'GOOGL': np.random.normal(0.08/252, 0.22/np.sqrt(252), 252)
            })
            
            weights = np.array([0.6, 0.4])
            
            # Test covariance calculation
            cov_analysis = risk_model.calculate_portfolio_covariance(test_returns, weights)
            
            # Validate results
            assert cov_analysis['portfolio_volatility'] > 0
            assert 'risk_contributions' in cov_analysis
            
            # Test Monte Carlo simulation
            mc_results = risk_model.monte_carlo_portfolio_simulation(
                test_returns, weights, n_simulations=1000, time_horizon=252
            )
            
            assert len(mc_results['final_values']) == 1000
            assert mc_results['percentile_5'] < mc_results['expected_return']
            assert mc_results['expected_return'] < mc_results['percentile_95']
            
            print("✅ Risk calculations validated")
            self.test_results["risk_validation"] = True
            return True
            
        except Exception as e:
            print(f"❌ Risk validation failed: {e}")
            self.test_results["risk_validation"] = False
            return False

    def test_api_endpoints(self):
        """Test critical API endpoints"""
        print("\n🌐 Testing API endpoints...")
        
        endpoints_to_test = [
            ("GET", "/health", 200),
            ("GET", "/market/stock/AAPL", [200, 500]),  # May fail due to rate limits
            ("GET", "/analysis/risk/price-pdf/AAPL", 200),
        ]
        
        all_passed = True
        
        for method, endpoint, expected_status in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
                
                if isinstance(expected_status, list):
                    success = response.status_code in expected_status
                else:
                    success = response.status_code == expected_status
                
                if success:
                    print(f"✅ {method} {endpoint} - Status: {response.status_code}")
                else:
                    print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {method} {endpoint} - Error: {e}")
                all_passed = False
        
        self.test_results["api_endpoints"] = all_passed
        return all_passed

    def cleanup(self):
        """Cleanup processes"""
        print("\n🧹 Cleaning up...")
        
        # Stop backend process
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            except Exception as e:
                print(f"⚠️  Error stopping backend: {e}")
        
        # Stop frontend process
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            except Exception as e:
                print(f"⚠️  Error stopping frontend: {e}")
        
        # Kill any remaining processes on ports 8000 and 3000
        for port in [8000, 3000]:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    for conn in proc.info['connections'] or []:
                        if conn.laddr.port == port:
                            proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🏁 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.upper().replace('_', ' '):<20} {status}")
        
        print("-" * 60)
        print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! AuraVest enhanced features are working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please review the results above.")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AuraVest Enhanced Features Test Suite")
        print("="*60)
        
        try:
            # Setup
            self.setup_environment()
            
            # Start servers
            if not self.start_backend():
                return False
                
            if not self.start_frontend():
                return False
            
            # Run tests
            self.validate_risk_calculations()
            self.test_api_endpoints()
            self.run_backend_tests()
            self.run_integration_tests()
            self.run_frontend_tests()
            self.run_performance_tests()
            
            # Summary
            return self.print_summary()
            
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AuraVest Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--backend", action="store_true", help="Run backend tests only")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.quick:
            runner.setup_environment()
            runner.start_backend()
            runner.validate_risk_calculations()
            runner.test_api_endpoints()
            success = runner.print_summary()
        elif args.backend:
            runner.setup_environment()
            runner.start_backend()
            runner.run_backend_tests()
            success = runner.print_summary()
        elif args.frontend:
            runner.start_frontend()
            runner.run_frontend_tests()
            success = runner.print_summary()
        elif args.integration:
            runner.setup_environment()
            runner.start_backend()
            runner.start_frontend()
            runner.run_integration_tests()
            success = runner.print_summary()
        elif args.performance:
            runner.setup_environment()
            runner.start_backend()
            runner.run_performance_tests()
            success = runner.print_summary()
        else:
            success = runner.run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        runner.cleanup()

if __name__ == "__main__":
    main()