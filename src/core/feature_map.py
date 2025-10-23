"""
Feature Map implementation for QuantEvolve
Multi-dimensional archive that maintains strategy diversity
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from loguru import logger
import pickle


@dataclass
class FeatureDimension:
    """Configuration for a feature dimension"""
    name: str
    type: str  # 'continuous' or 'binary'
    bins: int
    range: Optional[Tuple[float, float]] = None  # For continuous dimensions


@dataclass
class Strategy:
    """Container for a trading strategy"""
    hypothesis: str
    code: str
    metrics: Dict[str, float]  # Backtest metrics
    analysis: str
    feature_vector: Optional[Tuple[int, ...]] = None
    combined_score: float = 0.0
    generation: int = 0
    island_id: int = 0
    parent_id: Optional[str] = None
    strategy_id: str = field(default_factory=lambda: f"strat_{np.random.randint(1e9)}")

    def __post_init__(self):
        """Calculate combined score if metrics are available"""
        if self.metrics:
            self.combined_score = self.calculate_combined_score()

    def calculate_combined_score(self) -> float:
        """
        Calculate combined score: SR + IR + MDD
        Note: MDD is negative, so adding it acts as a penalty
        """
        sr = self.metrics.get('sharpe_ratio', 0.0)
        ir = self.metrics.get('information_ratio', 0.0)
        mdd = self.metrics.get('max_drawdown', 0.0)  # Already negative
        return sr + ir + mdd


class FeatureMap:
    """
    Multi-dimensional feature map for maintaining strategy diversity
    Based on MAP-Elites / Quality-Diversity optimization
    """

    def __init__(self, dimensions: List[FeatureDimension]):
        """
        Initialize feature map

        Args:
            dimensions: List of feature dimensions
        """
        self.dimensions = dimensions
        self.dimension_names = [d.name for d in dimensions]

        # Create multi-dimensional archive
        shape = tuple(d.bins for d in dimensions)
        self.archive = np.empty(shape, dtype=object)

        # Statistics
        self.num_added = 0
        self.num_rejected = 0
        self.num_improved = 0

        logger.info(f"Initialized feature map with shape {shape} ({np.prod(shape)} cells)")

    def _compute_feature_vector(self, strategy: Strategy) -> Tuple[int, ...]:
        """
        Compute feature vector from strategy metrics

        Args:
            strategy: Strategy to compute features for

        Returns:
            Tuple of bin indices
        """
        if strategy.feature_vector is not None:
            return strategy.feature_vector

        bins = []
        for dim in self.dimensions:
            if dim.name == 'strategy_category':
                # Binary encoding - should be provided in metrics
                category_bin = strategy.metrics.get('strategy_category_bin', 0)
                bins.append(int(category_bin) % dim.bins)

            elif dim.type == 'continuous':
                value = strategy.metrics.get(dim.name, 0.0)

                # Normalize to bin index
                if dim.range:
                    min_val, max_val = dim.range
                    normalized = (value - min_val) / (max_val - min_val)
                    normalized = np.clip(normalized, 0.0, 0.9999)  # Prevent overflow
                    bin_idx = int(normalized * dim.bins)
                else:
                    # No range specified, use quantile-based binning
                    bin_idx = 0  # Default to first bin

                bins.append(bin_idx)

            else:
                bins.append(0)  # Default

        return tuple(bins)

    def add(self, strategy: Strategy, island_id: Optional[int] = None) -> bool:
        """
        Add strategy to feature map

        Args:
            strategy: Strategy to add
            island_id: Island ID for tracking

        Returns:
            True if strategy was added or improved existing cell, False if rejected
        """
        # Compute feature vector
        feature_vector = self._compute_feature_vector(strategy)
        strategy.feature_vector = feature_vector
        if island_id is not None:
            strategy.island_id = island_id

        # Check if cell is empty
        existing = self.archive[feature_vector]

        if existing is None:
            # Empty cell - add strategy
            self.archive[feature_vector] = strategy
            self.num_added += 1
            logger.debug(f"Added strategy {strategy.strategy_id} to cell {feature_vector}")
            return True

        elif strategy.combined_score > existing.combined_score:
            # Better strategy - replace
            self.archive[feature_vector] = strategy
            self.num_improved += 1
            logger.debug(
                f"Replaced strategy in cell {feature_vector}: "
                f"{existing.combined_score:.3f} -> {strategy.combined_score:.3f}"
            )
            return True

        else:
            # Worse strategy - reject
            self.num_rejected += 1
            logger.debug(f"Rejected strategy {strategy.strategy_id} (score: {strategy.combined_score:.3f})")
            return False

    def get(self, feature_vector: Tuple[int, ...]) -> Optional[Strategy]:
        """
        Get strategy at feature vector

        Args:
            feature_vector: Tuple of bin indices

        Returns:
            Strategy or None if cell is empty
        """
        try:
            return self.archive[feature_vector]
        except IndexError:
            return None

    def get_all_strategies(self) -> List[Strategy]:
        """Get all strategies in the feature map"""
        strategies = []
        for idx in np.ndindex(self.archive.shape):
            strat = self.archive[idx]
            if strat is not None:
                strategies.append(strat)
        return strategies

    def get_filled_cells(self) -> int:
        """Count number of filled cells"""
        return np.sum(self.archive != None)

    def get_coverage(self) -> float:
        """Get percentage of cells filled"""
        return self.get_filled_cells() / np.prod(self.archive.shape)

    def get_statistics(self) -> Dict[str, Any]:
        """Get feature map statistics"""
        strategies = self.get_all_strategies()

        if not strategies:
            return {
                "num_strategies": 0,
                "coverage": 0.0,
                "num_added": self.num_added,
                "num_rejected": self.num_rejected,
                "num_improved": self.num_improved
            }

        scores = [s.combined_score for s in strategies]

        return {
            "num_strategies": len(strategies),
            "coverage": self.get_coverage(),
            "num_added": self.num_added,
            "num_rejected": self.num_rejected,
            "num_improved": self.num_improved,
            "mean_score": np.mean(scores),
            "max_score": np.max(scores),
            "min_score": np.min(scores),
            "std_score": np.std(scores)
        }

    def save(self, filepath: str):
        """Save feature map to file"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        logger.info(f"Saved feature map to {filepath}")

    @staticmethod
    def load(filepath: str) -> 'FeatureMap':
        """Load feature map from file"""
        with open(filepath, 'rb') as f:
            feature_map = pickle.load(f)
        logger.info(f"Loaded feature map from {filepath}")
        return feature_map


def create_feature_map_from_config(config: Dict[str, Any]) -> FeatureMap:
    """
    Create feature map from configuration

    Args:
        config: Configuration dictionary with 'feature_map' section

    Returns:
        Initialized FeatureMap
    """
    dimensions_config = config.get('feature_map', {}).get('dimensions', [])

    dimensions = []
    for dim_config in dimensions_config:
        dim = FeatureDimension(
            name=dim_config['name'],
            type=dim_config['type'],
            bins=dim_config['bins'],
            range=tuple(dim_config['range']) if 'range' in dim_config else None
        )
        dimensions.append(dim)

    return FeatureMap(dimensions)
