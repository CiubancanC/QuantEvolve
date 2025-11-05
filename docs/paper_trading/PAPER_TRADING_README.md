# Paper Trading Guide - Top 3 Evolved Strategies

This guide explains how to run the top 3 evolved strategies in paper trading for 1 month to validate their real-world performance.

## Overview

The paper trading system will:
- Run your top 3 strategies (556%, 433%, and 398% backtest returns) in parallel
- Allocate $10,000 virtual capital to each strategy
- Generate daily trading signals after market close
- Execute paper trades via Alpaca Paper Trading API
- Track performance, positions, and trades
- Generate daily performance reports

## Setup

### 1. API Keys Already Configured ✓

Your Alpaca paper trading API keys are already set in `.env`:
- `ALPACA_API_KEY`: Your API key
- `ALPACA_SECRET_KEY`: Your secret key
- `ALPACA_ENDPOINT`: https://paper-api.alpaca.markets

**Account Status**: ACTIVE with $100,000 paper trading capital available

### 2. Install Dependencies

```bash
# Already installed:
pip3 install --user alpaca-trade-api
```

### 3. Data Requirements

The system uses cached market data from `data/raw/`. Current data available:
- AAPL, AMZN, GOOGL, MSFT, TSLA (through Oct 29, 2025)
- NVDA data missing (will skip this symbol)

To update data for ongoing trading, run:
```bash
python3 scripts/download_real_data.py --symbols AAPL NVDA AMZN GOOGL MSFT TSLA \\
    --start 2025-07-01 --end $(date +%Y-%m-%d)
```

## Usage

### Check Current Signals (No Trading)

See what signals each strategy is generating today without executing trades:

```bash
python3 scripts/paper_trading_top3.py --mode check
```

**Example Output**:
```
Strategy #1: strat_730524051 (556% backtest return)
  AAPL: HOLD (0)
  AMZN: BUY (1)
  GOOGL: HOLD (0)
  MSFT: BUY (1)
  TSLA: HOLD (0)

Strategy #2: strat_175698548 (433% backtest return)
  All HOLD (0)

Strategy #3: strat_514146649 (398% backtest return)
  All HOLD (0)
```

### Execute Paper Trading

Run actual paper trades based on today's signals:

```bash
python3 scripts/paper_trading_top3.py --mode paper
```

This will:
1. Fetch latest market data
2. Generate signals for all 3 strategies
3. Execute BUY/SELL orders via Alpaca
4. Update tracking data
5. Record daily snapshot

### View Status and Performance

Check current positions and performance at any time:

```bash
python3 scripts/paper_trading_top3.py --status
```

### Generate Performance Report

Create a detailed performance report:

```bash
# Console output
python3 scripts/generate_paper_trading_report.py

# Markdown output (save to file)
python3 scripts/generate_paper_trading_report.py --format markdown > report.md
```

## Automated Daily Trading

### Option 1: Manual Daily Runs

Run daily after market close (after 4 PM ET):

```bash
./scripts/run_daily_paper_trading.sh
```

This script will:
1. Execute paper trades
2. Generate performance report
3. Log all activity to `logs/paper_trading/`

### Option 2: Automated via Cron (Recommended for 1-Month Test)

Set up automatic daily execution:

```bash
# Edit your crontab
crontab -e

# Add this line to run Monday-Friday at 5 PM ET:
0 17 * * 1-5 cd /Users/employee/QuantEvolve && ./scripts/run_daily_paper_trading.sh
```

**Note**: Adjust timezone if needed. Use `TZ='America/New_York'` in cron for ET.

### Option 3: launchd (macOS Alternative)

For macOS users, launchd is more reliable than cron:

```bash
# Create ~/Library/LaunchAgents/com.quantevolve.papertrading.plist
# (See launchd documentation for details)
```

## File Structure

```
QuantEvolve/
├── scripts/
│   ├── paper_trading_top3.py          # Main trading script
│   ├── run_daily_paper_trading.sh      # Daily runner
│   └── generate_paper_trading_report.py # Report generator
│
├── results/paper_trading/
│   └── tracking.json                   # Performance tracking data
│
└── logs/paper_trading/
    └── paper_trading_YYYYMMDD.log      # Daily logs
```

## Your Top 3 Strategies

### Strategy #1: strat_730524051 (Volatility)
- **Backtest Return**: 556.59%
- **Sharpe Ratio**: 3.68
- **Max Drawdown**: -5.77%
- **Trades**: 172
- **Hypothesis**: Closes within 1.2% of 3-day high = momentum continuation

### Strategy #2: strat_175698548 (Volume/Liquidity)
- **Backtest Return**: 433.41%
- **Sharpe Ratio**: 3.46
- **Max Drawdown**: -5.73%
- **Trades**: 117
- **Hypothesis**: Closes within 1.5% of 5-day high for exactly one day

