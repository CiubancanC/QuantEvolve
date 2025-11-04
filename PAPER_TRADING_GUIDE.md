# 3-Month Paper Trading Validation Guide

## Overview

You've built an AI trading system that showed **422% returns** in backtesting. Now it's time to prove it works in the real world with paper trading (fake money, real market data).

**This guide will help you run a professional 3-month validation.**

---

## What You're About To Do

### The Bot

Your paper trading bot will:
- ✅ Run automatically every day at 4:30 PM ET
- ✅ Analyze 7 tech stocks (AAPL, MSFT, AMZN, GOOGL, TSLA, META, NVDA)
- ✅ Generate buy/sell signals using your evolved strategy
- ✅ Execute trades in Alpaca paper account
- ✅ Hold positions for 3 days (per strategy)
- ✅ Use 5% stop losses
- ✅ Log everything for analysis

### The Goal

**Validate that your strategy works on new data (2024-2025)**

Success means:
- Win rate >40% (backtest was 48.66%)
- Sharpe ratio >1.0 (backtest was 2.811)
- Profitable after 3 months
- Max drawdown <20% (backtest was 2.25%)

---

## Setup (10 minutes)

### Step 1: Run the Setup Script

```bash
cd /Users/employee/QuantEvolve
chmod +x bots/setup_paper_bot.sh
./bots/setup_paper_bot.sh
```

This will:
1. Install required packages
2. Check for Alpaca API keys
3. Test connection
4. Create log directories

### Step 2: Get Alpaca API Keys

If you don't have them yet:

1. Go to https://alpaca.markets
2. Click "Sign Up" (free account)
3. Verify your email
4. Go to "Paper Trading" in dashboard
5. Click "Generate API Key"
6. Copy both keys (API Key and Secret Key)
7. Save them somewhere safe!

### Step 3: Configure Keys

```bash
# Add to ~/.zshrc (or ~/.bashrc if using bash)
echo 'export ALPACA_API_KEY="PK..."' >> ~/.zshrc
echo 'export ALPACA_SECRET_KEY="..."' >> ~/.zshrc

# Reload
source ~/.zshrc
```

### Step 4: Test

```bash
python3 bots/alpaca_paper_bot.py --run-once
```

You should see:
```
✓ Connected to Alpaca (PAPER)
  Portfolio Value: $100,000.00
  Cash: $100,000.00
✓ Daily cycle complete
```

---

## Running the Bot

### Option A: Manual (Recommended for First Week)

Run once per day after market close:

```bash
# Every day at 4:30 PM ET or later
python3 bots/alpaca_paper_bot.py --run-once
```

**Pros**: You see exactly what's happening
**Cons**: You have to remember to run it

### Option B: Automated (After You're Comfortable)

Set up cron job to run automatically:

```bash
crontab -e

# Add this line (runs at 4:30 PM ET, Mon-Fri)
30 16 * * 1-5 cd /Users/employee/QuantEvolve && python3 bots/alpaca_paper_bot.py --run-once >> logs/cron.log 2>&1
```

**Pros**: Completely automated
**Cons**: Less visibility

### Option C: Daemon Mode (Advanced)

Bot runs continuously, executes at 4:30 PM:

```bash
# Run in background
nohup python3 bots/alpaca_paper_bot.py --daemon > bot.log 2>&1 &
```

**Pros**: Always running, very reliable
**Cons**: Uses system resources 24/7

---

## Daily Routine (5 minutes/day)

### After Market Close (4:30 PM ET)

```bash
# 1. Run the bot (if manual mode)
python3 bots/alpaca_paper_bot.py --run-once

# 2. Check performance
python3 bots/performance_dashboard.py
```

### What to Look For

**Good signs:**
- ✅ Trades executing successfully
- ✅ Portfolio value stable or increasing
- ✅ Win rate around 40-50%
- ✅ No error messages

**Warning signs:**
- ⚠️ Multiple failed orders
- ⚠️ Portfolio down >5% from starting value
- ⚠️ Win rate <30%
- ⚠️ Errors in logs

**Red flags:**
- 🛑 Portfolio down >10%
- 🛑 No trades executing
- 🛑 System crashes
- 🛑 API errors

---

## Weekly Review (15 minutes/week)

### Export and Analyze

```bash
# Export to CSV
python3 bots/performance_dashboard.py --export

# Open in spreadsheet
open logs/paper_trading/trades_export.csv
```

### Track These Metrics

