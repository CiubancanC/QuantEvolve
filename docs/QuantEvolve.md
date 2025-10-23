# QuantEvolve: Automating Quantitative Strategy Discovery through Multi-Agent Evolutionary Framework

**Authors:** Junhyeog Yun*, Hyoun Jun Lee*, Insu Jeon†  
*Equal Contribution, †Corresponding Author

**Affiliation:** AI Tech Lab, Qraft Technologies  
**Contact:** {junhyeog.yun, hyounjun.lee, insu.jeon}@qraftec.com

**arXiv:** 2510.18569v1 [cs.AI] 21 Oct 2025

---

## Abstract

Automating quantitative trading strategy development in dynamic markets is challenging, especially with increasing demand for personalized investment solutions. Existing methods often fail to explore the vast strategy space while preserving the diversity essential for robust performance across changing market conditions. We present **QuantEvolve**, an evolutionary framework that combines quality-diversity optimization with hypothesis-driven strategy generation. QuantEvolve employs a feature map aligned with investor preferences—such as strategy type, risk profile, turnover, and return characteristics—to maintain a diverse set of effective strategies. It also integrates a hypothesis-driven multi-agent system to systematically explore the strategy space through iterative generation and evaluation. This approach produces diverse, sophisticated strategies that adapt to both market regime shifts and individual investment needs. Empirical results show that QuantEvolve outperforms conventional baselines, validating the effectiveness. We release a dataset of evolved strategies to support future research.

---

## 1. Introduction

As financial markets evolve, the demand for faster and more adaptive trading strategy development has become critical. Traditional quantitative research relies on human researchers to design, test, and refine trading algorithms. This process involves analyzing historical data, identifying profitable patterns, and adapting to market conditions [3, 5, 9, 15]. However, human researchers struggle to navigate diverse strategic frameworks due to inherent cognitive biases and limited attentional capacity [7, 18]. These constraints become especially acute during rapid regime changes, as delays in the research process often lead to missed alpha opportunities [3, 5, 9, 15].

Recent technological advances, particularly in large language models (LLMs) and multi-agent systems, have paved the way for sophisticated automation in quantitative finance. Researchers have begun deploying these systems throughout the investment pipeline, from discovering predictive alpha factors to executing real-time trading decisions, with the aim of supporting or extending traditional human-driven research [23, 25]. Notable examples, such as R&D-Agent-Quant and QuantAgent, leverage self-improving agent architectures to generate and refine trading strategies [10, 17]. These studies demonstrate that LLMs can facilitate efficient development and implementation of trading algorithms.

Despite these advances, current LLM-based and agent-driven approaches still face important limitations in real-world applications. First, although they enhance the automation of strategy discovery, they often struggle to accommodate the diversity and complexity of modern financial environments [2, 16]. Most existing work focuses on optimizing isolated strategies or narrow objectives such as short-term returns, limiting their ability to account for the breadth of market conditions, trading styles, and risk regimes that coexist in practice. Second, a major shortcoming of these automated systems lies in their inability to address the growing demand for personalized asset management. While scalable, such systems often overlook the fundamental heterogeneity in investor preferences. For example, direct indexing assets reached $864.3 billion by December 2024, growing at a 22.4% compound annual growth rate (CAGR). Robo-advisory platforms now manage $1.4 trillion in assets, yet still serve only 5% of U.S. investors, primarily due to limited personalization capabilities [4, 19]. These trends point to a critical gap: instead of relying on a single optimal strategy, future systems must dynamically generate and manage portfolios aligned with diverse investor preferences—each tailored to specific trading philosophies (e.g., momentum vs. mean-reversion), risk profiles, and investment horizons (e.g., high-frequency vs. low-turnover)—while maintaining adaptability to regime shifts.

To address these challenges, we present **QuantEvolve**, an evolutionary multi-agent framework, designed for the automated creation of trading strategies. Leveraging recent advancements—such as AlphaEvolve and The AI Scientist—that demonstrate the success of evolutionary computation in tackling intricate scientific problems [12, 14], we adapt these methodologies to quantitative finance. QuantEvolve explores a diverse set of strategies using a feature map aligned with investor preferences. It also utilizes a hypothesis-driven multi-agent system that facilitates a systematic exploration of the strategy search space through structured reasoning and iterative refinement during the evolutionary cycle. This integration enables QuantEvolve to generate a broad range of high-performance strategies adaptable to fluctuating market regimes while meeting the specific needs of personalized investment.

### Contributions

The primary contributions of this paper are as follows:

- We introduce **QuantEvolve**, a multi-agent evolutionary framework that produces diverse trading strategies, adaptable to changing markets and personalized investment goals.
- We design a **hypothesis-driven multi-agent system** within an evolutionary framework that enables efficient exploration of a vast, high-dimensional strategy space, thereby facilitating systematic and in-depth research.
- We demonstrate that QuantEvolve produces strategies that **outperform conventional baselines**, validating its effectiveness and potential for broader use in automated quantitative strategy development.
- We **release a detailed dataset** of strategies generated by QuantEvolve, facilitating further research on automated quantitative finance and evolutionary strategy generation.

---

## 2. Related Work

### 2.1 LLM Agents In Finance

The emergence of LLMs and their derivative agentic architectures has generated transformative applications across multiple industries, with finance among the most prominent domains. In this context, LLM-based agents have enabled advances in portfolio construction [8, 22], explainable investment products [6, 11], and signal processing [21, 26], broadening the analytical toolkit available to practitioners. Frameworks such as AlphaAgents and FinRobot demonstrate how agentic systems can integrate heterogeneous financial data sources and uncover insights beyond traditional human-driven methods [27, 28]. Yet most existing efforts remain oriented toward narrow subtasks and rely heavily on semantic cues, making them difficult to backtest and limiting their robustness in real-world settings. These challenges motivate further exploration into how multi-agent systems can be designed to address the more demanding requirements of quantitative trading.

