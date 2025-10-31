# QuantEvolve

**Automated Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

QuantEvolve is an evolutionary multi-agent framework for automatically discovering diverse, high-performing trading strategies. It combines quality-diversity optimization with hypothesis-driven strategy generation to systematically explore the strategy space while maintaining population diversity.

> **Based on Research**: This implementation is based on the paper ["QuantEvolve: Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework"](docs/QuantEvolve.md) by Yun et al., 2025 (arXiv:2510.18569).

---

## 🌟 Key Features

- **Multi-Agent System**: Specialized agents for research, coding, evaluation, and data analysis
- **Quality-Diversity Optimization**: Feature map maintains diverse strategies across risk profiles and trading styles
- **Hypothesis-Driven Evolution**: Generates testable hypotheses grounded in financial theory
- **Island Model**: Multiple populations evolve independently with periodic migration
- **Realistic Backtesting**: Paper-specified transaction costs (commission + volume-based slippage)
- **Automatic Trade Frequency Validation**: Rejects over-filtered strategies with insufficient trading activity
- **LLM-Powered**: Uses Qwen models for strategy generation and analysis

---

## 📖 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key (for LLM inference)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd QuantEvolve
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

4. **Prepare data** (optional - sample data included):
   ```bash
   # Place OHLCV CSV files in data/raw/
   # Format: columns [date, open, high, low, close, volume]
   # Example: data/raw/AAPL.csv
   ```

---

## ⚡ Quick Start

### Run with Sample Data (Fastest)

```bash
python -m src.main --sample-data --generations 5
```

This creates synthetic data and runs 5 generations to demonstrate the system.

### Run with Real Data

```bash
python -m src.main --config config/default_config.yaml --generations 10
```

### Analyze Results

```bash
# View overall statistics and best strategies
python scripts/analyze_results.py

# Inspect a specific strategy
python scripts/analyze_strategy.py <strategy_id>
```

---

## 🏗️ Architecture

QuantEvolve implements a multi-agent evolutionary framework with the following components:

### Core Components

1. **Feature Map** (`src/core/feature_map.py`)
   - Multi-dimensional archive organizing strategies by characteristics
   - Dimensions: Strategy Category, Sharpe Ratio, Sortino Ratio, Total Return, Max Drawdown, Trading Frequency
   - Binary encoding for strategy categories enables diverse combinations

2. **Evolutionary Database** (`src/core/evolutionary_database.py`)
   - Island model: Multiple populations evolve independently
   - Migration: Best strategies shared between islands periodically
   - Insight repository: Accumulated learnings guide future generations

3. **Multi-Agent System** (`src/agents/`)
   - **Data Agent**: Analyzes data schema and generates seed strategies
   - **Research Agent**: Generates hypothesis-driven strategy concepts
   - **Coding Team**: Implements strategies, runs backtests, debugs issues
   - **Evaluation Team**: Analyzes results, extracts insights, curates knowledge

4. **Backtesting Engine** (`src/backtesting/improved_backtest.py`)
   - Vectorized backtesting for performance
   - Realistic transaction costs:
     - Commission: $0.0075/share + $1.00 minimum per trade
     - Slippage: Quadratic function of traded volume percentage
   - Comprehensive metrics: Sharpe, Sortino, IR, MDD, Total Return, Win Rate, Profit Factor

### Evolution Process

```
Generation N:
  For each island:
    1. Sample parent (α=0.5 balance between best/diverse)
    2. Sample cousins (2 best + 3 diverse + 2 random)
    3. Research Agent → Generate hypothesis
    4. Coding Team → Implement & backtest (max 3 iterations)
    5. Evaluation Team → Analyze & extract insights
    6. Add to feature map (if better than existing in cell)

  Every 10 generations → Migration (share best strategies)
  Every 50 generations → Insight curation (consolidate learnings)
```

---

## ⚙️ Configuration

Configuration is managed via `config/default_config.yaml`. Key sections:

### Evolution Parameters

