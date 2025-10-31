"""
Improved backtesting engine for QuantEvolve
Provides realistic performance metrics using vectorized backtesting
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from pathlib import Path
from loguru import logger


class ImprovedBacktestEngine:
    """
    Improved backtesting engine with realistic metrics
    - Uses real market data (multiple assets)
    - Vectorized backtesting for speed
    - Proper commission and slippage modeling
    - Comprehensive performance metrics
    """

    def __init__(
        self,
        data_dir: str,
        initial_capital: float = 100000,
        commission_pct: float = 0.001,  # 0.1% per trade (legacy, not used if per_share_commission set)
        slippage_pct: float = 0.0005,   # 0.05% slippage (legacy, not used if volume_slippage enabled)
        risk_free_rate: float = 0.02,   # 2% annual risk-free rate
        per_share_commission: float = 0.0075,  # $0.0075 per share (paper spec)
        min_commission: float = 1.00,   # $1.00 minimum commission per trade (paper spec)
        volume_slippage: bool = True,   # Use quadratic volume-based slippage (paper spec)
        train_start: Optional[str] = None,
        train_end: Optional[str] = None,
        val_start: Optional[str] = None,
        val_end: Optional[str] = None,
        test_start: Optional[str] = None,
        test_end: Optional[str] = None
    ):
        """
        Initialize improved backtest engine

        Args:
            data_dir: Directory containing price data
            initial_capital: Starting capital
            commission_pct: Commission as percentage of trade value (legacy, not used if per_share_commission set)
            slippage_pct: Slippage as percentage of trade value (legacy, not used if volume_slippage enabled)
            risk_free_rate: Annual risk-free rate for Sharpe/Sortino
            per_share_commission: Commission per share in dollars (default: $0.0075, per paper)
            min_commission: Minimum commission per trade in dollars (default: $1.00, per paper)
            volume_slippage: If True, use quadratic volume-based slippage model (per paper)
            train_start: Training period start date (YYYY-MM-DD)
            train_end: Training period end date (YYYY-MM-DD)
            val_start: Validation period start date (YYYY-MM-DD)
            val_end: Validation period end date (YYYY-MM-DD)
            test_start: Test period start date (YYYY-MM-DD)
            test_end: Test period end date (YYYY-MM-DD)
        """
        self.data_dir = Path(data_dir)
        self.initial_capital = initial_capital

        # Transaction cost parameters (paper-specified model)
        self.per_share_commission = per_share_commission
        self.min_commission = min_commission
        self.volume_slippage = volume_slippage

        # Legacy parameters (for backward compatibility)
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct

        self.risk_free_rate = risk_free_rate
        self.data_cache = {}

        # Store period definitions
        self.train_start = pd.to_datetime(train_start) if train_start else None
        self.train_end = pd.to_datetime(train_end) if train_end else None
        self.val_start = pd.to_datetime(val_start) if val_start else None
        self.val_end = pd.to_datetime(val_end) if val_end else None
        self.test_start = pd.to_datetime(test_start) if test_start else None
        self.test_end = pd.to_datetime(test_end) if test_end else None

        # Current period being used for backtesting
        self.current_period = 'train'  # 'train', 'val', or 'test'

        # Load all available symbols
        self.symbols = self._discover_symbols()
        logger.info(f"Discovered {len(self.symbols)} symbols for backtesting")

        if self.train_start and self.train_end:
            logger.info(f"Train period: {self.train_start.date()} to {self.train_end.date()}")
        if self.val_start and self.val_end:
            logger.info(f"Val period: {self.val_start.date()} to {self.val_end.date()}")
        if self.test_start and self.test_end:
            logger.info(f"Test period: {self.test_start.date()} to {self.test_end.date()}")

        # Benchmark returns cache (market-cap-weighted)
        self.benchmark_returns_cache = None

    def set_period(self, period: str):
        """
        Set the current period for backtesting

        Args:
            period: One of 'train', 'val', or 'test'
        """
        if period not in ['train', 'val', 'test']:
            raise ValueError(f"Period must be 'train', 'val', or 'test', got '{period}'")

        self.current_period = period
        # Clear caches to force reloading with new period filter
        self.data_cache.clear()
        self.benchmark_returns_cache = None
        logger.info(f"Set backtest period to: {period}")

    def _get_period_bounds(self) -> tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
        """Get start and end dates for current period"""
        if self.current_period == 'train':
            return self.train_start, self.train_end
        elif self.current_period == 'val':
            return self.val_start, self.val_end
        elif self.current_period == 'test':
            return self.test_start, self.test_end
        return None, None

    def _discover_symbols(self) -> List[str]:
        """Discover all available symbols in data directory"""
        symbols = []
        for file_path in self.data_dir.glob("*.csv"):
            symbols.append(file_path.stem)
        for file_path in self.data_dir.glob("*.parquet"):
            if file_path.stem not in symbols:
                symbols.append(file_path.stem)
        return symbols

    def load_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load price data for symbol, filtered by current period"""
        if symbol in self.data_cache:
            return self.data_cache[symbol]

        # Try CSV first
        csv_path = self.data_dir / f"{symbol}.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.lower()
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)

                # Ensure we have required columns
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                if all(col in df.columns for col in required_cols):
                    # Normalize datetime index (Issue #3 fix)
                    df = self._normalize_datetime_index(df)
                    # Apply period filter
                    df = self._filter_by_period(df)
                    if df is not None and len(df) > 0:
                        self.data_cache[symbol] = df
                        return df
                else:
                    logger.warning(f"{symbol} missing required columns: {required_cols}")
            except Exception as e:
                logger.warning(f"Error loading {csv_path}: {e}")

        # Try Parquet
        parquet_path = self.data_dir / f"{symbol}.parquet"
        if parquet_path.exists():
            try:
                df = pd.read_parquet(parquet_path)
                df.columns = df.columns.str.lower()
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)

                required_cols = ['open', 'high', 'low', 'close', 'volume']
                if all(col in df.columns for col in required_cols):
                    # Normalize datetime index (Issue #3 fix)
                    df = self._normalize_datetime_index(df)
                    # Apply period filter
                    df = self._filter_by_period(df)
                    if df is not None and len(df) > 0:
                        self.data_cache[symbol] = df
                        return df
            except Exception as e:
                logger.warning(f"Error loading {parquet_path}: {e}")

        return None

    def _filter_by_period(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Filter dataframe by current period bounds"""
        start_date, end_date = self._get_period_bounds()

        # If no period bounds set, return full data
        if start_date is None or end_date is None:
            return df

        # Filter by date range
        filtered = df[(df.index >= start_date) & (df.index <= end_date)]

        if len(filtered) == 0:
            logger.warning(f"No data in period {self.current_period} ({start_date.date()} to {end_date.date()})")
            return None

        return filtered

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all available symbol data"""
        all_data = {}
        for symbol in self.symbols:
            data = self.load_data(symbol)
            if data is not None:
                all_data[symbol] = data
        return all_data

    def _calculate_benchmark_returns(self, symbols: Optional[List[str]] = None) -> Optional[pd.Series]:
        """
        Calculate market-cap-weighted benchmark returns

        As specified in paper Section 6.2: "For equities, we construct a market
        capitalization-weighted portfolio of the six stocks rebalanced monthly"

        Args:
            symbols: List of symbols to include in benchmark (uses all if None)

        Returns:
            Series of benchmark returns, or None if calculation fails
        """
        # Use cache if available
        if self.benchmark_returns_cache is not None:
            return self.benchmark_returns_cache

        # Use provided symbols or all available
        benchmark_symbols = symbols if symbols else self.symbols

        logger.info(f"Calculating market-cap-weighted benchmark for {len(benchmark_symbols)} symbols")

        # Load price data for all symbols
        all_prices = {}
        for symbol in benchmark_symbols:
            data = self.load_data(symbol)
            if data is not None:
                all_prices[symbol] = data['close']

        if not all_prices:
            logger.warning("No price data available for benchmark calculation")
            return None

        # Create DataFrame with all prices
        prices_df = pd.DataFrame(all_prices)

        # For simplicity, use equal weighting as proxy for market-cap weighting
        # Ideally, we'd use actual market cap data, but it's often not available
        # in OHLCV data. Equal-weighted is a reasonable approximation for the
        # paper's specification when market caps are similar.
        #
        # NOTE: For true market-cap weighting, you would need market cap data:
        # market_caps = {...}  # Load market cap data
        # weights = market_caps / market_caps.sum()
        #
        # For now, we use equal weights rebalanced monthly as specified in paper
        logger.info("Using equal-weighted portfolio as market-cap proxy (rebalanced monthly)")

        # Calculate monthly rebalancing dates (first business day of each month)
        monthly_dates = prices_df.resample('MS').first().index

        # Calculate returns
        returns = prices_df.pct_change()

        # Initialize weights (equal weight)
        num_assets = len(prices_df.columns)
        weights = pd.Series(1.0 / num_assets, index=prices_df.columns)

        # Calculate portfolio returns with monthly rebalancing
        portfolio_returns = pd.Series(0.0, index=returns.index)

        for i in range(len(monthly_dates) - 1):
            # Period between rebalancing
            start_date = monthly_dates[i]
            end_date = monthly_dates[i + 1]

            # Get returns for this period
            period_returns = returns.loc[start_date:end_date]

            # Apply weights to get portfolio returns
            portfolio_returns.loc[start_date:end_date] = (period_returns * weights).sum(axis=1)

        # Handle final period
        if len(monthly_dates) > 0:
            final_start = monthly_dates[-1]
            final_returns = returns.loc[final_start:]
            portfolio_returns.loc[final_start:] = (final_returns * weights).sum(axis=1)

        # Remove NaN values
        portfolio_returns = portfolio_returns.dropna()

        # Cache the result
        self.benchmark_returns_cache = portfolio_returns

        logger.info(f"Calculated benchmark returns: mean={portfolio_returns.mean()*252:.2%}, "
                   f"vol={portfolio_returns.std()*np.sqrt(252):.2%}")

        return portfolio_returns

    def run_backtest(self, strategy_code: str, symbols: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Run backtest for strategy code

        Args:
            strategy_code: Python code implementing the strategy
            symbols: List of symbols to backtest on (if None, uses all available)

        Returns:
            Dictionary of performance metrics
        """
        logger.info("Running improved backtest with real data")

        try:
            # Use provided symbols or default to all available
            test_symbols = symbols if symbols else self.symbols[:3]  # Use first 3 if not specified

            # Execute strategy code in a safe namespace
            namespace = self._create_strategy_namespace()

            # Execute the code
            exec(strategy_code, namespace)

            # Check if required functions exist
            if 'generate_signals' not in namespace:
                logger.warning("Strategy missing generate_signals function")
                return self._get_default_metrics()

            # Get signals function
            generate_signals = namespace['generate_signals']

            # Run backtest on each symbol and aggregate results
            all_returns = []
            all_signals = []

            for symbol in test_symbols:
                data = self.load_data(symbol)
                if data is None:
                    continue

                try:
                    # Generate signals for this symbol
                    signals = generate_signals(data.copy())

                    # Ensure signals is a Series aligned with data
                    if not isinstance(signals, pd.Series):
                        signals = pd.Series(signals, index=data.index)

                    # Validate and sanitize signals (Issue #2 fix)
                    signals = self._validate_signals(signals, data)

                    # Calculate returns for this symbol
                    symbol_returns = self._calculate_returns(data, signals)

                    if symbol_returns is not None and len(symbol_returns) > 0:
                        all_returns.append(symbol_returns)
                        all_signals.append(signals)

                except Exception as e:
                    logger.warning(f"Error backtesting {symbol}: {e}")
                    continue

            # If no valid returns, return worst-case metrics (Issue #4 fix)
            if len(all_returns) == 0:
                logger.warning("No valid backtest results - assigning worst-case metrics")
                logger.warning(f"Attempted symbols: {test_symbols}")
                return self._get_worst_case_metrics()

            # Combine returns from all symbols (equal weight)
            combined_returns = pd.concat(all_returns, axis=1).mean(axis=1)

            # Calculate comprehensive metrics
            metrics = self._calculate_metrics(combined_returns, all_signals)

            logger.info(f"Backtest complete: Sharpe={metrics['sharpe_ratio']:.2f}, Return={metrics['total_return']:.1f}%")

            return metrics

        except Exception as e:
            logger.error(f"Backtest error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_default_metrics()

    def _create_strategy_namespace(self) -> Dict:
        """Create namespace for strategy execution with timezone-safe Timestamp"""
        import pandas as pd
        import numpy as np

        # Wrap pd.Timestamp to force timezone-naive (Issue #3 fix)
        original_timestamp = pd.Timestamp

        def safe_timestamp(*args, **kwargs):
            """Timezone-naive Timestamp wrapper"""
            kwargs.pop('tz', None)  # Remove tz if present
            kwargs.pop('tzinfo', None)
            ts = original_timestamp(*args, **kwargs)
            if hasattr(ts, 'tz') and ts.tz is not None:
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

    def _validate_signals(self, signals: pd.Series, data: pd.DataFrame) -> pd.Series:
        """
        Validate and sanitize trading signals to prevent backtest errors.

        Handles:
        - NaN/inf values
        - Non-numeric values
        - Index misalignment
        - Type errors
        - Timezone issues

        Per paper Section 5.4: Handle edge cases before backtesting.

        Args:
            signals: Raw trading signals from strategy
            data: OHLCV data for alignment

        Returns:
            Validated and sanitized signals
        """
        # Track validation issues for logging
        validation_issues = []

        # Ensure Series type
        if not isinstance(signals, pd.Series):
            signals = pd.Series(signals, index=data.index)
            validation_issues.append("converted to Series")

        # Align with data index
        if len(signals) != len(data) or not signals.index.equals(data.index):
            signals = signals.reindex(data.index)
            validation_issues.append("reindexed to match data")

        # Check for NaN values
        original_nan_count = signals.isna().sum()
        if original_nan_count > 0:
            validation_issues.append(f"{original_nan_count} NaN values")

        # Check for inf values
        original_inf_count = np.isinf(signals).sum()
        if original_inf_count > 0:
            validation_issues.append(f"{original_inf_count} inf values")

        # Replace NaN/inf with neutral signal (0)
        signals = signals.fillna(0)
        signals = signals.replace([np.inf, -np.inf], 0)

        # Ensure numeric
        try:
            signals = pd.to_numeric(signals, errors='coerce').fillna(0)
        except Exception:
            validation_issues.append("non-numeric values")
            signals = pd.Series(0, index=data.index)

        # Clip to valid range [-1, 1]
        if (signals.abs() > 1).any():
            validation_issues.append("out-of-range values clipped")
            signals = signals.clip(-1, 1)

        # Ensure datetime index is timezone-naive (Issue #3 fix)
        if isinstance(signals.index, pd.DatetimeIndex):
            if signals.index.tz is not None:
                signals.index = signals.index.tz_localize(None)
                validation_issues.append("timezone removed from index")

        # Log validation issues if any
        if validation_issues:
            logger.debug(f"Signal validation corrected: {', '.join(validation_issues)}")

        return signals

    def _normalize_datetime_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure datetime index is timezone-naive and properly typed.

        Per paper data pipeline: All timestamps should be timezone-naive
        for consistent comparison operations.

        Args:
            df: DataFrame with datetime index

        Returns:
            DataFrame with normalized timezone-naive index
        """
        if isinstance(df.index, pd.DatetimeIndex):
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)

        # Ensure all datetime columns are also timezone-naive
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                if hasattr(df[col].dt, 'tz') and df[col].dt.tz is not None:
                    df[col] = df[col].dt.tz_localize(None)

        return df

    def _calculate_returns(self, data: pd.DataFrame, signals: pd.Series) -> Optional[pd.Series]:
        """
        Calculate returns for a single symbol with realistic transaction costs

        Args:
            data: OHLCV data
            signals: Trading signals (-1, 0, 1 for short, neutral, long)

        Returns:
            Series of strategy returns
        """
        try:
            # Align signals with data
            signals = signals.reindex(data.index).fillna(0)

            # Clip signals to [-1, 1] range
            signals = signals.clip(-1, 1)

            # Calculate daily returns
            returns = data['close'].pct_change()

            # Position-based returns (use previous signal for next day's return)
            positions = signals.shift(1).fillna(0)

            # Calculate transaction costs using paper-specified model
            transaction_costs = self._calculate_transaction_costs(
                data=data,
                positions=positions,
                signals=signals
            )

            # Strategy returns = position * return - transaction costs
            strategy_returns = (positions * returns) - transaction_costs

            # Remove NaNs
            strategy_returns = strategy_returns.dropna()

            return strategy_returns

        except Exception as e:
            logger.warning(f"Error calculating returns: {e}")
            return None

    def _calculate_transaction_costs(
        self,
        data: pd.DataFrame,
        positions: pd.Series,
        signals: pd.Series
    ) -> pd.Series:
        """
        Calculate realistic transaction costs per paper specification

        Paper spec (Section 6.1, line 239):
        - Commission: $0.0075 per share + $1.00 minimum per trade
        - Slippage: Quadratic function of traded volume percentage

        Args:
            data: OHLCV data with price and volume
            positions: Position sizes (-1, 0, 1)
            signals: Trading signals

        Returns:
            Series of transaction costs as fraction of capital
        """
        # Detect position changes (trades)
        position_changes = positions.diff().fillna(0)
        trades = position_changes.abs() > 0

        # Initialize cost series
        costs = pd.Series(0.0, index=data.index)

        if not trades.any():
            return costs

        # Get prices and volume where trades occur
        trade_prices = data.loc[trades, 'close']
        trade_volumes = data.loc[trades, 'volume']
        trade_position_changes = position_changes[trades].abs()

        # Assume we trade a fixed dollar amount per position unit
        # Position of 1.0 = 100% of capital allocated
        # So position change of 1.0 = trade worth (capital * position_change)
        capital_traded = self.initial_capital * trade_position_changes

        # Calculate shares traded
        shares_traded = capital_traded / trade_prices

        # Calculate commission: $0.0075/share + $1 minimum
        commission_cost = shares_traded * self.per_share_commission
        commission_cost = commission_cost.clip(lower=self.min_commission)

        # Calculate slippage
        if self.volume_slippage:
            # Volume-based slippage: quadratic function
            # Slippage increases quadratically with % of daily volume traded
            volume_pct = shares_traded / trade_volumes
            volume_pct = volume_pct.clip(upper=0.25)  # Cap at 25% of volume

            # Quadratic slippage: 0.5 * (volume_pct)^2 * price
            slippage_cost = 0.5 * (volume_pct ** 2) * trade_prices * shares_traded
        else:
            # Legacy flat percentage slippage
            slippage_cost = capital_traded * self.slippage_pct

        # Total cost in dollars
        total_cost_dollars = commission_cost + slippage_cost

        # Convert to fraction of capital
        costs[trades] = total_cost_dollars / self.initial_capital

        return costs

    def _calculate_metrics(self, returns: pd.Series, signals_list: List[pd.Series]) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""

        if len(returns) == 0 or returns.std() == 0:
            return self._get_default_metrics()

        # Remove any NaN or infinite values
        returns = returns.replace([np.inf, -np.inf], np.nan).dropna()

        if len(returns) == 0:
            return self._get_default_metrics()

        # Calculate cumulative returns
        cumulative_returns = (1 + returns).cumprod()
        total_return = (cumulative_returns.iloc[-1] - 1) * 100

        # Calculate Sharpe ratio (annualized)
        sharpe_ratio = self._calculate_sharpe(returns)

        # Calculate Sortino ratio (annualized)
        sortino_ratio = self._calculate_sortino(returns)

        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown(cumulative_returns)

        # Calculate trading frequency (average across symbols)
        trading_frequencies = []
        for signals in signals_list:
            freq = (signals.diff().abs() > 0).sum()
            trading_frequencies.append(freq)
        trading_frequency = int(np.mean(trading_frequencies)) if trading_frequencies else 50

        # Calculate Information Ratio using market-cap-weighted benchmark
        # Paper specification (Section 6.3.1): IR = (R̄_p - R̄_b) / σ_(p-b)
        # where R̄_b is benchmark return and σ_(p-b) is tracking error
        benchmark_returns = self._calculate_benchmark_returns()

        if benchmark_returns is not None:
            # Align benchmark with strategy returns
            aligned_benchmark = benchmark_returns.reindex(returns.index).fillna(0)

            # Calculate excess returns relative to benchmark
            excess_returns = returns - aligned_benchmark

            # Annualized excess return
            annualized_excess = excess_returns.mean() * 252

            # Tracking error (annualized)
            tracking_error = excess_returns.std() * np.sqrt(252)

            # Information Ratio
            information_ratio = annualized_excess / tracking_error if tracking_error > 0 else 0

            logger.debug(f"IR calculation: excess={annualized_excess:.2%}, "
                        f"tracking_error={tracking_error:.2%}, IR={information_ratio:.3f}")
        else:
            # Fallback to zero-benchmark if benchmark calculation fails
            logger.warning("Benchmark calculation failed, using zero-benchmark for IR")
            excess_returns = returns
            tracking_error = excess_returns.std() * np.sqrt(252)
            information_ratio = (excess_returns.mean() * 252) / tracking_error if tracking_error > 0 else 0

        # Calculate win rate
        win_rate = (returns > 0).sum() / len(returns) * 100

        # Calculate profit factor
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        profit_factor = gains / losses if losses > 0 else gains

        metrics = {
            'sharpe_ratio': float(sharpe_ratio),
            'sortino_ratio': float(sortino_ratio),
            'information_ratio': float(information_ratio),
            'total_return': float(total_return),
            'max_drawdown': float(max_drawdown),
            'trading_frequency': trading_frequency,
            'win_rate': float(win_rate),
            'profit_factor': float(profit_factor),
            'strategy_category_bin': 1  # Will be updated by evaluation team
        }

        return metrics

    def _calculate_sharpe(self, returns: pd.Series) -> float:
        """Calculate annualized Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # Annualize
        annual_return = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)

        # Subtract risk-free rate
        excess_return = annual_return - self.risk_free_rate

        sharpe = excess_return / annual_vol if annual_vol > 0 else 0.0

        return float(sharpe)

    def _calculate_sortino(self, returns: pd.Series) -> float:
        """Calculate annualized Sortino ratio"""
        if len(returns) == 0:
            return 0.0

        # Annualize
        annual_return = returns.mean() * 252

        # Downside deviation (only negative returns)
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return float(self._calculate_sharpe(returns) * 1.4)  # Approximate

        downside_std = downside_returns.std() * np.sqrt(252)

        # Subtract risk-free rate
        excess_return = annual_return - self.risk_free_rate

        sortino = excess_return / downside_std if downside_std > 0 else 0.0

        return float(sortino)

    def _calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """Calculate maximum drawdown (as negative percentage)"""
        if len(cumulative_returns) == 0:
            return -20.0

        # Calculate running maximum
        running_max = cumulative_returns.expanding().max()

        # Calculate drawdown at each point
        drawdowns = (cumulative_returns - running_max) / running_max * 100

        # Get maximum drawdown (most negative)
        max_dd = drawdowns.min()

        return float(max_dd) if not np.isnan(max_dd) and np.isfinite(max_dd) else -20.0

    def _get_default_metrics(self) -> Dict[str, float]:
        """Get default metrics when backtest fails or has no trades"""
        return {
            'sharpe_ratio': -0.5,  # Negative indicates poor performance
            'sortino_ratio': -0.5,
            'information_ratio': -0.5,
            'total_return': -10.0,  # Negative return
            'max_drawdown': -25.0,  # Significant drawdown
            'trading_frequency': 0,  # No trades
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'strategy_category_bin': 1
        }

    def _get_worst_case_metrics(self) -> Dict[str, float]:
        """
        Get worst-case metrics when all backtests fail.

        Per paper Section 6.3.2 (Equation 3): Combined Score = SR + IR + MDD
        Assigns worst observed values to ensure strategy is rejected in evolution.

        Returns worst-case metrics that ensure rejection in evolutionary selection.
        """
        return {
            'sharpe_ratio': -3.0,       # Worst observed in training
            'sortino_ratio': -3.0,      # Consistent with Sharpe
            'information_ratio': -2.0,  # Worst vs benchmark
            'total_return': -50.0,      # -50% loss
            'max_drawdown': -100.0,     # Complete loss
            'trading_frequency': 0,     # No trades executed
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'strategy_category_bin': 0,
            'combined_score': -6.0      # SR + IR + MDD = -3 + (-2) + (-1) = -6
        }


class PortfolioBacktestEngine(ImprovedBacktestEngine):
    """
    Extended backtest engine for portfolio-level strategies
    Supports multi-asset strategies with position sizing
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_portfolio_backtest(
        self,
        strategy_code: str,
        symbols: Optional[List[str]] = None,
        rebalance_frequency: str = 'daily'
    ) -> Dict[str, float]:
        """
        Run portfolio backtest with position sizing and rebalancing

        Args:
            strategy_code: Python code implementing portfolio strategy
            symbols: List of symbols to trade
            rebalance_frequency: 'daily', 'weekly', or 'monthly'

        Returns:
            Performance metrics
        """
        logger.info(f"Running portfolio backtest on {len(symbols or self.symbols)} symbols with {rebalance_frequency} rebalancing")

        try:
            # Use provided symbols or default to all available
            test_symbols = symbols if symbols else self.symbols[:5]

            # Load all data
            all_data = {}
            for symbol in test_symbols:
                data = self.load_data(symbol)
                if data is not None:
                    all_data[symbol] = data

            if len(all_data) == 0:
                logger.warning("No data available for portfolio backtest")
                return self._get_default_metrics()

            # Execute strategy code
            namespace = self._create_strategy_namespace()
            exec(strategy_code, namespace)

            # Check for portfolio signal generation function
            if 'generate_portfolio_signals' not in namespace:
                logger.info("No portfolio function found, falling back to single-asset backtest")
                return self.run_backtest(strategy_code, symbols)

            generate_portfolio_signals = namespace['generate_portfolio_signals']

            # Generate portfolio signals
            portfolio_signals = generate_portfolio_signals(all_data)

            # Run portfolio backtest with position sizing
            portfolio_returns = self._backtest_portfolio(
                all_data,
                portfolio_signals,
                rebalance_frequency
            )

            if portfolio_returns is None or len(portfolio_returns) == 0:
                return self._get_default_metrics()

            # Calculate metrics
            metrics = self._calculate_portfolio_metrics(portfolio_returns, portfolio_signals)

            logger.info(f"Portfolio backtest complete: Sharpe={metrics['sharpe_ratio']:.2f}, Return={metrics['total_return']:.1f}%")

            return metrics

        except Exception as e:
            logger.error(f"Portfolio backtest error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_default_metrics()

    def _backtest_portfolio(
        self,
        all_data: Dict[str, pd.DataFrame],
        portfolio_signals: Dict[str, pd.Series],
        rebalance_frequency: str
    ) -> Optional[pd.Series]:
        """
        Execute portfolio backtest with position sizing

        Args:
            all_data: Dictionary of symbol -> OHLCV data
            portfolio_signals: Dictionary of symbol -> signal series
            rebalance_frequency: Rebalancing frequency

        Returns:
            Portfolio returns series
        """
        try:
            # Align all data to common date index
            common_dates = None
            for symbol, data in all_data.items():
                if common_dates is None:
                    common_dates = data.index
                else:
                    common_dates = common_dates.intersection(data.index)

            if len(common_dates) == 0:
                logger.warning("No common dates across assets")
                return None

            # Create portfolio value series
            portfolio_value = pd.Series(index=common_dates, dtype=float)
            portfolio_value.iloc[0] = self.initial_capital

            # Track positions for each symbol
            positions = {symbol: 0.0 for symbol in all_data.keys()}
            cash = self.initial_capital

            # Determine rebalance dates
            if rebalance_frequency == 'daily':
                rebalance_dates = common_dates
            elif rebalance_frequency == 'weekly':
                rebalance_dates = common_dates[::5]  # Every 5 trading days
            elif rebalance_frequency == 'monthly':
                rebalance_dates = common_dates[::21]  # Every 21 trading days
            else:
                rebalance_dates = common_dates

            # Run backtest
            for i, date in enumerate(common_dates):
                # Check if we should rebalance
                if date in rebalance_dates:
                    # Calculate target weights from signals
                    target_weights = {}
                    total_signal = 0.0

                    for symbol in all_data.keys():
                        if symbol in portfolio_signals:
                            signal = portfolio_signals[symbol].get(date, 0.0)
                            # Use absolute value for weight calculation, sign for direction
                            total_signal += abs(signal)
                            target_weights[symbol] = signal
                        else:
                            target_weights[symbol] = 0.0

                    # Normalize weights
                    if total_signal > 0:
                        for symbol in target_weights:
                            target_weights[symbol] = target_weights[symbol] / total_signal
                    else:
                        # Equal weight if no signals
                        for symbol in target_weights:
                            target_weights[symbol] = 1.0 / len(all_data)

                    # Rebalance portfolio
                    portfolio_val = portfolio_value.iloc[i-1] if i > 0 else self.initial_capital

                    for symbol, target_weight in target_weights.items():
                        current_price = all_data[symbol].loc[date, 'close']
                        target_value = portfolio_val * target_weight
                        current_value = positions[symbol] * current_price

                        # Calculate trade
                        trade_value = target_value - current_value

                        # Apply transaction costs
                        transaction_cost = abs(trade_value) * (self.commission_pct + self.slippage_pct)
                        cash -= transaction_cost

                        # Update position
                        trade_shares = trade_value / current_price
                        positions[symbol] += trade_shares
                        cash -= trade_value

                # Calculate portfolio value for this date
                total_value = cash
                for symbol, shares in positions.items():
                    current_price = all_data[symbol].loc[date, 'close']
                    total_value += shares * current_price

                portfolio_value.iloc[i] = total_value

            # Calculate returns
            portfolio_returns = portfolio_value.pct_change().dropna()

            return portfolio_returns

        except Exception as e:
            logger.error(f"Error in portfolio backtest: {e}")
            return None

    def _calculate_portfolio_metrics(
        self,
        returns: pd.Series,
        portfolio_signals: Dict[str, pd.Series]
    ) -> Dict[str, float]:
        """Calculate portfolio-specific metrics"""

        if len(returns) == 0 or returns.std() == 0:
            return self._get_default_metrics()

        # Use existing metrics calculation
        # Calculate average trading frequency across assets
        all_signals = []
        for signals in portfolio_signals.values():
            all_signals.append(signals)

        metrics = self._calculate_metrics(returns, all_signals)

        return metrics
