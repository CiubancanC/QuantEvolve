# QuantEvolve - Quick Start Guide

## 🚀 Getting Started

### 1. Installation

```bash
# Clone the repository
cd QuantEvolve

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

The OpenRouter API key is already configured in `.env`:

```bash
# .env file (already configured)
OPENROUTER_API_KEY=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
SMALL_MODEL=qwen/qwen3-30b-a3b-instruct-2507
LARGE_MODEL=qwen/qwen3-next-80b-a3b-instruct
```

### 3. Run the Demo

To see what's currently implemented:

```bash
python demo_current_features.py
```

This will demonstrate:
- Configuration loading
- LLM client initialization
- Feature map creation
- Evolutionary database setup
- Strategy sampling mechanisms

## 📋 Current Status

**Implementation Progress: ~35% Complete**

### ✅ What's Working

1. **Core Infrastructure**
   - Project structure and configuration
   - OpenRouter API client with dual models
   - Logging system

2. **Core Data Structures**
   - Feature Map (MAP-Elites) for diversity maintenance
   - Evolutionary Database with island model
   - Strategy container with metrics

3. **Sampling Mechanisms**
   - Parent sampling (best vs diverse)
   - Cousin sampling (best, diverse, random)
   - Feature space neighbor sampling

4. **Agent System (Partial)**
   - Data Agent (schema analysis, seed generation)
   - All agent prompts designed
   - Research Agent (in progress)

### 🚧 What's Being Built

- Research Agent (hypothesis generation)
- Coding Team (strategy implementation)
- Evaluation Team (analysis and insights)
- Zipline backtesting integration
- Main evolution loop
- Data utilities
- Visualization tools

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     QuantEvolve System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌─────────────────────────────────┐ │
│  │ Data Agent   │─────▶│  Data Schema Prompt             │ │
│  └──────────────┘      │  + Seed Strategies (C+1)        │ │
│                        └─────────────────────────────────┘ │
│                                      │                       │
│                                      ▼                       │
│  ┌────────────────────────────────────────────────────────┐│
│  │          Evolutionary Database                          ││
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐      ││
│  │  │Island 0│  │Island 1│  │Island 2│  │Island N│  ... ││
│  │  │ (Cat1) │  │ (Cat2) │  │ (Cat3) │  │(Bench) │      ││
│  │  └────────┘  └────────┘  └────────┘  └────────┘      ││
│  │       │            │            │            │          ││
│  │       └────────────┴────────────┴────────────┘          ││
│  │                          │                               ││
│  │                    Migration (every 10 gen)              ││
│  └────────────────────────────────────────────────────────┘│
│                                      │                       │
│                                      ▼                       │
│  ┌────────────────────────────────────────────────────────┐│
│  │              Feature Map (MAP-Elites)                   ││
│  │                                                          ││
│  │  Multi-dimensional archive maintaining diversity:       ││
│  │  - Strategy Category (binary)                           ││
│  │  - Sharpe Ratio (continuous)                            ││
│  │  - Sortino Ratio (continuous)                           ││
│  │  - Total Return (continuous)                            ││
│  │  - Max Drawdown (continuous)                            ││
│  │  - Trading Frequency (continuous)                       ││
│  │                                                          ││
│  │  Each cell stores best strategy for that niche          ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌────────────────── Generation Loop ──────────────────────┐│
│  │                                                          ││
│  │  1. Sample Parent + Cousins  ────────────────────┐      ││
│  │                                                   │      ││
│  │  2. Research Agent ─────▶ Hypothesis             │      ││
│  │                                                   │      ││
│  │  3. Coding Team ────────▶ Strategy Code          │      ││
│  │         │                        │                │      ││
│  │         └──── Backtest ◀─────────┘                │      ││
│  │                   │                               │      ││
│  │                   ▼                               │      ││
│  │  4. Evaluation Team ────▶ Insights               │      ││
│  │                                                   │      ││
│  │  5. Add to Database/Feature Map ◀────────────────┘      ││
│  │                                                          ││
│  │  Every 10 gen: Migration                                ││
│  │  Every 50 gen: Insight Curation                         ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
QuantEvolve/
├── config/
│   └── default_config.yaml        # Hyperparameters and settings
├── data/
│   ├── raw/                        # Market data (OHLCV)
│   └── processed/                  # Processed data
├── src/
│   ├── agents/                     # Multi-agent system
│   │   ├── data_agent.py           # ✅ Data analysis & seeds
│   │   ├── research_agent.py       # 🚧 Hypothesis generation
│   │   ├── coding_team.py          # 📋 Strategy implementation
│   │   └── evaluation_team.py      # 📋 Analysis & insights
│   ├── backtesting/                # 📋 Zipline integration
│   ├── core/
│   │   ├── feature_map.py          # ✅ Quality-diversity map
│   │   └── evolutionary_database.py # ✅ Island model
│   └── utils/
│       ├── llm_client.py           # ✅ OpenRouter client
│       ├── config_loader.py        # ✅ Config management
│       └── logger.py               # ✅ Logging
├── demo_current_features.py        # Demo script
├── IMPLEMENTATION_STATUS.md        # Detailed progress
└── README.md                       # Full documentation
```

## 🔧 Configuration

