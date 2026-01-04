#!/bin/bash

# YouTube Video Classifier Setup Script

echo "🎬 YouTube Video Classifier Setup"
echo "=================================="

# Check if Python 3.11 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11 not found. Please install Python 3.11.10"
    exit 1
fi

echo "✅ Python 3.11 found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install Ollama from https://ollama.ai"
    echo "   After installation, run:"
    echo "   1. ollama serve"
    echo "   2. ollama pull qwen3-vl:4b"
    exit 1
fi

echo "✅ Ollama found"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Ollama is not running. Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Pull Qwen3VL model
echo "🤖 Pulling Qwen3VL model..."
ollama pull qwen3-vl:4b

# Test setup
echo "🧪 Testing setup..."
python test_ollama.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your browser is pinned to the taskbar"
echo "2. Update the browser image in img/ folder if needed"
echo "3. Run: python script.py"
echo ""
echo "Optional:"
echo "- Run demo: python demo_classification.py"
echo "- Analyze results: python playlist_manager.py --analyze"
