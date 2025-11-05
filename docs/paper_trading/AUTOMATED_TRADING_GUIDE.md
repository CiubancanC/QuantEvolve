# Automated 30-Day Paper Trading - Complete Guide

## Overview

Your paper trading system is now **fully automated**! Just start it once and let it run for 30 days. No cron jobs, no manual intervention—completely hands-off.

### What It Does

- **Runs continuously** for 30 days on your machine
- **Detects market hours** automatically (Mon-Fri, 9:30 AM - 4 PM ET)
- **Executes trades daily** at 3:30 PM ET (30 min before close)
- **Generates reports** after each trading day
- **Recovers from errors** automatically
- **Monitors its own health** and logs everything

### Your 3 Strategies (Running in Parallel)

| # | ID | Backtest Return | Sharpe | Trades | Capital |
|---|-----|-----------------|--------|--------|---------|
| 1 | strat_730524051 | 556.59% | 3.68 | 172 | $10,000 |
| 2 | strat_175698548 | 433.41% | 3.46 | 117 | $10,000 |
| 3 | strat_514146649 | 397.62% | 1.25 | 2 | $10,000 |

**Total Portfolio**: $30,000 virtual capital

---

## Quick Start (3 Commands)

### 1. Start the Daemon

```bash
./scripts/trading start
```

**Output**:
```
Starting 30-day paper trading daemon...
✓ Daemon started with PID: 12345

Monitor with:
  ./scripts/trading status
  ./scripts/trading logs

Stop with:
  ./scripts/trading stop
```

### 2. Check Status

```bash
./scripts/trading status
```

**Output**:
```
Daemon IS running (PID: 12345)

Current Status:
  State: running
  Started: 2025-11-05T09:00:00
  Last trade: None
  Trading days: 0
  Successful: 0
  Failed: 0
```

### 3. View Logs

```bash
./scripts/trading logs
```

Shows the last 50 log entries including market status, trade executions, and errors.

---

## How It Works

### Daily Cycle

1. **Daemon runs continuously**, checking every 5 minutes
2. **Detects market open** (Mon-Fri 9:30 AM - 4 PM ET)
3. **At 3:30 PM ET**: Executes daily trades
   - Fetches latest market data
   - Generates signals for all 3 strategies
   - Executes BUY/SELL orders via Alpaca
   - Records positions and trades
4. **Generates performance report**
5. **Sleeps until next check**

### Market Hours Detection

The daemon knows when to trade:
- ✅ **Weekdays** (Mon-Fri): Active
- ❌ **Weekends**: Skipped automatically
- ❌ **Outside 9:30 AM - 4 PM ET**: Waits
- ✅ **First time after 3:30 PM**: Executes trades

**You don't need to worry about schedules!** The daemon handles everything.

---

## Control Commands

### Start Daemon (Background)

```bash
./scripts/trading start
```

Starts daemon in background. It will run until:
- 30 days elapsed, OR
- You stop it manually, OR
- System crashes (then restart it)

### Stop Daemon

```bash
./scripts/trading stop
```

Gracefully stops the daemon. All state is saved.

### Check Status

```bash
./scripts/trading status
```

Shows:
- Is it running?
- When did it start?
- How many trades executed?
- Any errors?

### View Logs

```bash
./scripts/trading logs
```

Shows recent activity. Full logs in `logs/daemon/paper_trading_daemon.log`.

### Generate Report

```bash
./scripts/trading report
```

Generates detailed performance report (same as automatic daily reports).

---

## What Gets Tracked

### Daemon State (`results/paper_trading/daemon_state.json`)

```json
{
  "start_time": "2025-11-05T09:00:00-05:00",
  "last_trade_date": "2025-11-05",
  "total_trading_days": 1,
  "successful_trades": 1,
  "failed_trades": 0,
  "errors": [],
  "status": "running"
}
```

### Trading Data (`results/paper_trading/tracking.json`)

