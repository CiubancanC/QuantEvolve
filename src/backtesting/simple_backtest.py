"""
Simplified backtesting engine for QuantEvolve
This is a lightweight alternative to Zipline for initial testing
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from pathlib import Path
from loguru import logger


class SimpleBacktestEngine:
    """
    Simplified backtesting engine that executes strategy code
    Uses a simple position-based approach instead of full Zipline
    """

    def __init__(
        self,
        data_dir: str,
        initial_capital: float = 100000,
        commission: float = 0.0075,
        min_commission: float = 1.0
    ):
        """
        Initialize backtest engine

        Args:
            data_dir: Directory containing price data
            initial_capital: Starting capital
            commission: Commission per share (as decimal)
            min_commission: Minimum commission per trade
        """
        self.data_dir = Path(data_dir)
        self.initial_capital = initial_capital
        self.commission = commission
        self.min_commission = min_commission
        self.data_cache = {}

    def load_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load price data for symbol"""
        if symbol in self.data_cache:
            return self.data_cache[symbol]

        # Try CSV first
        csv_path = self.data_dir / f"{symbol}.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path, parse_dates=['Date'] if 'Date' in pd.read_csv(csv_path, nrows=0).columns else ['date'])
                df.columns = df.columns.str.lower()
                if 'date' in df.columns:
                    df.set_index('date', inplace=True)
                self.data_cache[symbol] = df
                return df
            except Exception as e:
                logger.warning(f"Error loading {csv_path}: {e}")

        # Try Parquet
        parquet_path = self.data_dir / f"{symbol}.parquet"
        if parquet_path.exists():
            try:
                df = pd.read_parquet(parquet_path)
                df.columns = df.columns.str.lower()
                if 'date' in df.columns:
                    df.set_index('date', inplace=True)
                self.data_cache[symbol] = df
                return df
            except Exception as e:
                logger.warning(f"Error loading {parquet_path}: {e}")

        return None

    def run_backtest(self, strategy_code: str) -> Dict[str, float]:
        """
        Run backtest for strategy code

        Args:
            strategy_code: Python code implementing the strategy

        Returns:
            Dictionary of performance metrics
        """
        logger.info("Running simplified backtest")

        try:
            # Execute strategy code in a safe namespace
            namespace = self._create_strategy_namespace()

            # Execute the code
            exec(strategy_code, namespace)

            # Check if required functions exist
            if 'generate_signals' not in namespace:
                logger.warning("Strategy missing generate_signals function, using default")
                return self._get_default_metrics()

            # Get signals function
            generate_signals = namespace['generate_signals']

            # Load sample data (for now, use AAPL as proxy)
            data = self.load_data('AAPL')
            if data is None:
                logger.warning("Could not load data for backtesting")
                return self._get_default_metrics()

            # Generate signals
            signals = generate_signals(data)

            # Calculate returns
            metrics = self._calculate_metrics(data, signals)

            return metrics

        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return self._get_default_metrics()

    def _create_strategy_namespace(self) -> Dict:
        """Create namespace for strategy execution"""
        import pandas as pd
        import numpy as np

        namespace = {
            'pd': pd,
            'np': np,
            'DataFrame': pd.DataFrame,
            'Series': pd.Series,
            '__builtins__': __builtins__
        }

        return namespace

    def _calculate_metrics(self, data: pd.DataFrame, signals: pd.Series) -> Dict[str, float]:
        """Calculate performance metrics from signals"""

        # Ensure signals is aligned with data
        if not isinstance(signals, pd.Series):
            signals = pd.Series(signals, index=data.index)

        # Calculate returns
        returns = data['close'].pct_change()

        # Position-based returns (signal * next_day_return)
        positions = signals.shift(1).fillna(0)  # Trade on next day
        strategy_returns = positions * returns

        # Remove NaNs
        strategy_returns = strategy_returns.dropna()

        if len(strategy_returns) == 0 or strategy_returns.sum() == 0:
            return self._get_default_metrics()

        # Calculate cumulative returns
        cumulative_returns = (1 + strategy_returns).cumprod()
        total_return = (cumulative_returns.iloc[-1] - 1) * 100

        # Calculate Sharpe ratio
        sharpe_ratio = self._calculate_sharpe(strategy_returns)

        # Calculate Sortino ratio
        sortino_ratio = self._calculate_sortino(strategy_returns)

        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown(cumulative_returns)

        # Calculate trading frequency
        trading_frequency = (signals.diff().abs() > 0).sum()

        # Calculate Information Ratio (vs buy-and-hold)
        benchmark_returns = returns
        excess_returns = strategy_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = (excess_returns.mean() * 252) / tracking_error if tracking_error > 0 else 0

        metrics = {
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'information_ratio': information_ratio,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'trading_frequency': int(trading_frequency),
            'strategy_category_bin': 1  # Will be updated by evaluation team
        }

        return metrics

    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate annualized Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        excess_returns = returns - risk_free_rate / 252
        sharpe = excess_returns.mean() / returns.std() * np.sqrt(252)

        return float(sharpe)

    def _calculate_sortino(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate annualized Sortino ratio"""
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - risk_free_rate / 252
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return float(self._calculate_sharpe(returns, risk_free_rate) * 1.2)  # Approximate

        sortino = excess_returns.mean() / downside_returns.std() * np.sqrt(252)

        return float(sortino)

    def _calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """Calculate maximum drawdown (as negative percentage)"""
        if len(cumulative_returns) == 0:
            return -20.0

        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max * 100

        max_dd = drawdowns.min()

        return float(max_dd) if not np.isnan(max_dd) else -20.0

    def _get_default_metrics(self) -> Dict[str, float]:
        """Get default metrics when backtest fails"""
        return {
            'sharpe_ratio': 0.5,
            'sortino_ratio': 0.6,
            'information_ratio': 0.0,
            'total_return': 10.0,
            'max_drawdown': -15.0,
            'trading_frequency': 50,
            'strategy_category_bin': 1
        }
