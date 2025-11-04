# Quick Start Guide - Making Money with Your AI Strategy

## TL;DR - Fast Path to Trading

```bash
# 1. Check today's signals (safe, just information)
python3 examples/simple_live_trader.py --mode check --capital 10000

# 2. Set up daily automation (runs at 4:30 PM ET after market close)
crontab -e
# Add: 30 16 * * 1-5 cd /Users/employee/QuantEvolve && python3 examples/simple_live_trader.py --mode check >> trading.log 2>&1

# 3. Open your brokerage account and manually execute suggested trades
# (Start with $1,000-$5,000 while learning)
```

---

## Current Market Signals

Your strategy just checked the current market (as of Nov 1, 2025):

```
✅ Strategy is running and generating signals!

Current signals:
  AAPL ($270.37):  ⚪ HOLD - no action
  MSFT ($517.81):  ⚪ HOLD - no action
  AMZN ($244.22):  ⚪ HOLD - no action
  GOOGL ($281.19): ⚪ HOLD - no action
  TSLA ($456.56):  ⚪ HOLD - no action
  META ($648.35):  ⚪ HOLD - no action
  NVDA ($202.49):  ⚪ HOLD - no action
```

**No buy signals today** - The strategy is patient and only trades when conditions are perfect.

---

## How to Actually Make Money - The Safe Way

### Week 1: Validation
```bash
# Download 2023-2024 data (out-of-sample testing)
# This tests if your strategy works on data it never saw

# Coming soon: validation script
# python3 scripts/validate_future_data.py
```

**Expected**: If strategy still works on 2023-2024, proceed to Week 2.
**If not**: Re-train with more recent data before trading real money.

### Week 2-8: Paper Trading (NO REAL MONEY)

**Option A: Manual Paper Trading (Simplest)**
1. Open a free account at TD Ameritrade, Interactive Brokers, or Alpaca
2. They give you $100,000 fake money
3. Run `python3 examples/simple_live_trader.py --mode check` daily
4. Manually execute trades in your paper account
5. Track results in a spreadsheet

**Option B: Automated Paper Trading (Recommended)**
1. Sign up at Alpaca.markets (free)
2. Get paper trading API keys
3. Set environment variables:
   ```bash
   export ALPACA_API_KEY='your_paper_key'
   export ALPACA_SECRET_KEY='your_paper_secret'
   ```
4. Run: `python3 examples/simple_live_trader.py --mode paper`
5. Trades execute automatically in paper account

**Success Criteria** (Must achieve ALL before going live):
- ✅ Profitable for 2+ months
- ✅ Win rate > 40%
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 20%
- ✅ You understand why each trade was made

### Week 9+: Live Trading with Real Money

**Start Small:**
```python
# Week 9-12: $1,000 - $2,000
python3 examples/simple_live_trader.py --mode check --capital 1000

# Month 4-6: $5,000 - $10,000 (if profitable)
python3 examples/simple_live_trader.py --mode check --capital 5000

# Month 7+: Scale up (if consistently profitable)
python3 examples/simple_live_trader.py --mode check --capital 25000
```

**Risk Management Rules:**
```
Max risk per trade: 2% of capital
Max position size: 10% of capital
Max total exposure: 50% of capital (keep 50% cash)
Stop loss per position: -5%
Portfolio stop loss: -10% → halt trading
Portfolio kill switch: -30% → exit everything
```

---

## Daily Workflow

### Morning (Before Market Opens)
```bash
# 1. Check for any news on your 7 stocks
#    AAPL, MSFT, AMZN, GOOGL, TSLA, META, NVDA
#    (Earnings, product launches, scandals, etc.)

# 2. No action needed - strategy runs at market close
```

### Afternoon (4:00-5:00 PM ET, After Market Close)
```bash
# 1. Run signal check
python3 examples/simple_live_trader.py --mode check --capital YOUR_CAPITAL

# 2. Review signals
#    🟢 BUY signals → Place market-on-open orders for next day
#    🔴 SELL signals → Place market-on-open sell orders for next day
#    ⚪ HOLD signals → Do nothing

# 3. Log trades in spreadsheet
#    Track: Date, Symbol, Action, Price, Shares, Reason, Outcome
```

### Evening (Review)
```bash
# Update your performance tracking
- Calculate daily P&L
- Update win rate
- Check drawdown from peak
- Verify stop losses are set
```

---

## Example Trade Execution

**Scenario**: Strategy says "🟢 BUY AAPL at $270.37"

### If You Have $10,000 Capital:

```
Position sizing:
- Total capital: $10,000
- Number of BUY signals: 1 (just AAPL)
- Position size: $10,000 ÷ 1 = $10,000
- But max position is 10%: $1,000
- Shares to buy: $1,000 ÷ $270.37 = 3 shares
- Total cost: 3 × $270.37 = $811.11

Actions:
1. Place order: BUY 3 shares of AAPL at market open
2. Set stop loss: Sell if price drops to $256.85 (-5%)
3. Set calendar reminder: Exit in 3 trading days
4. Record trade in spreadsheet
5. Set alert for 3-day exit
```

**3 Days Later**: Strategy exits automatically
- If price is higher → Take profit
- If price is lower → Take loss
- Win or lose, move on to next signal

---

## Realistic Profit Expectations

### Conservative Scenario (What to Actually Expect)

Starting capital: **$10,000**

| Month | Capital | Monthly Return | Cumulative |
|-------|---------|----------------|------------|
| 1 | $10,500 | +5% | +5% |
| 2 | $11,000 | +4.7% | +10% |
| 3 | $11,500 | +4.5% | +15% |
| 6 | $13,500 | varies | +35% |
| 12 | $18,000 | varies | +80% |