```json
{
  "strategies": {
    "strat_730524051": {
      "initial_capital": 10000,
      "current_value": 10250,
      "positions": [{"symbol": "AAPL", "shares": 100, ...}],
      "trades": [{"timestamp": "...", "action": "buy", ...}],
      "daily_returns": [2.5, 1.2, ...]
    }
  },
  "daily_snapshots": [...]
}
```

### Daily Reports (`results/paper_trading/daily_reports/`)

Markdown reports generated after each trading day:
- `report_20251105.md`
- `report_20251106.md`
- etc.

---

## Monitoring Your 30-Day Run

### Daily (Recommended)

```bash
./scripts/trading status
```

Quick health check. Takes 2 seconds.

### Weekly (Recommended)

```bash
./scripts/trading report
```

Review performance:
- Total return vs backtest
- Number of trades per strategy
- Open positions
- Any errors

### Real-Time (Optional)

```bash
tail -f logs/daemon/paper_trading_daemon.log
```

Watch live as trades execute (useful during market hours).

---

## What to Expect

### Week 1

- Daemon starts trading
- Initial positions opened
- 3-5 trading days of data
- Early performance indicators

### Week 2-3

- More trades accumulated
- Performance patterns emerge
- Can compare to backtest metrics

### Week 4 (End of Month)

- 20-22 trading days completed
- Statistically meaningful sample
- Final performance report
- Material for blog post #2!

---

## Troubleshooting

### "Daemon is NOT running"

**Cause**: Daemon stopped or crashed.

**Solution**:
1. Check logs: `./scripts/trading logs`
2. Look for errors
3. Restart: `./scripts/trading start`

### "No trades being executed"

**Cause**: Markets closed or already traded today.

**Check**:
```bash
./scripts/trading status
```

Look for "Last trade" date. If it's today, trading already happened.

**Markets are closed if**:
- Weekend (Sat/Sun)
- Before 9:30 AM or after 4 PM ET
- Market holiday (check Alpaca status)

### "Failed trades: X"

**Cause**: Errors during trade execution.

**Check**:
```bash
./scripts/trading status
```

Review the "errors" section. Common causes:
- Data fetching issues
- API connection problems
- Strategy code errors

**Solution**:
- Usually auto-recovers next day
- If persistent, check logs for details

### Computer went to sleep

**Issue**: Daemon might not trade if computer sleeps during market hours.

**Solutions**:
- Prevent sleep: System Preferences → Energy Saver
- Or: Run on always-on machine
- Or: Restart daemon when you wake computer

### Need to restart after crash

```bash
# Check if running
./scripts/trading status

# If not, restart
./scripts/trading start
```

**All data is preserved!** The daemon resumes from where it left off.

---

## File Locations

```
QuantEvolve/
├── scripts/
│   ├── trading                          # Main control script ⭐
│   ├── paper_trading_daemon.py          # Daemon engine
│   ├── paper_trading_top3.py            # Trading logic
│   └── generate_paper_trading_report.py # Reports
│
├── results/paper_trading/
│   ├── daemon_state.json                # Daemon status
│   ├── daemon.pid                       # Process ID
│   ├── tracking.json                    # All trading data ⭐
│   └── daily_reports/                   # Daily MD reports
│
└── logs/
    ├── daemon/
    │   └── paper_trading_daemon.log     # Daemon logs
    └── paper_trading/
        └── paper_trading_YYYYMMDD.log   # Daily trading logs
```

**⭐ = Critical files (backup regularly!)**

---

## Advanced Usage

### Custom Trading Time

Default is 3:30 PM ET (30 min before close). To change:

```bash
python3 scripts/paper_trading_daemon.py start --trade-time "14:00"  # 2 PM ET
```

### Different Duration

Default is 30 days. To change:

```bash
python3 scripts/paper_trading_daemon.py start --duration 60  # 2 months
```

### Faster Checks (More Responsive)

Default checks every 5 minutes. To check more frequently:

```bash
python3 scripts/paper_trading_daemon.py start --check-interval 60  # Every minute
```

**Note**: Uses slightly more CPU but more responsive.

---

## Data Management

### Backup Critical Data

**Weekly backup** (recommended):

