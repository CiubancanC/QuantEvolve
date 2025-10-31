#!/usr/bin/env python3
"""
Analyze a specific strategy from the evolutionary database
"""
import pickle
from pathlib import Path


def load_database():
    """Load evolutionary database"""
    db_path = Path("results/final/evolutionary_database.pkl")
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return None

    with open(db_path, 'rb') as f:
        db = pickle.load(f)

    return db


def find_strategy_by_id(db, strategy_id):
    """Find strategy by ID in database"""
    # Search through all islands
    for island_idx, island in enumerate(db.islands):
        for strategy in island.population:
            if strategy.strategy_id == strategy_id:
                return island_idx, strategy
    return None, None


def main():
    # Load database
    db = load_database()
    if db is None:
        return

    print(f"Loaded database with {len(db.islands)} islands")
    total_strats = sum(len(island.population) for island in db.islands)
    print(f"Total strategies: {total_strats}")
    print()

    # Find the top strategy from the logs
    strategy_id = "strat_952556673"

    island_idx, strategy = find_strategy_by_id(db, strategy_id)

    if strategy is None:
        print(f"Strategy {strategy_id} not found")
        # List all strategies
        print("\nAvailable strategies:")
        for island_idx, island in enumerate(db.islands):
            print(f"\nIsland {island_idx} ({island.category}):")
            for s in island.population[:5]:  # Show first 5
                print(f"  {s.strategy_id}: score={s.combined_score:.3f}, sharpe={s.metrics.get('sharpe_ratio', 0):.3f}")
        return

    print(f"Found strategy {strategy_id} in Island {island_idx}")
    print(f"Category: {db.islands[island_idx].category}")
    print(f"Generation: {strategy.generation}")
    print(f"Score: {strategy.combined_score:.3f}")
    print()

    print("="*80)
    print("HYPOTHESIS")
    print("="*80)
    print(strategy.hypothesis)
    print()

    print("="*80)
    print("METRICS")
    print("="*80)
    for key, value in strategy.metrics.items():
        print(f"{key:25s}: {value}")
    print()

    print("="*80)
    print("CODE")
    print("="*80)
    print(strategy.code)
    print()

    if strategy.analysis:
        print("="*80)
        print("ANALYSIS")
        print("="*80)
        print(strategy.analysis)
        print()

    # Note: insights may not be an attribute of Strategy
    if hasattr(strategy, 'insights') and strategy.insights:
        print("="*80)
        print("INSIGHTS")
        print("="*80)
        for insight in strategy.insights:
            print(f"- {insight}")
        print()


if __name__ == "__main__":
    main()
