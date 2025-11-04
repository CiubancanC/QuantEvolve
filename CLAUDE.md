# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

QuantEvolve is an evolutionary multi-agent framework for automatically discovering quantitative trading strategies. It implements the research paper "QuantEvolve: Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework" (Yun et al., 2025, arXiv:2510.18569) with ~95% fidelity.

**Core Innovation**: Combines quality-diversity optimization (feature map) with hypothesis-driven strategy generation via multi-agent LLM system to systematically explore diverse, high-performing trading strategies.

## Common Commands

### Running Evolution

```bash
# Quick test with synthetic data (5 generations)
python3 -m src.main --sample-data --generations 5

# Full evolution with real data (150 generations, ~12 hours)
python3 -m src.main --config config/default_config.yaml --generations 150

# Resume from checkpoint
python3 -m src.main --config config/default_config.yaml --resume results/checkpoint_gen_50
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_improved_backtest.py -v
pytest tests/test_basic_functionality.py -v

# Run with coverage
pytest --cov=src tests/
```

### Analysis

```bash
# Analyze evolution results
python3 scripts/analyze_results.py

# Inspect specific strategy
python3 scripts/analyze_strategy.py <strategy_id>

# Compare multiple runs
python3 scripts/compare_results.py results/run1 results/run2

# Export best strategy for deployment
python3 scripts/export_best_strategy.py
```

### Data Preparation

```bash
# Download real market data
python3 scripts/download_real_data.py --symbols AAPL NVDA AMZN GOOGL MSFT TSLA --start 2015-08-01 --end 2025-07-31
```

### Live Trading

```bash
# Check current signals (dry run)
python3 examples/simple_live_trader.py --mode check --capital 10000

# Paper trading (Alpaca API)
python3 examples/simple_live_trader.py --mode paper --capital 10000

# Live trading (requires confirmation)
python3 examples/simple_live_trader.py --mode live --capital 10000
```

## Architecture

### Evolution Flow

```
1. Initialization (src/main.py:111-145)
   ├─ Data Agent analyzes schema (src/agents/data_agent.py)
   ├─ Generate seed strategies (one per category + benchmark)
   └─ Initialize islands (src/core/evolutionary_database.py)

2. Evolution Loop (src/main.py:146-180)
   For each generation:
     For each island:
       ├─ Sample parent (α=0.5 exploitation-exploration balance)
       ├─ Sample cousins (2 best + 3 diverse + 2 random)
       ├─ Research Agent generates hypothesis (src/agents/research_agent.py)
       ├─ Coding Team implements & backtests (src/agents/coding_team.py)
       │   └─ Max 3 debug iterations if backtest fails
       ├─ Evaluation Team analyzes results (src/agents/evaluation_team.py)
       │   ├─ Validates trade frequency (>=10 trades/year)
       │   ├─ Extracts insights
       │   └─ Assigns strategy category (binary encoding)
       └─ Add to feature map if better than existing in cell

     Every 10 generations:  Migration (share 5 best strategies between islands)
     Every 50 generations:  Insight curation (consolidate learnings)

3. Final Output (src/main.py:356-364)
   └─ Save checkpoint with evolutionary database, feature map, insights
```

### Core Components

**Feature Map** (`src/core/feature_map.py`)
- Multi-dimensional archive maintaining strategy diversity
- Dimensions: Strategy Category (8-bit binary), Sharpe Ratio, Sortino Ratio, Total Return, Max Drawdown, Trading Frequency
- Each cell stores best strategy for that feature combination
- Binary category encoding allows 2^8 = 256 hybrid strategy types

**Evolutionary Database** (`src/core/evolutionary_database.py`)
- Island model: 8 islands (7 categories + 1 benchmark)
- Each island evolves independently with periodic migration
- Tracks: population, strategies on feature map, generation counter
- Insight repository: accumulated learnings guide future generations
- Sampling mechanisms: parent (α-balanced), cousins (best/diverse/random mix)

**Multi-Agent System** (`src/agents/`)
- **Data Agent**: Analyzes data schema, generates seed strategies
- **Research Agent**: Creates hypothesis-driven strategy concepts with rationale
- **Coding Team**: Implements strategies, runs backtests, debugs failures (max 3 iterations)
- **Evaluation Team**: Analyzes results, extracts insights, validates trade frequency, curates knowledge

**Backtesting Engine** (`src/backtesting/improved_backtest.py`)
- Custom vectorized engine (not Zipline - see docs/DEVIATIONS.md)
- Paper-specified transaction costs:
  - Commission: $0.0075/share + $1.00 minimum per trade
  - Slippage: Quadratic function of traded volume percentage