```bash
# Create backup
cp results/paper_trading/tracking.json ~/Backups/tracking_$(date +%Y%m%d).json

# Or use Time Machine / cloud backup
```

### Update Market Data

The daemon uses cached data from `data/raw/`. Update weekly:

```bash
python3 scripts/download_real_data.py --symbols AAPL NVDA AMZN GOOGL MSFT TSLA \
    --start 2025-10-01 --end $(date +%Y-%m-%d)
```

### Export Results

After 30 days, export everything:

```bash
# Create archive
tar -czf paper_trading_results_$(date +%Y%m%d).tar.gz results/paper_trading/

# Generate final report
./scripts/trading report > final_report.txt
./scripts/trading report --format markdown > final_report.md
```

---

## Safety Features

### Automatic Error Recovery

- **Trade execution fails**: Logged, retries next day
- **Data fetch fails**: Uses cached data, retries later
- **API errors**: Logged, continues monitoring

### State Persistence

- **Everything is saved**: Even if daemon crashes
- **Resumable**: Restart picks up where it left off
- **No data loss**: All trades and positions recorded

### Graceful Shutdown

- **CTRL+C**: Saves state and exits cleanly
- **`./scripts/trading stop`**: Graceful termination
- **System shutdown**: State saved on exit

---

## After 30 Days

### Final Report

```bash
# Generate comprehensive final report
./scripts/trading report

# Save to file
./scripts/trading report > results/final_report.txt
```

### Analysis

Review:
1. **Total return** vs backtest (expect some degradation)
2. **Sharpe ratio** (should still be positive)
3. **Max drawdown** (compare to backtest)
4. **Trade frequency** (did strategies trade regularly?)
5. **Strategy diversity** (did all 3 strategies contribute?)

### Decision Time

Based on results:

✅ **Success** (returns > 0%, Sharpe > 1.0):
- Continue with same strategies
- Consider increasing capital
- Move to live trading (carefully!)

⚠️ **Mixed** (some strategies work, others don't):
- Keep winners, drop losers
- Run another month with top 2
- Analyze what changed

❌ **Failure** (negative returns, high drawdown):
- Analyze what went wrong
- Market regime change?
- Re-run evolution with recent data
- Refine strategy categories

### Blog Post #2

You'll have material for: **"Month 1 of Paper Trading: What AI-Evolved Strategies Learned from Reality"**

Topics:
- Backtest vs reality comparison
- Which strategies adapted best
- Unexpected market conditions
- Lessons for evolution v2
- Decision on live trading

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  AUTOMATED PAPER TRADING - QUICK REFERENCE      │
├─────────────────────────────────────────────────┤
│  START:    ./scripts/trading start              │
│  STOP:     ./scripts/trading stop               │
│  STATUS:   ./scripts/trading status             │
│  LOGS:     ./scripts/trading logs               │
│  REPORT:   ./scripts/trading report             │
├─────────────────────────────────────────────────┤
│  Duration: 30 days                              │
│  Trade Time: 3:30 PM ET daily                   │
│  Capital: $30,000 ($10k per strategy)           │
│  Strategies: 3 (top performers)                 │
│  Mode: Paper Trading (no real money)            │
└─────────────────────────────────────────────────┘
```

---

## Support & Resources

- **Logs**: `logs/daemon/paper_trading_daemon.log`
- **State**: `results/paper_trading/daemon_state.json`
- **Trading Data**: `results/paper_trading/tracking.json`
- **Alpaca Dashboard**: https://app.alpaca.markets/paper/dashboard/overview

---

## Ready to Start!

Your system is **fully automated and tested**. When you're ready:

```bash
# Start your 30-day automated trading test
./scripts/trading start

# Confirm it's running
./scripts/trading status

# Check logs
./scripts/trading logs
```

**That's it!** The daemon will handle everything for the next 30 days. Just check status occasionally to monitor progress.

Good luck! 🚀

---

**Pro Tip**: Set a calendar reminder for 7, 14, 21, and 30 days to review performance with `./scripts/trading report`.
