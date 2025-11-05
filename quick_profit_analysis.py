"""
Quick profit analysis for top strategies (2015-2025)
"""
import sys
sys.path.insert(0, 'src')

from core.evolutionary_database import EvolutionaryDatabase

print("=" * 80)
print("QuantEvolve - Profit Analysis (2015-2025)")
print("=" * 80)
print()

# Load results
print("Loading results from results/final/...")
db = EvolutionaryDatabase.load('results/final')
print(f"✓ Loaded database with {db.current_generation} generations")
print()

# Get all strategies
all_strategies = db.feature_map.get_all_strategies()
print(f"Total strategies on feature map: {len(all_strategies)}")
print()

# Sort by total return
all_strategies.sort(key=lambda s: s.metrics.get('total_return', 0), reverse=True)

print("=" * 80)
print("Top 20 Strategies by Total Return (2015-2025)")
print("=" * 80)
print()

for i, strategy in enumerate(all_strategies[:20], 1):
    total_return = strategy.metrics.get('total_return', 0)
    sharpe = strategy.metrics.get('sharpe_ratio', 0)
    sortino = strategy.metrics.get('sortino_ratio', 0)
    max_dd = strategy.metrics.get('max_drawdown', 0)
    num_trades = strategy.metrics.get('trading_frequency', 0)

    # Calculate approximate profit on $10,000 starting capital
    profit = 10000 * (total_return / 100)
    final_value = 10000 + profit

    print(f"{i:2d}. Strategy {strategy.strategy_id}")
    print(f"    Category: {db.islands[strategy.island_id].category}")
    print(f"    Total Return: {total_return:.2f}%")
    print(f"    Starting Capital: $10,000")
    print(f"    Final Value: ${final_value:,.2f}")
    print(f"    Profit: ${profit:,.2f}")
    print(f"    Sharpe Ratio: {sharpe:.2f}")
    print(f"    Max Drawdown: {max_dd:.2f}%")
    print(f"    Trades: {num_trades}")
    print(f"    Hypothesis: {strategy.hypothesis[:120]}...")
    print()

# Summary statistics
print("=" * 80)
print("Summary Statistics")
print("=" * 80)
print()

if all_strategies:
    returns = [s.metrics.get('total_return', 0) for s in all_strategies]
    avg_return = sum(returns) / len(returns)
    max_return = max(returns)
    min_return = min(returns)

    print(f"Average Return: {avg_return:.2f}%")
    print(f"Best Return: {max_return:.2f}%")
    print(f"Worst Return: {min_return:.2f}%")
    print()
    print(f"On $10,000 starting capital:")
    print(f"  Average Final Value: ${10000 * (1 + avg_return/100):,.2f}")
    print(f"  Best Final Value: ${10000 * (1 + max_return/100):,.2f}")
    print(f"  Worst Final Value: ${10000 * (1 + min_return/100):,.2f}")
    print()

    # Count profitable vs unprofitable
    profitable = len([r for r in returns if r > 0])
    unprofitable = len([r for r in returns if r <= 0])

    print(f"Profitable Strategies: {profitable}/{len(all_strategies)} ({100*profitable/len(all_strategies):.1f}%)")
    print(f"Unprofitable Strategies: {unprofitable}/{len(all_strategies)} ({100*unprofitable/len(all_strategies):.1f}%)")

print()
print("=" * 80)
print("Note: These returns are based on the validation period used during evolution.")
print("The actual period depends on your config (typically 2020-2022 for validation).")
print("For full 2015-2025 analysis, strategies would need to be re-backtested.")
print("=" * 80)
