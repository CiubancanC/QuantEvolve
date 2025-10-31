# QuantEvolve System Improvements

This document summarizes the improvements made to the QuantEvolve system based on analysis of the initial run.

## Date: October 23, 2025

## Summary

After running the system for 1 generation and analyzing the results, we identified several critical issues and implemented fixes to improve strategy quality and evolution effectiveness.

---

## 1. Fixed Pandas Deprecation Warnings

**Problem**: Generated strategies were using deprecated pandas syntax (`fillna(method='ffill')`)

**Solution**: Updated prompts to instruct the LLM to use modern pandas API
- Use `.ffill()` instead of `fillna(method='ffill')`
- Use `.bfill()` instead of `fillna(method='bfill')`

**Files Modified**:
- `src/agents/prompts.py` (3 locations)

**Impact**: Future strategies will use current pandas API, avoiding deprecation warnings

---

## 2. Added Trade Frequency Constraints

**Problem**: The top strategy (strat_952556673) achieved excellent Sharpe/Sortino ratios BUT only generated 1 trade in 3 years, making the metrics statistically meaningless.

**Root Cause**: Over-filtering - strategy stacked 3 aggressive filters:
1. Price > 20-day high
2. Volume > 1.2σ above average
3. Price > 50-day SMA

These conditions rarely aligned simultaneously.

**Solution**: Implemented automatic rejection of over-filtered strategies
- Added `min_trades_per_year` parameter (default: 10 trades/year)
- Evaluation team now calculates trades per year and rejects strategies below threshold
- Rejected strategies receive category_bin=9999 and detailed rejection message
- Insights explain why over-filtering is problematic

**Files Modified**:
- `src/agents/evaluation_team.py`
- `src/main.py` (to calculate backtest years and pass to evaluator)

**Impact**: Evolutionary process will automatically reject strategies with insufficient trading activity, pushing the system toward more practical strategies.

---

## 3. Improved Prompt Guidance

**Problem**: LLM was generating strategies without considering trading frequency requirements

**Solution**: Enhanced prompts with explicit guidance and examples

### Research Agent Prompts:
- Added trading frequency as a CRITICAL requirement
- Explained common over-filtering mistakes:
  - Stacking too many filters
  - Using overly aggressive sigma thresholds (>1.2σ)
  - Using slow trend indicators (50-day SMA)
  - Requiring rare conditions to align

- Provided good practices:
  - Use 2-3 complementary filters maximum
  - Start with moderate thresholds (0.8-1.0σ)
  - Use faster indicators for tech stocks (10-20 day)
  - Target: 15-30 trades per asset over 3 years

### Coding Team Prompts:
- Added examples of good vs bad strategies
- Bad: 4 stacked filters → 1-2 signals in 3 years
- Good: 2 balanced filters → 15-30 signals in 3 years
- Emphasized target trading frequency in implementation notes

**Files Modified**:
- `src/agents/prompts.py`

**Impact**: LLM will be more likely to generate strategies with appropriate trading frequencies from the start.

---

## 4. Added Parameter Optimization Layer

**Problem**: Promising strategies often use arbitrary parameter values that may not be optimal

**Solution**: Created `ParameterOptimizer` class for grid search optimization
- Automatically identifies tunable parameters (windows, thresholds, sigma values)
- Generates parameter combinations via grid search
- Tests each combination via backtest
- Returns best-performing variant
- Includes optimization report with all tested combinations

**Key Features**:
- Pattern matching to find tunable parameters in code
- Smart parameter range selection (e.g., window ±10, sigma ±0.4)
- Limits combinations to prevent explosion (default: max 9 tests)
- Optimization score balances Sharpe with trading frequency
- Penalizes very low trade counts to avoid over-fitting

**Files Created**:
- `src/optimization/parameter_optimizer.py`
- `src/optimization/__init__.py`

**Usage Example**:
```python
from src.optimization import ParameterOptimizer

optimizer = ParameterOptimizer(backtest_engine)
best_code, best_metrics, report = optimizer.optimize_strategy(
    code=strategy_code,
    metrics=original_metrics,
    max_iterations=9
)
```

**Impact**: Strategies that show promise but use sub-optimal parameters can be automatically tuned to improve performance.

---

## 5. Configuration Recommendations