- Metrics: Sharpe, Sortino, IR (⚠️ uses zero benchmark, should be market-cap weighted), MDD, Total Return, Win Rate, Profit Factor
- Combined score: `SR + IR + MDD` (MDD is negative, so this penalizes drawdown)

### Key Design Patterns

**Strategy Execution**: Strategies are pure Python functions with signature:
```python
def strategy_function(data: pd.DataFrame) -> pd.Series:
    """
    Args:
        data: OHLCV dataframe with columns [open, high, low, close, volume]
    Returns:
        Series of signals: 1 (buy), 0 (hold), -1 (sell)
    """
```

**LLM Ensemble** (`src/utils/llm_client.py`):
- Small model (Qwen3-30B): Fast generation for coding, hypothesis
- Large model (Qwen3-80B): Thoughtful analysis for evaluation, curation
- Uses OpenRouter API (not local inference - see docs/DEVIATIONS.md)

**Insight Scoring** (`src/core/evolutionary_database.py:_calculate_insight_importance`):
- Factors: Recency, performance impact, novelty (keywords), actionability
- Diversity selection using Jaccard similarity to avoid redundancy
- This goes beyond the paper specification

**Trade Frequency Validation** (`src/agents/evaluation_team.py:56-91`):
- Critical safeguard: Reject strategies with <10 trades/year
- Prevents over-fitting via excessive filter stacking
- Not in original paper, but essential for practical utility

## Configuration

### Key Parameters (`config/default_config.yaml`)

```yaml
evolution:
  num_generations: 150        # Total evolutionary cycles
  migration_interval: 10      # Share best strategies every N gens
  insight_curation_interval: 50  # Consolidate insights every N gens
  alpha: 0.5                  # 0=exploit best, 1=explore diverse

feature_map:
  dimensions:
    - strategy_category: 8 bins (binary encoding)
    - sharpe_ratio: 16 bins, range [-2.0, 5.0]
    - sortino_ratio: 16 bins, range [-2.0, 5.0]
    - total_return: 16 bins, range [-100, 500]%
    - max_drawdown: 16 bins, range [-100, 0]%
    - trading_frequency: 16 bins, range [0, 1000] trades

sampling:
  num_best_cousins: 2         # Top performers for learning
  num_diverse_cousins: 3      # Diverse strategies for exploration
  num_random_cousins: 2       # Random for novelty

llm:
  small_model: "qwen/qwen3-30b-a3b-instruct-2507"  # Fast
  large_model: "qwen/qwen3-next-80b-a3b-instruct"  # Thoughtful
  temperature: 0.7            # Balance creativity and consistency

backtesting:
  periods:
    equities:
      train: 2015-08-01 to 2020-07-31  # 5 years
      val:   2020-08-01 to 2022-07-31  # 2 years
      test:  2022-08-01 to 2025-07-31  # 3 years
```

### Environment Variables

Required for LLM inference:
```bash
OPENROUTER_API_KEY=sk-or-v1-...  # Get from openrouter.ai
```

Optional for live trading:
```bash
ALPACA_API_KEY=...       # Paper/live trading
ALPACA_SECRET_KEY=...
ALPACA_ENDPOINT=...      # paper or live
```

## Important Implementation Notes

### Known Deviations from Paper (see docs/DEVIATIONS.md)

1. **🔴 CRITICAL**: Information Ratio calculation is INCORRECT
   - Currently uses zero benchmark instead of market-cap weighted portfolio
   - Affects evolutionary selection pressure
   - Fix needed at `src/backtesting/improved_backtest.py:446-450`
   - Priority: HIGH before production use

2. **Backtesting Framework**: Custom vectorized engine instead of Zipline
   - Transaction costs match paper specification ✅
   - May not handle corporate actions (splits, dividends, delistings)
   - Assumes clean, split-adjusted data

3. **LLM Inference**: OpenRouter API instead of local models
   - Models are identical, only hosting differs
   - Adds 1-3 second network latency per generation
   - Requires internet connection and API key

### Data Requirements

**Expected Format**:
- CSV or Parquet files in `data/raw/`
- Columns: `[date, open, high, low, close, volume]`
- Date format: YYYY-MM-DD (timezone-aware, preferably UTC or ET)
- Prices: Split-adjusted (use Yahoo Finance or similar)
- Frequency: Daily bars

**Critical**: Data MUST be split-adjusted or backtests will show false breakouts/crashes at split dates.

### Over-Filtering Detection

Strategies with <10 trades/year are automatically rejected. This prevents:
- High Sharpe ratios on tiny sample sizes (n=1 or n=2 trades)
- Statistical meaninglessness
- Wasted compute on over-fitted strategies