### 2.2 LLM Agents in Quant Trading

Subsequent research focuses on multi-agent frameworks that can be empirically tested with reusable evaluation methodologies. AlphaGPT and R&D-Agent-Quant demonstrate how specialized agents can collaborate to generate and refine trading strategies through distributed processing and iterative improvement [10, 23]. These systems primarily focus on alpha factor discovery, identifying individual predictive signals that require subsequent integration into complete trading systems. While such approaches show promise in controlled environments, they remain constrained by architectural limitations that restrict deployment to narrow factor mining tasks rather than comprehensive strategy development. Current implementations lack mechanisms for developing end-to-end trading systems that integrate multiple interacting factors with execution logic, position sizing, and risk management components. This persistent gap highlights the imperative to advance multi-agent orchestration toward architectures that can systematically generate complete trading strategies through scientific methodology, moving beyond individual factor discovery to maintain empirical rigor, ensure reproducibility, and deliver operational adaptability across diverse market regimes.

### 2.3 Evolutionary LLM

The limitations of traditional multi-agent frameworks have prompted exploration of evolutionary approaches that systematically navigate complex strategy spaces while maintaining behavioral diversity. Recent systems such as AI Scientist [12] and AlphaEvolve [14] demonstrate how evolutionary algorithms can enhance multi-agent coordination by preventing mode collapse and promoting novel solution exploration. These approaches, inspired by Darwin-Gödel machines [24] that combine evolutionary principles with formal reasoning, have shown promise in general AI domains but remain largely unexplored in quantitative trading. Building upon these insights, our work introduces an evolutionary multi-agent architecture specifically designed for quantitative strategy development, combining population-based diversity preservation with hypothesis-driven strategy generation to achieve robust performance across varying market conditions.

---

## 3. Methodology

We propose **QuantEvolve**, a multi-agent-aided evolutionary framework for generating diverse, high-performing trading strategies. QuantEvolve addresses two key challenges: maintaining population diversity across investor preferences and efficiently exploring the high-dimensional strategy search space [13]. To preserve diversity, we employ a **feature map**—a multi-dimensional archive that characterizes strategies by attributes aligned with investor needs (risk profile, trading frequency, return characteristics) and retains only the best performer in each behavioral niche. To enable effective search, we deploy a **hypothesis-driven multi-agent system** that systematically explores and refines promising strategy concepts through structured reasoning. Figure 1 illustrates the framework architecture. We describe the feature map design in Sec. 4 and the multi-agent evolution process in Sec. 5.

---

## 4. Feature Map of QuantEvolve

The feature map organizes the strategy population as a multidimensional grid where each dimension represents a strategy attribute (e.g., Sharpe ratio, trading frequency, strategy category). Each dimension is discretized into bins, and their combination forms a feature vector that uniquely identifies a cell. Each cell stores the best-performing strategy for that feature vector, ensuring that diverse behavioral profiles are preserved throughout evolution.

This structure provides two advantages: it enables **personalized strategy recommendation** by matching investor preferences to specific feature combinations, and it improves **robustness** by maintaining strategies optimized for different market regimes. The likelihood of discovering superior strategies also increases with greater population diversity.

### 4.1 Feature Dimensions

We select dimensions that align with common investor requirements as detailed in Table 1.

**Table 1: Feature map dimensions**

| Dimension | Description |
|-----------|-------------|
| Strategy Category | Momentum, mean-reversion, arbitrage, etc. |
| Trading Frequency | Number of trades per period |
| Maximum Drawdown | Largest peak-to-trough decline |
| Sharpe Ratio | Risk-adjusted return |
| Sortino Ratio | Downside risk-adjusted return |
| Total Return | Cumulative return |

This design enables targeted matching: risk-averse investors seeking stable returns can select strategies with high Sharpe ratios and low maximum drawdown, while aggressive investors may prefer high trading frequency and total return.

The feature map is extensible to asset-specific requirements. For futures trading, dimensions such as rollover costs or roll yield can be added; for cryptocurrency markets, asset type categories (payment tokens, utility tokens, meme coins) can be incorporated.

### 4.2 Feature Bins

Each feature dimension is partitioned into discrete bins, with the number of bins per dimension determined by the desired granularity. Continuous variables such as trading frequency or Sharpe ratio are discretized by equally dividing the range between the minimum and maximum values.

To maximize strategy diversity, we represent the strategy category dimension using **binary encoding**. Given three strategy families—momentum, arbitrage, and mean-reversion—a strategy exhibiting both momentum and mean-reversion characteristics would be encoded as `101`. This binary representation ensures that all possible category combinations occupy distinct bins, preventing strategies with different behavioral profiles from competing directly for the same cell.

### 4.3 Feature Cells

When a new strategy is generated, its characteristics are evaluated and mapped to a feature vector by determining the appropriate bin for each dimension. This vector identifies a unique cell in the feature map. The new strategy is added to that cell only if it outperforms the currently stored strategy; otherwise, the existing strategy is retained. Although rejected strategies are not added to the feature map, we preserve them in a separate archive for potential use in future strategy generation. We refer to the feature map together with this archive as the **Evolutionary Database**.

### 4.4 Islands and Migration

To balance exploration and exploitation, we employ an **island model** where multiple populations evolve independently while sharing a common feature map. Each island is initialized with strategies from different categories (Sec. 5.1) and evolves in isolation during early generations, developing specialized expertise in particular trading approaches.

Periodically, islands exchange their best-performing strategies through **migration**. This mechanism gradually enriches each population with diverse trading concepts, enabling the emergence of sophisticated hybrid strategies that combine characteristics from multiple approaches. Over time, the evolutionary focus shifts from depth within specialized categories to breadth across the entire strategy landscape (Fig. 3), producing increasingly complex and robust solutions.

