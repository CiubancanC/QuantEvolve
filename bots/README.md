# Paper Trading Bot - 3-Month Validation

This bot will automatically trade your evolved strategy in an Alpaca paper trading account for 3 months to validate real-world performance.

## Quick Start

### 1. Install Dependencies

```bash
pip install alpaca-trade-api pandas yfinance loguru
```

### 2. Get Alpaca Paper Trading Account (FREE)

1. Go to https://alpaca.markets
2. Sign up (free account)
3. Go to "Paper Trading" section
4. Generate API keys
5. Save them securely

### 3. Set Up Environment Variables

```bash
# Add to your ~/.zshrc or ~/.bashrc
export ALPACA_API_KEY='your_paper_api_key_here'
export ALPACA_SECRET_KEY='your_paper_secret_key_here'

# Reload shell
source ~/.zshrc
```

### 4. Test the Bot

```bash
# Run a single test cycle
python3 bots/alpaca_paper_bot.py --run-once
```

You should see:
```
✓ Connected to Alpaca (PAPER)
  Account: PA...
  Portfolio Value: $100,000.00
  Cash: $100,000.00
```

### 5. Start Paper Trading

```bash
# Run continuously (daemon mode)
python3 bots/alpaca_paper_bot.py --daemon
```

The bot will:
- Check signals daily at 4:30 PM ET (after market close)
- Execute trades automatically
- Hold positions for 3 days
- Use 5% stop losses
- Log everything

### 6. Monitor Performance

```bash
# View performance dashboard (run anytime)
python3 bots/performance_dashboard.py
```

## How It Works

### Daily Trading Cycle (Runs at 4:30 PM ET)

1. **Check Stop Losses**
   - Monitors all open positions
   - Sells if any position down >5%

2. **Check 3-Day Exits**
   - Exits positions held for 3 days
   - Per strategy specification

3. **Generate Signals**
   - Analyzes all 7 stocks (AAPL, MSFT, AMZN, GOOGL, TSLA, META, NVDA)
   - Uses your evolved strategy

4. **Execute Trades**
   - BUY: Opens new positions when signals appear
   - SELL: Closes positions on exit signals
   - HOLD: Does nothing

5. **Log Performance**
   - Records all trades
   - Tracks portfolio value
   - Calculates metrics

### Position Sizing

- **Max 10% per position** - Limits individual stock risk
- **Max 80% total exposure** - Keeps 20% cash reserve
- **Equal weighting** - Splits capital across buy signals

Example with $100,000:
- 1 buy signal: $10,000 position (10%)
- 3 buy signals: $10,000 each = $30,000 total (30%)
- 7 buy signals: $10,000 each = $70,000 total (70%)
- Cash reserve: Always 20%+ for emergencies

### Risk Management

1. **Stop Losses**: -5% per position
2. **3-Day Hold**: Forced exit after 3 trading days
3. **Position Limits**: Max 10% per stock
4. **Cash Reserve**: Min 20% always available
5. **Daily Monitoring**: Automated checks

## Files Created

```
logs/paper_trading/
├── bot_20251101.log          # Daily bot logs
├── trades.jsonl               # All trades (append-only)
├── performance.jsonl          # Daily snapshots
├── positions_tracker.json     # Current open positions
├── trades_export.csv          # CSV export
└── performance_export.csv     # CSV export
```

## Commands

### Basic Operations

```bash
# Run one cycle (testing)
python3 bots/alpaca_paper_bot.py --run-once

# Run continuously
python3 bots/alpaca_paper_bot.py --daemon

# Check performance
python3 bots/performance_dashboard.py

# Export to CSV for analysis
python3 bots/performance_dashboard.py --export
```

### Advanced Options

```bash
# Custom initial capital
python3 bots/alpaca_paper_bot.py --run-once --initial-capital 50000

# Custom symbols
python3 bots/alpaca_paper_bot.py --run-once --symbols AAPL MSFT GOOGL

# Different log directory
python3 bots/performance_dashboard.py --log-dir custom_logs/
```

## Monitoring

### Daily (2 minutes)

```bash
# Check today's trades and performance
python3 bots/performance_dashboard.py
```

Look for:
- ✅ Portfolio value increasing
- ✅ Win rate >40%
- ✅ Sharpe ratio >1.0
- ⚠️ Any losses >10%

### Weekly (10 minutes)

```bash
# Export and analyze in spreadsheet
python3 bots/performance_dashboard.py --export

# Open in Excel/Google Sheets
open logs/paper_trading/trades_export.csv
```

Track:
- Weekly P&L
- Win rate trend
- Max drawdown
- Compare to backtest

### Monthly (30 minutes)

1. Review full performance report
2. Compare to backtest expectations
3. Check if Sharpe ratio >1.5
4. Verify win rate >40%
5. Decide: continue, adjust, or stop

## Expected Results

### After 1 Month

**Success indicators:**
- Portfolio: $100k → $105k-$115k (+5-15%)
- Win rate: 40-55%
- Sharpe ratio: >1.0
- Max drawdown: <10%
- No major bugs or execution errors

**Warning signs:**
- Portfolio down >5%
- Win rate <35%
- Sharpe ratio <0.5
- Max drawdown >20%
- Frequent execution errors

### After 3 Months

**Best case** (like backtest):
- Portfolio: $100k → $150k-$180k (+50-80%)
- Proves strategy still works
- Ready for live trading with $1k-$5k

**Realistic case:**
- Portfolio: $100k → $110k-$130k (+10-30%)
- Decent performance
- Consider live trading with $1k-$2k

**Warning case:**
- Portfolio: $100k → $95k-$105k (-5% to +5%)
- Marginal performance
- Need more data or strategy adjustment