### Current Settings (config.yaml):
```yaml
evolution:
  num_generations: 5
  population_per_island: 10
```

### Recommended Settings for Better Results:
```yaml
evolution:
  num_generations: 20        # Increase from 5 to allow more evolution
  population_per_island: 10   # Keep current

evaluation:
  min_trades_per_year: 10     # New setting for trade frequency filter
```

**Rationale**:
- More generations allow the system to learn from failures and iterate
- The initial generations often produce many rejected strategies
- By generation 10-15, the system should converge on viable patterns
- Trade frequency filter prevents wasted compute on over-filtered strategies

---

## Key Insights from First Run

### Top Strategy Analysis (strat_952556673)

**Strategy**: "Confident Breakout"
- **Concept**: Volume-confirmed breakouts with trend alignment
- **Filters**: Breakout + Volume spike (1.2σ) + 50-SMA

**Metrics** (deceptively good):
- Sharpe: 0.18
- Sortino: 18.96
- Win Rate: 94.3%
- Profit Factor: 878
- **But**: Only 1 trade in 3 years!

**Why It Failed**:
1. 50-SMA is too slow for fast-trending tech stocks
2. 1.2σ volume threshold is too aggressive
3. Three filters stack multiplicatively, eliminating most signals
4. In trending markets, price is usually ABOVE 50-SMA, so filter does nothing useful
5. Only caught 1 rare convergence event - not a systematic edge

**Lessons Learned**:
1. Volume confirmation must be relative, not absolute (use adaptive thresholds)
2. Trend filters should use slope/direction, not price position
3. Over-filtering is the #1 failure mode for algorithmic strategies
4. High metrics with n=1 are statistical noise, not alpha
5. Trade frequency is a first-order constraint - optimize for it early

---

## Next Steps

1. **Run Evolution for 10-20 Generations**
   - The system needs time to learn from rejection feedback
   - Early generations will have many rejections
   - Later generations should produce better strategies

2. **Monitor Trade Frequency Distribution**
   - Track how many strategies are rejected for low frequency
   - Adjust min_trades_per_year if too many/few rejections

3. **Apply Parameter Optimization to Top Strategies**
   - After evolution completes, optimize the top 10 strategies
   - Report improvement statistics

4. **Implement Validation Set Testing**
   - Current: trains on train period only
   - Add: test top strategies on validation period
   - Prevents overfitting to training data

5. **Add Regime Analysis**
   - Track strategy performance in different market regimes
   - Bull markets: 2020-2021
   - Bear markets: 2022
   - Choppy markets: 2023

---

## Testing the Improvements

To verify the improvements work correctly:

```bash
# Run with sample data for 2 generations
python3 -m src.main --sample-data --generations 2

# Expected outcomes:
# - Some strategies should be rejected for low trading frequency
# - Logs should show "Strategy over-filtered" warnings
# - LLM should generate strategies targeting 15-30 trades
# - No pandas deprecation warnings
```

---

## Files Modified Summary

**Core Changes**:
1. `src/agents/evaluation_team.py` - Added trade frequency check
2. `src/agents/prompts.py` - Enhanced with frequency guidance
3. `src/main.py` - Calculate backtest years for evaluation

**New Features**:
4. `src/optimization/parameter_optimizer.py` - Parameter tuning
5. `src/optimization/__init__.py` - Module init

**Documentation**:
6. `IMPROVEMENTS.md` (this file)
7. `analyze_strategy.py` - Tool to inspect strategies from DB

---

## Performance Expectations

After these improvements, we expect:

**Short Term (Generations 1-5)**:
- 50-70% rejection rate due to over-filtering
- System learning from rejection feedback
- Gradual increase in trading frequencies

**Medium Term (Generations 5-15)**:
- 20-40% rejection rate
- Emergence of consistent patterns (e.g., "use 0.8σ threshold")
- Sharpe ratios: 0.5-1.2 range with 20-50 trades

**Long Term (Generations 15+)**:
- <20% rejection rate
- Convergence on viable strategy families
- Potential discovery of genuine alpha (Sharpe >1.5 with 30+ trades)

---

## Questions?

For questions about these improvements, see:
- Code comments in modified files
- Logs from test runs (check for "over-filtered" warnings)
- Strategy analysis tool: `python3 analyze_strategy.py`
