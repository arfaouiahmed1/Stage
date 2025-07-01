#!/bin/bash

# Question Generation RAG Setup Script
echo "🚀 Setting up Question Generation RAG System..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the 'Models/Question Generation' directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your GOOGLE_API_KEY"
    echo "   You can get a free API key from: https://makersuite.google.com/app/apikey"
else
    echo "✅ .env file already exists"
fi

# Check if API key is set
if [ -f ".env" ]; then
    source .env
    if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
        echo "⚠️  GOOGLE_API_KEY not set in .env file"
        echo "   Please edit .env and add your actual API key"
    else
        echo "✅ GOOGLE_API_KEY is configured"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your GOOGLE_API_KEY in the .env file"
echo "2. Run the system:"
echo "   • Basic demo: python question_generation_rag.py"
echo "   • API server: python api.py"
echo "   • Client demo: python client_demo.py"
echo ""
echo "📚 See README.md for detailed usage instructions"
