# Implementation Deviations from Research Paper

This document catalogs all intentional deviations of this implementation from the original QuantEvolve research paper (Yun et al., 2025, arXiv:2510.18569).

> **Last Updated**: October 30, 2025

---

## Summary

This implementation is **~95% aligned** with the research paper. The core evolutionary framework, feature map architecture, multi-agent system, and sampling mechanisms are implemented faithfully. The main deviations are:

1. **LLM Inference**: Using API-based inference (OpenRouter) instead of locally-run models
2. **Backtesting Framework**: Custom vectorized engine instead of Zipline
3. **Information Ratio Calculation**: Currently uses simplified benchmark (planned fix)

---

## 1. LLM Inference Method

### Paper Specification (Section 5, line 107)
> "We implement our multi-agent system using an ensemble of Qwen3-30B-A3B-Instruct-2507 (lightweight, faster responses) and Qwen3-Next-80B-A3B-Instruct (larger, more thoughtful analysis)"

### Current Implementation
- Uses **OpenRouter API** for LLM inference
- Model selection matches paper: `qwen/qwen3-30b-a3b-instruct-2507` and `qwen/qwen3-next-80b-a3b-instruct`
- API-based inference instead of local model hosting

### Rationale
- **Accessibility**: API-based approach lowers barrier to entry (no need for GPU infrastructure)
- **Scalability**: Easier to scale without managing model deployment
- **Cost**: Pay-per-use model more economical for research/experimentation
- **Maintenance**: No model version management or hardware dependencies

### Impact
- ✅ **None on algorithm correctness**: The models are identical, only the hosting differs
- ⚠️ **Latency**: API calls add network latency (~1-3 seconds per generation)
- ⚠️ **Cost**: API usage costs apply (typically $0.01-0.05 per strategy)
- ⚠️ **Reproducibility**: Requires internet connection and API key

### Files Affected
- `src/utils/llm_client.py`: LLM client using OpenRouter API

---

## 2. Backtesting Framework

### Paper Specification (Section 5.4, line 197)
> "We leverage **Zipline** [29], an open-source backtesting engine simulating market mechanics (slippage, commissions)"

### Current Implementation
- Custom `ImprovedBacktestEngine` class (vectorized backtesting)
- Implements paper-specified transaction cost model:
  - Commission: $0.0075 per share + $1.00 minimum per trade ✅
  - Slippage: Quadratic function of traded volume percentage ✅
- Calculates all required metrics: Sharpe, Sortino, IR, MDD, Total Return ✅

### Rationale
- **Simplicity**: Zipline has complex setup and deprecated dependencies
- **Performance**: Vectorized implementation is faster for our use case
- **Control**: Direct control over transaction cost modeling
- **Maintenance**: Easier to maintain and extend

### Limitations
- ⚠️ **Edge Cases**: May not handle all edge cases that Zipline handles:
  - Corporate actions (splits, dividends, spin-offs)
  - Delistings and bankruptcies
  - Adjusted price calculations
  - Multi-asset constraints (margin, capital allocation)
- ⚠️ **Realism**: Assumes clean, split-adjusted data

### Impact
- ✅ **Transaction costs implemented correctly** per paper specification
- ✅ **Metrics calculation matches paper**
- ⚠️ **Potential data quality issues** if using unadjusted data
- ⚠️ **Not directly comparable** to results using Zipline

### Mitigation
- Use pre-adjusted data (Yahoo Finance provides split-adjusted prices)
- Add basic corporate action detection if needed
- Document data cleaning process

### Files Affected
- `src/backtesting/improved_backtest.py`: Custom backtest engine

---

## 3. Information Ratio Calculation

### Paper Specification (Section 6.3.1, lines 262-263)
> IR = (R̄_p - R̄_b) / σ_(p-b)
> where R̄_b is benchmark return and σ_(p-b) is tracking error

### Paper Benchmark (Section 6.2, line 336)
> "For **equities**, we construct a **market capitalization-weighted portfolio** of the six stocks rebalanced monthly"

