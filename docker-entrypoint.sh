#!/bin/bash

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

# Start Ollama
echo "🤖 Starting Ollama..."
ollama serve > /dev/null 2>&1 &

# Wait and pull model
echo "⏳ Waiting for Ollama..."
sleep 15
echo "📥 Pulling qwen2.5vl:7b model..."
ollama pull qwen2.5vl:7b

echo "✅ Setup complete!"
echo ""
echo "🎬 YouTube Video Classifier Ready!"
echo "🖥️  GUI: http://localhost:6080/vnc.html"
echo "🤖 API: http://localhost:11434"
echo ""
echo "📖 Commands:"
echo "   python test_ollama.py"
echo "   python demo_classification.py"
echo "   python script.py"

# Keep running
exec "$@"
