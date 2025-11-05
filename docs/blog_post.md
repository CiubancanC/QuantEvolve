# Teaching AI to Evolve Trading Strategies: Our Journey Building QuantEvolve

Ever wondered if AI could discover profitable trading strategies on its own? Not by following pre-programmed rules, but by actually *evolving* strategies through trial, error, and collective learning?

That's exactly what we set out to build with QuantEvolve. After 150 generations of evolution, the system discovered 363 unique strategies—including several that would have turned $10,000 into $50,000+ during backtests. The entire evolution cost $20 in API fees.

**But here's the real question: do AI-evolved strategies work in live markets?** We've built the infrastructure for paper trading and are preparing to test these strategies against real-time market conditions. We're about to find out if backtested brilliance survives contact with reality.

## The Challenge: Finding Needles in an Infinite Haystack

Here's the problem: the space of possible trading strategies is practically infinite. You could combine momentum indicators with volatility filters, add some mean-reversion logic, sprinkle in volume analysis... the combinations never end. Traditional approaches either rely on human intuition (slow, biased) or brute-force parameter sweeps (expensive, shallow).

We needed something smarter. Something that could *think* about what makes a good strategy, learn from failures, and systematically explore diverse approaches without getting stuck in local optima.

## Enter: Evolutionary AI with a Hypothesis-Driven Twist

Our implementation is based on the recent QuantEvolve research paper (Yun et al., 2025), and it combines two powerful ideas:

### 1. **Quality-Diversity Optimization**

Instead of searching for the single "best" strategy, we maintain a diverse population across multiple dimensions—think of it as a strategic ecosystem. We organize strategies in a multi-dimensional feature map by their characteristics:
- Risk profiles (Sharpe ratio, Sortino ratio, max drawdown)
- Trading styles (momentum, mean-reversion, volatility-based)
- Activity levels (from conservative rebalancing to active trading)

Each cell in this map stores the best strategy for that particular combination of features. This prevents the evolution from converging prematurely and gives us a rich palette of strategies suited for different market conditions and investor preferences.

### 2. **Multi-Agent LLM System**

Here's where it gets interesting. Instead of random mutations, our strategies evolve through structured reasoning. We built a team of specialized AI agents powered by Qwen language models:

**The Data Agent** analyzes market data patterns and generates seed strategies to kickstart evolution.

**The Research Agent** acts like a quantitative researcher, formulating testable hypotheses: "What if we combine volume momentum with volatility-adjusted position sizing? Here's why it might work, what we expect to learn, and potential failure modes."

**The Coding Team** implements these hypotheses into executable Python strategies, runs backtests, and iteratively debugs issues—complete with realistic transaction costs (commission + volume-based slippage).