---

## 5. Multi-Agent System of QuantEvolve

To effectively explore the high-dimensional search space of trading strategies and discover high-performance solutions, we propose a novel multi-agent system that evolves strategies based on hypotheses, as illustrated in Fig. 2. This multi-agent system generates new strategies following the process outlined below, using a parent strategy sampled from the feature map and cousin strategies with similar characteristics. We implement our multi-agent system using an ensemble of Qwen3-30B-A3B-Instruct-2507 (lightweight, faster responses) and Qwen3-Next-80B-A3B-Instruct (larger, more thoughtful analysis), balancing efficiency with reasoning depth [20].

The strategy generation process consists of four steps:

1. **Hypothesis Generation:** The research agent analyzes parent and cousin strategies to generate new hypotheses about trading strategies.
2. **Strategy Implementation:** Based on the generated hypotheses, the coding team develops trading strategy code. They perform a backtest with the generated code and iteratively refine it if issues are identified.
3. **Evaluation and Analysis:** The evaluation team analyzes the hypotheses, strategy code, and backtesting results to derive new insights.
4. **Strategy Storage:** The generated strategy is stored in the appropriate cell of the feature map according to its characteristics. If a superior strategy already exists in that cell, the new strategy is rejected.

### 5.1 Initialization with Data Agent

We initialize QuantEvolve by constructing an evolutionary database that serves as the foundation for subsequent optimization. As shown in Fig. 4, we provide the **Data Agent** with the available data universe—in our case, daily OHLCV data for six equities and two futures contracts. The agent analyzes the input data structure, including file format (CSV, Parquet), schema, column definitions, and metadata required for reliable backtesting. Based on this analysis, the agent generates a **Data Schema Prompt**, a structured specification that guides subsequent strategy design.

In parallel, the data agent identifies *C* strategy categories derivable from the data universe, such as momentum, breakout, seasonality, and mean-reversion. For each category, the Coding Team generates a simple but representative seed strategy using the schema prompt and category specification. For instance, the team produces a baseline momentum strategy for the momentum category and a prototypical breakout strategy for the breakout category. The team also generates a buy-and-hold benchmark, yielding *C* + 1 initial strategies total.

Each of these *C* + 1 strategies forms a separate **island** in the evolutionary database, representing distinct starting points for strategy evolution. The initialization procedure thus constructs *N* = *C* + 1 islands, with each island populated by a single seed strategy that serves as the foundation for subsequent evolutionary processes. Subsequent evolutionary cycles iteratively reproduce, mutate, recombine, and migrate strategies within and across islands, enabling the emergence of increasingly sophisticated solutions.

### 5.2 Parent and Cousins Sampling

In our framework, reproduction is performed by sampling a **parent strategy** and **cousin strategies** that share similar characteristics with the parent. The parent strategy serves as the primary reference for generating a new strategy, while the cousin strategies help to diversify its traits and explore novel combinations.

#### 5.2.1 Parent Strategy Selection

When sampling a parent strategy, we balance exploitation of high-performing strategies with exploration of diverse characteristics to prevent premature convergence. We randomly select an island, then apply one of two sampling methods:

- **Best parent:** Uniformly samples from strategies on the feature map within the selected island.
- **Diverse parent:** Uniformly samples from the entire population of the selected island.

Formally, let *I* denote the selected island and *M_I* ⊆ *I* represent strategies from island *I* that exist on the feature map. The parent selection probability is:

```
P(s_p = s) = {
  α/|M_I|     if s ∈ M_I  (best parent)
  (1-α)/|I|   if s ∈ I    (diverse parent)
}
```

where α ∈ [0, 1] controls the exploitation-exploration tradeoff. Higher α increases selection pressure toward high-performing strategies, while lower α promotes diversity. We use α = 0.5 in our experiments to balance performance and diversity equally.

#### 5.2.2 Cousin Strategies Selection

To enrich the context for reproduction, we select not only a parent strategy but also other strategies with similar characteristics, which we refer to as **cousin strategies**. To enhance strategy quality while promoting diversity, we select cousin strategies using three methods:

- **Best Cousins:** High-performing strategies from the parent's island.
- **Diverse Cousins:** Strategies close to the parent in the feature space.
- **Random Cousins:** Strategies selected uniformly at random from the entire population of the parent's island.

We formalize diverse cousin selection as follows. Let **f_p** = (*f¹_p*, *f²_p*, ..., *f^D_p*) denote the parent strategy's feature vector, where *D* is the number of feature dimensions and *f^d_p* represents the bin index for dimension *d*. For each dimension, we perturb the parent's feature bin to generate a neighbor feature vector **f_c**:

```
f^d_c = {
  ⌊N(f^d_p, σ²_d)⌋           if dimension d is continuous
  BitFlip(f^d_p, k_bf)       if dimension d is strategy category
}
```

where σ_d controls the sampling radius for continuous dimension *d*, and BitFlip(*b*, *k_bf*) randomly selects and flips one bit from the binary encoding *b*, repeated *k_bf* times. Note that the same bit can be selected multiple times, potentially canceling out previous flips.

We then retrieve from the feature map the strategy with feature vector **f_c** as a diverse cousin.

For instance, given a parent with Sharpe ratio in bin 3 and strategy category bin '1001', we sample a diverse cousin by drawing the Sharpe ratio bin from ⌊N(3, σ²_d)⌋ and performing *k_bf* bitflips on '1001'. In our experiments, we set σ_d = 1.0 for all continuous dimensions and *k_bf* = *n*/4, where *n* is the bit length of the strategy category. We select **two best cousins, three diverse cousins, and two random cousins** per parent.

### 5.3 Research Agent

The research agent generates new hypotheses for trading strategies based on insights from parent and cousin strategies. To formulate a hypothesis, we provide three key inputs to the agent:

