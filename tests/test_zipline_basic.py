"""
Basic test to verify Zipline installation works
"""

print("Testing Zipline installation...")
print("=" * 80)

# Test 1: Import Zipline
print("\n1. Testing Zipline import...")
try:
    import zipline
    print("   ✓ Zipline imported successfully")
    print(f"   Version: {zipline.__version__}")
except ImportError as e:
    print(f"   ✗ Failed to import Zipline: {e}")
    exit(1)

# Test 2: Import Zipline API
print("\n2. Testing Zipline API imports...")
try:
    from zipline.api import (
        order_target_percent,
        record,
        symbol,
        get_datetime
    )
    print("   ✓ Zipline API imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import Zipline API: {e}")
    exit(1)

# Test 3: Import QuantStats
print("\n3. Testing QuantStats import...")
try:
    import quantstats as qs
    print("   ✓ QuantStats imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import QuantStats: {e}")
    exit(1)

# Test 4: Check Zipline TradingAlgorithm
print("\n4. Testing Zipline TradingAlgorithm...")
try:
    from zipline import TradingAlgorithm
    print("   ✓ TradingAlgorithm imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import TradingAlgorithm: {e}")
    exit(1)

# Test 5: Check data handling
print("\n5. Testing pandas_datareader...")
try:
    import pandas_datareader
    print("   ✓ pandas_datareader available")
except ImportError:
    print("   ! pandas_datareader not installed (optional)")

print("\n" + "=" * 80)
print("✓ All Zipline components installed and working!")
print("=" * 80)
print()
print("Next steps:")
print("  1. Create data bundle for Zipline")
print("  2. Test simple strategy")
print("  3. Integrate with QuantEvolve")
print()
