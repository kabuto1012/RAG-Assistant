#!/bin/bash
# Setup script for RDR2-RAG-Assistant

echo "🎮 RDR2-RAG-Assistant Setup"
echo "=========================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Set up environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys"
else
    echo "✅ .env file already exists"
fi

# Run setup test
echo "🧪 Running setup test..."
python3 test_setup.py

echo ""
echo "🚀 Setup complete! Next steps:"
echo "1. Edit .env file and add your Gemini API key"
echo "2. Run: cd RedDeadRemeption2 && python3 agent.py"
echo "   OR: cd RedDeadRemeption2/Search_Crew_Agent_System && python3 crew_agent.py"