1. The parent and cousin strategies' hypothesis, code, backtesting results, and analysis
2. The Data Schema Prompt
3. Insights accumulated from previous generations

The agent constructs each hypothesis with the following components:

1. **Hypothesis:** A testable statement grounded in financial theory, market dynamics, or statistical analysis that defines the core trading strategy.
2. **Rationale:** Theoretical and empirical justification based on parent and cousin strategies, data patterns, or financial theories.
3. **Objectives:** Specific quantitative and qualitative goals serving as evaluation criteria.
4. **Expected Insights:** Anticipated learning outcomes and contributions to future strategy evolution.
5. **Risks and Limitations:** Potential risks and limitations, including data bias, overfitting risks, and exceptional market conditions.
6. **Experimentation Ideas:** Future directions for modifying, extending, or combining the hypothesis with other approaches.

We adopt this hypothesis-driven method to address two fundamental challenges in evolutionary strategy generation. First, the trading strategy search space is exceptionally high-dimensional. Second, evolutionary frameworks naturally favor broad, shallow exploration over deep, focused refinement. Our approach provides directional guidance that enables systematic improvement while preserving diversity, allowing convergence toward superior performance within limited generations.

### 5.4 Coding Team

The coding team translates hypotheses into executable Python trading strategies. When a hypothesis presents well-defined logic, the team implements it directly; when further exploration is needed, the team develops experimental code to validate concepts before full implementation. The workflow follows four stages:

1. **Initial Implementation:** We translate the hypothesis into Python code adhering to the data schema and backtesting framework, handling edge cases (missing data, execution constraints).
2. **Backtesting:** We execute backtests to generate performance metrics (total return, Sharpe ratio, Sortino ratio, Maximum Drawdown, Trading frequency, Information Ratio).
3. **Iterative Refinement:** When backtesting reveals issues—logical errors, performance anomalies, unexpected behaviors—we iteratively refine the code by debugging edge cases, optimizing efficiency, adjusting parameters, or adding risk constraints.
4. **Performance Reporting:** Once the strategy passes backtesting without errors and demonstrates stable performance, we finalize the implementation and report code with metrics.

We leverage **Zipline** [29], an open-source backtesting engine simulating market mechanics (slippage, commissions), and **QuantStats** [1] for quantitative analysis and risk metrics.

### 5.5 Evaluation Team

The evaluation team analyzes hypotheses, code, and backtesting results to derive actionable insights guiding evolution. This team provides critical feedback, ensuring each generation's learnings are systematically captured. The analysis comprises five functions:

1. **Hypothesis Analysis:** We evaluate hypothesis quality—assessing financial grounding, comprehensiveness (rationale, objectives, risks), testability, internal consistency, and market alignment.
2. **Code Analysis:** We verify implementation fidelity to hypotheses, checking correct trading logic, proper edge case handling, code quality (e.g., readability, efficiency), and categorize strategies for feature map placement.
3. **Backtest Analysis:** We treat results as hypothesis experiments, determining whether outcomes support, refute, or nuance the hypothesis. We identify successful/failed components, diagnose failure modes, and propose modifications or additional experiments (parameter optimization, alternative indicators, robustness tests).
4. **Insight Extraction:** We synthesize actionable insights from hypotheses, code, and results—capturing success/failure patterns, promising directions, and unexplored strategy space areas. These insights directly inform future hypothesis generation.
5. **Insight Management:** Every 50 generations, we curate accumulated insights—filtering redundancy, consolidating findings, and maintaining island-specific institutional memory to prevent repeated failures while reinforcing successful patterns.

This systematic analysis creates a **knowledge feedback loop** accelerating evolution. By transforming results into structured insights, we enable the research agent to generate increasingly sophisticated hypotheses building on prior learnings. This cumulative knowledge acquisition distinguishes our approach from purely stochastic methods, enabling efficient convergence while maintaining population diversity.

---

## 6. Experimental Setup

### 6.1 Datasets

We evaluate QuantEvolve across two asset universes with different temporal configurations due to data availability constraints. Table 2 presents the asset universes, while Table 3 details the temporal split configuration for each asset universe.

**Table 2: Asset Universes**

| Market | Symbols |
|--------|---------|
| Equities | AAPL, NVDA, AMZN, GOOGL, MSFT, TSLA |
| Futures | ES, NQ |

**Table 3: Temporal Data Split Configuration**

| Market | Period | Date Range | Duration |
|--------|--------|------------|----------|
| **Equities** |
| | Training | 2015-08-01 to 2020-07-31 | 5 years |
| | Validation | 2020-08-01 to 2022-07-31 | 2 years |
| | Test | 2022-08-01 to 2025-07-31 | 3 years |
| **Futures** |
| | Training | 2018-01-01 to 2021-07-31 | 3.6 years |
| | Validation | 2021-08-01 to 2022-07-31 | 1 year |
| | Test | 2022-08-01 to 2024-01-01 | 1.4 years |

To ensure realistic backtesting conditions, we simulate per-share commission costs of $0.0075 with a minimum of $1.00 per trade, and implement volume-based slippage as a quadratic function of percentage of historical volume. All results are reported using a train-validation-test framework: strategies evolve on training data, the best-performing strategy on the validation set (measured by combined score) is selected, and final performance is evaluated on the held-out test period.

### 6.2 Baseline Strategies

For **equities**, we construct a market capitalization-weighted portfolio of the six stocks rebalanced monthly, and an equal-weighted portfolio strategy rebalanced daily. We also compare against three technical indicator-based strategies: Risk Parity (RP), Relative Strength Index (RSI), and Moving Average Convergence Divergence (MACD). These strategies represent common quantitative approaches and serve as active baselines. All strategies, including baselines and evolved strategies, apply identical transaction costs (0.075% commission) to ensure comparability.