| Metric | Target | Your Value | Status |
|--------|--------|------------|--------|
| Portfolio Value | >$100k | $______ | ✅/⚠️/🛑 |
| Weekly Return | +2-5% | ____% | ✅/⚠️/🛑 |
| Win Rate | >40% | ____% | ✅/⚠️/🛑 |
| Sharpe Ratio | >1.0 | ____ | ✅/⚠️/🛑 |
| Max Drawdown | <-10% | ____% | ✅/⚠️/🛑 |
| Total Trades | 5-15 | ____ | ✅/⚠️/🛑 |

### Decision Tree

**All ✅** → Keep going, everything's working

**Mix of ✅ and ⚠️** → Monitor closely, normal variance

**Any 🛑** → Investigate immediately:
- Check logs for errors
- Verify market data is current
- Consider pausing if major issues

---

## Monthly Deep Dive (1 hour/month)

### Month 1 Review

**Questions to answer:**
1. Is the bot executing trades correctly? ____
2. Are fills happening at reasonable prices? ____
3. Is the win rate acceptable (>35%)? ____
4. Any unexpected behavior? ____
5. Portfolio up, down, or flat? ____

**Decision:**
- [ ] Continue → Everything looks good
- [ ] Adjust → Minor issues, keep watching
- [ ] Stop → Major problems, need to fix

### Month 2 Review

**Compare to backtest:**

| Metric | Backtest | Paper Trading | Match? |
|--------|----------|---------------|--------|
| Total Return | +422% | ____% | ✅/❌ |
| Sharpe Ratio | 2.811 | ____ | ✅/❌ |
| Win Rate | 48.66% | ____% | ✅/❌ |
| Max DD | -2.25% | ____% | ✅/❌ |

**Expected:** Paper trading will be somewhat worse than backtest
**Acceptable:** 50-80% of backtest performance
**Concerning:** <50% of backtest performance

**Decision:**
- [ ] On track → Profitable and reasonable metrics
- [ ] Marginal → Breakeven, need more data
- [ ] Failing → Consistent losses, may need to stop

### Month 3 Final Review

**Calculate final metrics:**

```python
# Final numbers
Initial: $100,000
Final: $______
Profit: $______
Return: ____%

Sharpe: ____
Max DD: ____%
Win Rate: ____%
Total Trades: ____
```

**The BIG Question: Ready for live trading?**

Checklist:
- [ ] Profitable overall (any profit, even $1)
- [ ] Win rate >40%
- [ ] Sharpe ratio >1.0
- [ ] Max drawdown <20%
- [ ] No major technical issues
- [ ] You understand why trades win/lose
- [ ] You're comfortable with the risk

**If all checked** → Start live trading with $1,000-$5,000

**If some checked** → Continue paper trading, may need adjustments

**If few checked** → Strategy may need retraining with new data

---

## Troubleshooting

### Bot Not Trading

**Symptom:** No trades for days/weeks

**Possible causes:**
1. No buy signals → This is NORMAL, strategy is selective
2. Market conditions don't match criteria
3. Already holding max positions

**What to do:**
- Check if strategy generates signals manually
- Review recent market conditions
- Be patient - backtested 13-16 trades/year per stock

### Execution Errors

**Symptom:** Orders failing, error messages

**Possible causes:**
1. API rate limits → Wait 1 minute, retry
2. Market closed → Trades execute next day
3. Insufficient cash → Check position sizing
4. Invalid symbols → Verify ticker symbols correct

**What to do:**
- Check `logs/paper_trading/bot_*.log`
- Verify API keys are valid
- Test connection manually

### Poor Performance

**Symptom:** Losing money consistently

**Possible causes:**
1. Market regime changed (bull → bear)
2. Strategy overfit to training data
3. Execution issues (slippage, fills)
4. Bad luck (short-term variance)

**What to do:**
- Week 1-2: Keep going (too early)
- Week 3-4: Monitor closely
- Month 2: Consider if consistent pattern
- Month 3: May need to retrain strategy

---

## Data to Collect

### Create a Tracking Spreadsheet

**Daily Log:**
| Date | Action | Symbol | Shares | Price | P&L | Portfolio Value | Notes |
|------|--------|--------|--------|-------|-----|-----------------|-------|
| 11/1 | BUY | AAPL | 10 | $270 | - | $100,000 | First trade |
| 11/4 | SELL | AAPL | 10 | $275 | +$50 | $100,050 | 3-day exit |

**Weekly Summary:**
| Week | Starting Value | Ending Value | P&L | Return | Win Rate | Notes |
|------|---------------|--------------|-----|--------|----------|-------|
| 1 | $100,000 | $101,500 | +$1,500 | +1.5% | 66% | Strong start |
| 2 | $101,500 | $100,800 | -$700 | -0.7% | 40% | Pullback |

