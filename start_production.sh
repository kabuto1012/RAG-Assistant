#!/bin/bash

# Production startup script for RDR2 Agent API
# This script handles production deployment with proper error handling

set -e

echo "🚀 Starting RDR2 Agent API Production Server..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p chroma_db

# Check if required API keys are set
if ! grep -q "GEMINI_API_KEY=.*[^=]" .env; then
    echo "❌ Error: GEMINI_API_KEY not set in .env file"
    exit 1
fi

if ! grep -q "SERPER_API_KEY=.*[^=]" .env; then
    echo "❌ Error: SERPER_API_KEY not set in .env file"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Set production environment
export PYTHONPATH=$PWD
export PYTHONUNBUFFERED=1

echo "✅ Environment configured"
echo "📊 Starting with configuration:"
echo "   - Host: ${API_HOST:-0.0.0.0}"
echo "   - Port: ${API_PORT:-8000}"
echo "   - Workers: ${API_WORKERS:-4}"
echo "   - Log Level: ${LOG_LEVEL:-INFO}"

# Start the production server with Gunicorn
echo "🔥 Starting Gunicorn server..."

exec gunicorn api.main:app \
    --bind ${API_HOST:-0.0.0.0}:${API_PORT:-8000} \
    --workers ${API_WORKERS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 120 \
    --keep-alive 2 \
    --log-level ${LOG_LEVEL:-info} \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --pid /tmp/gunicorn.pid \
    --preload
