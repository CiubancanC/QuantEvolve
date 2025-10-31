# QuantEvolve Training Issues - Deep Analysis and Proposed Fixes

## Executive Summary

Analysis of 5-generation training run on real 10-year market data revealed 6 types of issues:
- **44 warnings**, **1 error**
- Training completed successfully but with reduced strategy quality
- All proposed fixes conform to paper methodology (QuantEvolve.md sections 4-6)

---

## Issue 1: Over-Filtered Strategies (26 occurrences)

### Current Behavior
- **Threshold:** 10 trades/year minimum (hard-coded)
- **Impact:** 48% of strategies rejected (26 out of 54)
- **Real vs Sample Data:** Real markets are significantly harder, leading to more conservative strategies

### Deep Analysis

**From Paper (Section 5.4, line 194):**
> "Trading frequency" is a key evaluation metric and feature dimension

**From Paper (Section 4.1, Table 1):**
> Feature dimensions include "Trading Frequency: Number of trades per period"

**Problem:** The 10 trades/year threshold is strategy-category agnostic. Different categories have inherently different trading frequencies:
- **Momentum/Trend:** Typically 10-50 trades/year (holds positions for weeks/months)
- **Mean-Reversion:** 20-100 trades/year (faster mean-reversion cycles)
- **Risk/Allocation:** 3-12 trades/year (periodic rebalancing, NOT high-frequency)
- **Seasonal/Calendar:** 12-48 trades/year (by definition, calendar-based)
- **Correlation/Pairs:** 5-30 trades/year (waits for cointegration opportunities)

**Evidence from Paper Results (Section 7.4, Table 4):**
- Risk Parity baseline: Likely trades monthly = 12 times/year
- MarketCap: Monthly rebalancing = 12 times/year
- Both are valid strategies despite low frequency

**Paper's Gen 130 Strategy (Section 7.2, Figure 7):**
> "The strategy retained volume-momentum signals as the core component, incorporated per-asset volatility adjustments... and adopted continuous position monitoring"

This suggests evolved strategies should be allowed to have low trading frequencies if they're high-quality.

### Proposed Fix

**Decision:** Make threshold **category-aware** based on strategy type:

```python
MIN_TRADES_PER_YEAR = {
    'Momentum/Trend': 10,           # Holds positions weeks-months
    'Mean-Reversion': 15,           # Faster cycle times
    'Volatility': 12,               # Volatility regime changes
    'Volume/Liquidity': 15,         # Needs sufficient activity
    'Breakout/Pattern': 8,          # Waits for pattern formation
    'Correlation/Pairs': 6,         # Waits for cointegration
    'Risk/Allocation': 4,           # Portfolio rebalancing
    'Seasonal/Calendar Effects': 12 # Calendar-driven
}
```

**Rationale:**
- Aligns with paper's emphasis on strategy diversity (Section 4, Feature Map)
- Prevents premature rejection of valid low-frequency strategies
- Risk/Allocation strategies SHOULD trade infrequently (quarterly rebalancing is valid)
- Still filters out truly inactive strategies (0-3 trades/year)

**Implementation:** Modify `src/agents/evaluation_team.py:61`

**Conformance:** ✅ Maintains paper's focus on diversity across behavioral niches

---

## Issue 2: Backtest NA/NaN Masking Errors (6 occurrences)

### Current Behavior
```
Error backtesting AMZN: Cannot mask with non-boolean array containing NA / NaN values
```

### Root Cause Analysis

**Problem Location:** Generated strategy code produces NaN values in signals, then tries to use them as boolean masks.

**Example Failure Pattern:**
```python
# Generated strategy calculates RSI
rsi = calculate_rsi(data['close'], period=14)  # First 14 values are NaN

# Tries to use as mask
signals[rsi > 70] = -1  # FAILS: rsi contains NaN, can't be used as boolean mask
```

**Why it happens:**
1. LLM generates strategy with indicator calculation
2. Indicators have warm-up periods (first N days are NaN)
3. Strategy doesn't explicitly handle NaN before using as mask
4. Pandas raises: "Cannot mask with non-boolean array containing NA / NaN values"

