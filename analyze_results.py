"""
Analyze QuantEvolve results and extract actionable strategies
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.evolutionary_database import EvolutionaryDatabase
from core.feature_map import Strategy
import pickle

print("=" * 80)
print("QuantEvolve - Results Analysis")
print("=" * 80)
print()

# Load results
print("Loading results from results/final/...")
db = EvolutionaryDatabase.load('results/final')

print(f"✓ Loaded database with {db.current_generation} generations")
print()

# Get statistics
stats = db.get_statistics()

print("=" * 80)
print("Overall Statistics")
print("=" * 80)
print(f"Total Strategies Generated: {stats['total_strategies']}")
print(f"Strategies on Feature Map: {stats['total_on_map']}")
print(f"Rejected Strategies: {stats['total_rejected']}")
print(f"Insights Collected: {stats['num_insights']}")
print(f"Feature Map Coverage: {stats['feature_map']['coverage']*100:.4f}%")
print()

if stats['feature_map']['num_strategies'] > 0:
    print(f"Performance Metrics:")
    print(f"  Mean Score: {stats['feature_map']['mean_score']:.3f}")
    print(f"  Max Score: {stats['feature_map']['max_score']:.3f}")
    print(f"  Min Score: {stats['feature_map']['min_score']:.3f}")
    print(f"  Std Score: {stats['feature_map']['std_score']:.3f}")
print()

# Island statistics
print("=" * 80)
print("Island Performance")
print("=" * 80)
for island_stat in stats['islands']:
    print(f"\nIsland {island_stat['id']}: {island_stat['category']}")
    print(f"  Population: {island_stat['population_size']}")
    print(f"  On Map: {island_stat['map_size']}")
    if 'mean_score' in island_stat:
        print(f"  Mean Score: {island_stat['mean_score']:.3f}")
        print(f"  Max Score: {island_stat['max_score']:.3f}")
        print(f"  Best Strategy: {island_stat.get('best_strategy_id', 'N/A')}")

print()

# Get all strategies
all_strategies = db.feature_map.get_all_strategies()
print("=" * 80)
print(f"Top 10 Strategies (by Combined Score)")
print("=" * 80)

# Sort by score
all_strategies.sort(key=lambda s: s.combined_score, reverse=True)

for i, strategy in enumerate(all_strategies[:10], 1):
    print(f"\n{i}. Strategy {strategy.strategy_id}")
    print(f"   Generation: {strategy.generation}, Island: {strategy.island_id} ({db.islands[strategy.island_id].category})")
    print(f"   Combined Score: {strategy.combined_score:.3f}")
    print(f"   Metrics:")
    print(f"     - Sharpe Ratio: {strategy.metrics['sharpe_ratio']:.3f}")
    print(f"     - Sortino Ratio: {strategy.metrics['sortino_ratio']:.3f}")
    print(f"     - Information Ratio: {strategy.metrics['information_ratio']:.3f}")
    print(f"     - Total Return: {strategy.metrics['total_return']:.2f}%")
    print(f"     - Max Drawdown: {strategy.metrics['max_drawdown']:.2f}%")
    print(f"     - Trading Frequency: {strategy.metrics['trading_frequency']}")
    print(f"   Hypothesis (first 200 chars):")
    print(f"     {strategy.hypothesis[:200]}...")

print()

# Analyze by category
print("=" * 80)
print("Strategies by Category")
print("=" * 80)

from collections import defaultdict
by_category = defaultdict(list)

for strategy in all_strategies:
    island = db.islands[strategy.island_id]
    by_category[island.category].append(strategy)

for category, strategies in sorted(by_category.items()):
    print(f"\n{category}: {len(strategies)} strategies")
    if strategies:
        avg_score = sum(s.combined_score for s in strategies) / len(strategies)
        best = max(strategies, key=lambda s: s.combined_score)
        print(f"  Average Score: {avg_score:.3f}")
        print(f"  Best Score: {best.combined_score:.3f}")
        print(f"  Best Strategy: {best.strategy_id}")

print()

# Insights analysis
print("=" * 80)
print(f"Insights Collected ({len(db.insights)})")
print("=" * 80)

if db.insights:
    print("\nTop 10 Recent Insights:")
    for i, insight in enumerate(db.insights[:10], 1):
        content = insight.get('content', insight.get('insight', ''))
        gen = insight.get('generation', 'N/A')
        print(f"{i}. [Gen {gen}] {content[:150]}...")
else:
    print("No insights collected yet.")

print()

# Save detailed analysis
print("=" * 80)
print("Detailed Strategy Analysis")
print("=" * 80)

# Pick top 3 strategies for detailed view
print("\nTop 3 Strategies - Full Details:\n")

for i, strategy in enumerate(all_strategies[:3], 1):
    print(f"\n{'='*80}")
    print(f"Strategy #{i}: {strategy.strategy_id}")
    print(f"{'='*80}")

    print(f"\nMetadata:")
    print(f"  Generation: {strategy.generation}")
    print(f"  Island: {strategy.island_id} ({db.islands[strategy.island_id].category})")
    print(f"  Combined Score: {strategy.combined_score:.3f}")

    print(f"\nHypothesis:")
    print(f"  {strategy.hypothesis}")

    print(f"\nPerformance Metrics:")
    for metric, value in strategy.metrics.items():
        if metric != 'strategy_category_bin':
            if isinstance(value, float):
                print(f"  {metric}: {value:.3f}")
            else:
                print(f"  {metric}: {value}")

    print(f"\nStrategy Code:")
    code_lines = strategy.code.split('\n')
    print("  " + "\n  ".join(code_lines[:20]))
    if len(code_lines) > 20:
        remaining = len(code_lines) - 20
        print(f"  ... ({remaining} more lines)")

    print(f"\nAnalysis:")
    print(f"  {strategy.analysis[:300]}...")

print()
print("=" * 80)
print("Analysis Complete!")
print("=" * 80)
print()
print("Results saved in: results/final/")
print("Feature map: results/final/feature_map.pkl")
print("Database: results/final/evolutionary_database.pkl")
print()
print("To use these strategies:")
print("  1. Review the hypotheses and code above")
print("  2. Test on historical data with proper backtesting")
print("  3. Implement risk management and position sizing")
print("  4. Paper trade before live deployment")
print("  5. Monitor performance and adapt")
