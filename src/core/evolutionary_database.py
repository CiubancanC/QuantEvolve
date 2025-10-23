"""
Evolutionary Database with Island Model
Maintains populations across multiple islands with migration
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from loguru import logger
import pickle
from pathlib import Path

from .feature_map import Strategy, FeatureMap


class Island:
    """
    Represents an evolutionary island with its own population
    """

    def __init__(self, island_id: int, category: str, seed_strategy: Optional[Strategy] = None):
        """
        Initialize island

        Args:
            island_id: Unique island identifier
            category: Strategy category for this island
            seed_strategy: Initial seed strategy
        """
        self.island_id = island_id
        self.category = category
        self.population: List[Strategy] = []
        self.strategies_on_map: List[Strategy] = []  # Strategies that made it to feature map

        if seed_strategy:
            self.add_strategy(seed_strategy, on_map=True)

        logger.info(f"Initialized island {island_id} for category '{category}'")

    def add_strategy(self, strategy: Strategy, on_map: bool = False):
        """
        Add strategy to island population

        Args:
            strategy: Strategy to add
            on_map: Whether strategy is on the feature map
        """
        strategy.island_id = self.island_id
        self.population.append(strategy)

        if on_map:
            self.strategies_on_map.append(strategy)

    def get_population_size(self) -> int:
        """Get total population size"""
        return len(self.population)

    def get_map_size(self) -> int:
        """Get number of strategies on feature map"""
        return len(self.strategies_on_map)

    def get_best_strategies(self, n: int = 10) -> List[Strategy]:
        """
        Get top n strategies from feature map

        Args:
            n: Number of strategies to return

        Returns:
            List of best strategies
        """
        if not self.strategies_on_map:
            return []

        sorted_strats = sorted(
            self.strategies_on_map,
            key=lambda s: s.combined_score,
            reverse=True
        )
        return sorted_strats[:n]

    def sample_from_map(self) -> Optional[Strategy]:
        """Uniformly sample strategy from feature map"""
        if not self.strategies_on_map:
            return None
        return np.random.choice(self.strategies_on_map)

    def sample_from_population(self) -> Optional[Strategy]:
        """Uniformly sample strategy from entire population"""
        if not self.population:
            return None
        return np.random.choice(self.population)


class EvolutionaryDatabase:
    """
    Manages the evolutionary process across multiple islands
    Integrates with feature map for diversity maintenance
    """

    def __init__(
        self,
        feature_map: FeatureMap,
        num_islands: int,
        categories: List[str]
    ):
        """
        Initialize evolutionary database

        Args:
            feature_map: Shared feature map across all islands
            num_islands: Number of islands
            categories: List of strategy categories
        """
        self.feature_map = feature_map
        self.num_islands = num_islands
        self.categories = categories

        # Initialize islands
        self.islands: List[Island] = []

        # Archive for rejected strategies (not on map but still useful)
        self.rejected_archive: List[Strategy] = []

        # Insights accumulated during evolution
        self.insights: List[Dict[str, Any]] = []

        # Generation counter
        self.current_generation = 0

        logger.info(
            f"Initialized evolutionary database with {num_islands} islands "
            f"and {len(categories)} categories"
        )

    def initialize_islands(self, seed_strategies: List[Strategy]):
        """
        Initialize islands with seed strategies

        Args:
            seed_strategies: List of seed strategies (one per island)
        """
        if len(seed_strategies) != self.num_islands:
            raise ValueError(
                f"Expected {self.num_islands} seed strategies, got {len(seed_strategies)}"
            )

        for i, (category, seed) in enumerate(zip(self.categories + ["benchmark"], seed_strategies)):
            island = Island(island_id=i, category=category, seed_strategy=seed)
            self.islands.append(island)

            # Add seed to feature map
            self.feature_map.add(seed, island_id=i)
            island.strategies_on_map = [seed]

        logger.info(f"Initialized {len(self.islands)} islands with seed strategies")

    def add_strategy(self, strategy: Strategy, island_id: int) -> bool:
        """
        Add strategy to database and feature map

        Args:
            strategy: Strategy to add
            island_id: Island that generated the strategy

        Returns:
            True if added to feature map, False if rejected
        """
        island = self.islands[island_id]
        island.add_strategy(strategy, on_map=False)

        # Try to add to feature map
        added = self.feature_map.add(strategy, island_id=island_id)

        if added:
            island.strategies_on_map.append(strategy)
            logger.debug(f"Strategy {strategy.strategy_id} added to feature map from island {island_id}")
        else:
            # Keep in rejected archive
            self.rejected_archive.append(strategy)
            logger.debug(f"Strategy {strategy.strategy_id} rejected from feature map")

        return added

    def sample_parent(self, island_id: int, alpha: float = 0.5) -> Optional[Strategy]:
        """
        Sample parent strategy from island

        Args:
            island_id: Island to sample from
            alpha: Probability of sampling from feature map (best parent)
                  vs entire population (diverse parent)

        Returns:
            Sampled parent strategy or None
        """
        island = self.islands[island_id]

        if np.random.random() < alpha:
            # Best parent: sample from feature map
            return island.sample_from_map()
        else:
            # Diverse parent: sample from entire population
            return island.sample_from_population()

    def sample_cousins(
        self,
        parent: Strategy,
        island_id: int,
        num_best: int = 2,
        num_diverse: int = 3,
        num_random: int = 2,
        sigma: float = 1.0,
        bitflip_rate: float = 0.25
    ) -> List[Strategy]:
        """
        Sample cousin strategies similar to parent

        Args:
            parent: Parent strategy
            island_id: Island to sample from
            num_best: Number of best cousins
            num_diverse: Number of diverse cousins (nearby in feature space)
            num_random: Number of random cousins
            sigma: Sampling radius for continuous dimensions
            bitflip_rate: Bit flip probability for binary dimensions

        Returns:
            List of cousin strategies
        """
        island = self.islands[island_id]
        cousins = []

        # Best cousins: top strategies from island's feature map
        best_strategies = island.get_best_strategies(n=num_best * 2)  # Sample more to ensure diversity
        if best_strategies:
            # Filter out parent
            best_strategies = [s for s in best_strategies if s.strategy_id != parent.strategy_id]
            cousins.extend(best_strategies[:num_best])

        # Diverse cousins: sample near parent in feature space
        if parent.feature_vector:
            diverse = self._sample_diverse_cousins(
                parent.feature_vector,
                num_diverse,
                sigma,
                bitflip_rate
            )
            cousins.extend(diverse)

        # Random cousins: uniform sample from population
        population = [s for s in island.population if s.strategy_id != parent.strategy_id]
        if population:
            random_cousins = np.random.choice(
                population,
                size=min(num_random, len(population)),
                replace=False
            ).tolist()
            cousins.extend(random_cousins)

        logger.debug(f"Sampled {len(cousins)} cousin strategies for parent {parent.strategy_id}")
        return cousins

    def _sample_diverse_cousins(
        self,
        parent_vector: Tuple[int, ...],
        num_samples: int,
        sigma: float,
        bitflip_rate: float
    ) -> List[Strategy]:
        """
        Sample strategies near parent in feature space

        Args:
            parent_vector: Parent's feature vector
            num_samples: Number of samples
            sigma: Sampling radius
            bitflip_rate: Bit flip rate for binary dimensions

        Returns:
            List of nearby strategies
        """
        cousins = []

        for _ in range(num_samples * 3):  # Try more times to get enough samples
            # Perturb parent vector
            perturbed = list(parent_vector)

            for i, dim in enumerate(self.feature_map.dimensions):
                if dim.type == 'continuous':
                    # Gaussian perturbation
                    perturbed[i] = int(np.clip(
                        np.floor(np.random.normal(parent_vector[i], sigma)),
                        0,
                        dim.bins - 1
                    ))
                elif dim.type == 'binary':
                    # Bit flip
                    num_bits = int(np.log2(dim.bins)) if dim.bins > 1 else 1
                    num_flips = max(1, int(num_bits * bitflip_rate))

                    # Convert to binary and flip bits
                    val = parent_vector[i]
                    for _ in range(num_flips):
                        bit_pos = np.random.randint(num_bits)
                        val ^= (1 << bit_pos)
                    perturbed[i] = val % dim.bins

            # Get strategy at perturbed location
            strategy = self.feature_map.get(tuple(perturbed))
            if strategy and strategy not in cousins:
                cousins.append(strategy)

            if len(cousins) >= num_samples:
                break

        return cousins[:num_samples]

    def migrate_strategies(self, num_migrants: int = 5):
        """
        Perform migration between islands

        Args:
            num_migrants: Number of best strategies to migrate from each island
        """
        # Collect best strategies from each island
        migrants_per_island = []
        for island in self.islands:
            best = island.get_best_strategies(n=num_migrants)
            migrants_per_island.append(best)

        # Distribute to all islands
        for target_island in self.islands:
            for source_island_id, migrants in enumerate(migrants_per_island):
                if source_island_id != target_island.island_id:
                    for migrant in migrants:
                        # Add to target island population (not as a new generation)
                        target_island.population.append(migrant)

        logger.info(f"Migrated {num_migrants} strategies between {len(self.islands)} islands")

    def add_insight(self, insight: Dict[str, Any]):
        """Add insight to repository"""
        insight['generation'] = self.current_generation
        self.insights.append(insight)

    def get_recent_insights(self, n: int = 50) -> List[Dict[str, Any]]:
        """Get n most recent insights"""
        return self.insights[-n:] if self.insights else []

    def curate_insights(self, max_insights: int = 100):
        """
        Curate insights to remove redundancy and keep most important

        Args:
            max_insights: Maximum number of insights to keep
        """
        if len(self.insights) <= max_insights:
            return

        # For now, keep most recent insights
        # TODO: Implement more sophisticated curation (e.g., clustering, importance scoring)
        self.insights = self.insights[-max_insights:]
        logger.info(f"Curated insights to {len(self.insights)} entries")

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            "generation": self.current_generation,
            "num_islands": len(self.islands),
            "total_strategies": sum(island.get_population_size() for island in self.islands),
            "total_on_map": sum(island.get_map_size() for island in self.islands),
            "total_rejected": len(self.rejected_archive),
            "num_insights": len(self.insights),
            "feature_map": self.feature_map.get_statistics(),
            "islands": []
        }

        for island in self.islands:
            island_stats = {
                "id": island.island_id,
                "category": island.category,
                "population_size": island.get_population_size(),
                "map_size": island.get_map_size()
            }

            if island.strategies_on_map:
                scores = [s.combined_score for s in island.strategies_on_map]
                island_stats.update({
                    "mean_score": np.mean(scores),
                    "max_score": np.max(scores),
                    "best_strategy_id": island.strategies_on_map[np.argmax(scores)].strategy_id
                })

            stats["islands"].append(island_stats)

        return stats

    def save(self, directory: str):
        """
        Save database to directory

        Args:
            directory: Directory to save to
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        # Save database
        with open(path / "evolutionary_database.pkl", 'wb') as f:
            pickle.dump(self, f)

        # Save feature map separately
        self.feature_map.save(str(path / "feature_map.pkl"))

        logger.info(f"Saved evolutionary database to {directory}")

    @staticmethod
    def load(directory: str) -> 'EvolutionaryDatabase':
        """
        Load database from directory

        Args:
            directory: Directory to load from

        Returns:
            Loaded database
        """
        path = Path(directory)

        with open(path / "evolutionary_database.pkl", 'rb') as f:
            db = pickle.load(f)

        logger.info(f"Loaded evolutionary database from {directory}")
        return db
