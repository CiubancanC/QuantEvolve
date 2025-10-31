"""
Quick test script for QuantEvolve
Runs a short evolution (5 generations) with sample data
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.config_loader import load_config
from utils.logger import setup_logger
from main import QuantEvolve


def main():
    print("=" * 80)
    print("QuantEvolve - Quick Test (5 Generations)")
    print("=" * 80)
    print()

    # Load config
    print("Loading configuration...")
    config = load_config()

    # Setup logging
    print("Setting up logger...")
    setup_logger(
        log_dir='./logs',
        level='INFO'
    )

    # Create QuantEvolve instance with sample data
    print("Initializing QuantEvolve...")
    qe = QuantEvolve(config, use_sample_data=True)

    # Initialize
    print("Initializing with data analysis...")
    assets = ['AAPL', 'NVDA', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
    qe.initialize(
        data_dir='./data/raw',
        assets=assets,
        asset_type='equities'
    )

    # Run short evolution
    print("\nRunning evolution (5 generations)...")
    print("This will take several minutes due to LLM calls...")
    print()

    qe.run(num_generations=5)

    # Show results
    print("\n" + "=" * 80)
    print("Results Summary")
    print("=" * 80)

    stats = qe.evol_db.get_statistics()
    print(f"\nTotal Strategies Generated: {stats['total_strategies']}")
    print(f"Strategies on Feature Map: {stats['total_on_map']}")
    print(f"Feature Map Coverage: {stats['feature_map']['coverage']*100:.2f}%")
    print(f"Total Insights: {stats['num_insights']}")

    print(f"\nBest Score: {stats['feature_map'].get('max_score', 0):.3f}")
    print(f"Mean Score: {stats['feature_map'].get('mean_score', 0):.3f}")

    # Show best strategies
    print("\n" + "=" * 80)
    print("Top 5 Strategies")
    print("=" * 80)

    best = qe.get_best_strategies(5)
    for i, strategy in enumerate(best, 1):
        print(f"\n{i}. Strategy {strategy.strategy_id}")
        print(f"   Generation: {strategy.generation}")
        print(f"   Island: {strategy.island_id}")
        print(f"   Combined Score: {strategy.combined_score:.3f}")
        print(f"   Sharpe Ratio: {strategy.metrics.get('sharpe_ratio', 0):.3f}")
        print(f"   Total Return: {strategy.metrics.get('total_return', 0):.2f}%")
        print(f"   Max Drawdown: {strategy.metrics.get('max_drawdown', 0):.2f}%")
        print(f"   Trading Freq: {strategy.metrics.get('trading_frequency', 0)}")

    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)
    print("\nTo run full evolution (150 generations):")
    print("  python -m src.main --sample-data")
    print("\nResults saved to: ./results/")
    print("Logs saved to: ./logs/")


if __name__ == "__main__":
    main()