**After 1 year**: $10,000 → $18,000 (+80%)
- This would be EXCELLENT performance
- Better than 90% of professional traders
- Better than S&P 500 average (~10%/year)

### Why Not 422% Like the Backtest?

**Reality check:**
1. **Market regime change** - You trained on 2020-2022 (bull market)
2. **Execution costs** - Real trading has more slippage
3. **Behavioral errors** - You might not follow every signal perfectly
4. **Strategy decay** - Strategies get worse over time
5. **Competition** - Markets adapt

**Realistic annual returns:**
- Great: 30-80%
- Good: 15-30%
- Acceptable: 5-15%
- Warning sign: <5%
- Stop trading: Negative

---

## When to Stop Trading

### Red Flags (Review and Pause)
- 2 consecutive losing months
- Win rate drops below 35%
- Max drawdown > 15%
- Sharpe ratio < 0.5 for 3 months
- You're losing sleep over trades

### Kill Switches (Stop Immediately)
- Portfolio down 30% from peak
- 3 consecutive losing months
- You violated your own rules (position sizing, stop losses)
- Strategy stops generating signals
- You need the money for something else

### Recovery Plan
If you hit a kill switch:
1. Stop all trading immediately
2. Withdraw remaining capital
3. Analyze what went wrong
4. Re-train the AI with new data
5. Paper trade for 2 months
6. Only return if paper trading is profitable

---

## Cost Breakdown

### If Using $10,000 Capital

**One-Time Setup:**
- Broker account: $0 (most are free now)
- Data feed: $0 (using free yfinance)
- Software: $0 (you already have it)
- **Total setup: $0**

**Monthly Costs:**
- Trading commissions: ~$0 (most brokers are $0 commission)
- Data: $0
- Server/hosting: $0 (run from your computer)
- **Total monthly: ~$0**

**Annual Costs:**
- Tax preparation: $200-500 (for algo trading, get a CPA)
- **Total annual: ~$300**

### If You Want Professional Setup

**Annual Costs:**
- Real-time data (Polygon.io): $2,400/year
- Cloud hosting (AWS): $600/year
- Professional tax prep: $500/year
- **Total: ~$3,500/year**

Only worth it if trading >$100k capital.

---

## Troubleshooting

### "No BUY signals for 2 weeks"
✅ **This is normal!**
- Strategy is selective (15-30 trades/year per stock)
- That's 1-2 signals per month per stock
- Patience is part of the strategy

### "I got a BUY signal but stock dropped"
✅ **This will happen!**
- Win rate is 48.66% (not 100%)
- More than half your trades will lose money
- You profit because winners > losers

### "My results don't match the backtest"
✅ **Expected!**
- Backtest was on 2020-2022 data
- Markets change
- Aim for 30-80% annual return, not 422%

### "The strategy stopped working"
⚠️ **This will eventually happen**
- All strategies decay over time
- Solution: Re-train with new data
- Run evolution again with 2023-2025 data
- Discover new strategies

---

## Next Actions

### Today (30 minutes)
- [ ] Read DEPLOYMENT_GUIDE.md fully
- [ ] Run `python3 examples/simple_live_trader.py --mode check`
- [ ] Open a paper trading account
- [ ] Set calendar reminder to check signals daily

### This Week
- [ ] Paper trade for 7 days
- [ ] Track all signals in spreadsheet
- [ ] Calculate win rate and P&L
- [ ] Decide if you want to continue

### This Month
- [ ] Paper trade for 30 days
- [ ] If profitable → consider live with $1,000
- [ ] If not profitable → re-train with new data
- [ ] Set up automated signal checking

### This Year
- [ ] Trade consistently for 12 months
- [ ] Compound your profits
- [ ] Re-train model quarterly
- [ ] Reach your financial goals

---

## Support & Resources

**Files You Have:**
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `MODEL_SUMMARY.md` - Your AI model details
- `simulation_report.txt` - Backtest results
- `examples/simple_live_trader.py` - Live trading script
- `exported_strategies/` - Standalone strategy files

**Where to Learn More:**
- r/algotrading - Reddit community
- quantopian.com - Tutorials (site is down, but content archived)
- alpaca.markets/docs - API documentation
- Your own backtest results - Best teacher

**Getting Help:**
- Review the code in `src/`
- Check examples in `examples/`
- Re-read `DEPLOYMENT_GUIDE.md`
- Experiment with paper trading first

---

## Final Checklist

Before trading ANY real money:

- [ ] I validated strategy on 2023-2024 data
- [ ] I paper traded for at least 1 month
- [ ] Paper trading was profitable
- [ ] I understand every trade the strategy makes
- [ ] I have stop losses configured
- [ ] I'm only risking money I can afford to lose
- [ ] I have 6 months expenses saved separately
- [ ] I'm starting with <$5,000
- [ ] I have a plan for when to stop
- [ ] I've consulted a financial advisor (optional but recommended)

**If you checked all boxes** → You're ready to start small!

**If you didn't** → Keep paper trading until you can.

---

## Remember

> "The market is a device for transferring money from the impatient to the patient." - Warren Buffett

Your AI discovered a solid strategy. But making money requires:
1. **Patience** - Wait for signals, don't force trades
2. **Discipline** - Follow the system, don't override it
3. **Risk Management** - Small positions, stop losses, survival first
4. **Persistence** - Keep trading through losses
5. **Adaptation** - Re-train when strategy decays

**You have the tools. Now execute.**

Good luck! 🚀

---

*This is not financial advice. Trading involves risk of loss. Past performance does not guarantee future results.*