```yaml
evolution:
  num_generations: 150        # Number of evolutionary cycles
  migration_interval: 10      # Generations between island migrations
  insight_curation_interval: 50  # Generations between insight consolidation
  alpha: 0.5                  # Exploitation-exploration balance
```

### Feature Map

```yaml
feature_map:
  dimensions:
    - name: "strategy_category"
      type: "binary"
      bins: 8  # 2^8 = 256 possible category combinations
    - name: "sharpe_ratio"
      type: "continuous"
      bins: 16
      range: [-2.0, 5.0]
    # ... more dimensions
```

### LLM Models

```yaml
llm:
  small_model: "qwen/qwen3-30b-a3b-instruct-2507"  # Fast generation
  large_model: "qwen/qwen3-next-80b-a3b-instruct"  # Thoughtful analysis
  temperature: 0.7
  max_tokens: 4000
```

### Backtesting Periods

```yaml
backtesting:
  periods:
    equities:
      train_start: "2015-08-01"
      train_end: "2020-07-31"    # 5 years
      val_start: "2020-08-01"
      val_end: "2022-07-31"      # 2 years
      test_start: "2022-08-01"
      test_end: "2025-07-31"     # 3 years
```

See `config/default_config.yaml` for all available options.

---

## 📚 Usage

### Basic Usage

```python
from src.utils.config_loader import load_config
from src.main import QuantEvolve

# Load configuration
config = load_config('config/default_config.yaml')

# Initialize QuantEvolve
qe = QuantEvolve(config, use_sample_data=False)

# Initialize with data
qe.initialize(
    data_dir='./data/raw',
    assets=['AAPL', 'NVDA', 'AMZN', 'GOOGL', 'MSFT', 'TSLA'],
    asset_type='equities'
)

# Run evolution
qe.run(num_generations=20)

# Get best strategies
best_strategies = qe.get_best_strategies(n=10)
for i, strategy in enumerate(best_strategies, 1):
    print(f"{i}. Score: {strategy.combined_score:.3f}")
    print(f"   Sharpe: {strategy.metrics['sharpe_ratio']:.2f}")
    print(f"   Return: {strategy.metrics['total_return']:.1f}%")
```

### Advanced: Parameter Optimization

```python
from src.optimization import ParameterOptimizer

optimizer = ParameterOptimizer(backtest_engine)
best_code, best_metrics, report = optimizer.optimize_strategy(
    code=strategy.code,
    metrics=strategy.metrics,
    max_iterations=9
)
```

### Analyzing Results

```python
from src.core.evolutionary_database import EvolutionaryDatabase

# Load saved results
db = EvolutionaryDatabase.load('results/final')

# Get statistics
stats = db.get_statistics()
print(f"Total strategies: {stats['total_strategies']}")
print(f"Feature map coverage: {stats['feature_map']['coverage']:.1%}")

# Get best strategies
all_strategies = db.feature_map.get_all_strategies()
sorted_strategies = sorted(all_strategies,
                          key=lambda s: s.combined_score,
                          reverse=True)
```

---

## 📁 Project Structure

