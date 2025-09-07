#!/bin/bash
set -e

echo "🚀 QuickTARA Office Deployment Script"
echo "======================================"

# Get local IP for LAN access
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)

echo "📍 Detected LAN IP: $LOCAL_IP"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Clone or update repository
if [ -d "QuickTARA" ]; then
    echo "📁 Updating existing QuickTARA..."
    cd QuickTARA
    git pull
else
    echo "📥 Cloning QuickTARA..."
    git clone https://github.com/leonkalema/QuickTARA.git
    cd QuickTARA
fi

echo ""

# Create virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""

# Build frontend
echo "🎨 Building frontend..."
cd tara-web
npm install
npm run build
cd ..

echo ""

# Create default SQLite database (no config needed)
echo "🗄️  Setting up database..."
if [ ! -f "quicktara.db" ]; then
    python quicktara_web.py --db ./quicktara.db --host 127.0.0.1 --port 8080 &
    SERVER_PID=$!
    sleep 5
    kill $SERVER_PID 2>/dev/null || true
    echo "✅ Database initialized"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🌐 Starting QuickTARA on LAN..."
echo "   Local access:  http://localhost:8080"
echo "   LAN access:    http://$LOCAL_IP:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server with LAN access
python quicktara_web.py --host 0.0.0.0 --port 8080