**From Paper (Section 5.4, line 192-195):**
> "When backtesting reveals issues—logical errors, performance anomalies, unexpected behaviors—we iteratively refine the code by debugging edge cases, optimizing efficiency, adjusting parameters, or adding risk constraints."

The paper expects the **Coding Team** to handle edge cases properly, but the current implementation allows NaN-containing strategies to reach backtesting.

### Proposed Fix

**Three-Layer Defense:**

#### Layer 1: Signal Validation in Backtest Engine (Primary Fix)
Add robust signal validation immediately after generation in `improved_backtest.py:341`:

```python
# After line 341: signals = generate_signals(data.copy())

# Validate and sanitize signals
signals = self._validate_signals(signals, data)
```

```python
def _validate_signals(self, signals: pd.Series, data: pd.DataFrame) -> pd.Series:
    """
    Validate and sanitize trading signals to prevent backtest errors.

    Handles:
    - NaN/inf values
    - Non-numeric values
    - Index misalignment
    - Type errors

    Per paper Section 5.4: Handle edge cases before backtesting
    """
    # Ensure Series type
    if not isinstance(signals, pd.Series):
        signals = pd.Series(signals, index=data.index)

    # Align with data index
    signals = signals.reindex(data.index)

    # Replace NaN/inf with neutral signal (0)
    signals = signals.fillna(0)
    signals = signals.replace([np.inf, -np.inf], 0)

    # Ensure numeric
    signals = pd.to_numeric(signals, errors='coerce').fillna(0)

    # Clip to valid range [-1, 1]
    signals = signals.clip(-1, 1)

    # Ensure datetime index is timezone-naive
    if isinstance(signals.index, pd.DatetimeIndex):
        if signals.index.tz is not None:
            signals.index = signals.index.tz_localize(None)

    return signals
```

**Rationale:**
- Defensive programming: assumes generated code may have issues
- Fails gracefully: converts invalid signals to neutral (0) instead of crashing
- Maintains paper's intent: allows backtest to complete and evaluate strategy
- Per Section 5.4: Edge case handling is expected

#### Layer 2: Datetime Normalization in Data Loading
Add to `improved_backtest.py` load_data method:

```python
def _normalize_datetime_index(self, df: pd.DataFrame) -> pd.DataFrame:
    """Ensure datetime index is timezone-naive and properly typed"""
    if isinstance(df.index, pd.DatetimeIndex):
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

    # Ensure all datetime columns are also timezone-naive
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            if hasattr(df[col].dt, 'tz') and df[col].dt.tz is not None:
                df[col] = df[col].dt.tz_localize(None)

    return df
```

Call after loading CSV in `load_data()` method.

#### Layer 3: Enhanced Logging for Debugging
When signal validation triggers, log details for evaluation team:

```python
def _validate_signals(self, signals: pd.Series, data: pd.DataFrame) -> pd.Series:
    """... (as above) ..."""

    # Track validation issues
    validation_issues = []

    original_nan_count = signals.isna().sum()
    if original_nan_count > 0:
        validation_issues.append(f"{original_nan_count} NaN values")

    original_inf_count = np.isinf(signals).sum()
    if original_inf_count > 0:
        validation_issues.append(f"{original_inf_count} inf values")

    # ... rest of validation ...

    if validation_issues:
        logger.warning(f"Signal validation corrected: {', '.join(validation_issues)}")

    return signals
```

This provides feedback to the Evaluation Team about code quality issues.

**Implementation Files:**
- `src/backtesting/improved_backtest.py` (lines 341, 394)

**Conformance:** ✅ Aligns with paper Section 5.4 (edge case handling) and Section 5.5 (code quality analysis)

---

## Issue 3: Invalid Datetime Comparison (3 occurrences)

### Current Behavior
```
Error backtesting AMZN: Invalid comparison between dtype=datetime64[ns] and Timestamp
```

### Root Cause Analysis

**Problem:** Mixing timezone-naive and timezone-aware datetime objects in comparisons.

