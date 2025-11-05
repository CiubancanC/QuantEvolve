#!/bin/bash
#
# Daily Paper Trading Runner
#
# This script should be run daily after market close (e.g., 5 PM ET).
# It executes paper trades based on today's signals and logs all activity.
#
# To set up as a cron job (runs Mon-Fri at 5 PM ET):
# 0 17 * * 1-5 cd /Users/employee/QuantEvolve && ./scripts/run_daily_paper_trading.sh
#

# Change to project directory
cd "$(dirname "$0")/.." || exit 1

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Log start
echo "========================================"
echo "Paper Trading Run: $(date)"
echo "========================================"

# Run the paper trading script
python3 scripts/paper_trading_top3.py --mode paper

# Check exit status
if [ $? -eq 0 ]; then
    echo "✓ Paper trading completed successfully"

    # Generate daily report
    python3 scripts/generate_paper_trading_report.py

else
    echo "✗ Paper trading failed"
    exit 1
fi

echo "========================================"
echo "Run completed: $(date)"
echo "========================================"