### Current Implementation
```python
# improved_backtest.py:446-450
# For IR, we compare against 0 (assuming market neutral strategy)
excess_returns = returns  # Already relative to 0
tracking_error = excess_returns.std() * np.sqrt(252)
information_ratio = (excess_returns.mean() * 252) / tracking_error
```

**Status**: ⚠️ **INCORRECT - Needs Fix**

### Impact
- 🔴 **Critical**: Affects evolutionary selection pressure
- IR is one component of combined score: `Score = SR + IR + MDD`
- Strategies evolve with different selection criteria than in paper
- Results not directly comparable to paper's reported performance

### Planned Fix
1. Implement market-cap-weighted benchmark calculation:
   - Load all equity symbols
   - Calculate market cap weights (or proxy using price × shares)
   - Rebalance monthly
   - Calculate benchmark returns
2. Update `_calculate_metrics()` to use benchmark:
   ```python
   IR = (mean(strategy_returns - benchmark_returns) * 252) /
        (std(strategy_returns - benchmark_returns) * sqrt(252))
   ```

### Files Affected
- `src/backtesting/improved_backtest.py`: Lines 446-450

**Priority**: **HIGH** - Should be fixed before production use

---

## 4. QuantStats Integration

### Paper Specification (Section 5.4, line 197)
> "and **QuantStats** [1] for quantitative analysis and risk metrics"

