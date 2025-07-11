#!/bin/bash

# Start VNC server for GUI access
echo "Starting VNC server..."
Xvfb :1 -screen 0 1920x1080x24 > /dev/null 2>&1 &
sleep 2

export DISPLAY=:1

# Start window manager
fluxbox > /dev/null 2>&1 &

# Start VNC server
x11vnc -display :1 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -quiet > /dev/null 2>&1 &

# Start noVNC
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080 > /dev/null 2>&1 &

echo "🖥️  GUI available at: http://localhost:6080/vnc.html"

# Start Ollama
echo "🤖 Starting Ollama..."
ollama serve > /dev/null 2>&1 &

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 15

# Pull the required model
echo "📥 Pulling qwen2.5vl:7b model (this may take a while)..."
ollama pull qwen2.5vl:7b

# Test setup
echo "🧪 Testing setup..."
cd /workspace
python test_ollama.py

echo "✅ Container setup complete!"
echo ""
echo "🎬 YouTube Video Classifier is ready!"
echo "📖 Available commands:"
echo "   python test_ollama.py           # Test Ollama setup"
echo "   python demo_classification.py   # Run classification demo"
echo "   python script.py               # Run main classifier"
echo "   python playlist_manager.py --help  # Manage classifications"
echo ""
echo "🖥️  Access GUI at: http://localhost:6080/vnc.html"
echo "🤖 Ollama API at: http://localhost:11434"

# Keep container running
sleep infinity
