#!/bin/bash

# Moments API - Development Server

echo "🚀 Starting Moments API..."
echo ""

# Check if we're in the backend directory
if [ ! -d "app" ]; then
    echo "❌ Error: Must run from backend/ directory"
    exit 1
fi

# Set Python path to include parent directory (for core module imports)
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# Start FastAPI server
echo "📡 Starting FastAPI server on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""

python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