For **futures**, we use individual buy-and-hold baselines for ES and NQ contracts. Each contract is sized with equal notional allocation at initialization based on price and point value, then held throughout the evaluation period. We report the average performance across both contracts as the aggregate baseline. While unified futures portfolio benchmarks are impractical due to heterogeneous contract specifications, this approach provides a fair reference for evaluating per-contract performance.

### 6.3 Evaluation Metrics

We evaluate strategies using four standard quantitative metrics and a composite objective for evolutionary selection.

#### 6.3.1 Individual Metrics

- **Sharpe Ratio (SR):** Risk-adjusted return measuring excess return per unit of volatility:  
  SR = (R̄_p - R_f) / σ_p  
  where R̄_p is average portfolio return, R_f is the risk-free rate (set to 0), and σ_p is return standard deviation.

- **Sortino Ratio (SOR):** Similar to Sharpe but penalizes only downside volatility:  
  SOR = (R̄_p - R_f) / σ_d  
  where σ_d is the standard deviation of negative returns.

- **Information Ratio (IR):** Benchmark-relative performance:  
  IR = (R̄_p - R̄_b) / σ_(p-b)  
  where R̄_b is benchmark return and σ_(p-b) is tracking error.

- **Maximum Drawdown (MDD):** Largest peak-to-trough decline:  
  MDD = min_t [(Trough_t - Peak_t) / Peak_t]

#### 6.3.2 Combined Score for Evolution

To guide evolutionary selection, we construct a composite objective balancing profitability, benchmark outperformance, and downside risk:

**Score = SR + IR + MDD** ... (3)

This formulation rewards both absolute (SR) and relative (IR) risk-adjusted returns while penalizing drawdown severity. The equal weighting (1:1:1) avoids overemphasizing any single dimension, encouraging strategies that balance consistent alpha generation with capital preservation. This composite objective transforms evolution from pure return maximization into a robust measure of long-term viability across market regimes.

---

## 7. Results in Equity Markets

### 7.1 Evolution of the Feature Map

Figure 5 presents three-dimensional projections of the feature map, enabling us to track its evolution across generations. We visualize the feature map using strategy category and max drawdown as the two axes, where each cell displays the strategy with the highest Sharpe ratio among all strategies sharing the same category and max drawdown bin.

At generation 0, the feature map consists exclusively of a buy-and-hold baseline and representative strategies from each predefined category, the details of which are provided in Table 6. As evolution progresses, the cells of the feature map gradually become populated with increasingly diverse strategies, and the performance within each cell shows consistent improvement. This visualization demonstrates both the exploratory capacity of the evolutionary process—filling previously empty regions of the strategy space—and its ability to refine solution quality within each niche over successive generations.

**Table 6: Strategy categories in equity markets**

| Category | Description |
|----------|-------------|
| Momentum/Trend | Momentum/Trend Following Strategies |
| Mean-Reversion | Mean Reversion Strategies |
| Volatility | Volatility-Based Strategies |
| Volume/Liquidity | Volume/Liquidity Analysis Strategies |
| Breakout/Pattern | Breakout/Pattern Recognition Strategies |
| Correlation/Pairs | Correlation / Pairs / Cross-Asset / Statistical Arbitrage Trading Strategies |
| Risk/Allocation | Risk Parity / Allocation / Risk Management Strategies |
| Seasonal/Calendar Effects | Seasonal/Calendar Effects Strategies |

Figure 6 presents the final generation's feature map visualizations across different dimension pairs, including number of transactions and cumulative return, among others, evaluated using the information ratio. Several noteworthy patterns emerge from these visualizations:

1. Strategies with higher cumulative returns tend to exhibit **moderate levels of maximum drawdown** rather than extreme values at either end of the spectrum. This inverted U-shaped relationship suggests a trade-off between risk-taking and return generation: strategies with excessively low maximum drawdown appear to operate conservatively, resulting in limited upside potential, while those with very high maximum drawdown may expose portfolios to excessive downside risk that undermines long-term compounding.

2. We observe a **positive association between Sharpe ratio and information ratio** across the feature map, which is intuitive given that both metrics evaluate risk-adjusted performance, albeit with different benchmark specifications.

These patterns indicate that the evolutionary process successfully identifies a diverse set of strategies occupying distinct regions of the risk-return space, rather than converging prematurely to a narrow subset of solutions.

### 7.2 Evolution of the Strategy

Figure 7 illustrates the evolutionary trajectory from generation 0 to 130, showing how the framework explores different strategy designs through iterative hypothesis testing.

- **Generation 0:** Employed volume-momentum signals.

- **Generation 10:** Expanded the signal space by incorporating momentum analysis across multiple timeframes, volatility filtering, and mean-reversion components. While this approach increased cumulative returns, the maximum drawdown expanded. Analysis suggested that the primary limitation had shifted from signal diversity to portfolio-level risk management: uniform weighting across assets did not account for differing volatility characteristics, and periodic rebalancing generated trades regardless of market conditions.

- **Generation 40:** Redirected focus toward risk management design. Rather than continuing to refine individual signals, this iteration introduced portfolio-wide volatility monitoring. It separated exit decisions from the monthly rebalancing schedule, enabling more responsive position management during adverse market movements. These changes reduced the maximum drawdown compared to generation 10, although the improvement in the Sharpe ratio remained modest.

- **Generation 80:** Explored an alternative approach based on cointegration pairs trading, testing whether relative-value strategies could offer different risk-return characteristics. This exploration failed to generate positive returns, primarily due to the unstable cointegration relationships during volatile periods.