**The Evaluation Team** analyzes results, extracts insights about what worked (and what didn't), and builds up institutional knowledge that guides future generations.

This hypothesis-driven approach means every strategy has a *reason* for existing—a clear lineage of ideas we can trace and understand.

## The Evolution Process: Islands of Innovation

We use an "island model" where 8 populations evolve independently, each starting from different strategy categories (momentum, mean-reversion, volatility, correlation trading, etc.). Every 10 generations, the best strategies migrate between islands, enabling hybrid approaches while maintaining diversity.

Every generation follows this cycle:
1. Sample a parent strategy (balancing exploitation of good performers with exploration of diverse niches)
2. Sample "cousin" strategies—some from the elite, some diverse, some random
3. Research Agent generates a hypothesis building on these influences
4. Coding Team implements and backtests (with automatic debugging if needed)
5. Evaluation Team extracts insights and validates the strategy
6. Add to feature map if it's the best for its particular niche

Over 150 generations, the system explores hundreds of strategy variations, accumulating insights and systematically filling the feature map with diverse, high-quality strategies.

## Our Results: Real Performance on Real Data

Building QuantEvolve taught us as much about AI systems as it did about trading strategies. After running 150 generations of evolution on real 10-year market data (AAPL, NVDA, AMZN, GOOGL, MSFT, TSLA), here's what we discovered:

### The Numbers: 363 Strategies, Real Profits

The evolutionary system generated **363 unique strategies** that made it onto the feature map. Here's the bottom line:

**Top 3 Performers:**
- **🏆 Best Strategy (Volatility-based)**: 556.59% return
  - Turned $10,000 → $65,659.50
  - Sharpe ratio: 3.68 (exceptional risk-adjusted returns)
  - Max drawdown: -5.77% (incredibly low risk)
  - 172 trades over the validation period

- **🥈 Second Place (Volume/Liquidity)**: 433.41% return
  - Turned $10,000 → $53,341.36
  - Sharpe ratio: 3.46
  - Max drawdown: -5.73%
  - 117 trades

- **🥉 Third Place (Breakout/Pattern)**: 397.62% return
  - Turned $10,000 → $49,761.76
  - Sharpe ratio: 1.25
  - Max drawdown: -36.37%
  - Only 2 trades (higher risk due to small sample size)

**Overall Performance:**
- **80.2% of strategies were profitable** (291 out of 363)
- Average return across all strategies: 21.61%
- 20 strategies achieved 67%+ returns (nearly doubling capital or better)
- Average $10,000 investment → $12,161

### Context: An Exceptional Period

Let's be clear: **2020-2022 was an extraordinary time for markets**. This was the COVID crash followed by massive recovery, then the tech bubble peak. Our validation period (Aug 2020 - Jul 2022) captured extreme volatility where well-timed entries and exits could generate outsized returns.

**The real test** is whether these strategies adapt to 2025's market conditions. That's exactly why we're moving to paper trading rather than claiming victory based on backtests alone. These numbers represent what *might have been* possible during that specific period—not what *will be* possible going forward.

### The Multiple Testing Problem

We tested 363 strategies. By pure chance alone, we'd expect some to show impressive results even if they were randomly generated. This is the multiple testing problem that plagues quantitative research.

**Our safeguards:**
- **Hypothesis coherence**: Every strategy has a documented rationale, not just random combinations of indicators
- **Out-of-sample validation**: Train (2015-2020), validation (2020-2022), and test (2022-2025) periods
- **Trade frequency validation**: Strategies must make ≥10 trades/year (adjusted by category) to avoid statistical noise
- **Live trading phase**: The ultimate test—do these strategies generate signals that make sense in real-time?

We're not claiming these strategies will definitely work. We're claiming they passed our evolutionary filter and deserve real-world testing. That's a meaningful distinction.

### Transaction Cost Assumptions Matter

With 172 trades, our top strategy's returns are heavily dependent on transaction cost assumptions. Here's what we modeled:

**Per-trade costs:**
- Commission: $0.0075/share + $1.00 minimum per trade
- Slippage: Quadratic function based on traded volume as percentage of daily volume
- Total effective cost: ~0.10% for larger positions in liquid stocks, up to 0.25% for smaller positions where the $1 minimum dominates

These assumptions are **conservative for the stocks we tested** (AAPL, NVDA, etc. have deep liquidity), but they may underestimate costs for:
- Smaller positions where the $1 minimum dominates
- Faster strategies with higher turnover
- Less liquid names or extended hours trading
- Market impact during high volatility periods

The paper trading phase will reveal the true cost structure. If our assumptions were optimistic, returns will compress—potentially significantly.

**Cost to Generate?** The entire 150-generation evolution run cost approximately **$20 in API fees** (using Qwen models via OpenRouter). But let's be honest about the full cost:

- **LLM API fees**: $20 (the cheap part)
- **Data subscription**: $0 (we used free Yahoo Finance data with its limitations)
- **Development time**: ~100+ hours building the infrastructure
- **Compute**: Negligible (runs on a laptop)
- **The hard part**: Building reliable backtesting, handling edge cases, debugging strategies that fail in creative ways

Traditional quant shops pay $150K-500K salaries for researchers to develop a handful of strategies per year. We generated 363 testable hypotheses for $20 in LLM costs. The infrastructure investment pays dividends once it's built.

### The System Works—And Real Markets Are Harder Than Synthetic Data

Our initial tests with synthetic data were smooth. The evolution completed quickly, strategies looked reasonable, and metrics were impressive. Then we ran it on real market data and hit reality.

Real markets are *messy*. Strategies that looked perfect on paper failed with NaN errors. Datetime comparisons broke. API calls timed out. We discovered that about 48% of strategies were being rejected for having too few trades—not because they were bad, but because our validation was too rigid.

### What the System Learned NOT to Do

Beyond the successes, we encountered important failure modes that shaped our approach:

**The Low-Sample Problem**
Early in evolution, we saw strategies with spectacular returns (400%+) but only 2-4 trades total. Statistically meaningless, but they'd dominate cells in the feature map. This taught us to implement trade frequency validation (≥10 trades/year, adjusted by category) to filter out over-fitted noise.

**The NaN Propagation Problem**
We encountered strategies that failed during backtesting due to division by near-zero values (volatility calculations during low-volume periods) creating NaN values that cascaded through the signal generation. This led us to add defensive signal validation checking for NaN, infinity, and extreme values before execution.

**The Over-Filtering Problem**
Some strategies combined multiple filters that, when stacked, resulted in only a handful of qualifying trading days across the entire validation period. While those few trades might look perfect, the strategy wasn't practically useful. We adjusted our evaluation to penalize excessive filtering and prefer strategies that trade more regularly.

These patterns emerged repeatedly across generations, teaching the system (and us) valuable lessons about robustness over cleverness.

### The Importance of Smart Safeguards

One of our biggest improvements beyond the paper was category-aware trade frequency validation. A risk allocation strategy that rebalances quarterly (4 trades/year) is perfectly valid, while a momentum strategy with 4 trades/year is probably over-fitted. We adjusted our thresholds by strategy category, which dramatically reduced false rejections while still filtering out statistical noise.

We also added robust signal validation to handle edge cases—NaN values from indicator warm-up periods, infinite values from division errors, timezone mismatches between data sources. The LLM-generated code isn't always perfect, so we added defensive layers that fail gracefully rather than crashing the evolution.

### The Diversity Advantage

The feature map's diversity proved invaluable. Instead of converging to a single "best" strategy, we ended up with a portfolio of 363 distinct approaches across different categories:

**By Strategy Type:**
- **Volatility strategies**: Including our top performer with 556% return and only -5.77% max drawdown
- **Volume/Liquidity strategies**: 433% return with excellent risk metrics
- **Breakout/Pattern strategies**: Multiple strategies with 70-397% returns
- **Risk/Allocation strategies**: 226% return with 385 trades (active rebalancing)
- **Momentum/Trend strategies**: 68-92% returns with moderate risk
- **Correlation/Pairs strategies**: 186% return with minimal -2.12% drawdown
- **Seasonal/Calendar strategies**: 68% return with good Sharpe ratios

Different strategies dominate in different market regimes. Our top 20 strategies span multiple categories, proving that there's no single "best" approach—the optimal strategy depends on your risk tolerance, holding period, and market conditions. Having this diversity means we can select strategies matching specific investor preferences or even combine them into ensembles for more robust performance.

**But are these truly diverse, or just variations on a theme?** That's a valid question. The feature map's multi-dimensional structure is designed to maintain diversity across risk profiles, trading frequencies, and strategy categories—not just optimize for a single objective.

This matters because ensemble approaches rely on combining uncorrelated strategies. A portfolio of 10 highly correlated strategies isn't more robust than one—it's just the same bet with different names. Our binary category encoding (8 bits = 256 possible category combinations) allows strategies to span multiple categories simultaneously, creating genuinely hybrid approaches rather than forcing them into single buckets.

### LLM-Driven Evolution Is Surprisingly Coherent

We were initially skeptical about using LLMs for strategy generation. Would they just produce random combinations? Would quality degrade over generations?

Surprisingly, no. The hypothesis-driven approach keeps things grounded. The Research Agent builds on accumulated insights, avoiding known failure modes and exploring logical extensions of successful ideas. We saw genuine innovation: strategies that started as simple momentum indicators evolved to incorporate volatility adjustments, cross-asset correlations, and adaptive position sizing.

**Example: Our Top Strategy's Hypothesis**

Our best-performing strategy (556% return) demonstrates this coherence. The Research Agent's hypothesis was:

> "When a stock closes within 1.2% of its 3-day high for one consecutive day (single-day resistance test), this indicates a localized momentum buildup without excessive crowding. Enter long positions when this condition is met, as it suggests buyers are present but not yet exhausted."

This isn't random—it's a testable market theory about how price behavior near short-term highs can signal continuation rather than reversal. The strategy evolved from earlier generations that explored the relationship between proximity to recent highs and subsequent performance, refining the threshold (1.2% vs 1.5% or 2.0%) and the lookback period (3 days vs 5 or 10) through systematic experimentation.

**Here's what's notable: the top performers were often relatively simple, focused ideas executed consistently** rather than complex multi-indicator combinations. This aligns with quantitative trading wisdom that disciplined simplicity often beats clever complexity.

The key was giving the LLM *context*—not just parent strategies, but also insights from the entire evolutionary history. It's like having an institutional memory that accumulates over generations, with the Research Agent building on proven concepts and learning from documented failures.

## What's Coming Next: From Backtest to Reality

Here's where things get exciting—and a bit nerve-wracking. We have real strategies with real performance: 556% returns, 80% success rate, and strategies spanning multiple market approaches. Now we need to see if they work in live markets.

### Demo Trading with Alpaca

We've built the infrastructure to test our evolved strategies in real market conditions using Alpaca's trading API. With 363 validated strategies in hand—including several that turned $10k into $50k+ in backtests—we're planning a phased rollout:

**Phase 1: Signal Checking (Now)**
We're already running our best strategies against live data daily, generating signals and comparing them to actual market movements. This gives us a reality check—do our backtested strategies still make sense with real-time data?

**Phase 2: Paper Trading (Coming Soon)**
We'll execute trades automatically in Alpaca's paper trading environment. No real money at risk, but complete simulation of order execution, partial fills, market impact, and all the messy details that backtests can't fully capture.

**Phase 3: Live Micro-Trading (Planned)**
If paper trading validates our approach, we'll run live trades with small capital ($1,000-$5,000) to test the full pipeline—including psychological factors like watching real money move. This is where theory meets reality.

**Phase 4: Strategy Refinement**
The feedback loop here is crucial. We'll feed real-world performance back into the evolutionary system, treating live trading results as the ultimate validation set. Strategies that backtest well but fail in practice will teach the system about hidden market realities.

### What We're Watching For

The transition from backtest to live trading is treacherous. Our top strategy showed 556% returns with a 3.68 Sharpe ratio in historical data—but here's what could go wrong:

- **Overfitting**: Strategies might be too tuned to 2020-2022 market patterns that no longer hold in 2025
- **Execution Differences**: Real slippage and market impact might differ from our transaction cost models
- **Market Regime Change**: The strategies evolved during a specific period—will they adapt to new market conditions?
- **Scale Effects**: Our backtests assume small position sizes—what happens with real capital and order execution?
- **Psychological Reality**: One thing backtests can't simulate: the emotional experience of watching a strategy lose money in real-time, even if it's mathematically expected

The good news? We have 363 strategies to choose from, spanning different risk profiles and market approaches. If one fails, we can rotate to others or ensemble them for more robust performance.

But that's exactly why we're doing this systematically. Each phase will teach us something new, and we'll feed those lessons back into the evolution.

### Technical Details: Data and Reproducibility

For those wondering "can I actually run this?"—yes, but with some caveats:

**Data source**: We used free Yahoo Finance data via the `yfinance` Python library. This means:
- Split-adjusted daily OHLCV data (critical—unadjusted data will show false breakouts at split dates)
- Limited to stocks with good Yahoo coverage (large-caps work great, obscure tickers may have gaps)
- No survivorship bias handling (delisted companies aren't included)
- Timezone: Market close times (typically ET for US equities)

**Computational requirements**:
- Runs on a laptop (we used a MacBook Pro)
- ~8-12 hours for 150 generations with 8 islands
- No GPU required (all LLM inference via API)
- RAM: ~4-8GB depending on data size

**API keys needed**:
- OpenRouter API key for LLM inference (Qwen models)
- Optional: Alpaca API key for paper/live trading

The entire codebase is open source. You can replicate our run, test on different assets (crypto? futures?), or modify the evolution parameters. We've tried to make it as accessible as possible—no proprietary data vendors or expensive infrastructure required.

### Open Questions We're Exploring

**Can strategies adapt to regime changes?** We're considering periodic re-evolution—running new generations quarterly to adapt to evolving markets.

**Should we ensemble or select?** Do we pick the single best strategy, or combine multiple strategies to balance their strengths?

**How much human oversight?** The system can run autonomously, but should it? We're exploring hybrid approaches where the system proposes trades and humans approve.

## Similar Systems in Other Domains

Evolutionary approaches combined with AI aren't unique to trading. We're seeing similar systems emerge across domains:

**Drug Discovery**: AI-driven systems evolve molecular structures, using models to predict binding affinity and diversity metrics to explore chemical space systematically—discovering drug candidates humans might never have considered.

**Robotics**: Quality-diversity algorithms discover diverse locomotion gaits for robots. Some optimize for speed, others for energy efficiency, others for robustness to terrain variations. The result: robot controllers that adapt to damage or changing conditions.

**Game AI**: The AI Scientist project (which inspired part of our approach) uses LLMs to automatically generate and test machine learning research ideas, evolving better algorithms through iterative experimentation and paper writing.

**Engineering Design**: Generative design systems explore vast design spaces for aircraft components, antenna designs, and structural optimization—maintaining diversity while optimizing for multiple objectives like weight, strength, and manufacturability.

The common thread? **Combining evolutionary search (for exploring vast spaces) with learned models (for intelligent guidance) creates systems that discover solutions humans might never imagine.** It's not human vs. AI—it's human + AI exploring possibilities together.

## The Bigger Picture: Collaborative Intelligence

What excites us most isn't just building a profitable trading system—it's demonstrating a new paradigm for AI-assisted discovery.

Traditional AI is about prediction: given X, predict Y. But many real-world problems are about *search*: exploring vast possibility spaces to find solutions that didn't exist before. Trading strategies, drug molecules, engineering designs, even business models—these aren't prediction problems, they're search problems.

QuantEvolve shows that combining evolutionary algorithms (systematic exploration) with LLMs (intelligent reasoning) creates something powerful: AI that can **discover, explain, and improve** solutions autonomously.

The strategies it creates aren't black boxes—each comes with a hypothesis, rationale, and clear ancestry. We can trace why a strategy exists, what assumptions it makes, and where it might fail. This transparency is crucial for trust, debugging, and genuine understanding.

## Try It Yourself

We've open-sourced the entire implementation. If you're curious about evolutionary AI, quantitative trading, or just want to see LLMs do something more interesting than answer questions, check out the project:

**GitHub**: [QuantEvolve Repository](https://github.com/CiubancanC/QuantEvolve)

You can run a quick demo with synthetic data in minutes, or dive deep with real market data. The system is modular—want to evolve strategies for crypto instead of equities? Swap the data source. Prefer different strategy categories? Update the config. Want to use different LLMs? Change two lines.

We're just getting started, and we'd love to hear from others exploring evolutionary AI, quantitative trading, or the intersection of LLMs and systematic search.

## Final Thoughts

Building QuantEvolve has been a journey through the frontier of AI capabilities. We've seen LLMs reason about financial markets, debug their own code, and build on collective knowledge across generations. We've watched evolutionary algorithms systematically explore strategy space, maintaining diversity while climbing fitness landscapes.

The results speak for themselves: 363 unique strategies, 80% profitable, with the top performer achieving 556% returns at a 3.68 Sharpe ratio. These aren't incremental improvements over existing approaches—they're entirely novel strategies discovered through AI-driven exploration.

But the real excitement is in what comes next. As we move from backtest to paper trading to live trading, we'll learn whether these AI-discovered strategies can survive contact with reality. We'll discover the gap between simulated and actual markets. And we'll feed all those lessons back into the system, making it smarter with each iteration.

The future of quantitative trading might not be about humans discovering strategies or AI predicting markets—it might be about AI systems that evolve strategies while humans provide guidance, oversight, and strategic direction. A collaboration where each brings their strengths: AI's tireless exploration and pattern recognition, humans' intuition and real-world judgment.

Stay tuned. The evolution is just beginning.

---

*Want updates on our paper trading results? Follow our journey as we take these evolved strategies from backtest to reality. The next post will cover our first month of paper trading—lessons learned, surprises discovered, and whether AI-evolved strategies can actually make money in live markets.*

*Have questions or ideas? Reach out—we're always excited to discuss evolutionary AI, trading systems, or creative applications of LLMs.*
