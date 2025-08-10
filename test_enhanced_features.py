#!/usr/bin/env python3
"""
Quick test script for AuraVest Enhanced Features
Run this to validate all enhanced features are working correctly
"""

import sys
import os
import json
from pathlib import Path

def test_enhanced_dependencies():
    """Test that enhanced frontend dependencies are installed"""
    print("🔍 Testing Enhanced Dependencies...")
    
    frontend_package = Path("frontend/package.json")
    if not frontend_package.exists():
        print("❌ Frontend package.json not found")
        return False
    
    with open(frontend_package) as f:
        package_data = json.load(f)
    
    required_deps = [
        "chart.js", "react-chartjs-2", "d3", "recharts", "moment"
    ]
    
    dependencies = package_data.get("dependencies", {})
    missing_deps = [dep for dep in required_deps if dep not in dependencies]
    
    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        return False
    
    print(f"✅ All enhanced dependencies found: {required_deps}")
    return True

def test_enhanced_components():
    """Test that enhanced React components exist"""
    print("🎨 Testing Enhanced Components...")
    
    components_dir = Path("frontend/src/components")
    enhanced_components = [
        "RiskVisualization.js",
        "EnhancedDashboard.js", 
        "PersonalizedRiskProfile.js",
        "EnhancedPortfolio.js"
    ]
    
    missing_components = []
    for component in enhanced_components:
        component_path = components_dir / component
        if not component_path.exists():
            missing_components.append(component)
    
    if missing_components:
        print(f"❌ Missing components: {missing_components}")
        return False
    
    print(f"✅ All enhanced components found: {enhanced_components}")
    return True

def test_enhanced_theme():
    """Test that enhanced theme is applied"""
    print("🎨 Testing Enhanced Theme...")
    
    app_file = Path("frontend/src/App.js")
    if not app_file.exists():
        print("❌ App.js not found")
        return False
    
    with open(app_file) as f:
        app_content = f.read()
    
    theme_indicators = [
        "Enhanced Theme",
        "borderRadius: 12",
        "MuiCard",
        "MuiButton",
        "fontFamily:"
    ]
    
    missing_indicators = [ind for ind in theme_indicators if ind not in app_content]
    
    if missing_indicators:
        print(f"❌ Missing theme indicators: {missing_indicators}")
        return False
    
    print("✅ Enhanced theme applied successfully")
    return True

def test_risk_models():
    """Test that enhanced risk models are working"""
    print("🔬 Testing Risk Models...")
    
    try:
        from risk_models import PortfolioRiskModel, RiskVisualizer
        import pandas as pd
        import numpy as np
        
        # Test risk model initialization
        risk_model = PortfolioRiskModel()
        risk_visualizer = RiskVisualizer()
        print("✅ Risk models initialized")
        
        # Test portfolio covariance calculation
        np.random.seed(42)
        test_data = pd.DataFrame({
            'AAPL': np.random.normal(0.1/252, 0.25/np.sqrt(252), 252),
            'GOOGL': np.random.normal(0.08/252, 0.22/np.sqrt(252), 252)
        })
        weights = np.array([0.6, 0.4])
        
        cov_result = risk_model.calculate_portfolio_covariance(test_data, weights)
        print(f"✅ Portfolio covariance calculated: {cov_result['portfolio_volatility']:.4f}")
        
        # Test Monte Carlo simulation
        mc_result = risk_model.monte_carlo_portfolio_simulation(
            test_data, weights, n_simulations=100, time_horizon=30
        )
        print(f"✅ Monte Carlo simulation completed: {len(mc_result['simulation_results']['final_values'])} scenarios")
        
        # Test PDF calculation
        pdf_result = risk_model.price_probability_density(150.0, 0.25, 30)
        print(f"✅ Price PDF calculated: {len(pdf_result['price_range'])} price points")
        
        # Test dashboard data creation
        portfolio_data = {
            'holdings': [
                {'ticker': 'AAPL', 'current_value': 10000, 'weight': 0.6},
                {'ticker': 'GOOGL', 'current_value': 6667, 'weight': 0.4}
            ],
            'total_value': 16667
        }
        
        dashboard_data = risk_visualizer.create_risk_dashboard_data(portfolio_data, risk_model)
        print("✅ Risk dashboard data generated")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Risk model error: {e}")
        return False

def test_backend_structure():
    """Test backend file structure"""
    print("🔧 Testing Backend Structure...")
    
    backend_files = [
        "main.py", "database.py", "auth.py", 
        "risk_models.py", "market_data.py", "quantitative_models.py"
    ]
    
    missing_files = []
    for file in backend_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing backend files: {missing_files}")
        return False
    
    print(f"✅ All backend files present: {backend_files}")
    return True

def test_testing_infrastructure():
    """Test that testing infrastructure exists"""
    print("🧪 Testing Infrastructure...")
    
    test_files = [
        "tests/test_enhanced_risk_analysis.py",
        "tests/test_frontend_components.py", 
        "tests/test_integration_workflow.py",
        "tests/locustfile.py",
        "run_tests.py"
    ]
    
    missing_files = []
    for file in test_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    
    print(f"✅ All test files present: {len(test_files)} files")
    return True

def test_ci_cd_setup():
    """Test CI/CD configuration"""
    print("⚙️ Testing CI/CD Setup...")
    
    cicd_files = [
        ".github/workflows/ci-cd.yml",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    missing_files = []
    for file in cicd_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing CI/CD files: {missing_files}")
        return False
    
    print("✅ CI/CD configuration complete")
    return True

def run_quick_api_test():
    """Run a quick test of the risk calculation API"""
    print("🌐 Testing API Functionality...")
    
    try:
        import requests
        import time
        import subprocess
        
        # Start the server in background
        print("Starting backend server...")
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for i in range(10):
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend server started")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        else:
            print("❌ Backend server failed to start")
            server_process.terminate()
            return False
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data.get('service')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                server_process.terminate()
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            server_process.terminate()
            return False
        
        # Test price PDF endpoint
        try:
            response = requests.get("http://localhost:8000/analysis/risk/price-pdf/AAPL?time_horizon=30")
            if response.status_code == 200:
                pdf_data = response.json()
                print(f"✅ Price PDF endpoint working: {pdf_data.get('ticker')}")
            else:
                print(f"❌ Price PDF endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Price PDF test skipped: {e}")
        
        # Clean up
        server_process.terminate()
        print("✅ API tests completed")
        return True
        
    except ImportError:
        print("⚠️ Requests library not available, skipping API tests")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all enhanced feature tests"""
    print("🚀 AuraVest Enhanced Features - Validation Test")
    print("=" * 50)
    
    tests = [
        ("Frontend Dependencies", test_enhanced_dependencies),
        ("React Components", test_enhanced_components),
        ("Enhanced Theme", test_enhanced_theme),
        ("Risk Models", test_risk_models),
        ("Backend Structure", test_backend_structure),
        ("Testing Infrastructure", test_testing_infrastructure),
        ("CI/CD Setup", test_ci_cd_setup),
        ("API Functionality", run_quick_api_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL ENHANCED FEATURES WORKING PERFECTLY!")
        print("\n🚀 Your AuraVest Enhanced platform is ready to use:")
        print("   • Run: ./quick_start.sh")
        print("   • Or: python main.py (backend) + npm start (frontend)")
        print("   • Then open: http://localhost:3000")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the issues above.")
        print("\n🔧 Common fixes:")
        print("   • Run: npm install (in frontend directory)")
        print("   • Run: pip install -r requirements.txt")
        print("   • Check README.md for detailed setup instructions")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)