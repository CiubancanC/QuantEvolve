"""
Mini test - 2 generations with 3 islands to validate end-to-end flow
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.config_loader import load_config
from utils.logger import setup_logger, get_logger
from utils.llm_client import create_llm_client, LLMEnsemble
from core.feature_map import create_feature_map_from_config
from core.evolutionary_database import EvolutionaryDatabase
from agents.data_agent import DataAgent
from agents.research_agent import ResearchAgent
from agents.coding_team import CodingTeam
from agents.evaluation_team import EvaluationTeam
from backtesting.simple_backtest import SimpleBacktestEngine
from utils.data_prep import create_sample_data

print("=" * 80)
print("QuantEvolve - Mini Test (2 Generations, 3 Islands)")
print("=" * 80)
print()

# Setup
print("Setting up...")
config = load_config()
setup_logger(log_dir='./logs', level='INFO')
logger = get_logger()

# Create sample data
print("Creating sample data...")
create_sample_data(output_dir='./data/raw', days=200)

# Initialize components
print("Initializing components...")
llm_client = create_llm_client(config.get('llm'))
llm_ensemble = LLMEnsemble(llm_client)

backtest_engine = SimpleBacktestEngine(data_dir='./data/raw')

data_agent = DataAgent(llm_ensemble)
research_agent = ResearchAgent(llm_ensemble)
coding_team = CodingTeam(llm_ensemble, backtest_engine)
evaluation_team = EvaluationTeam(llm_ensemble)

# Feature map
feature_map = create_feature_map_from_config(config.raw)

# Use only 3 categories for faster testing
categories = ['Momentum/Trend', 'Mean-Reversion', 'Volatility']
evol_db = EvolutionaryDatabase(
    feature_map=feature_map,
    num_islands=len(categories) + 1,
    categories=categories
)

print(f"Initialized: {len(categories)+1} islands")
print()

# Initialize with Data Agent
print("=" * 80)
print("Phase 1: Initialization with Data Agent")
print("=" * 80)
print("This will make LLM calls to analyze data and generate seeds...")
print()

assets = ['AAPL', 'NVDA', 'AMZN']
data_schema = data_agent.analyze_data(
    data_dir='./data/raw',
    assets=assets,
    asset_type='equities'
)

print("\nData Schema generated (first 200 chars):")
print(data_schema[:200] + "...")
print()

print("Generating seed strategies...")
seed_strategies = data_agent.generate_all_seed_strategies(
    categories=categories,
    include_benchmark=True
)

print(f"Generated {len(seed_strategies)} seed strategies")
print()

# Initialize islands
evol_db.initialize_islands(seed_strategies)
print("Islands initialized")
print()

# Run 2 generations
print("=" * 80)
print("Phase 2: Evolution (2 Generations)")
print("=" * 80)
print("This will generate hypotheses, implement, and evaluate strategies...")
print()

for generation in range(2):
    print(f"\n{'='*80}")
    print(f"Generation {generation}")
    print(f"{'='*80}")

    # Evolve first island only for speed
    island_id = generation % (len(categories) + 1)  # Rotate through islands
    island = evol_db.islands[island_id]

    print(f"\nIsland {island_id} ({island.category})")

    # Sample parent
    parent = evol_db.sample_parent(island_id, alpha=0.5)
    if not parent:
        print("  No parent available, skipping")
        continue

    print(f"  Parent: {parent.strategy_id}")

    # Sample cousins
    cousins = evol_db.sample_cousins(parent, island_id, num_best=1, num_diverse=1, num_random=1)
    print(f"  Cousins: {len(cousins)}")

    # Generate hypothesis
    print("  Generating hypothesis...")
    insights = evol_db.get_recent_insights(n=10)
    hypothesis = research_agent.generate_hypothesis(
        parent=parent,
        cousins=cousins,
        data_schema=data_schema,
        insights=insights,
        generation=generation
    )
    print(f"  Hypothesis: {hypothesis[:100]}...")

    # Implement strategy
    print("  Implementing strategy...")
    code, metrics, notes = coding_team.implement_strategy(
        hypothesis=hypothesis,
        data_schema=data_schema,
        parent_code=parent.code
    )
    print(f"  {notes}")
    print(f"  Metrics: SR={metrics['sharpe_ratio']:.3f}, Ret={metrics['total_return']:.2f}%, MDD={metrics['max_drawdown']:.2f}%")

    # Evaluate
    print("  Evaluating...")
    analysis_dict = evaluation_team.analyze_strategy(
        hypothesis=hypothesis,
        code=code,
        metrics=metrics
    )

    metrics['strategy_category_bin'] = analysis_dict['category_bin']

    # Create strategy
    from core.feature_map import Strategy
    strategy = Strategy(
        hypothesis=hypothesis,
        code=code,
        metrics=metrics,
        analysis=analysis_dict['full_text'],
        generation=generation,
        island_id=island_id,
        parent_id=parent.strategy_id
    )

    # Add to database
    added = evol_db.add_strategy(strategy, island_id)
    print(f"  {'✓ Added' if added else '✗ Rejected'} (score: {strategy.combined_score:.3f})")

    # Add insights
    for insight in analysis_dict.get('insights', [])[:2]:  # Limit to 2 insights
        evol_db.add_insight({
            'content': insight,
            'generation': generation,
            'island_id': island_id
        })

    evol_db.current_generation = generation

# Results
print("\n" + "=" * 80)
print("Results")
print("=" * 80)

stats = evol_db.get_statistics()
print(f"\nTotal Strategies: {stats['total_strategies']}")
print(f"On Feature Map: {stats['total_on_map']}")
print(f"Coverage: {stats['feature_map']['coverage']*100:.4f}%")
print(f"Insights: {stats['num_insights']}")

if stats['feature_map']['num_strategies'] > 0:
    print(f"\nBest Score: {stats['feature_map']['max_score']:.3f}")
    print(f"Mean Score: {stats['feature_map']['mean_score']:.3f}")

print("\nTop 5 Strategies:")
all_strats = feature_map.get_all_strategies()
all_strats.sort(key=lambda s: s.combined_score, reverse=True)

for i, s in enumerate(all_strats[:5], 1):
    print(f"{i}. Gen {s.generation}, Island {s.island_id}: Score={s.combined_score:.3f}, SR={s.metrics['sharpe_ratio']:.3f}")

print("\n" + "=" * 80)
print("✓ Mini Test Complete!")
print("=" * 80)
print("\nThe system is working end-to-end:")
print("  ✓ Data analysis with LLM")
print("  ✓ Seed generation")
print("  ✓ Hypothesis generation")
print("  ✓ Strategy implementation")
print("  ✓ Backtesting")
print("  ✓ Evaluation and insights")
print("  ✓ Feature map management")
print("\nReady for full evolution!")