- **Generation 130:** Selectively integrated insights from previous generations while maintaining implementation simplicity. The strategy retained volume-momentum signals as the core component, incorporated per-asset volatility adjustments to address the uniform weighting limitation identified in generation 10, and adopted continuous position monitoring rather than schedule-dependent exits as explored in generation 40. Notably, the framework avoided the complexity that contributed to the failure of generation 80. The resulting strategy is comprised of three straightforward components: momentum-based entry signals, volatility-scaled position sizing, and trailing stop-loss rules. This design contrasts with accumulating all features from each iteration, which would increase the parameter count and risk of overfitting.

This trajectory illustrates that strategy evolution in our framework proceeds through the **exploration of different design choices**, the **selective retention of practical components**, and the **prioritization of robustness over architectural complexity**.

### 7.3 Evolution of the Insights

Figure 8 presents the evolutionary process of the insights in equity markets.

- **Generation 10:** Identified that simple volatility indicators fail during market crises, and recognized the need to combine volatility z-scores with VIX or moving averages. Additionally, an alternative hypothesis emerged proposing sector diversification instead of signal refinement. This diversity of approaches prevented premature convergence on a single solution.

- **Generations 40-80:** Yielded specialized insights. For example, building on generation 10's observations, generation 40 found that growth stocks require sector-specific risk controls in high-volatility regimes. As migration progressed, the framework began to combine previously separate findings: VIX integration, asset-specific thresholds, and volatility modeling emerged together in unified insights. It also began distinguishing implementation errors from conceptual failures. For instance, it determined that regime detection mechanisms failed due to incorrect volatility annualization rather than flawed logic. Generation 80 integrated per-asset volatility thresholds with correlation effects, while new directions emerged investigating momentum persistence and market microstructure.

- **Generation 130:** Demonstrates insight consolidation and refinement. The framework documented over 30 failed approaches, including returns-based volatility detection, sector moving average filters, and various covariance estimation methods. Generation 10's insights evolved into detailed implementation specifications, such as requiring dynamic volatility thresholds to be computed per-asset rather than across the portfolio. Through experimental validation, the framework found several techniques used in quantitative finance practice, including multi-signal confirmation, Kalman filtering for beta estimation, and risk parity scaling.

### 7.4 Performance of the Strategies

In our study, we benchmarked the proposed framework against a set of widely adopted portfolio management approaches. The baseline methods comprised:
- **MarketCap:** A market capitalization-weighted portfolio rebalanced monthly (serves as the benchmark for information ratio calculations)
- **Equal:** An equal-weighted portfolio rebalanced daily
- **Risk Parity (RP):** Equalizes risk contributions across assets through inverse-volatility weighting
- **RSI:** A contrarian mean-reversion framework based on Relative Strength Index
- **MACD:** A momentum-following rule based on Moving Average Convergence Divergence

These baselines represent complementary investment paradigms—passive indexing, risk balancing, momentum persistence, and mean reversion—providing a rigorous basis for comparison.

**Table 4: Experimental results in equity markets**

| Model | SR | MDD | IR | CR |
|-------|-----|-----|-----|-----|
| **Baselines** |
| MarketCap | 0.99 | -33% | - | 99% |
| Equal | 1.07 | -36% | 0.80 | 129% |
| MACD | 1.10 | -39% | 0.75 | 171% |
| RSI | 1.03 | -37% | 0.39 | 136% |
| RP | 1.22 | -29% | 0.44 | 130% |
| **Ours** |
| Gen 0 | 0.99 | -35% | 0.03 | 100% |
| Gen 50 | 1.07 | -34% | 0.49 | 119% |
| Gen 100 | 1.11 | -32% | 0.87 | 128% |
| **Gen 150** | **1.52** | **-32%** | **0.69** | **256%** |

Table 4 shows that our framework achieves **competitive out-of-sample test performance**, demonstrating favorable results across both SR and CR relative to the baseline strategies. These results suggest that evolutionary frameworks can be effectively applied to quantitative research and automated strategy generation.

---

## 8. Results in Futures Markets

### 8.1 Evolution of the Strategy

Figure 9 illustrates the evolutionary trajectory in ES futures trading.

- **Generation 0:** Employed static mean reversion with fixed Bollinger Band thresholds and time-based exits, suffering from the inability to adapt to regime changes.

- **Generation 10:** Introduced dynamic volatility scaling and momentum confirmation. By calculating adaptive Z-scores from rolling volatility and requiring directional momentum alignment, it prevented counter-trend trades during strong moves. ATR-based position sizing and contract roll management substantially reduced drawdown, though performance remained inconsistent across regimes.

- **Generation 20:** Implemented a **dual-mode system** with explicit regime detection. During low-volatility periods, it applied mean-reversion with adaptive Bollinger Bands (2σ to 3σ) and volume confirmation; during high-volatility regimes, it switched to momentum-following with trend filters. Rolling ATR quantiles and sigmoid transitions enabled smooth regime adaptation.

Despite evolution continuing through generation 100, **generation 20 achieved superior out-of-sample performance**. Later generations introduced increasingly complex mechanisms—ADX regime detection, multi-signal systems—that degraded generalization. Generation 20's balance between adaptive sophistication and implementation parsimony exemplifies successful navigation of the bias-variance tradeoff.

### 8.2 Evolution of the Insights

Figure 10 shows the accumulation of strategic knowledge.

- **Generation 10:** Identified that static volatility thresholds fail during regime transitions and documented that ATR-based position sizing reduces drawdowns more effectively than fixed contract allocation. It also recognized the importance of momentum confirmation to avoid premature mean-reversion entries.

- **Generation 20:** Synthesized these findings into regime-specific insights: low-volatility environments favor mean-reversion with tight bands, while high-volatility periods require momentum-following with wider thresholds. It discovered that volume confirmation prevents false signals during low-liquidity periods and that trailing stops should scale with current ATR rather than entry-time volatility. Critically, it documented failed approaches including returns-based regime detection and fixed holding periods, preventing future iterations from repeating these errors.

By generation 20, the framework had established that regime-aware systems outperform static rules in futures markets, that smooth transitions between modes reduce whipsaws, and that implementation simplicity often trumps theoretical sophistication.

