#!/bin/bash
# Frexy AI Bot - Quick Setup Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              🤖 FREXY AI BOT - Setup Script                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit frexy_ai_bot.py and set your BOT_TOKEN"
echo "   2. Run: python frexy_ai_bot.py"
echo ""
echo "🔥 POWERED BY FREXY 🔥"
