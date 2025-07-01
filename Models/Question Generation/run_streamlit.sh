#!/bin/bash

# Question Generation Streamlit App Launcher
echo "🚀 Starting Question Generation System..."

# Check if we're in the right directory
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Error: Please run this script from the 'Models/Question Generation' directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "   Please edit .env and add your GOOGLE_API_KEY"
    echo "   You can get a free API key from: https://makersuite.google.com/app/apikey"
    read -p "   Press Enter after setting up your API key..."
fi

# Check if API key is set
source .env
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    echo "⚠️  GOOGLE_API_KEY not properly set in .env file"
    echo "   The app will start but won't work without a valid API key"
    read -p "   Press Enter to continue anyway or Ctrl+C to exit..."
fi

echo ""
echo "🎉 Starting Streamlit app..."
echo "📱 The app will open in your browser automatically"
echo "🌐 If it doesn't open, go to: http://localhost:8501"
echo ""
echo "💡 Tip: Press Ctrl+C to stop the app"
echo ""

# Start Streamlit
streamlit run streamlit_app.py
