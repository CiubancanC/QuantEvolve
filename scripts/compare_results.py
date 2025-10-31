#!/usr/bin/env python3
"""
Compare results from sample data vs real data training runs.

This script loads and compares the evolutionary results from two different
training runs to see how the system performs on synthetic vs real market data.

Usage:
    python scripts/compare_results.py
"""

import pickle
import sys
from pathlib import Path
from typing import Dict, Any


def load_results(results_dir: str) -> Dict[str, Any]:
    """Load evolutionary database from pickle file."""
    pkl_path = Path(results_dir) / "evolutionary_database.pkl"

    if not pkl_path.exists():
        print(f"Error: {pkl_path} not found")
        return None

    with open(pkl_path, 'rb') as f:
        db = pickle.load(f)

    return db


def analyze_database(db: Any, name: str):
    """Analyze and print statistics for an evolutionary database."""
    print(f"\n{'='*70}")
    print(f"{name.upper()} RESULTS")
    print(f"{'='*70}")

    # Basic statistics
    total_strategies = len(db.all_strategies)
    feature_map_size = len(db.feature_map.cells)
    occupied_cells = sum(1 for cell in db.feature_map.cells.values() if cell['strategy'] is not None)
    total_insights = len(db.insights)

    print(f"\nOverall Statistics:")
    print(f"  Total Strategies Generated: {total_strategies}")
    print(f"  Feature Map Occupied Cells: {occupied_cells:,}")
    print(f"  Feature Map Coverage: {occupied_cells/feature_map_size*100:.4f}%")
    print(f"  Total Insights Collected: {total_insights}")

    # Find best strategies
    if db.all_strategies:
        strategies_with_scores = [
            (s, s.get('metrics', {}).get('combined_score', float('-inf')))
            for s in db.all_strategies.values()
            if s.get('metrics', {}).get('combined_score') is not None
        ]

        if strategies_with_scores:
            strategies_with_scores.sort(key=lambda x: x[1], reverse=True)

            print(f"\nTop 5 Strategies:")
            for i, (strategy, score) in enumerate(strategies_with_scores[:5], 1):
                metrics = strategy.get('metrics', {})
                print(f"\n  #{i} - {strategy.get('strategy_id', 'Unknown')}")
                print(f"      Combined Score: {score:.3f}")
                print(f"      Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
                print(f"      Information Ratio: {metrics.get('information_ratio', 0):.3f}")
                print(f"      Sortino Ratio: {metrics.get('sortino_ratio', 0):.3f}")
                print(f"      Total Return: {metrics.get('total_return', 0)*100:.2f}%")
                print(f"      Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%")
                print(f"      Trading Freq: {metrics.get('trading_frequency', 0):.0f} trades")
                print(f"      Generation: {strategy.get('generation', 'N/A')}")
                print(f"      Island: {strategy.get('island_id', 'N/A')}")

    # Island statistics
    print(f"\nIsland Statistics:")
    for island_id, island in db.islands.items():
        strategies_count = len(island['strategies'])
        print(f"  Island {island_id}: {strategies_count} strategies")

    return {
        'total_strategies': total_strategies,
        'occupied_cells': occupied_cells,
        'coverage': occupied_cells/feature_map_size*100,
        'total_insights': total_insights,
        'best_score': strategies_with_scores[0][1] if strategies_with_scores else 0,
        'best_sharpe': strategies_with_scores[0][0].get('metrics', {}).get('sharpe_ratio', 0) if strategies_with_scores else 0,
        'best_ir': strategies_with_scores[0][0].get('metrics', {}).get('information_ratio', 0) if strategies_with_scores else 0,
        'best_return': strategies_with_scores[0][0].get('metrics', {}).get('total_return', 0) if strategies_with_scores else 0,
    }


def compare_results(sample_stats: Dict, real_stats: Dict):
    """Print comparison between sample and real data results."""
    print(f"\n{'='*70}")
    print("COMPARISON: SAMPLE DATA vs REAL DATA")
    print(f"{'='*70}")

    print(f"\nMetric                          Sample Data    Real Data      Difference")
    print(f"{'-'*70}")

    metrics = [
        ('Total Strategies', 'total_strategies', ''),
        ('Feature Map Coverage', 'coverage', '%'),
        ('Total Insights', 'total_insights', ''),
        ('Best Combined Score', 'best_score', ''),
        ('Best Sharpe Ratio', 'best_sharpe', ''),
        ('Best Information Ratio', 'best_ir', ''),
        ('Best Total Return', 'best_return', '%'),
    ]

    for name, key, unit in metrics:
        sample_val = sample_stats[key]
        real_val = real_stats[key]

        if unit == '%':
            if 'return' in key.lower():
                sample_val *= 100
                real_val *= 100
            diff = real_val - sample_val
            print(f"{name:30s} {sample_val:10.2f}{unit}  {real_val:10.2f}{unit}  {diff:+10.2f}{unit}")
        else:
            diff = real_val - sample_val
            print(f"{name:30s} {sample_val:10.2f}{unit}  {real_val:10.2f}{unit}  {diff:+10.2f}{unit}")

    print(f"\n{'='*70}")
    print("KEY INSIGHTS:")
    print(f"{'='*70}")

    # Performance comparison
    if real_stats['best_score'] > sample_stats['best_score']:
        print("✓ Real data produced BETTER overall performance")
    elif real_stats['best_score'] < sample_stats['best_score']:
        print("⚠ Sample data produced BETTER overall performance")
        print("  This may indicate overfitting or easier synthetic patterns")
    else:
        print("= Similar performance on both datasets")

    # Diversity comparison
    if real_stats['coverage'] > sample_stats['coverage']:
        print("✓ Real data led to MORE diverse strategies")
    else:
        print("⚠ Sample data led to MORE diverse strategies")

    # Risk-adjusted returns
    if real_stats['best_sharpe'] > sample_stats['best_sharpe']:
        print("✓ Real data achieved BETTER risk-adjusted returns (Sharpe)")
    else:
        print("⚠ Sample data achieved BETTER risk-adjusted returns (Sharpe)")

    # Information ratio (vs benchmark)
    if real_stats['best_ir'] > sample_stats['best_ir']:
        print("✓ Real data achieved BETTER performance vs benchmark (IR)")
    else:
        print("⚠ Sample data achieved BETTER performance vs benchmark (IR)")


def main():
    print(f"\n{'='*70}")
    print("QUANTEVOLVE: SAMPLE vs REAL DATA COMPARISON")
    print(f"{'='*70}")

    # Load sample data results
    sample_db = load_results("results/final_sample_data_backup")
    if sample_db is None:
        print("Error: Could not load sample data results")
        sys.exit(1)

    # Load real data results
    real_db = load_results("results/final")
    if real_db is None:
        print("Error: Could not load real data results")
        print("Make sure the real data training run has completed.")
        sys.exit(1)

    # Analyze both
    sample_stats = analyze_database(sample_db, "Sample Data")
    real_stats = analyze_database(real_db, "Real Data")

    # Compare
    compare_results(sample_stats, real_stats)

    print(f"\n{'='*70}")
    print("Analysis complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
