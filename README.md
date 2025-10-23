# QuantEvolve

**Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework**

QuantEvolve is an evolutionary multi-agent framework that automatically generates diverse, high-performing trading strategies. It combines quality-diversity optimization with hypothesis-driven strategy generation to explore the vast strategy space while maintaining diversity.

## Overview

Based on the paper "QuantEvolve: Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework" (arXiv:2510.18569), this implementation provides:

- **Feature Map**: Multi-dimensional archive aligned with investor preferences (risk profile, trading frequency, return characteristics)
- **Island Model**: Multiple populations evolving independently with periodic migration
- **Multi-Agent System**: Hypothesis-driven strategy generation using specialized agents:
  - Data Agent: Analyzes data schema and generates seed strategies
  - Research Agent: Generates trading hypotheses from parent/cousin strategies
  - Coding Team: Implements and backtests strategies
  - Evaluation Team: Analyzes results and extracts insights
- **Evolution Loop**: Iterative improvement with structured reasoning and diversity preservation

## Architecture

```
QuantEvolve/
├── config/                    # Configuration files
│   └── default_config.yaml   # Default hyperparameters
├── data/                     # Data directory
│   ├── raw/                  # Raw market data
│   └── processed/            # Processed data
├── src/                      # Source code
│   ├── agents/              # Multi-agent system
│   │   ├── data_agent.py    # Data schema analysis & seed generation
│   │   ├── research_agent.py # Hypothesis generation
│   │   ├── coding_team.py   # Strategy implementation
│   │   └── evaluation_team.py # Strategy analysis
│   ├── backtesting/         # Backtesting engine integration
│   │   ├── zipline_engine.py # Zipline backtesting
│   │   └── metrics.py       # Performance metrics
│   ├── core/                # Core data structures
│   │   ├── feature_map.py   # Feature map implementation
│   │   └── evolutionary_database.py # Island model & DB
│   └── utils/               # Utilities
│       ├── llm_client.py    # OpenRouter API client
│       ├── config_loader.py # Configuration management
│       └── logger.py        # Logging setup
├── logs/                    # Log files
├── results/                 # Evolution results
└── docs/                    # Documentation
```

## Features

### 1. Feature Map (Quality-Diversity)
- Multi-dimensional archive maintaining behavioral diversity
- Dimensions: strategy category, Sharpe ratio, Sortino ratio, total return, max drawdown, trading frequency
- Each cell stores the best-performing strategy for that feature combination
- Enables personalized strategy recommendation and robust performance

### 2. Island Model
- Multiple populations evolve independently (one per strategy category + benchmark)
- Periodic migration of best strategies between islands
- Balances exploration (early specialization) vs exploitation (later hybridization)

### 3. Hypothesis-Driven Multi-Agent System
- **Research Agent**: Generates hypotheses grounded in financial theory
- **Coding Team**: Translates hypotheses into executable Python strategies
- **Evaluation Team**: Analyzes results and extracts actionable insights
- Structured reasoning enables systematic exploration of high-dimensional strategy space

### 4. Evolutionary Process
- Parent & cousin sampling for reproduction
- Feature-based selection maintaining diversity
- Insight accumulation and curation every 50 generations
- Migration between islands every 10 generations

## Installation

```bash
# Clone repository
git clone <repository-url>
cd QuantEvolve

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenRouter API key
```

## Configuration

Edit `config/default_config.yaml` to customize:

- Evolution parameters (generations, islands, migration interval)
- Feature map dimensions and bins
- Strategy categories
- LLM models and parameters
- Backtesting configuration (assets, time periods, transaction costs)
- Performance metrics and weights

## Usage

### Basic Usage

```python
from src.main import QuantEvolve
from src.utils.config_loader import load_config

# Load configuration
config = load_config()

# Initialize QuantEvolve
qe = QuantEvolve(config)

# Run evolution
qe.run(num_generations=150)

# Get best strategies
best_strategies = qe.get_best_strategies(n=10)
```

### Command Line

```bash
# Run evolution with default config
python -m src.main

# Run with custom config
python -m src.main --config path/to/config.yaml

# Resume from checkpoint
python -m src.main --resume results/checkpoint_gen_50

# Visualize results
python -m src.visualization.plot_results --results results/run_001
```

## Data Preparation

QuantEvolve works with daily OHLCV data in CSV or Parquet format:

```python
# Example: Prepare equity data
from src.utils.data_prep import prepare_equity_data

assets = ["AAPL", "NVDA", "AMZN", "GOOGL", "MSFT", "TSLA"]
prepare_equity_data(
    assets=assets,
    start_date="2015-08-01",
    end_date="2025-07-31",
    output_dir="data/raw"
)
```

## Models

QuantEvolve uses two LLMs through OpenRouter:
- **Small Model** (Qwen3-30B-A3B-Instruct-2507): Fast responses for coding and implementation
- **Large Model** (Qwen3-Next-80B-A3B-Instruct): Thoughtful analysis for research and evaluation

## Performance Metrics

Strategies are evaluated on:
- **Sharpe Ratio**: Risk-adjusted return
- **Sortino Ratio**: Downside risk-adjusted return
- **Information Ratio**: Benchmark-relative performance
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Total Return**: Cumulative return
- **Trading Frequency**: Number of trades per period

Combined Score: `SR + IR + MDD` (where MDD is negative)

## Results

QuantEvolve generates:
- Diverse strategies across the feature map
- Evolution visualizations (feature map projections, performance over time)
- Detailed strategy reports (hypothesis, code, metrics, analysis)
- Curated insights from the evolutionary process
- Checkpoints for resuming evolution

## Paper Results

From the original paper (equity markets):

| Model | Sharpe Ratio | Max Drawdown | Information Ratio | Cumulative Return |
|-------|--------------|--------------|-------------------|-------------------|
| MarketCap | 0.99 | -33% | - | 99% |
| Equal | 1.07 | -36% | 0.80 | 129% |
| Risk Parity | 1.22 | -29% | 0.44 | 130% |
| **QuantEvolve Gen 150** | **1.52** | **-32%** | **0.69** | **256%** |

## Citation

```bibtex
@article{yun2025quantevolve,
  title={QuantEvolve: Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework},
  author={Yun, Junhyeog and Lee, Hyoun Jun and Jeon, Insu},
  journal={arXiv preprint arXiv:2510.18569},
  year={2025}
}
```

## License

This implementation is for research purposes only. See paper for full disclaimer.

## Contributing

Contributions welcome! Please open an issue or pull request.

## Acknowledgments

- Original paper by Qraft Technologies AI Tech Lab
- Built on Zipline (backtesting) and QuantStats (analysis)
- Powered by Qwen models via OpenRouter
