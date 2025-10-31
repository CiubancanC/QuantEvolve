"""
Parameter Optimization for Promising Strategies

This module provides basic parameter optimization for strategies that show promise
but may benefit from tuning key parameters like thresholds, lookback windows, etc.
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Optional
from loguru import logger


class ParameterOptimizer:
    """
    Simple grid search optimizer for strategy parameters
    """

    def __init__(self, backtest_engine):
        """
        Initialize parameter optimizer

        Args:
            backtest_engine: Backtesting engine to evaluate parameter variants
        """
        self.backtest_engine = backtest_engine

    def identify_parameters(self, code: str) -> Dict[str, List[float]]:
        """
        Identify tunable numeric parameters in strategy code

        Args:
            code: Strategy code

        Returns:
            Dictionary mapping parameter names to suggested values to test
        """
        parameters = {}

        # Look for common patterns like:
        # window = 20, threshold = 0.8, sigma = 1.2, etc.

        # Extract window/lookback periods
        window_matches = re.findall(r'(?:window|lookback|period)\s*=\s*(\d+)', code, re.IGNORECASE)
        if window_matches:
            base_window = int(window_matches[0])
            parameters['window'] = [max(5, base_window - 10), base_window, base_window + 10]

        # Extract sigma/threshold values
        sigma_matches = re.findall(r'(?:sigma|threshold)\s*=\s*([0-9.]+)', code, re.IGNORECASE)
        if sigma_matches:
            base_sigma = float(sigma_matches[0])
            parameters['sigma'] = [
                max(0.5, base_sigma - 0.4),
                base_sigma,
                min(2.0, base_sigma + 0.4)
            ]

        # Extract SMA periods
        sma_matches = re.findall(r'(?:sma|moving_average).*?(\d+)', code, re.IGNORECASE)
        if sma_matches:
            # Get unique SMA periods
            sma_periods = list(set([int(m) for m in sma_matches]))
            if sma_periods:
                base_sma = sma_periods[0]
                parameters['sma_period'] = [
                    max(10, base_sma - 20),
                    base_sma,
                    min(100, base_sma + 20)
                ]

        return parameters

    def optimize_strategy(
        self,
        code: str,
        metrics: Dict[str, float],
        max_iterations: int = 9
    ) -> Tuple[str, Dict[str, float], Dict]:
        """
        Optimize strategy parameters using grid search

        Args:
            code: Original strategy code
            metrics: Original strategy metrics
            max_iterations: Maximum number of parameter combinations to test

        Returns:
            Tuple of (best_code, best_metrics, optimization_report)
        """
        logger.info("Starting parameter optimization")

        # Identify tunable parameters
        parameters = self.identify_parameters(code)

        if not parameters:
            logger.info("No tunable parameters found - skipping optimization")
            return code, metrics, {'status': 'no_parameters'}

        logger.info(f"Found {len(parameters)} parameter groups: {list(parameters.keys())}")

        # Generate parameter combinations (grid search)
        param_combinations = self._generate_combinations(parameters, max_iterations)

        best_code = code
        best_metrics = metrics
        best_score = self._calculate_optimization_score(metrics)
        best_params = {}

        results = []

        for i, params in enumerate(param_combinations):
            logger.info(f"Testing parameter combination {i+1}/{len(param_combinations)}: {params}")

            # Modify code with new parameters
            modified_code = self._apply_parameters(code, params)

            try:
                # Run backtest with modified parameters
                test_metrics = self.backtest_engine.run_backtest(modified_code)

                # Calculate optimization score
                score = self._calculate_optimization_score(test_metrics)

                results.append({
                    'params': params,
                    'metrics': test_metrics,
                    'score': score
                })

                logger.info(f"  Score: {score:.3f}, Sharpe: {test_metrics.get('sharpe_ratio', 0):.3f}")

                # Update best if improved
                if score > best_score:
                    best_score = score
                    best_code = modified_code
                    best_metrics = test_metrics
                    best_params = params
                    logger.info(f"  ✓ New best found!")

            except Exception as e:
                logger.warning(f"  Failed to test parameters {params}: {e}")
                continue

        # Create optimization report
        report = {
            'status': 'completed',
            'original_score': self._calculate_optimization_score(metrics),
            'best_score': best_score,
            'improvement': best_score - self._calculate_optimization_score(metrics),
            'best_params': best_params,
            'tested_combinations': len(results),
            'results': results
        }

        if best_score > self._calculate_optimization_score(metrics):
            logger.info(f"Optimization successful! Score improved by {report['improvement']:.3f}")
        else:
            logger.info("No improvement found - keeping original")

        return best_code, best_metrics, report

    def _generate_combinations(
        self,
        parameters: Dict[str, List[float]],
        max_combinations: int
    ) -> List[Dict]:
        """Generate parameter combinations for grid search"""
        # Start with all combinations of first parameter
        if not parameters:
            return []

        param_names = list(parameters.keys())
        param_values = [parameters[name] for name in param_names]

        # Generate all combinations
        from itertools import product
        all_combinations = list(product(*param_values))

        # Limit to max_combinations
        if len(all_combinations) > max_combinations:
            # Sample evenly across the space
            indices = np.linspace(0, len(all_combinations) - 1, max_combinations, dtype=int)
            all_combinations = [all_combinations[i] for i in indices]

        # Convert to list of dicts
        combinations = []
        for combo in all_combinations:
            param_dict = {name: value for name, value in zip(param_names, combo)}
            combinations.append(param_dict)

        return combinations

    def _apply_parameters(self, code: str, params: Dict) -> str:
        """Apply parameter modifications to code"""
        modified_code = code

        for param_name, param_value in params.items():
            # Try to find and replace the parameter in code
            if param_name == 'window':
                # Replace window/lookback values
                modified_code = re.sub(
                    r'((?:window|lookback|period)\s*=\s*)\d+',
                    f'\\g<1>{int(param_value)}',
                    modified_code,
                    count=1,
                    flags=re.IGNORECASE
                )
            elif param_name == 'sigma':
                # Replace sigma/threshold values
                modified_code = re.sub(
                    r'((?:sigma|threshold)\s*=\s*)[0-9.]+',
                    f'\\g<1>{param_value:.2f}',
                    modified_code,
                    count=1,
                    flags=re.IGNORECASE
                )
            elif param_name == 'sma_period':
                # Replace SMA period
                modified_code = re.sub(
                    r'(rolling\s*\(\s*window\s*=\s*)\d+',
                    f'\\g<1>{int(param_value)}',
                    modified_code,
                    count=1,
                    flags=re.IGNORECASE
                )

        return modified_code

    def _calculate_optimization_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculate optimization score from metrics
        Balances Sharpe ratio with trading frequency to avoid over-fitting

        Returns:
            Combined score (higher is better)
        """
        sharpe = metrics.get('sharpe_ratio', -0.5)
        trading_freq = metrics.get('trading_frequency', 0)
        max_dd = metrics.get('max_drawdown', -25.0)

        # Penalize very low trading frequencies (likely over-fit)
        freq_penalty = 0
        if trading_freq < 10:
            freq_penalty = -5.0
        elif trading_freq < 20:
            freq_penalty = -2.0

        # Combined score: Sharpe + (capped MDD) + freq_penalty
        score = sharpe + (max_dd / 10.0) + freq_penalty

        return score