**Monthly Summary:**
| Month | Return | Sharpe | Max DD | Trades | Win Rate | Grade |
|-------|--------|--------|--------|--------|----------|-------|
| 1 | +5% | 1.2 | -3% | 12 | 58% | B+ |
| 2 | -2% | 0.8 | -8% | 10 | 40% | C+ |
| 3 | +8% | 1.5 | -5% | 15 | 60% | A- |

---

## What Success Looks Like

### After 1 Month

**Excellent:**
- Portfolio: $105k-$115k (+5-15%)
- Sharpe: >1.5
- Win rate: >50%
- Smooth upward curve

**Good:**
- Portfolio: $102k-$105k (+2-5%)
- Sharpe: >1.0
- Win rate: >45%
- Some volatility but generally up

**Acceptable:**
- Portfolio: $100k-$102k (0-2%)
- Sharpe: >0.5
- Win rate: >40%
- Choppy but not losing

**Concerning:**
- Portfolio: <$100k (losing)
- Sharpe: <0.5
- Win rate: <35%
- Consistent losses

### After 3 Months

**Best Case** (Ready for live):
- Portfolio: $115k-$140k (+15-40%)
- Sharpe: >2.0
- Win rate: >50%
- Strategy clearly works

**Realistic Case** (Cautiously ready):
- Portfolio: $105k-$115k (+5-15%)
- Sharpe: >1.0
- Win rate: >45%
- Decent performance, some variance

**Marginal Case** (More testing needed):
- Portfolio: $98k-$105k (-2% to +5%)
- Sharpe: 0.5-1.0
- Win rate: 40-45%
- Unclear if strategy has edge

**Failure Case** (Back to drawing board):
- Portfolio: <$95k (loss >5%)
- Sharpe: <0.5
- Win rate: <40%
- Strategy not working

---

## Next Steps After 3 Months

### If Successful (Profitable & Consistent)

**Week 1:** Celebrate! Your AI works! 🎉

**Week 2:** Open live brokerage account
- Alpaca (algorithmic trading friendly)
- Interactive Brokers (professional platform)
- TD Ameritrade/Schwab (traditional)

**Week 3:** Start with $1,000-$5,000
- Use same bot, just change API endpoint
- Run paper AND live in parallel
- Compare results daily

**Month 2:** Scale up slowly
- If profitable → add $2k-$5k more
- If breakeven → wait another month
- If losing → stop and investigate

**Month 3+:** Compound and grow
- Keep 50% of profits
- Reinvest 50%
- Document everything
- Share your success!

### If Marginal (Breakeven ±5%)

**Don't give up!** Markets are hard.

**Options:**
1. **More data:** Run another 3 months paper
2. **Retrain:** Use 2023-2025 data, evolve again
3. **Adjust:** Tweak position sizing, stops
4. **Combine:** Try multiple strategies together

**Not ready for live trading yet**, but not a failure.

### If Failed (Consistent Losses)

**This is valuable data!** You learned:
- Strategy doesn't work on new data
- Market regime changed
- Need to adapt

**What to do:**
1. Analyze what went wrong
2. Gather 2023-2025 data
3. Re-run evolution (500 generations)
4. Test new strategy in paper
5. Repeat until profitable

**The system works** - you just need a strategy that matches current markets.

---

## Final Thoughts

### Remember

1. **This is paper trading** - No real money at risk
2. **Be patient** - 3 months is minimum
3. **Track everything** - Data is gold
4. **Learn constantly** - Every trade teaches something
5. **Stay disciplined** - Follow the system

### The Real Value

Even if the strategy doesn't work perfectly, you've built:
- ✅ An AI system that can evolve strategies
- ✅ Automated trading infrastructure
- ✅ Performance tracking and analysis tools
- ✅ Experience with real market data
- ✅ Knowledge to adapt and improve

This is not a one-shot system. It's a **strategy factory**.

When markets change, you re-train and adapt.

### Your Advantage

Most traders:
- Use static strategies
- Don't adapt to market changes
- Give up after first failure

You have:
- AI that evolves new strategies
- Systematic approach
- Tools to validate and improve
- Ability to adapt continuously

**This is your edge.** Use it wisely.

---

## Support

**Questions?**
- Read `bots/README.md` for technical details
- Check `DEPLOYMENT_GUIDE.md` for live trading
- Review `MODEL_SUMMARY.md` for strategy details
- Check bot logs: `logs/paper_trading/`

**Issues?**
- Alpaca docs: https://alpaca.markets/docs/
- Python alpaca-trade-api: https://github.com/alpacahq/alpaca-trade-api-python

**Community:**
- r/algotrading on Reddit
- Alpaca community forums
- QuantConnect forums

---

**You've got this!** 🚀

Take it seriously, track everything, and in 3 months you'll know if you're ready for real money trading.

Good luck!