### 8.3 Performance on Futures Markets

To demonstrate QuantEvolve's scalability across asset classes, we applied the framework to ES and NQ futures contracts. Table 5 and Fig. 11 present the results.

**Table 5: Performance on futures test set (Aug 2022 - Jan 2024)**

| Model | SR | MDD | IR | CR |
|-------|-----|-----|-----|-----|
| **Baseline** |
| B&H ES | 0.66 | -16.7% | - | 14.4% |
| B&H NQ | 0.97 | -21.6% | - | 31.3% |
| **Ours** |
| Gen 0 | -1.21 | -26.1% | -1.36 | -25.4% |
| Gen 10 | -0.41 | -15.0% | -0.76 | -7.1% |
| **Gen 20** | **1.03** | **-15.4%** | **0.49** | **37.4%** |

The futures results demonstrate QuantEvolve's ability to generate effective strategies across asset classes with distinct characteristics. Generation 0's poor performance (SR=-1.21, CR=-25.4%) confirms that naive mean-reversion fails in trending futures markets. The framework rapidly adapted: generation 10 substantially reduced drawdown to -15.0%, while generation 20 achieved positive risk-adjusted returns (SR=1.03) that exceeded both ES (SR=0.66) and NQ (SR=0.97) baselines.

Notably, the evolved strategy delivered **37.4% cumulative return** compared to 14.4% for ES and 31.3% for NQ, with lower maximum drawdown than the NQ baseline (-15.4% vs -21.6%). The Information Ratio of 0.49 indicates consistent outperformance relative to the baseline, validating that the hypothesis-driven evolutionary process successfully identified regime-adaptive mechanisms suited to futures market dynamics. This cross-asset generalization—without manual recalibration of the framework—supports QuantEvolve's potential for scalable automated strategy discovery across diverse financial instruments.

---

## 9. Ablation Study

### 9.1 Feature Bin Sizes

To investigate the impact of bin size on evolutionary dynamics, we conducted an ablation study comparing three configurations: **1-bin, 4-bin, and 16-bin** per feature dimension. The bin size determines the resolution of the feature map, directly influencing the balance between diversity maintenance and selection pressure.

Figure 12 presents the evolution of test performance across generations for different bin size configurations:

- The **16-bin configuration** exhibits sustained improvement throughout the evolutionary process, achieving a Sharpe ratio of 1.52 and a cumulative return of 256% by generation 150. This trajectory demonstrates continuous exploration and refinement, with performance gains accelerating in later generations.

- In contrast, both **1-bin and 4-bin configurations** display early convergence followed by performance stagnation or degradation. The 1-bin setting begins with relatively strong initial performance (SR = 1.24, CR = 191%) but fails to sustain improvement beyond generation 50, ultimately declining to SR = 1.12 and CR = 150% by generation 150. The 4-bin configuration follows a similar pattern.

These results suggest that **insufficient bin resolution leads to premature convergence** by constraining niche diversity. When the feature map contains too few cells, strategies with distinct behavioral characteristics are forced to compete within the same niche, eliminating potentially valuable exploration directions. Furthermore, the sustained performance of the 16-bin configuration indicates that higher bin resolution enables the preservation of diverse strategy populations, potentially reducing the risk of overfitting.

### 9.2 Feature Dimensions

To examine the impact of including the strategy category as a feature dimension, we compare two evolutionary runs: one excluding the category dimension (Figure 13a) and one including it (Figure 13b).

**Without the category dimension**, the most dominant bin accounts for **46.3%** of all strategies, indicating a strong bias toward specific strategy categories. This concentration suggests limited strategic diversity, with the evolutionary process favoring specific categories disproportionately. Consequently, the framework may fail to adequately explore diverse strategic approaches, instead converging prematurely on a narrow subset of solution types.

**In contrast, including the category dimension** results in a more balanced distribution, with the top category accounting for only **17.9%** of strategies. This more equitable allocation indicates that incorporating strategy category as a feature dimension effectively **promotes population diversity** and reduces the risk of premature convergence, enabling the evolutionary process to explore a broader range of strategic paradigms.

---

## 10. Discussion

### Robustness and Overfitting
This study focuses on applying evolutionary frameworks to quantitative finance; consequently, comprehensive robustness testing remains an area for improvement. As such, strategies generated by the framework may be susceptible to data snooping bias. Future work will integrate more sophisticated and rigorous validation methodologies.

### Hypothesis Quality
We have not formally validated whether generated hypotheses reflect established market theories or provide post-hoc rationalizations for data-mined patterns. Future work should incorporate external validation mechanisms—comparison against academic literature, expert review, or causal inference frameworks—to verify hypotheses represent meaningful insights.

### LLM Inference Cost
Each evolutionary cycle requires 5-10 LLM inferences. This limits scalability for resource-constrained settings.

### Evaluation Scope
Our evaluation uses six equities and two futures over limited date ranges with relatively simple baselines. While adequate for demonstrating comparative performance, these baselines do not represent state-of-the-art quantitative approaches. Future work should evaluate against sophisticated benchmarks and expand to larger asset universes with longer time horizons.

Fully automated quantitative research remains an open challenge. While QuantEvolve demonstrates the feasibility of an evolutionary framework for generating diverse strategies, substantial work is needed to ensure robustness, validate the quality of hypotheses, and bridge the research-to-deployment gap.

---

## 11. Conclusion

We present **QuantEvolve**, a multi-agent-aided evolutionary framework that systematically generates diverse, high-performing trading strategies. QuantEvolve employs a feature map that preserves population diversity across feature dimensions relevant to investor needs, and utilizes a multi-agent system to effectively explore a high-dimensional search space of trading strategies through hypothesis-driven reproduction. By combining evolutionary computation's exploration with structured hypothesis-driven reasoning, QuantEvolve bridges the gap between broad discovery and deep, theoretically-grounded refinement.

