#!/bin/bash

echo "🎬 YouTube Video Classifier Dev Container"
echo "========================================"

# Install Python dependencies if not already installed
if [ -f "/workspace/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    cd /workspace
    pip install --user -r requirements.txt
fi

# Start display server
echo "🖥️  Starting display server..."
Xvfb :1 -screen 0 1920x1080x24 > /dev/null 2>&1 &
sleep 2
export DISPLAY=:1

# Start window manager
fluxbox > /dev/null 2>&1 &

# Start VNC
x11vnc -display :1 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -quiet > /dev/null 2>&1 &

# Start noVNC
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080 > /dev/null 2>&1 &

echo "🖥️  GUI available at: http://localhost:6080/vnc.html"

# Wait for Ollama container to be ready
echo "⏳ Waiting for Ollama container to start..."
for i in {1..30}; do
    if curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama container is ready!"
        break
    fi
    echo "   Attempt $i/30 - waiting for Ollama..."
    sleep 2
done

# Pull the required model
echo "📥 Pulling qwen2.5vl:7b model (this may take a while)..."
curl -X POST http://ollama:11434/api/pull -d '{"name":"qwen2.5vl:7b"}' > /dev/null 2>&1 &

echo "✅ Setup complete!"
echo ""
echo "🎬 YouTube Video Classifier is ready!"
echo "📖 Available commands:"
echo "   python test_ollama.py           # Test Ollama setup"
echo "   python demo_classification.py   # Run classification demo"
echo "   python script.py               # Run main classifier"
echo ""
echo "🖥️  Access GUI at: http://localhost:6080/vnc.html"
echo "🤖 Ollama API at: http://localhost:11434 (via ollama container)"
echo ""
echo "💡 Note: Model download happens in background"
echo "   Check status with: curl http://ollama:11434/api/tags"

# Keep container running
exec sleep infinity
