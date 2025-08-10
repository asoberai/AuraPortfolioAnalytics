#!/bin/bash

# AuraVest Enhanced - Quick Start Script
echo "🚀 AuraVest Enhanced - Quick Start"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check port availability
check_port() {
    lsof -ti:$1 >/dev/null 2>&1
}

echo "🔍 Checking prerequisites..."

# Check Python
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Check Node.js
if command_exists node; then
    echo "✅ Node.js found: $(node --version)"
    NODE_AVAILABLE=true
else
    echo "⚠️  Node.js not found. Frontend will not be available."
    NODE_AVAILABLE=false
fi

# Check npm
if command_exists npm; then
    echo "✅ npm found: $(npm --version)"
else
    echo "⚠️  npm not found. Frontend will not be available."
    NODE_AVAILABLE=false
fi

# Check PostgreSQL
if command_exists psql; then
    echo "✅ PostgreSQL found: $(psql --version | head -n 1)"
    POSTGRES_AVAILABLE=true
else
    echo "⚠️  PostgreSQL not found. Will use SQLite fallback."
    POSTGRES_AVAILABLE=false
fi

echo ""
echo "🛠️  Starting setup..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Set up environment variables
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cat > .env << EOF
# AuraVest Enhanced Configuration
SECRET_KEY=auravest-enhanced-secret-key-$(date +%s)
DATABASE_URL=sqlite:///./auravest.db
ENVIRONMENT=development
EOF
    echo "✅ Environment file created"
else
    echo "✅ Environment file already exists"
fi

# Initialize database
echo "🗄️  Initializing database..."
$PYTHON_CMD -c "
try:
    from database import init_database
    init_database()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
"

# Test risk models
echo "🔬 Testing risk calculation models..."
$PYTHON_CMD -c "
try:
    from risk_models import PortfolioRiskModel
    import pandas as pd
    import numpy as np
    
    # Quick test
    np.random.seed(42)
    risk_model = PortfolioRiskModel()
    test_data = pd.DataFrame({
        'AAPL': np.random.normal(0.1/252, 0.25/np.sqrt(252), 100),
        'GOOGL': np.random.normal(0.08/252, 0.22/np.sqrt(252), 100)
    })
    weights = np.array([0.6, 0.4])
    
    # Test covariance calculation
    result = risk_model.calculate_portfolio_covariance(test_data, weights)
    print(f'✅ Risk models working (Portfolio Vol: {result[\"portfolio_volatility\"]:.4f})')
    
except Exception as e:
    print(f'❌ Risk models test failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Check if ports are available
echo "🔌 Checking ports..."
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Please stop the existing service or use a different port."
    echo "   You can find what's using port 8000 with: lsof -ti:8000"
else
    echo "✅ Port 8000 is available for backend"
fi

if [ "$NODE_AVAILABLE" = true ]; then
    if check_port 3000; then
        echo "⚠️  Port 3000 is already in use. Frontend may not start properly."
    else
        echo "✅ Port 3000 is available for frontend"
    fi
fi

echo ""
echo "🚀 Starting AuraVest Enhanced..."

# Start backend
echo "🔧 Starting backend server..."
$PYTHON_CMD main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend started successfully"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start after 30 seconds"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    sleep 1
done

# Test backend
echo "🧪 Testing backend endpoints..."
HEALTH_CHECK=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend if Node.js is available
if [ "$NODE_AVAILABLE" = true ]; then
    echo "🎨 Setting up frontend..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
        
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install frontend dependencies"
            kill $BACKEND_PID 2>/dev/null
            exit 1
        fi
    fi
    
    # Build frontend
    echo "🔨 Building frontend..."
    npm run build
    
    if [ $? -ne 0 ]; then
        echo "❌ Frontend build failed"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    # Start frontend server
    echo "🌐 Starting frontend server..."
    npx serve -s build -p 3000 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    echo "⏳ Waiting for frontend to start..."
    for i in {1..20}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✅ Frontend started successfully"
            break
        fi
        
        if [ $i -eq 20 ]; then
            echo "❌ Frontend failed to start after 20 seconds"
            kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
            exit 1
        fi
        
        sleep 1
    done
    
    cd ..
else
    echo "⚠️  Skipping frontend setup (Node.js not available)"
fi

echo ""
echo "🎉 AuraVest Enhanced is now running!"
echo "====================================="
echo ""
echo "🔗 Access your application:"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"

if [ "$NODE_AVAILABLE" = true ]; then
    echo "   • Frontend:     http://localhost:3000"
fi

echo ""
echo "📊 Quick API Tests:"
echo "   • Health:       curl http://localhost:8000/health"
echo "   • Market Data:  curl http://localhost:8000/market/stock/AAPL"
echo "   • Risk PDF:     curl http://localhost:8000/analysis/risk/price-pdf/AAPL"
echo ""

if [ "$NODE_AVAILABLE" = true ]; then
    echo "🖥️  Open http://localhost:3000 to start using AuraVest!"
else
    echo "🖥️  Use http://localhost:8000/docs to explore the API!"
fi

echo ""
echo "⚠️  To stop the servers:"
echo "   Press Ctrl+C or run: kill $BACKEND_PID"

if [ "$NODE_AVAILABLE" = true ] && [ -n "$FRONTEND_PID" ]; then
    echo "   Frontend PID: $FRONTEND_PID"
fi

echo ""
echo "📖 For detailed usage instructions, see README.md"
echo ""

# Keep script running until user interrupts
trap "echo ''; echo '🛑 Shutting down AuraVest Enhanced...'; kill $BACKEND_PID 2>/dev/null; if [ -n \"$FRONTEND_PID\" ]; then kill $FRONTEND_PID 2>/dev/null; fi; echo '✅ Shutdown complete'; exit 0" INT

# Wait for user interrupt
while true; do
    sleep 1
done