```
QuantEvolve/
├── config/                      # Configuration files
│   └── default_config.yaml      # Main configuration
├── data/                        # Data directory
│   ├── raw/                     # Raw OHLCV data (CSV/Parquet)
│   └── processed/               # Processed data
├── docs/                        # Documentation
│   ├── QuantEvolve.md          # Research paper
│   ├── DEVIATIONS.md           # Implementation deviations from paper
│   └── IMPROVEMENTS.md         # Enhancement history
├── examples/                    # Example scripts
│   ├── demo_current_features.py # Feature demonstration
│   ├── run_quick_test.py       # Quick 5-generation test
│   └── run_mini_test.py        # Mini test
├── logs/                        # Log files
├── results/                     # Evolution results
├── scripts/                     # Utility scripts
│   ├── analyze_results.py      # Analyze evolution results
│   └── analyze_strategy.py     # Inspect specific strategies
├── src/                         # Source code
│   ├── agents/                  # Multi-agent system
│   │   ├── data_agent.py       # Data analysis & seed generation
│   │   ├── research_agent.py   # Hypothesis generation
│   │   ├── coding_team.py      # Strategy implementation
│   │   ├── evaluation_team.py  # Analysis & insights
│   │   └── prompts.py          # LLM prompts
│   ├── backtesting/             # Backtesting engines
│   │   ├── improved_backtest.py # Vectorized backtesting
│   │   └── simple_backtest.py   # Simple baseline
│   ├── core/                    # Core framework
│   │   ├── feature_map.py      # Quality-diversity archive
│   │   └── evolutionary_database.py  # Island model & evolution
│   ├── optimization/            # Strategy optimization
│   │   └── parameter_optimizer.py    # Grid search tuning
│   ├── utils/                   # Utilities
│   │   ├── config_loader.py    # Configuration management
│   │   ├── llm_client.py       # LLM API client
│   │   ├── logger.py           # Logging setup
│   │   └── data_prep.py        # Data utilities
│   └── main.py                  # Main entry point
├── tests/                       # Unit tests
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── LICENSE                      # License file
├── README.md                    # This file
├── CONTRIBUTING.md              # Contribution guidelines
└── requirements.txt             # Python dependencies
```

---

## 📖 Documentation

- **[Research Paper](docs/QuantEvolve.md)**: Full paper describing the methodology
- **[Deviations from Paper](docs/DEVIATIONS.md)**: Implementation differences and rationale
- **[Improvements Log](docs/IMPROVEMENTS.md)**: Enhancement history and lessons learned
- **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to the project

---

## 🎯 Key Concepts

### Feature Map

A multi-dimensional archive that maintains strategy diversity. Each cell stores the best strategy for that feature combination (e.g., "high Sharpe + momentum + low drawdown").

**Benefits**:
- Prevents premature convergence to single solution
- Enables personalized strategy recommendation (match investor preferences to features)
- Improves robustness across market regimes

### Hypothesis-Driven Evolution

Unlike random mutation, strategies evolve through structured hypotheses with:
1. **Hypothesis Statement**: Testable claim about market behavior
2. **Rationale**: Why this might work (theory, observations)
3. **Objectives**: Quantitative goals
4. **Expected Insights**: What we'll learn
5. **Risks & Limitations**: Failure modes
6. **Experimentation Ideas**: Future variations

This enables systematic exploration with clear reasoning trails.

### Island Model

Multiple populations evolve independently, each starting from different strategy categories (momentum, mean-reversion, volatility, etc.). Periodic migration shares best strategies between islands, enabling hybrid strategies while maintaining diversity.

### Trade Frequency Validation

A critical safeguard against over-fitting: strategies with <10 trades/year are automatically rejected. This prevents the common failure mode where stacking too many filters produces excellent metrics on tiny sample sizes (statistically meaningless).

---

## 🧪 Testing

Run tests with:

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_improved_backtest.py -v

# With coverage
pytest --cov=src tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas for contribution:
- Additional strategy categories
- Improved backtesting features (corporate actions, alternative data)
- Visualization tools for feature maps and evolution
- Additional validation metrics
- Performance optimizations

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📚 Citation

If you use QuantEvolve in your research, please cite the original paper:

```bibtex
@article{yun2025quantevolve,
  title={QuantEvolve: Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework},
  author={Yun, Junhyeog and Lee, Hyoun Jun and Jeon, Insu},
  journal={arXiv preprint arXiv:2510.18569},
  year={2025}
}
```

---

## 🙏 Acknowledgments

- Original research by Qraft Technologies AI Tech Lab
- Inspired by AlphaEvolve and The AI Scientist frameworks
- Built with Qwen models for LLM inference

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/QuantEvolve/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/QuantEvolve/discussions)
- **Documentation**: See `docs/` directory

---

**Happy Evolving! 🚀**