**Failure case:**
- Portfolio: <$95k (loss >5%)
- Strategy not working on new data
- Re-train with 2023-2025 data

## Troubleshooting

### "API connection failed"

```bash
# Check environment variables
echo $ALPACA_API_KEY
echo $ALPACA_SECRET_KEY

# Make sure they're set
export ALPACA_API_KEY='PK...'
export ALPACA_SECRET_KEY='...'
```

### "No module named 'alpaca_trade_api'"

```bash
pip install alpaca-trade-api
```

### "Strategy not found"

```bash
# Make sure you're in the QuantEvolve directory
cd /Users/employee/QuantEvolve

# Run with full path
python3 bots/alpaca_paper_bot.py --run-once
```

### "Bot not trading"

Check:
1. Is it 4:30 PM ET or later?
2. Is the market open today (Mon-Fri)?
3. Are there any buy signals? (Strategy is selective)
4. Check logs: `tail -f logs/paper_trading/bot_*.log`

### "Trades not executing"

Common causes:
- Insufficient cash (check portfolio value)
- Position already open (check positions tracker)
- API rate limits (wait 1 minute, try again)
- Market closed (trades execute next day)

## Automation Options

### Option 1: Keep Terminal Open

```bash
# Just run in background
nohup python3 bots/alpaca_paper_bot.py --daemon > bot_output.log 2>&1 &
```

### Option 2: Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (runs at 4:30 PM weekdays)
30 16 * * 1-5 cd /Users/employee/QuantEvolve && python3 bots/alpaca_paper_bot.py --run-once >> logs/cron.log 2>&1
```

### Option 3: LaunchAgent (Mac)

Create `~/Library/LaunchAgents/com.quantevolve.paperbot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.quantevolve.paperbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/employee/QuantEvolve/bots/alpaca_paper_bot.py</string>
        <string>--run-once</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>16</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>/Users/employee/QuantEvolve</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>ALPACA_API_KEY</key>
        <string>YOUR_KEY_HERE</string>
        <key>ALPACA_SECRET_KEY</key>
        <string>YOUR_SECRET_HERE</string>
    </dict>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.quantevolve.paperbot.plist
```

### Option 4: Cloud (AWS/GCP)

Deploy to cloud for 24/7 uptime:
- Use AWS Lambda (serverless, runs on schedule)
- Use Google Cloud Functions
- Use Heroku (free tier)
- Use a $5/month VPS (DigitalOcean, Linode)

## Safety Features

### Built-in Protections

1. **Paper Trading Only**
   - Hard-coded to paper API endpoint
   - Impossible to trade real money by accident

2. **Stop Losses**
   - Automatic -5% stops
   - Checked before every trade cycle

3. **Position Limits**
   - Max 10% per position
   - Max 80% total exposure
   - Prevents concentration risk

4. **Complete Logging**
   - Every trade logged
   - Every decision logged
   - Can audit everything

5. **Position Tracking**
   - Saves to disk
   - Survives bot restarts
   - Never loses track of open positions

### Manual Override

To stop the bot:
```bash
# If running in foreground
Ctrl+C

# If running in background
pkill -f alpaca_paper_bot

# Check it stopped
ps aux | grep alpaca_paper_bot
```

To close all positions manually:
```python
python3
>>> import alpaca_trade_api as tradeapi
>>> api = tradeapi.REST('key', 'secret', 'https://paper-api.alpaca.markets', api_version='v2')
>>> api.close_all_positions()
```

## What to Track

### Weekly Spreadsheet

| Date | Portfolio Value | Weekly P&L | Win Rate | Open Positions | Notes |
|------|----------------|------------|----------|----------------|-------|
| 11/1 | $100,000 | - | - | 0 | Started |
| 11/8 | $102,500 | +$2,500 | 60% | 2 | Good week |
| 11/15 | $101,000 | -$1,500 | 45% | 1 | Pullback |
| ... | ... | ... | ... | ... | ... |

### Decision Points

**After 1 month:**
- [ ] Profitable? → Continue
- [ ] Breakeven? → Continue with caution
- [ ] Losing >5%? → Review and possibly stop

**After 2 months:**
- [ ] Win rate >40%? → Looking good
- [ ] Sharpe >1.0? → Solid performance
- [ ] Max DD <15%? → Risk under control

**After 3 months:**
- [ ] Profitable overall? → Ready for live trading
- [ ] Consistent performance? → Start with $1k-$5k
- [ ] Issues detected? → Re-train or adjust

## Next Steps After 3 Months

### If Successful (Profitable)

1. Start live trading with $1,000-$5,000
2. Run both paper and live in parallel
3. Compare results
4. Scale up slowly

### If Marginal (Breakeven ±5%)

1. Continue paper trading 3 more months
2. Re-train model with 2023-2025 data
3. Test new strategy in parallel
4. Don't risk real money yet

### If Failed (Loss >5%)

1. Stop paper trading
2. Analyze what went wrong
3. Re-train with recent data
4. Paper trade new strategy 3 months
5. Don't give up - markets change, adapt!

## Support

For issues or questions:
1. Check logs: `logs/paper_trading/bot_*.log`
2. Review this README
3. Check Alpaca docs: https://alpaca.markets/docs/
4. Review bot source code (well-commented)

---

**Remember**: This is PAPER TRADING - no real money at risk. Use this time to:
- Learn how the bot works
- Understand the strategy
- Build confidence
- Prove profitability
- Find and fix bugs

Take it seriously, track everything, and only move to live trading when you're consistently profitable for 3+ months.

**Good luck!** 🚀📈
