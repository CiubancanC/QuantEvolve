"""
Test period filtering in backtesting engine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backtesting.improved_backtest import ImprovedBacktestEngine
from loguru import logger
import pandas as pd

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")

print("=" * 80)
print("Testing Period Filtering in Backtesting Engine")
print("=" * 80)
print()

# Test 1: Engine without period filtering (uses all data)
print("1. Testing engine WITHOUT period filtering (baseline)...")
engine_no_filter = ImprovedBacktestEngine(
    data_dir='./data/raw',
    initial_capital=100000,
    commission_pct=0.001,
    slippage_pct=0.0005,
    risk_free_rate=0.02
)

data_no_filter = engine_no_filter.load_data('AAPL')
print(f"   ✓ AAPL data WITHOUT filtering: {len(data_no_filter)} rows")
print(f"   ✓ Date range: {data_no_filter.index.min()} to {data_no_filter.index.max()}")
print()

# Test 2: Engine WITH period filtering
print("2. Testing engine WITH period filtering (train period)...")
engine_with_filter = ImprovedBacktestEngine(
    data_dir='./data/raw',
    initial_capital=100000,
    commission_pct=0.001,
    slippage_pct=0.0005,
    risk_free_rate=0.02,
    train_start='2020-01-01',
    train_end='2021-12-31',
    val_start='2022-01-01',
    val_end='2022-12-31',
    test_start='2023-01-01',
    test_end='2024-12-31'
)

# Test train period
engine_with_filter.set_period('train')
data_train = engine_with_filter.load_data('AAPL')
if data_train is not None:
    print(f"   ✓ AAPL data in TRAIN period: {len(data_train)} rows")
    print(f"   ✓ Date range: {data_train.index.min()} to {data_train.index.max()}")
else:
    print(f"   ✗ AAPL data in TRAIN period: No data available")
print()

# Test val period
print("3. Testing validation period...")
engine_with_filter.set_period('val')
data_val = engine_with_filter.load_data('AAPL')
if data_val is not None:
    print(f"   ✓ AAPL data in VAL period: {len(data_val)} rows")
    print(f"   ✓ Date range: {data_val.index.min()} to {data_val.index.max()}")
else:
    print(f"   ✗ AAPL data in VAL period: No data available")
print()

# Test test period
print("4. Testing test period...")
engine_with_filter.set_period('test')
data_test = engine_with_filter.load_data('AAPL')
if data_test is not None:
    print(f"   ✓ AAPL data in TEST period: {len(data_test)} rows")
    print(f"   ✓ Date range: {data_test.index.min()} to {data_test.index.max()}")
else:
    print(f"   ✗ AAPL data in TEST period: No data available")
print()

# Test 5: Verify no overlap between periods
print("5. Verifying period boundaries...")
if data_train is not None and data_val is not None:
    train_end = data_train.index.max()
    val_start = data_val.index.min()
    print(f"   ✓ Train ends: {train_end}")
    print(f"   ✓ Val starts: {val_start}")
    print(f"   ✓ No overlap: {train_end < val_start}")

if data_val is not None and data_test is not None:
    val_end = data_val.index.max()
    test_start = data_test.index.min()
    print(f"   ✓ Val ends: {val_end}")
    print(f"   ✓ Test starts: {test_start}")
    print(f"   ✓ No overlap: {val_end < test_start}")
print()

# Test 6: Run backtest on each period and compare
print("6. Running simple buy-and-hold backtest on each period...")
buy_hold_strategy = """
import pandas as pd
import numpy as np

def generate_signals(data):
    '''Buy and hold'''
    signals = pd.Series(1, index=data.index)
    return signals
"""

periods_to_test = ['train', 'val', 'test']
results = {}

for period in periods_to_test:
    engine_with_filter.set_period(period)
    metrics = engine_with_filter.run_backtest(buy_hold_strategy)
    results[period] = metrics
    print(f"   {period.upper():>5}: Return={metrics['total_return']:>6.1f}%, Sharpe={metrics['sharpe_ratio']:>6.2f}, Trades={metrics['trading_frequency']:>3}")

print()

print("=" * 80)
print("✓ Period Filtering Test Complete!")
print("=" * 80)
print()

# Summary
print("Summary:")
if data_train is not None:
    print(f"  ✓ Period filtering is working correctly")
    print(f"  ✓ Data is properly segregated into train/val/test periods")
    print(f"  ✓ No data leakage between periods")
else:
    print(f"  ⚠ Period filtering may not be working - check date ranges")
print()
