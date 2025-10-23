"""
Test the improved backtesting engine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backtesting.improved_backtest import ImprovedBacktestEngine
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")

print("=" * 80)
print("Testing Improved Backtesting Engine")
print("=" * 80)
print()

# Initialize engine
print("1. Initializing improved backtest engine...")
engine = ImprovedBacktestEngine(
    data_dir='./data/raw',
    initial_capital=100000,
    commission_pct=0.001,  # 0.1%
    slippage_pct=0.0005,   # 0.05%
    risk_free_rate=0.02    # 2%
)

print(f"   ✓ Engine initialized")
print(f"   ✓ Found {len(engine.symbols)} symbols: {', '.join(engine.symbols)}")
print()

# Test loading data
print("2. Testing data loading...")
for symbol in engine.symbols[:3]:  # Test first 3
    data = engine.load_data(symbol)
    if data is not None:
        print(f"   ✓ {symbol}: {len(data)} rows, columns: {list(data.columns)}")
    else:
        print(f"   ✗ {symbol}: Failed to load")
print()

# Test simple momentum strategy
print("3. Testing simple momentum strategy...")
simple_strategy = """
import pandas as pd
import numpy as np

def generate_signals(data):
    '''Simple momentum strategy: buy when 20-day MA > 50-day MA'''

    # Calculate moving averages
    data['ma_20'] = data['close'].rolling(20).mean()
    data['ma_50'] = data['close'].rolling(50).mean()

    # Generate signals
    signals = pd.Series(0, index=data.index)
    signals[data['ma_20'] > data['ma_50']] = 1   # Long
    signals[data['ma_20'] < data['ma_50']] = -1  # Short

    return signals
"""

metrics = engine.run_backtest(simple_strategy)

print(f"   Results:")
print(f"   - Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
print(f"   - Sortino Ratio: {metrics['sortino_ratio']:.3f}")
print(f"   - Information Ratio: {metrics['information_ratio']:.3f}")
print(f"   - Total Return: {metrics['total_return']:.2f}%")
print(f"   - Max Drawdown: {metrics['max_drawdown']:.2f}%")
print(f"   - Trading Frequency: {metrics['trading_frequency']}")
print(f"   - Win Rate: {metrics.get('win_rate', 0):.1f}%")
print(f"   - Profit Factor: {metrics.get('profit_factor', 0):.2f}")
print()

# Test mean reversion strategy
print("4. Testing mean reversion strategy...")
mean_reversion_strategy = """
import pandas as pd
import numpy as np

def generate_signals(data):
    '''Mean reversion: buy oversold, sell overbought'''

    # Calculate z-score
    returns = data['close'].pct_change()
    mean_return = returns.rolling(20).mean()
    std_return = returns.rolling(20).std()
    z_score = (returns - mean_return) / std_return

    # Generate signals
    signals = pd.Series(0, index=data.index)
    signals[z_score < -2.0] = 1   # Buy oversold
    signals[z_score > 2.0] = -1   # Sell overbought

    return signals
"""

metrics2 = engine.run_backtest(mean_reversion_strategy)

print(f"   Results:")
print(f"   - Sharpe Ratio: {metrics2['sharpe_ratio']:.3f}")
print(f"   - Sortino Ratio: {metrics2['sortino_ratio']:.3f}")
print(f"   - Information Ratio: {metrics2['information_ratio']:.3f}")
print(f"   - Total Return: {metrics2['total_return']:.2f}%")
print(f"   - Max Drawdown: {metrics2['max_drawdown']:.2f}%")
print(f"   - Trading Frequency: {metrics2['trading_frequency']}")
print(f"   - Win Rate: {metrics2.get('win_rate', 0):.1f}%")
print(f"   - Profit Factor: {metrics2.get('profit_factor', 0):.2f}")
print()

# Test buy-and-hold benchmark
print("5. Testing buy-and-hold benchmark...")
buy_hold_strategy = """
import pandas as pd
import numpy as np

def generate_signals(data):
    '''Buy and hold'''
    signals = pd.Series(1, index=data.index)  # Always long
    return signals
"""

metrics3 = engine.run_backtest(buy_hold_strategy)

print(f"   Results:")
print(f"   - Sharpe Ratio: {metrics3['sharpe_ratio']:.3f}")
print(f"   - Sortino Ratio: {metrics3['sortino_ratio']:.3f}")
print(f"   - Information Ratio: {metrics3['information_ratio']:.3f}")
print(f"   - Total Return: {metrics3['total_return']:.2f}%")
print(f"   - Max Drawdown: {metrics3['max_drawdown']:.2f}%")
print(f"   - Trading Frequency: {metrics3['trading_frequency']}")
print(f"   - Win Rate: {metrics3.get('win_rate', 0):.1f}%")
print(f"   - Profit Factor: {metrics3.get('profit_factor', 0):.2f}")
print()

# Compare strategies
print("6. Strategy Comparison:")
print("-" * 80)
print(f"{'Strategy':<25} {'Sharpe':<10} {'Return':<12} {'MaxDD':<12} {'Trades':<10}")
print("-" * 80)
print(f"{'Momentum (MA Cross)':<25} {metrics['sharpe_ratio']:>8.2f}  {metrics['total_return']:>10.1f}%  {metrics['max_drawdown']:>10.1f}%  {metrics['trading_frequency']:>8}")
print(f"{'Mean Reversion (Z-Score)':<25} {metrics2['sharpe_ratio']:>8.2f}  {metrics2['total_return']:>10.1f}%  {metrics2['max_drawdown']:>10.1f}%  {metrics2['trading_frequency']:>8}")
print(f"{'Buy and Hold':<25} {metrics3['sharpe_ratio']:>8.2f}  {metrics3['total_return']:>10.1f}%  {metrics3['max_drawdown']:>10.1f}%  {metrics3['trading_frequency']:>8}")
print("-" * 80)
print()

# Determine winner
strategies = [
    ("Momentum", metrics),
    ("Mean Reversion", metrics2),
    ("Buy and Hold", metrics3)
]

best = max(strategies, key=lambda x: x[1]['sharpe_ratio'])
print(f"✓ Best Strategy by Sharpe Ratio: {best[0]} ({best[1]['sharpe_ratio']:.2f})")
print()

print("=" * 80)
print("✓ Improved Backtesting Engine Test Complete!")
print("=" * 80)
print()
print("Next steps:")
print("  1. Run a new evolution with improved backtesting:")
print("     python3 -m src.main --sample-data --quick-test")
print()
print("  2. Or run full 150-generation evolution:")
print("     python3 -m src.main --sample-data --generations 150")
print()