Our empirical evaluation across equity and futures markets demonstrates that QuantEvolve produces diverse strategies with distinct behavioral characteristics, suggesting our framework can complement human expertise by exploring combinations and inefficiencies at scales infeasible for manual research. By generating strategies across the full spectrum of risk profiles and trading philosophies, QuantEvolve enables personalized asset management adapting to individual constraints—a capability increasingly demanded yet underserved by existing platforms.

---

## 12. Disclaimer

This framework is intended for research purposes only. Users are solely responsible for validating all generated strategies and assessing their suitability for specific use cases. The framework's outputs do not reflect the opinions of Qraft Technologies. Qraft Technologies assumes no liability for any outcomes resulting from the use of this framework.

---

## References

[1] Ran Aroussi. 2024. QuantStats: Portfolio Analytics for Quants. https://github.com/ranaroussi/quantstats

[2] Ahmed BenSaïda. 2015. The frequency of regime switching in financial market volatility. Journal of Empirical Finance 32 (2015), 63–79.

[3] Md. Abul Bhuiyan et al. 2025. Deep learning for algorithmic trading: A systematic review. Finance Research Letters 66 (2025), 104123.

[4] Cerulli Associates. 2025. Direct Indexing Assets Close Year-End 2024 at $864.3 Billion.

[5] Farah Dakalbab et al. 2024. Artificial intelligence techniques in financial trading. Journal of King Saud University - Computer and Information Sciences 36, 6 (2024).

[6] Sorouralsadat Fatemi and Yuheng Hu. 2024. FinVision: A multi-agent framework for stock market prediction. In Proceedings of the 5th ACM International Conference on AI in Finance. 582–590.

[7] Jian Guo et al. 2024. Quant 4.0: engineering quantitative investment with automated, explainable, and knowledge-driven artificial intelligence. Frontiers of Information Technology & Electronic Engineering 25, 11 (2024).

[8] Taian Guo et al. 2025. MASS: Multi-Agent Simulation Scaling for Portfolio Construction. arXiv preprint arXiv:2505.10278.

[9] Minh Le. 2025. Quantitative Trading, Discretionary Trading, Hedge Funds: Traditional Traders vs. Quant Traders. SSRN Electronic Journal.

[10] Yuante Li et al. 2025. R&D-Agent-Quant: A Multi-Agent Framework for Data-Centric Factors and Model Joint Optimization. arXiv preprint arXiv:2505.15155.

[11] Xiao-Yang Liu et al. 2023. Fingpt: Democratizing internet-scale data for financial large language models. arXiv preprint arXiv:2307.10485.

[12] Chris Lu et al. 2024. The ai scientist: Towards fully automated open-ended scientific discovery. arXiv preprint arXiv:2408.06292.

[13] Jean-Baptiste Mouret and Jeff Clune. 2015. Illuminating search spaces by mapping elites. arXiv preprint arXiv:1504.04909.

[14] Alexander Novikov et al. 2025. AlphaEvolve: A coding agent for scientific and algorithmic discovery. arXiv preprint arXiv:2506.13131.

[15] Philip Treleaven et al. 2013. Algorithmic Trading Review. Commun. ACM 56, 11 (2013), 76–85.

[16] Jun Tu. 2010. Is regime switching in stock returns important in portfolio decisions? Management Science 56, 7 (2010), 1198–1215.

[17] Saizhuo Wang et al. 2024. Quantagent: Seeking holy grail in trading by self-improving large language model. arXiv preprint arXiv:2402.03755.

[18] Saizhuo Wang et al. 2023. Alpha-gpt: Human-ai interactive alpha mining for quantitative investment. arXiv preprint arXiv:2308.00016.

[19] Yahoo Finance. 2025. Robo Advisor Market Projected to Reach USD 3.2 Trillion by 2030.

[20] An Yang et al. 2025. Qwen3 technical report. arXiv preprint arXiv:2505.09388.

[21-29] [Additional references continue in similar format...]

---

## Appendices

### A. Multi-agent Evolution Prompts

[The document contains detailed prompts for Data Agent, Strategy Agent, Code Team, and Evaluation Team - these are preserved in the code blocks in the original document]

### B. Baseline Strategy Codes for Equity Markets

[The document contains complete Python implementations for Equal-Weighted Rebalancing, MACD, RSI & KDJ, and Risk Parity strategies - these are preserved in the code blocks in the original document]

---

**Algorithm 1: QuantEvolve**

```
Input: Number of islands N, generations G, migration interval M, 
       insight curation interval K, feature dimensions D, bin sizes B, 
       exploitation-exploration balance α ∈ [0,1]

1. Initialize feature map F with dimensions D and bin sizes B
2. Initialize evolutionary database DB
3. Initialize N islands with seed strategies using DataAgent
4. Initialize insight repository I ← ∅

5. for generation g = 0 to G-1 do
6.   for each island I_i where i ∈ {1,...,N} do
7.     s_p ← SampleParent(I_i, DB, α)
8.     C ← SampleCousins(s_p, I_i, DB)
9.     h ← ResearchAgent(s_p, C, I)
10.    (c,m) ← CodingTeam(h, s_p, C)
11.    a ← EvaluationTeam(h, c, m)
12.    s_new ← (h, c, m, a)
13.    f ← ComputeFeatures(s_new)
14.    UpdateDatabase(s_new, f, DB, I_i)
15.    I ← I ∪ {a}
16.  end for
17.  if g mod M = 0 and g > 0 then
18.    MigrateStrategies({I_1,...,I_N}, DB)
19.  end if
20.  if g mod K = 0 and g > 0 then
21.    I ← ManageInsights(I)
22.  end if
23. end for
24. return DB
```

---

*End of Document*