### Strategy #3: strat_514146649 (Breakout/Pattern)
- **Backtest Return**: 397.62%
- **Sharpe Ratio**: 1.25
- **Max Drawdown**: -36.37%
- **Trades**: 2
- **Hypothesis**: Closes within 1.0% of 10-day high for two consecutive days
- **Note**: Only 2 trades in backtest - high risk, include for diversity

## What to Watch For

### Success Indicators:
- ✅ Strategies generate reasonable trade frequency (not too many, not too few)
- ✅ Returns correlate somewhat with backtest performance
- ✅ Sharpe ratios remain positive
- ✅ Drawdowns stay manageable
- ✅ No technical failures (API errors, signal generation issues)

### Warning Signs:
- ⚠️ Strategy makes 0 trades for extended periods (may be over-fit)
- ⚠️ Returns significantly underperform backtests (regime change)
- ⚠️ High volatility in returns (market conditions differ from validation period)
- ⚠️ Drawdowns exceed backtest max drawdown significantly

## Monitoring Recommendations

### Daily (During 1-Month Test):
1. Check logs for errors: `tail -20 logs/paper_trading/paper_trading_$(date +%Y%m%d).log`
2. Review signals: Run `--mode check` to see what's happening
3. Check Alpaca dashboard for order confirmations

### Weekly:
1. Generate performance report
2. Compare to backtest metrics
3. Note any unusual patterns
4. Update data if needed

### End of Month:
1. Generate final comprehensive report
2. Analyze vs backtest performance
3. Calculate correlation between strategies
4. Decide: Continue trading, refine strategies, or re-evolve

## Troubleshooting

### Issue: No trades being executed
- **Check**: Are markets open? (Mon-Fri, 9:30 AM - 4 PM ET)
- **Check**: Is data up-to-date? Run data download script
- **Check**: Are signals generating? Run `--mode check`

### Issue: API connection errors
- **Check**: Alpaca API status at https://status.alpaca.markets/
- **Check**: API keys in `.env` are correct
- **Check**: Paper trading endpoint is correct (not live trading!)

### Issue: Missing market data
- **Solution**: Run download script for missing symbols
- **Alternative**: Remove missing symbols from `--symbols` argument

### Issue: Strategy generating unexpected signals
- **This is normal**: Real market data may differ from backtest data
- **Monitor**: If persistent, may indicate regime change or data quality issues
- **Document**: Note these occurrences for end-of-month analysis

## Data Tracking

All data is stored in `results/paper_trading/tracking.json`:

```json
{
  "start_date": "2025-11-05T...",
  "strategies": {
    "strat_730524051": {
      "initial_capital": 10000,
      "current_value": 10000,
      "positions": [...],
      "trades": [...],
      "daily_returns": [...]
    }
  },
  "daily_snapshots": [...]
}
```

**Backup this file regularly** - it contains your full trading history.

## Expected Timeline

### Day 1 (Today):
- ✅ Setup complete
- ✅ API connection verified
- ✅ Signal generation working
- 🎯 Next: First paper trading execution

### Week 1:
- Strategies will start taking positions
- Initial performance data accumulates
- Early indication of signal quality

### Week 2-3:
- More trades executed
- Performance patterns emerge
- Can start comparing to backtests

### End of Month:
- Full month of data
- Statistically meaningful sample size
- Can draw conclusions about live performance

## Next Steps

1. **Review today's signals**: Run `python3 scripts/paper_trading_top3.py --mode check`

2. **Execute first paper trades** (when ready):
   ```bash
   python3 scripts/paper_trading_top3.py --mode paper
   ```

3. **Set up daily automation**:
   ```bash
   # Test the daily runner
   ./scripts/run_daily_paper_trading.sh

   # If successful, add to crontab
   crontab -e
   ```

4. **Monitor for first week**, then let it run automatically

5. **After 1 month**: Generate final report and analyze results

## Support

- **Logs**: `logs/paper_trading/`
- **Tracking data**: `results/paper_trading/tracking.json`
- **Alpaca Dashboard**: https://app.alpaca.markets/paper/dashboard/overview

## Important Notes

⚠️ **This is paper trading** - No real money at risk
⚠️ **Markets are closed** Nov 5-6 (testing OK, but no trades will execute until market open)
⚠️ **Data freshness** - Update data weekly for best results
⚠️ **Backtest vs Reality** - Expect some degradation from backtest performance
✅ **Learning opportunity** - Document everything for blog post #2!

---

**Good luck with your 1-month paper trading test!** 🚀

This will generate valuable data for your follow-up blog post: "Month 1 of Paper Trading: What AI-Evolved Strategies Learned from Reality"
