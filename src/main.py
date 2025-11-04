"""
Main QuantEvolve evolution loop
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from tqdm import tqdm

from .utils.config_loader import load_config, Config
from .utils.logger import setup_logger, get_logger
from .utils.llm_client import create_llm_client, LLMEnsemble
from .core.feature_map import create_feature_map_from_config
from .core.evolutionary_database import EvolutionaryDatabase
from .agents.data_agent import DataAgent
from .agents.research_agent import ResearchAgent
from .agents.coding_team import CodingTeam
from .agents.evaluation_team import EvaluationTeam
from .backtesting.improved_backtest import ImprovedBacktestEngine
from .utils.data_prep import verify_data, create_sample_data


class QuantEvolve:
    """
    Main QuantEvolve system orchestrating the evolutionary process
    """

    def __init__(self, config: Config, use_sample_data: bool = False):
        """
        Initialize QuantEvolve

        Args:
            config: Configuration object
            use_sample_data: If True, create and use synthetic data
        """
        self.config = config
        self.logger = get_logger()

        self.logger.info("=" * 80)
        self.logger.info("Initializing QuantEvolve")
        self.logger.info("=" * 80)

        # Setup data
        if use_sample_data:
            self.logger.info("Creating sample data...")
            create_sample_data()

        # Initialize LLM
        self.logger.info("Initializing LLM client...")
        llm_config = config.get('llm', {})
        llm_client = create_llm_client(llm_config)
        self.llm_ensemble = LLMEnsemble(llm_client)

        # Initialize backtesting engine (using improved engine)
        self.logger.info("Initializing improved backtesting engine...")
        data_dir = config.get('data_path', './data/raw')

        # Get period definitions from config (assume equities for now)
        periods = config.get('backtesting.periods.equities', {})

        self.backtest_engine = ImprovedBacktestEngine(
            data_dir=data_dir,
            initial_capital=config.get('backtesting.initial_capital', 100000),
            commission_pct=config.get('backtesting.commission', 0.001),  # 0.1%
            slippage_pct=0.0005,  # 0.05%
            risk_free_rate=0.02,  # 2%
            train_start=periods.get('train_start'),
            train_end=periods.get('train_end'),
            val_start=periods.get('val_start'),
            val_end=periods.get('val_end'),
            test_start=periods.get('test_start'),
            test_end=periods.get('test_end')
        )
        self.logger.info(f"Backtesting on {len(self.backtest_engine.symbols)} symbols")

        # Initialize agents
        self.logger.info("Initializing agents...")
        self.data_agent = DataAgent(self.llm_ensemble)
        self.research_agent = ResearchAgent(self.llm_ensemble)
        self.coding_team = CodingTeam(self.llm_ensemble, self.backtest_engine)
        self.evaluation_team = EvaluationTeam(self.llm_ensemble)

        # Initialize feature map
        self.logger.info("Creating feature map...")
        self.feature_map = create_feature_map_from_config(config.raw)

        # Initialize evolutionary database
        self.categories = config.get('strategy_categories', [])
        self.num_islands = len(self.categories) + 1  # +1 for benchmark

        self.logger.info("Creating evolutionary database...")
        self.evol_db = EvolutionaryDatabase(
            feature_map=self.feature_map,
            num_islands=self.num_islands,
            categories=self.categories
        )

        # Evolution parameters
        self.num_generations = config.get('evolution.num_generations', 150)
        self.migration_interval = config.get('evolution.migration_interval', 10)
        self.insight_curation_interval = config.get('evolution.insight_curation_interval', 50)
        self.alpha = config.get('evolution.alpha', 0.5)

        # Data schema (will be set during initialization)
        self.data_schema_prompt = None

        self.logger.info("QuantEvolve initialized successfully")

    def initialize(self, data_dir: str, assets: list, asset_type: str = "equities"):
        """
        Initialize with data analysis and seed strategies

        Args:
            data_dir: Data directory
            assets: List of assets
            asset_type: Type of assets
        """
        self.logger.info("=" * 80)
        self.logger.info("Phase 1: Initialization")
        self.logger.info("=" * 80)

        # Analyze data
        self.logger.info("Analyzing data schema...")
        self.data_schema_prompt = self.data_agent.analyze_data(
            data_dir=data_dir,
            assets=assets,
            asset_type=asset_type
        )

        # Generate seed strategies
        self.logger.info("Generating seed strategies...")
        seed_strategies = self.data_agent.generate_all_seed_strategies(
            categories=self.categories,
            include_benchmark=True
        )

        # Initialize islands
        self.logger.info("Initializing islands...")
        self.evol_db.initialize_islands(seed_strategies)

        stats = self.evol_db.get_statistics()
        self.logger.info(f"Initialized with {stats['total_strategies']} seed strategies across {stats['num_islands']} islands")

    def evolve_generation(self, generation: int):
        """
        Evolve one generation

        Args:
            generation: Generation number
        """
        self.logger.info(f"\n{'=' * 80}")
        self.logger.info(f"Generation {generation}")
        self.logger.info(f"{'=' * 80}")

        # Evolve each island
        for island_id in range(self.num_islands):
            try:
                self.evolve_island(island_id, generation)
            except Exception as e:
                self.logger.error(f"Error evolving island {island_id}: {e}")
                continue

        # Update generation counter
        self.evol_db.current_generation = generation

        # Migration
        if generation > 0 and generation % self.migration_interval == 0:
            self.logger.info(f"\n--- Migration (Generation {generation}) ---")
            self.evol_db.migrate_strategies(num_migrants=5)

        # Insight curation
        if generation > 0 and generation % self.insight_curation_interval == 0:
            self.logger.info(f"\n--- Insight Curation (Generation {generation}) ---")
            self.curate_insights()

        # Log statistics
        self.log_statistics()

    def evolve_island(self, island_id: int, generation: int):
        """
        Evolve one island for one generation

        Args:
            island_id: Island ID
            generation: Generation number
        """
        island = self.evol_db.islands[island_id]
        self.logger.info(f"\nIsland {island_id} ({island.category})")

        # Sample parent
        parent = self.evol_db.sample_parent(island_id, self.alpha)
        if parent is None:
            self.logger.warning(f"  No parent available for island {island_id}")
            return

        self.logger.info(f"  Parent: {parent.strategy_id} (score: {parent.combined_score:.3f})")

        # Sample cousins
        cousins = self.evol_db.sample_cousins(
            parent=parent,
            island_id=island_id,
            num_best=self.config.get('sampling.num_best_cousins', 2),
            num_diverse=self.config.get('sampling.num_diverse_cousins', 3),
            num_random=self.config.get('sampling.num_random_cousins', 2)
        )

        self.logger.info(f"  Sampled {len(cousins)} cousins")

        # Generate hypothesis
        insights = self.evol_db.get_recent_insights(n=50)
        hypothesis = self.research_agent.generate_hypothesis(
            parent=parent,
            cousins=cousins,
            data_schema=self.data_schema_prompt,
            insights=insights,
            generation=generation
        )

        self.logger.info(f"  Generated hypothesis: {hypothesis[:100]}...")

        # Implement strategy
        code, metrics, notes = self.coding_team.implement_strategy(
            hypothesis=hypothesis,
            data_schema=self.data_schema_prompt,
            parent_code=parent.code
        )

        self.logger.info(f"  Implementation: {notes}")
        self.logger.info(f"  Metrics: SR={metrics.get('sharpe_ratio', 0):.3f}, "
                        f"Return={metrics.get('total_return', 0):.2f}%, "
                        f"MDD={metrics.get('max_drawdown', 0):.2f}%")

        # Calculate backtest period in years
        backtest_years = 3.0  # Default assumption
        if hasattr(self.backtest_engine, 'train_start') and hasattr(self.backtest_engine, 'train_end'):
            if self.backtest_engine.train_start and self.backtest_engine.train_end:
                days = (self.backtest_engine.train_end - self.backtest_engine.train_start).days
                backtest_years = days / 365.25

        # Evaluate strategy
        analysis_dict = self.evaluation_team.analyze_strategy(
            hypothesis=hypothesis,
            code=code,
            metrics=metrics,
            backtest_years=backtest_years
        )

        # Update metrics with category from evaluation
        metrics['strategy_category_bin'] = analysis_dict['category_bin']

        # Create strategy object
        from .core.feature_map import Strategy
        strategy = Strategy(
            hypothesis=hypothesis,
            code=code,
            metrics=metrics,
            analysis=analysis_dict['full_text'],
            generation=generation,
            island_id=island_id,
            parent_id=parent.strategy_id
        )

        # Add to database
        added = self.evol_db.add_strategy(strategy, island_id)

        if added:
            self.logger.info(f"  ✓ Strategy added to feature map (score: {strategy.combined_score:.3f})")
        else:
            self.logger.info(f"  ✗ Strategy rejected (score: {strategy.combined_score:.3f})")

        # Extract insights
        for insight_text in analysis_dict.get('insights', []):
            self.evol_db.add_insight({
                'content': insight_text,
                'generation': generation,
                'island_id': island_id,
                'strategy_id': strategy.strategy_id
            })

    def curate_insights(self):
        """Curate insights for all islands"""
        for island in self.evol_db.islands:
            # Get insights for this island
            island_insights = [
                i for i in self.evol_db.insights
                if i.get('island_id') == island.island_id
            ]

            if len(island_insights) > 100:
                self.logger.info(f"Curating insights for island {island.island_id} ({island.category})")
                curated = self.evaluation_team.curate_insights(
                    insights=island_insights,
                    island_category=island.category,
                    max_insights=50
                )

                # Replace old insights with curated ones
                # Remove old insights for this island
                self.evol_db.insights = [
                    i for i in self.evol_db.insights
                    if i.get('island_id') != island.island_id
                ]

                # Add curated insights
                for curated_insight in curated:
                    curated_insight['island_id'] = island.island_id
                    self.evol_db.insights.append(curated_insight)

    def log_statistics(self):
        """Log current statistics"""
        stats = self.evol_db.get_statistics()

        self.logger.info(f"\n{'=' * 80}")
        self.logger.info(f"Statistics (Generation {stats['generation']})")
        self.logger.info(f"{'=' * 80}")
        self.logger.info(f"Total Strategies: {stats['total_strategies']}")
        self.logger.info(f"On Feature Map: {stats['total_on_map']}")
        self.logger.info(f"Rejected: {stats['total_rejected']}")
        self.logger.info(f"Insights: {stats['num_insights']}")
        self.logger.info(f"Feature Map Coverage: {stats['feature_map']['coverage']*100:.2f}%")

        if stats['feature_map']['num_strategies'] > 0:
            self.logger.info(f"Mean Score: {stats['feature_map']['mean_score']:.3f}")
            self.logger.info(f"Max Score: {stats['feature_map']['max_score']:.3f}")

    def run(self, num_generations: Optional[int] = None):
        """
        Run evolution for specified generations

        Args:
            num_generations: Number of generations (uses config if None)
        """
        num_gens = num_generations or self.num_generations

        self.logger.info(f"\n{'=' * 80}")
        self.logger.info(f"Starting Evolution: {num_gens} generations")
        self.logger.info(f"{'=' * 80}")

        for generation in tqdm(range(num_gens), desc="Evolution Progress"):
            self.evolve_generation(generation)

            # Save checkpoint every 10 generations
            if generation > 0 and generation % 10 == 0:
                self.save_checkpoint(f"checkpoint_gen_{generation}")

        self.logger.info(f"\n{'=' * 80}")
        self.logger.info("Evolution Complete!")
        self.logger.info(f"{'=' * 80}")

        # Final statistics
        self.log_statistics()

        # Save final state
        self.save_checkpoint("final")

    def save_checkpoint(self, name: str):
        """Save checkpoint"""
        checkpoint_dir = Path(self.config.get('results_path', './results')) / name
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.evol_db.save(str(checkpoint_dir))
        self.logger.info(f"Checkpoint saved to {checkpoint_dir}")

    def get_best_strategies(self, n: int = 10):
        """Get top n strategies"""
        all_strategies = self.feature_map.get_all_strategies()
        sorted_strategies = sorted(all_strategies, key=lambda s: s.combined_score, reverse=True)
        return sorted_strategies[:n]


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="QuantEvolve - Evolutionary Trading Strategy Discovery")
    parser.add_argument('--config', type=str, default=None, help="Path to config file")
    parser.add_argument('--generations', type=int, default=None, help="Number of generations")
    parser.add_argument('--sample-data', action='store_true', help="Use sample synthetic data")
    parser.add_argument('--quick-test', action='store_true', help="Run quick test (5 generations)")

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Setup logging
    setup_logger(
        log_dir=config.get('logs_path', './logs'),
        level=config.get('logging.level', 'INFO')
    )

    # Create QuantEvolve instance
    qe = QuantEvolve(config, use_sample_data=args.sample_data)

    # Initialize
    assets = config.get('backtesting.assets.equities', ['AAPL', 'NVDA', 'AMZN', 'GOOGL', 'MSFT', 'TSLA'])
    data_dir = config.get('data_path', './data/raw')

    qe.initialize(
        data_dir=data_dir,
        assets=assets,
        asset_type='equities'
    )

    # Run evolution
    num_gens = 5 if args.quick_test else args.generations
    qe.run(num_generations=num_gens)

    # Print best strategies
    print("\n" + "=" * 80)
    print("Top 10 Strategies")
    print("=" * 80)

    best = qe.get_best_strategies(10)
    for i, strategy in enumerate(best, 1):
        print(f"\n{i}. Strategy {strategy.strategy_id} (Gen {strategy.generation}, Island {strategy.island_id})")
        print(f"   Score: {strategy.combined_score:.3f}")
        print(f"   Sharpe: {strategy.metrics.get('sharpe_ratio', 0):.3f}")
        print(f"   Return: {strategy.metrics.get('total_return', 0):.2f}%")
        print(f"   MDD: {strategy.metrics.get('max_drawdown', 0):.2f}%")


if __name__ == "__main__":
    main()
