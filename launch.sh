#!/bin/bash

echo "🚀 Launching AuraVest MVP - Phase 1 (PRD Compliant)"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the AuraVest root directory"
    exit 1
fi

# Check for environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your database configuration"
fi

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "🐳 Using Docker Compose (Recommended)"
    echo "Starting PostgreSQL and web application..."
    docker-compose up --build
else
    echo "📦 Docker not found. Using manual setup..."
    
    # Install dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Start the application
    echo "🌐 Starting AuraVest API server..."
    echo "Make sure PostgreSQL is running and configured in .env"
    python main.py
fi

echo ""
echo "🎉 AuraVest MVP Phase 1 is running!"
echo "=================================="
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔗 Health Check: http://localhost:8000/health"
echo "🌐 Frontend: http://localhost:3000 (when React app is started)"
echo ""
echo "✅ PRD Phase 1 Features Available:"
echo "   • User Authentication (JWT)"
echo "   • Risk Profiling Questionnaire"
echo "   • Manual Portfolio Input"
echo "   • Real-time Market Data (yfinance)"
echo "   • PostgreSQL Database" 