Edit `config/default_config.yaml` to customize:

### Evolution Parameters
```yaml
evolution:
  num_islands: 8
  num_generations: 150
  migration_interval: 10
  insight_curation_interval: 50
  alpha: 0.5  # Exploration-exploitation balance
```

### Feature Map
```yaml
feature_map:
  dimensions:
    - name: "sharpe_ratio"
      type: "continuous"
      bins: 16
      range: [-2.0, 5.0]
    # ... more dimensions
```

### Strategy Categories
```yaml
strategy_categories:
  - "Momentum/Trend"
  - "Mean-Reversion"
  - "Volatility"
  - "Volume/Liquidity"
  - "Breakout/Pattern"
  - "Correlation/Pairs"
  - "Risk/Allocation"
  - "Seasonal/Calendar Effects"
```

## 🧪 Testing Current Features

### 1. Test LLM Client

```python
from src.utils.llm_client import create_llm_client, LLMEnsemble
from src.utils.config_loader import load_config

config = load_config()
client = create_llm_client(config.get('llm'))
ensemble = LLMEnsemble(client)

# Fast generation
response = ensemble.fast_generate("Explain momentum trading in one sentence.")
print(response)

# Thoughtful generation
response = ensemble.thoughtful_generate("Explain the theory behind momentum trading.")
print(response)
```

### 2. Test Feature Map

```python
from src.core.feature_map import create_feature_map_from_config, Strategy
from src.utils.config_loader import load_config
import numpy as np

config = load_config()
feature_map = create_feature_map_from_config(config.raw)

# Create sample strategy
strategy = Strategy(
    hypothesis="Test momentum strategy",
    code="# code here",
    metrics={
        'sharpe_ratio': 1.5,
        'sortino_ratio': 1.8,
        'information_ratio': 0.7,
        'total_return': 150.0,
        'max_drawdown': -25.0,
        'trading_frequency': 100,
        'strategy_category_bin': 1  # Momentum
    },
    analysis="Test analysis",
    generation=0,
    island_id=0
)

# Add to map
added = feature_map.add(strategy)
print(f"Strategy added: {added}")
print(f"Combined score: {strategy.combined_score:.3f}")

# Get statistics
stats = feature_map.get_statistics()
print(stats)
```

### 3. Test Data Agent (requires LLM calls)

```python
from src.agents.data_agent import DataAgent
from src.utils.llm_client import create_llm_client, LLMEnsemble
from src.utils.config_loader import load_config

config = load_config()
client = create_llm_client(config.get('llm'))
ensemble = LLMEnsemble(client)

# Create Data Agent
data_agent = DataAgent(ensemble)

# Analyze data (when you have data files)
# schema = data_agent.analyze_data(
#     data_dir='./data/raw',
#     assets=['AAPL', 'NVDA', 'AMZN'],
#     asset_type='equities'
# )
# print(schema)

# Generate seed strategies
# categories = config.get('strategy_categories')
# seeds = data_agent.generate_all_seed_strategies(categories)
# print(f"Generated {len(seeds)} seed strategies")
```

## 📊 Expected Output (Demo)

When you run `python demo_current_features.py`, you should see:

```
================================================================================
QuantEvolve - Current Features Demo
================================================================================

1. Loading configuration...
   ✓ Loaded config from: config/default_config.yaml
   - Evolution: 150 generations, 9 islands
   - Feature Map: 6 dimensions

2. Setting up logger...
   ✓ Logger configured

3. Initializing LLM client (OpenRouter)...
   ✓ Connected to OpenRouter
   - Small Model: qwen/qwen3-30b-a3b-instruct-2507
   - Large Model: qwen/qwen3-next-80b-a3b-instruct

4. Creating feature map...
   ✓ Feature map created
   - Shape: (8, 16, 16, 16, 16, 16)
   - Total cells: 524288
   - Dimensions:
     • strategy_category (binary): 8 bins
     • sharpe_ratio (continuous): 16 bins
     • sortino_ratio (continuous): 16 bins
     • total_return (continuous): 16 bins
     • max_drawdown (continuous): 16 bins
     • trading_frequency (continuous): 16 bins

...
```

## 🗺️ Roadmap

### Phase 1: Core Agents (Current)
- [x] Data Agent
- [ ] Research Agent
- [ ] Coding Team
- [ ] Evaluation Team

### Phase 2: Backtesting
- [ ] Zipline integration
- [ ] Metrics calculation
- [ ] Data preparation utilities

### Phase 3: Evolution Loop
- [ ] Main evolution engine
- [ ] Checkpointing
- [ ] Progress tracking

### Phase 4: Analysis & Viz
- [ ] Result visualization
- [ ] Strategy analysis tools
- [ ] Performance reporting

## 📚 Resources

- **Paper**: arXiv:2510.18569
- **Implementation Status**: `IMPLEMENTATION_STATUS.md`
- **Full Documentation**: `README.md`

## 🤝 Contributing

The project is currently in active development. Key areas needing implementation:

1. Coding Team (strategy generation)
2. Evaluation Team (analysis)
3. Backtesting integration
4. Evolution loop
5. Visualization tools

## ❓ Questions?

Check `IMPLEMENTATION_STATUS.md` for detailed component status and known issues.
