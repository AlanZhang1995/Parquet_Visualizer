#!/bin/bash

# Parquet Visualizer - Startup Script for macOS

echo "🚀 Starting Parquet Visualizer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Start the application
echo "✅ Starting application..."
echo "📊 Opening Parquet Visualizer in your browser..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