LLM prompts warn against over-filtering. If evolution struggles, reduce filter complexity.

### Memory Management

Long evolution runs (150 generations) accumulate:
- ~150-1000 strategies in feature map
- ~500-5000 insights in repository
- Checkpoints saved every 10 generations to `results/`

Each checkpoint includes:
- Feature map state
- All islands and populations
- Insight repository
- Generation counter

Resume from checkpoint if interrupted.

## Common Development Tasks

### Adding a New Strategy Category

1. Edit `config/default_config.yaml`:
   ```yaml
   strategy_categories:
     - "Your New Category"
   ```

2. Update `src/agents/prompts.py` to include category description in system prompts

3. Rebuild feature map (automatically handles new categories)

### Modifying Transaction Costs

Edit `src/backtesting/improved_backtest.py:29-31`:
```python
per_share_commission: float = 0.0075  # $/share
min_commission: float = 1.00          # $ minimum
volume_slippage: bool = True          # Quadratic model
```

### Adding New Metrics

1. Calculate metric in `ImprovedBacktestEngine._calculate_metrics()` (line ~446)
2. Add to returned `metrics` dict
3. Optionally add to `combined_score` formula (line ~460)
4. Update feature map dimensions in config if dimensionality needed

### Recent Cleanup (Nov 2025)

The following deprecated files were removed:
- `src/backtesting/simple_backtest.py` - Replaced by ImprovedBacktestEngine
- `src/optimization/parameter_optimizer.py` - Never integrated into main loop
- `tests/test_zipline_basic.py` - Zipline not used (custom engine instead)

All core functionality remains intact.

### Debugging Strategy Failures

Strategies fail during implementation when:
- Syntax errors (caught by Coding Team, auto-debugged max 3 iterations)
- Runtime errors (division by zero, NaN propagation)
- Insufficient trades (caught by Evaluation Team)

To debug:
```python
# Load strategy code
strategy_code = strategy.code

# Run backtest manually
from src.backtesting.improved_backtest import ImprovedBacktestEngine
engine = ImprovedBacktestEngine(data_dir='./data/raw')
metrics = engine.run_backtest(strategy_code)
```

Check logs in `logs/` directory for detailed error traces.

## Testing Strategy

**Unit Tests**: Cover individual components
- `tests/test_basic_functionality.py` - Core system sanity checks
- `tests/test_improved_backtest.py` - Backtesting engine validation
- `tests/test_period_filtering.py` - Data period filtering
- `tests/test_llm_connection.py` - LLM API connectivity

**Integration Test**: Full evolution run with sample data
```bash
python3 -m src.main --sample-data --generations 5
```
Should complete in ~5-10 minutes, produce ~40-50 strategies.

**Validation**: Compare against paper results (Table 4)
- Run with same data periods as paper
- Verify Sharpe ratios are in similar range
- Check feature map coverage (should reach 5-10% after 150 gens)

## Performance Considerations

**Bottlenecks**:
1. LLM API calls (~2-3 sec/call, 3-5 calls per strategy)
2. Backtesting (~0.1-0.5 sec/strategy depending on data size)
3. Total: ~10-20 sec per strategy generation

**Optimization**:
- Use `llm.small_model` for fast operations (hypothesis, coding)
- Use `llm.large_model` only for analysis/curation
- Backtest engine is already vectorized (avoid loops)
- Consider parallelizing island evolution (not currently implemented)

**Scaling**:
- 150 generations × 8 islands = 1200 strategies
- At 15 sec/strategy: ~5 hours total
- With debug iterations: ~8-12 hours typical

## Related Documentation

- `README.md` - Project overview and installation
- `docs/QuantEvolve.md` - Full research paper
- `docs/DEVIATIONS.md` - Implementation deviations from paper (IMPORTANT)
- `docs/IMPROVEMENTS.md` - Enhancement history
- `DEPLOYMENT_GUIDE.md` - Production deployment guide
- `PAPER_TRADING_GUIDE.md` - Live/paper trading setup
- `QUICK_START.md` - Fast path to trading real money

## Critical Files

- `src/main.py` - Entry point and evolution orchestration
- `src/core/feature_map.py` - Quality-diversity archive (core innovation)
- `src/core/evolutionary_database.py` - Island model and sampling
- `src/agents/prompts.py` - All LLM prompts (modify with care)
- `src/backtesting/improved_backtest.py` - Performance evaluation
- `config/default_config.yaml` - All hyperparameters

When modifying prompts in `src/agents/prompts.py`, be careful to maintain:
- Clear instructions for LLM output format
- Trade frequency warnings (prevent over-filtering)
- Data schema descriptions
- Strategy category definitions
