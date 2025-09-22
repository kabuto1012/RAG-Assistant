@echo off
REM Production startup script for RDR2 Agent API (Windows)
REM This script handles production deployment with proper error handling

echo 🚀 Starting RDR2 Agent API Production Server...

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found!
    echo Please copy .env.example to .env and configure your API keys
    exit /b 1
)

REM Create necessary directories
if not exist logs mkdir logs
if not exist chroma_db mkdir chroma_db

REM Set production environment
set PYTHONPATH=%CD%
set PYTHONUNBUFFERED=1

echo ✅ Environment configured
echo 📊 Starting production server...

REM Start the production server with Uvicorn (simpler for Windows)
echo 🔥 Starting Uvicorn server...

uvicorn api.main:app ^
    --host 0.0.0.0 ^
    --port 8000 ^
    --workers 1 ^
    --log-level info ^
    --access-log ^
    --no-use-colors

pause