**Despite CSV timezone fixes, this still occurs because:**
1. Generated strategy code creates new pd.Timestamp objects
2. pd.Timestamp() default behavior varies by pandas version
3. Some operations (date range filtering, rolling windows) may introduce tz-aware timestamps

**Example Failure:**
```python
# Data has tz-naive index (from fixed CSVs)
data.index -> datetime64[ns] (no timezone)

# Strategy code creates timestamp for comparison
cutoff = pd.Timestamp('2020-01-01')  # May be tz-aware depending on pandas version

# Comparison fails
data[data.index > cutoff]  # ERROR if timezone mismatch
```

### Proposed Fix

**Comprehensive datetime normalization at data loading and execution boundaries:**

Already proposed in Issue 2, Layer 2. Additional enforcement:

```python
def _create_strategy_namespace(self) -> Dict:
    """Create namespace for strategy execution with timezone-safe pandas"""
    import pandas as pd
    import numpy as np

    # Wrap pd.Timestamp to force timezone-naive
    original_timestamp = pd.Timestamp

    def safe_timestamp(*args, **kwargs):
        """Timezone-naive Timestamp wrapper"""
        kwargs.pop('tz', None)  # Remove tz if present
        kwargs.pop('tzinfo', None)
        ts = original_timestamp(*args, **kwargs)
        if ts.tz is not None:
            ts = ts.tz_localize(None)
        return ts

    namespace = {
        'pd': pd,
        'np': np,
        'DataFrame': pd.DataFrame,
        'Series': pd.Series,
        'Timestamp': safe_timestamp,  # Use safe wrapper
        '__builtins__': __builtins__
    }

    return namespace
```

**Rationale:**
- Prevents generated code from creating tz-aware timestamps
- Maintains consistency with paper's data handling
- Transparent to strategy code (no syntax changes needed)

**Implementation:** `src/backtesting/improved_backtest.py:379-392`

**Conformance:** ✅ Maintains paper's data pipeline integrity

---

## Issue 4: No Valid Backtest Results (3 occurrences)

### Current Behavior
```
WARNING | No valid backtest results
```

### Root Cause

This is a **consequence** of Issues 2 and 3. When all stocks fail due to NaN masking or datetime errors, no results are produced.

### Proposed Fix

**Two-part solution:**

#### Part 1: Fix Issues 2 & 3 (Primary Solution)
The signal validation and datetime normalization will prevent most "No valid backtest results" cases.

#### Part 2: Graceful Degradation (Fallback)
If ALL stocks still fail after validation, assign worst-case metrics instead of returning None:

```python
# In improved_backtest.py:358-361

if len(all_returns) == 0:
    logger.warning("No valid backtest results - assigning worst-case metrics")
    logger.warning(f"Attempted symbols: {test_symbols}")

    # Return worst possible metrics per paper's Combined Score (SR + IR + MDD)
    # This ensures strategy is rejected but provides comparable metrics
    return {
        'sharpe_ratio': -3.0,      # Worst observed in training
        'sortino_ratio': -3.0,
        'information_ratio': -2.0,
        'total_return': -0.50,     # -50%
        'max_drawdown': -1.0,      # -100%
        'trading_frequency': 0,
        'strategy_category_bin': 0,
        'combined_score': -6.0     # SR + IR + MDD = -3 + (-2) + (-1)
    }
```

**Rationale:**
- Paper's Combined Score = SR + IR + MDD (Section 6.3.2, Equation 3)
- Assigning worst-case ensures strategy is rejected in evolutionary selection
- Maintains comparability: scores are in same range as valid strategies
- Per Section 5.5: Failed strategies should be documented, not excluded

**Implementation:** `src/backtesting/improved_backtest.py:358-361`

**Conformance:** ✅ Maintains paper's evolutionary selection mechanism

---

## Issue 5: API Request Failures (1 occurrence)

### Current Behavior
```
ERROR | src.utils.llm_client:_make_request:97 - API request failed: Response ended prematurely
```

### Analysis

**From Paper (Section 10, Discussion):**
> "LLM Inference Cost: Each evolutionary cycle requires 5-10 LLM inferences. This limits scalability for resource-constrained settings."

