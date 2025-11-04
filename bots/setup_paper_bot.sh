#!/bin/bash
#
# Setup script for Alpaca Paper Trading Bot
# This will install dependencies and configure the bot
#

set -e  # Exit on error

echo "========================================================================"
echo "QuantEvolve Paper Trading Bot - Setup"
echo "========================================================================"
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -q alpaca-trade-api pandas yfinance loguru

echo "✓ Dependencies installed"
echo ""

# Check for API keys
echo "Checking for Alpaca API keys..."

if [ -z "$ALPACA_API_KEY" ] || [ -z "$ALPACA_SECRET_KEY" ]; then
    echo "⚠️  Alpaca API keys not found in environment"
    echo ""
    echo "To get API keys:"
    echo "  1. Go to https://alpaca.markets"
    echo "  2. Sign up for free account"
    echo "  3. Go to Paper Trading section"
    echo "  4. Generate API keys"
    echo ""
    echo "Then add to your ~/.zshrc or ~/.bashrc:"
    echo ""
    echo "  export ALPACA_API_KEY='your_paper_api_key'"
    echo "  export ALPACA_SECRET_KEY='your_paper_secret_key'"
    echo ""
    echo "And reload: source ~/.zshrc"
    echo ""
    read -p "Do you want to enter keys now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter ALPACA_API_KEY: " API_KEY
        read -p "Enter ALPACA_SECRET_KEY: " SECRET_KEY

        echo "export ALPACA_API_KEY='$API_KEY'" >> ~/.zshrc
        echo "export ALPACA_SECRET_KEY='$SECRET_KEY'" >> ~/.zshrc

        export ALPACA_API_KEY="$API_KEY"
        export ALPACA_SECRET_KEY="$SECRET_KEY"

        echo "✓ Keys saved to ~/.zshrc"
        echo "  Run: source ~/.zshrc"
    fi
else
    echo "✓ API keys found in environment"
fi
echo ""

# Create log directory
echo "Creating log directories..."
mkdir -p logs/paper_trading
echo "✓ Created logs/paper_trading/"
echo ""

# Make scripts executable
echo "Setting permissions..."
chmod +x bots/alpaca_paper_bot.py
chmod +x bots/performance_dashboard.py
echo "✓ Scripts are executable"
echo ""

# Test connection (if keys are set)
if [ -n "$ALPACA_API_KEY" ] && [ -n "$ALPACA_SECRET_KEY" ]; then
    echo "Testing Alpaca connection..."
    python3 -c "
import alpaca_trade_api as tradeapi
import os

try:
    api = tradeapi.REST(
        os.environ['ALPACA_API_KEY'],
        os.environ['ALPACA_SECRET_KEY'],
        'https://paper-api.alpaca.markets',
        api_version='v2'
    )
    account = api.get_account()
    print(f'✓ Connected to Alpaca!')
    print(f'  Account: {account.account_number}')
    print(f'  Portfolio Value: \${float(account.portfolio_value):,.2f}')
    print(f'  Cash: \${float(account.cash):,.2f}')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    print('Check your API keys!')
"
fi
echo ""

# Show next steps
echo "========================================================================"
echo "Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test the bot:"
echo "   python3 bots/alpaca_paper_bot.py --run-once"
echo ""
echo "2. If successful, start paper trading:"
echo "   python3 bots/alpaca_paper_bot.py --daemon"
echo ""
echo "3. Monitor performance:"
echo "   python3 bots/performance_dashboard.py"
echo ""
echo "4. Set up automation (optional):"
echo "   See bots/README.md for cron/launchd setup"
echo ""
echo "For help, read: bots/README.md"
echo ""
echo "Good luck! 🚀"
echo ""