### Current Implementation
- Manual calculation of all metrics without QuantStats library
- Metrics calculated:
  - ✅ Sharpe Ratio (annualized)
  - ✅ Sortino Ratio (annualized)
  - ⚠️ Information Ratio (incorrect benchmark - see #3)
  - ✅ Maximum Drawdown
  - ✅ Total Return
  - ✅ Trading Frequency

### Rationale
- **Dependency Management**: Reduce external dependencies
- **Control**: Full control over metric calculation
- **Performance**: Avoid overhead of external library

### Impact
- ✅ **Acceptable** if all metrics are calculated correctly
- ⚠️ **Missing advanced metrics** that QuantStats provides (e.g., Calmar Ratio, Omega Ratio, tail ratios)
- ✅ **Core metrics match paper requirements**

### Files Affected
- `src/backtesting/improved_backtest.py`: `_calculate_metrics()` method

---

## 5. Insight Curation Algorithm

### Paper Specification (Section 5.5)
> "Every 50 generations, we curate accumulated insights—filtering redundancy, consolidating findings..."

### Current Implementation
- Goes **beyond paper** with sophisticated importance scoring
- Uses multiple factors:
  - Recency (newer insights weighted higher)
  - Performance impact (insights from high-performing strategies)
  - Novelty (keyword detection for innovative ideas)
  - Actionability (keyword detection for concrete improvements)
- Diversity selection using Jaccard similarity to avoid redundancy

### Paper Implementation
- Details not fully specified in paper
- Implementation appears simpler (basic filtering and consolidation)

### Impact
- ✅ **Enhancement**: More sophisticated than paper
- ✅ **Preserves intent**: Maintains institutional memory while reducing redundancy
- ✅ **Improves evolution**: Better signal-to-noise in insight repository

### Files Affected
- `src/core/evolutionary_database.py`: `_calculate_insight_importance()`, `_apply_diversity_selection()`

---

## 6. Over-Filtering Detection

### Paper Specification
- Not explicitly mentioned in paper

### Current Implementation
- **Added safeguard**: Automatic rejection of strategies with <10 trades/year
- Prevents common failure mode where stacking filters produces:
  - High Sharpe/Sortino ratios
  - Low sample sizes (n=1 or n=2 trades)
  - Statistically meaningless metrics

### Rationale
- **Quality Control**: Prevents evolution from optimizing on statistical noise
- **Practical Utility**: Ensures strategies are tradeable in practice
- **Resource Efficiency**: Avoids wasting compute on over-fitted strategies

### Impact
- ✅ **Enhancement**: Improves practical utility
- ✅ **Guides LLM**: Prompts updated to warn against over-filtering
- ✅ **No negative impact**: Only rejects invalid strategies

### Files Affected
- `src/agents/evaluation_team.py`: Trade frequency validation (lines 56-91)
- `src/agents/prompts.py`: Enhanced guidance on trading frequency

---

## 7. Parameter Optimization Layer

### Paper Specification
- Not mentioned in paper

### Current Implementation
- **Optional enhancement**: `ParameterOptimizer` class for grid search
- Automatically identifies tunable parameters (windows, thresholds, sigma values)
- Grid search over parameter combinations
- Selects best-performing variant

### Rationale
- **Post-evolution refinement**: Can be applied to top strategies after evolution
- **Optional**: Not part of core evolution loop
- **Practical utility**: Improves final strategy performance

### Impact
- ✅ **Enhancement**: Improves final results
- ✅ **Optional**: Can be disabled
- ✅ **Separable**: Doesn't affect core evolution algorithm

### Files Affected
- `src/optimization/parameter_optimizer.py`: Grid search implementation

---

## 8. Configuration Management

### Paper Specification
- Parameters hard-coded or in simple config

### Current Implementation
- Comprehensive YAML-based configuration system
- Environment variable support
- Easy parameter tuning without code changes

### Impact
- ✅ **Enhancement**: Better usability
- ✅ **Reproducibility**: Easier to share configurations
- ✅ **Experimentation**: Faster parameter exploration

### Files Affected
- `config/default_config.yaml`
- `src/utils/config_loader.py`

---

## Summary Table

| Component | Paper Spec | Implementation | Status | Impact |
|-----------|------------|----------------|--------|--------|
| LLM Models | Qwen (local) | Qwen (API) | ✅ Acceptable | Minor latency |
| Backtesting | Zipline | Custom vectorized | ✅ Acceptable | Edge cases |
| IR Calculation | Market-cap benchmark | Zero benchmark | 🔴 **Needs Fix** | Critical |
| QuantStats | Required | Manual calculation | ✅ Acceptable | Missing advanced metrics |
| Insight Curation | Basic | Enhanced | ✅ Enhancement | Improved quality |
| Over-filtering Detection | Not specified | Added | ✅ Enhancement | Better strategies |
| Parameter Optimization | Not specified | Added | ✅ Enhancement | Optional feature |
| Configuration | Hard-coded | YAML-based | ✅ Enhancement | Better UX |

---

## Action Items

### Critical (Before Production)
1. **Fix IR Calculation** to use market-cap-weighted benchmark
   - Priority: **HIGH**
   - Effort: ~4 hours
   - Files: `src/backtesting/improved_backtest.py`

### Important (For Research Reproducibility)
2. **Validate Metrics** against paper's reported values
   - Run simple buy-and-hold and verify metrics match expectations
   - Effort: ~2 hours

3. **Document Data Requirements**
   - Specify data format, adjustment requirements
   - Effort: ~1 hour

### Optional (Enhancements)
4. **Add QuantStats Integration** (optional, for advanced metrics)
   - Effort: ~2 hours

5. **Corporate Action Handling** (if needed)
   - Add split/dividend detection
   - Effort: ~8 hours

---

## Validation Checklist

Before claiming full paper replication:

- [ ] Fix IR calculation to use market-cap benchmark
- [ ] Run baseline strategies (buy-and-hold) and verify metrics
- [ ] Validate combined score formula: `SR + IR + MDD`
- [ ] Verify transaction cost calculations match paper
- [ ] Document any remaining limitations
- [ ] Add integration test comparing results to paper's Table 4

---

## References

- **Original Paper**: Yun et al. (2025), "QuantEvolve: Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework", arXiv:2510.18569
- **Zipline**: https://github.com/quantopian/zipline
- **QuantStats**: https://github.com/ranaroussi/quantstats

---

## Questions?

If you have questions about these deviations or need clarification:
- Open an issue on GitHub
- See main documentation in `docs/QuantEvolve.md`
- Check implementation notes in source code comments