The paper acknowledges LLM reliability is critical but doesn't specify retry logic.

**Industry Best Practice:**
- Exponential backoff with jitter
- Max 3-5 retries
- Preserve request idempotency

### Proposed Fix

**Robust retry mechanism with exponential backoff:**

```python
# In src/utils/llm_client.py

import time
import random
from typing import Optional

def _make_request_with_retry(
    self,
    messages: List[Dict],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Optional[str]:
    """
    Make LLM API request with exponential backoff retry.

    Implements retry logic for transient failures (network errors, rate limits, etc.)
    per industry best practices for LLM API calls.

    Args:
        messages: List of message dicts for LLM
        max_retries: Maximum retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)

    Returns:
        Response string or None if all retries exhausted
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            # Original request logic
            response = self._make_request(messages)
            return response

        except Exception as e:
            last_exception = e

            # Log the failure
            logger.warning(
                f"API request failed (attempt {attempt + 1}/{max_retries}): {e}"
            )

            # Don't retry on last attempt
            if attempt == max_retries - 1:
                logger.error(f"API request failed after {max_retries} attempts")
                break

            # Calculate exponential backoff with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # ±10% jitter
            total_delay = delay + jitter

            logger.info(f"Retrying in {total_delay:.2f} seconds...")
            time.sleep(total_delay)

    # All retries exhausted
    logger.error(f"All retry attempts exhausted. Last error: {last_exception}")
    raise last_exception
```

**Usage:** Replace all calls to `_make_request()` with `_make_request_with_retry()`.

**Retry Strategy:**
- Attempt 1: immediate
- Attempt 2: wait 1-1.1 seconds
- Attempt 3: wait 2-2.2 seconds
- Total max time: ~3 seconds of retries

**Rationale:**
- Handles transient network failures
- Respects rate limits (exponential backoff)
- Jitter prevents thundering herd
- 3 retries balances reliability vs latency

**Implementation:** `src/utils/llm_client.py`

**Conformance:** ✅ Enhances paper's multi-agent system reliability

---

## Issue 6: Missing Earnings Calendar (6 occurrences)

### Current Behavior
```
WARNING: No earnings calendar provided. Using dummy dates — this will cause false signals.
```

### Analysis

**Source:** Some generated strategies attempt to use earnings-based signals (e.g., "buy before earnings", "avoid during earnings volatility").

**Problem:** Without real earnings dates:
- Dummy dates create false signals
- Strategy appears to work but is fitted to random dates
- Severe overfitting risk

**From Paper (Section 10, Discussion, Robustness and Overfitting):**
> "strategies generated by the framework may be susceptible to data snooping bias"

Using dummy earnings dates **amplifies** data snooping bias.

### Proposed Fix

**Option A: Disable earnings-based features (RECOMMENDED)**

Add configuration to Data Agent to exclude earnings-based signals when calendar unavailable:

```python
# In prompts for Research Agent and Coding Team

FEATURES_BLACKLIST = []

if not earnings_calendar_available:
    FEATURES_BLACKLIST.extend([
        'earnings dates',
        'earnings announcements',
        'pre-earnings drift',
        'post-earnings drift',
        'earnings surprises'
    ])

# In Research Agent prompt:
"""
IMPORTANT: The following features are NOT available in this dataset and must NOT be used:
{', '.join(FEATURES_BLACKLIST)}

Strategies that attempt to use these features will fail validation.
"""
```

**Option B: Download earnings calendar data**

Use free APIs (e.g., Yahoo Finance, Alpha Vantage) to fetch earnings dates:

```python
# scripts/download_earnings_calendar.py

import yfinance as yf
import pandas as pd

def download_earnings_calendar(symbols, output_dir='data/earnings'):
    """Download earnings calendar for given symbols"""
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        calendar = ticker.calendar  # Returns earnings dates

        if calendar is not None:
            df = pd.DataFrame(calendar)
            df.to_csv(f"{output_dir}/{symbol}_earnings.csv")
```

However, this adds complexity and may not be worth it for 6 warnings.

### Recommended Fix: Option A

