"""
Basic functionality test - doesn't require LLM calls
Tests all core components
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("QuantEvolve - Basic Functionality Test")
print("=" * 80)
print()

# Test 1: Configuration
print("Test 1: Configuration System")
try:
    from utils.config_loader import load_config
    config = load_config()
    print(f"  ✓ Config loaded")
    print(f"    - Generations: {config.get('evolution.num_generations')}")
    print(f"    - Islands: {config.get('evolution.num_islands')}")
    print(f"    - Feature dimensions: {len(config.get('feature_map.dimensions'))}")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Test 2: Logging
print("\nTest 2: Logging System")
try:
    from utils.logger import setup_logger, get_logger
    setup_logger(log_dir='./logs', level='INFO')
    logger = get_logger()
    logger.info("Test log message")
    print("  ✓ Logger configured")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Test 3: Feature Map
print("\nTest 3: Feature Map")
try:
    from core.feature_map import create_feature_map_from_config, Strategy
    import numpy as np

    feature_map = create_feature_map_from_config(config.raw)
    print(f"  ✓ Feature map created")
    print(f"    - Shape: {feature_map.archive.shape}")
    print(f"    - Total cells: {np.prod(feature_map.archive.shape)}")

    # Add a test strategy
    strategy = Strategy(
        hypothesis="Test strategy",
        code="# test code",
        metrics={
            'sharpe_ratio': 1.5,
            'sortino_ratio': 1.8,
            'information_ratio': 0.7,
            'total_return': 150.0,
            'max_drawdown': -25.0,
            'trading_frequency': 100,
            'strategy_category_bin': 1
        },
        analysis="Test analysis",
        generation=0,
        island_id=0
    )

    added = feature_map.add(strategy)
    print(f"  ✓ Test strategy added: {added}")
    print(f"    - Combined score: {strategy.combined_score:.3f}")

    stats = feature_map.get_statistics()
    print(f"  ✓ Statistics: {stats['num_strategies']} strategies, {stats['coverage']*100:.4f}% coverage")

except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Evolutionary Database
print("\nTest 4: Evolutionary Database")
try:
    from core.evolutionary_database import EvolutionaryDatabase

    categories = config.get('strategy_categories', [])
    evol_db = EvolutionaryDatabase(
        feature_map=feature_map,
        num_islands=len(categories) + 1,
        categories=categories
    )
    print(f"  ✓ Evolutionary DB created")
    print(f"    - Islands: {len(evol_db.islands)}")
    print(f"    - Categories: {len(categories)}")

    # Initialize with seed strategies
    seed_strategies = []
    for i in range(len(categories) + 1):
        seed = Strategy(
            hypothesis=f"Seed strategy {i}",
            code=f"# Seed code {i}",
            metrics={
                'sharpe_ratio': np.random.uniform(0.5, 2.0),
                'sortino_ratio': np.random.uniform(0.5, 2.0),
                'information_ratio': np.random.uniform(-0.5, 1.0),
                'total_return': np.random.uniform(0, 200),
                'max_drawdown': -np.random.uniform(10, 40),
                'trading_frequency': np.random.randint(10, 500),
                'strategy_category_bin': 1 << i
            },
            analysis=f"Seed analysis {i}",
            generation=0,
            island_id=i
        )
        seed_strategies.append(seed)

    evol_db.initialize_islands(seed_strategies)
    print(f"  ✓ Islands initialized with {len(seed_strategies)} seeds")

    # Test parent sampling
    parent = evol_db.sample_parent(island_id=0, alpha=0.5)
    if parent:
        print(f"  ✓ Parent sampled: {parent.strategy_id}")

        # Test cousin sampling
        cousins = evol_db.sample_cousins(parent, island_id=0)
        print(f"  ✓ Cousins sampled: {len(cousins)}")

    db_stats = evol_db.get_statistics()
    print(f"  ✓ DB Statistics: {db_stats['total_strategies']} strategies")

except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Data Preparation
print("\nTest 5: Data Preparation")
try:
    from utils.data_prep import create_sample_data, verify_data

    # Create sample data
    create_sample_data(output_dir='./data/raw', days=100)
    print("  ✓ Sample data created")

    # Verify data
    assets = ['AAPL', 'NVDA', 'AMZN']
    verified = verify_data('./data/raw', assets)
    print(f"  ✓ Data verified: {verified}")

except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Backtesting Engine
print("\nTest 6: Simple Backtesting Engine")
try:
    from backtesting.simple_backtest import SimpleBacktestEngine

    engine = SimpleBacktestEngine(data_dir='./data/raw')
    print("  ✓ Backtest engine created")

    # Test with simple strategy code
    simple_strategy = """
import pandas as pd
import numpy as np

def generate_signals(data):
    # Simple moving average crossover
    short_ma = data['close'].rolling(10).mean()
    long_ma = data['close'].rolling(30).mean()

    # Signal: 1 when short > long, 0 otherwise
    signals = (short_ma > long_ma).astype(int)

    return signals
"""

    metrics = engine.run_backtest(simple_strategy)
    print("  ✓ Backtest executed")
    print(f"    - Sharpe: {metrics['sharpe_ratio']:.3f}")
    print(f"    - Return: {metrics['total_return']:.2f}%")
    print(f"    - MDD: {metrics['max_drawdown']:.2f}%")

except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Agent Prompts
print("\nTest 7: Agent Prompts")
try:
    from agents import prompts

    print("  ✓ Data Agent prompts loaded")
    print("  ✓ Research Agent prompts loaded")
    print("  ✓ Coding Team prompts loaded")
    print("  ✓ Evaluation Team prompts loaded")

    # Test formatting functions
    test_insights = [
        {'generation': 1, 'content': 'Test insight 1'},
        {'generation': 2, 'content': 'Test insight 2'}
    ]
    formatted = prompts.format_insights(test_insights)
    print(f"  ✓ Insight formatting works ({len(formatted)} chars)")

except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("All Basic Tests Passed! ✓")
print("=" * 80)
print("\nCore components are working correctly:")
print("  ✓ Configuration system")
print("  ✓ Logging infrastructure")
print("  ✓ Feature map (MAP-Elites)")
print("  ✓ Evolutionary database (island model)")
print("  ✓ Parent/cousin sampling")
print("  ✓ Data preparation")
print("  ✓ Backtesting engine")
print("  ✓ Agent prompts")
print("\nReady for LLM-powered evolution!")
print("\nNext steps:")
print("  1. Test LLM connection: python3 test_llm_connection.py")
print("  2. Run quick test: python3 run_quick_test.py")
print("  3. Run full evolution: python3 -m src.main --sample-data")