**Rationale:**
- Simpler implementation
- Prevents overfitting to dummy data
- Paper doesn't use earnings-based strategies in results
- Can add real data later if needed

**Implementation:**
- Modify Research Agent and Coding Team prompts
- Add earnings calendar check in Data Agent

**Conformance:** ✅ Reduces data snooping bias per Section 10 discussion

---

## Implementation Priority

### High Priority (Fixes critical errors):
1. **Issue 2:** Signal validation (prevents crashes)
2. **Issue 3:** Datetime normalization (prevents crashes)
3. **Issue 5:** API retry mechanism (prevents evolutionary stalls)

### Medium Priority (Improves quality):
4. **Issue 1:** Category-aware trading frequency
5. **Issue 4:** Graceful degradation

### Low Priority (Quality of life):
6. **Issue 6:** Disable earnings-based features

---

## Testing Plan

### Unit Tests
```python
# tests/test_signal_validation.py

def test_signal_validation_nan():
    """Test that NaN signals are replaced with 0"""
    engine = ImprovedBacktestEngine(...)
    signals = pd.Series([1, np.nan, -1, 0])
    validated = engine._validate_signals(signals, data)
    assert validated.isna().sum() == 0
    assert validated.iloc[1] == 0

def test_signal_validation_inf():
    """Test that inf signals are replaced with 0"""
    signals = pd.Series([1, np.inf, -np.inf, 0])
    validated = engine._validate_signals(signals, data)
    assert not np.isinf(validated).any()

def test_datetime_normalization():
    """Test that tz-aware datetimes are converted to tz-naive"""
    df = pd.DataFrame(
        {'close': [100, 101]},
        index=pd.date_range('2020-01-01', periods=2, tz='UTC')
    )
    normalized = engine._normalize_datetime_index(df)
    assert normalized.index.tz is None
```

### Integration Test
```bash
# Run 5-generation training and verify:
# 1. No "Cannot mask" errors
# 2. No "Invalid comparison" errors
# 3. API retry logs appear on transient failures
# 4. Reduced over-filtering warnings

python3 -m src.main --generations 5 2>&1 | tee test_run.log

# Verify fixes
grep -c "Cannot mask" test_run.log  # Should be 0
grep -c "Invalid comparison" test_run.log  # Should be 0
grep -c "Retrying" test_run.log  # Should show retry attempts if API failed
```

---

## Expected Outcomes

### Quantitative Improvements:
- **Backtest crash rate:** 11% → 0% (eliminate 6 NaN + 3 datetime errors)
- **Over-filtering rate:** 48% → 30% (category-aware thresholds)
- **API failure recovery:** 0% → 100% (with retry mechanism)

### Qualitative Improvements:
- More reliable evolutionary process
- Better strategy diversity (fewer false rejections)
- Improved data quality and consistency
- Enhanced debugging capabilities (validation logging)

### Paper Conformance:
All fixes align with:
- **Section 4:** Feature Map diversity principles
- **Section 5.4:** Edge case handling and iterative refinement
- **Section 5.5:** Code quality analysis
- **Section 6:** Evaluation methodology
- **Section 10:** Robustness considerations

---

## Rollout Plan

### Phase 1: Critical Fixes (Week 1)
- Implement signal validation
- Implement datetime normalization
- Implement API retry mechanism
- Deploy and test on 5-generation run

### Phase 2: Quality Improvements (Week 2)
- Implement category-aware trading frequency
- Implement graceful degradation for failed backtests
- Update prompts to disable earnings features

### Phase 3: Validation (Week 3)
- Run 20-generation training on real data
- Compare results with baseline (current 5-gen run)
- Verify improvements in stability and diversity

---

## Conclusion

These fixes address all 6 identified issue types while maintaining strict conformance with the QuantEvolve paper's methodology. The fixes prioritize:

1. **Robustness:** Handle edge cases gracefully
2. **Diversity:** Preserve valid strategies across categories
3. **Reliability:** Prevent transient failures from disrupting evolution
4. **Quality:** Improve signal validation and data consistency

Implementation of these fixes will significantly improve training stability and strategy quality on real market data.
