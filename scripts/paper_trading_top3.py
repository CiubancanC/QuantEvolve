#!/usr/bin/env python3
"""
Paper Trading Script for Top 3 Evolved Strategies

This script runs the top 3 performing strategies in parallel on Alpaca paper trading
for a 1-month evaluation period. Each strategy trades independently with equal capital
allocation.

Usage:
    python3 scripts/paper_trading_top3.py --mode check    # Check signals only (no trades)
    python3 scripts/paper_trading_top3.py --mode paper    # Execute paper trades
    python3 scripts/paper_trading_top3.py --status        # Show current positions/performance
"""

import os
import sys
import json
import pickle
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path("logs/paper_trading")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"paper_trading_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import Alpaca (install if needed: pip install alpaca-trade-api)
try:
    import alpaca_trade_api as tradeapi
except ImportError:
    logger.error("alpaca-trade-api not installed. Run: pip install alpaca-trade-api")
    sys.exit(1)

# Try to import data fetching libraries
try:
    import yfinance as yf
    HAS_YFINANCE = True
except:
    HAS_YFINANCE = False
    logger.warning("yfinance not available, will try alternative data sources")


class PaperTradingManager:
    """Manages paper trading for multiple strategies in parallel"""

    def __init__(self, capital_per_strategy: float = 10000):
        """
        Initialize paper trading manager

        Args:
            capital_per_strategy: Initial capital allocated to each strategy ($)
        """
        self.capital_per_strategy = capital_per_strategy

        # Initialize Alpaca API
        self.api = self._initialize_alpaca()

        # Load strategies
        self.strategies = self._load_top_strategies()

        # Results tracking directory
        self.results_dir = Path("results/paper_trading")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize tracking data
        self.tracking_file = self.results_dir / "tracking.json"
        self.tracking_data = self._load_tracking_data()

        logger.info(f"Initialized PaperTradingManager with {len(self.strategies)} strategies")
        logger.info(f"Capital per strategy: ${capital_per_strategy:,.2f}")

    def _initialize_alpaca(self) -> tradeapi.REST:
        """Initialize Alpaca API connection"""
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        endpoint = os.getenv('ALPACA_ENDPOINT', 'https://paper-api.alpaca.markets')

        if not api_key or not secret_key:
            logger.error("ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env file")
            sys.exit(1)

        try:
            api = tradeapi.REST(api_key, secret_key, endpoint, api_version='v2')

            # Test connection
            account = api.get_account()
            logger.info(f"Connected to Alpaca Paper Trading")
            logger.info(f"Account Status: {account.status}")
            logger.info(f"Buying Power: ${float(account.buying_power):,.2f}")
            logger.info(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")

            return api
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            sys.exit(1)

    def _load_top_strategies(self) -> List[Dict]:
        """Load top 3 strategies from evolutionary database"""
        db_path = Path("results/final/evolutionary_database.pkl")

        if not db_path.exists():
            logger.error(f"Evolutionary database not found at {db_path}")
            sys.exit(1)

        with open(db_path, 'rb') as f:
            db = pickle.load(f)

        all_strategies = db.feature_map.get_all_strategies()
        sorted_strategies = sorted(
            all_strategies,
            key=lambda s: s.metrics.get('total_return', 0),
            reverse=True
        )

        top_3 = []
        for i, strat in enumerate(sorted_strategies[:3], 1):
            strategy_info = {
                'rank': i,
                'id': strat.strategy_id,
                'code': strat.code,
                'hypothesis': strat.hypothesis,
                'backtest_metrics': {
                    'total_return': strat.metrics.get('total_return', 0),
                    'sharpe_ratio': strat.metrics.get('sharpe_ratio', 0),
                    'max_drawdown': strat.metrics.get('max_drawdown', 0),
                    'num_trades': strat.metrics.get('trading_frequency', 0)
                }
            }
            top_3.append(strategy_info)

            logger.info(f"Loaded Strategy #{i} ({strat.strategy_id})")
            logger.info(f"  Backtest Return: {strat.metrics.get('total_return', 0):.2f}%")
            logger.info(f"  Sharpe: {strat.metrics.get('sharpe_ratio', 0):.2f}")

        return top_3

    def _load_tracking_data(self) -> Dict:
        """Load or initialize tracking data"""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded existing tracking data from {self.tracking_file}")
                return data
        else:
            data = {
                'start_date': datetime.now().isoformat(),
                'strategies': {},
                'daily_snapshots': []
            }

            # Initialize tracking for each strategy
            for strat in self.strategies:
                data['strategies'][strat['id']] = {
                    'rank': strat['rank'],
                    'initial_capital': self.capital_per_strategy,
                    'current_value': self.capital_per_strategy,
                    'positions': [],
                    'trades': [],
                    'daily_returns': []
                }

            self._save_tracking_data(data)
            logger.info(f"Initialized new tracking data at {self.tracking_file}")
            return data

    def _save_tracking_data(self, data: Optional[Dict] = None):
        """Save tracking data to file"""
        if data is None:
            data = self.tracking_data

        with open(self.tracking_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_market_data(self, symbols: List[str], lookback_days: int = 100) -> Dict[str, pd.DataFrame]:
        """
        Fetch recent market data for symbols (uses existing cached data or pandas_datareader)

        Args:
            symbols: List of ticker symbols
            lookback_days: Number of days of historical data to fetch

        Returns:
            Dict mapping symbol to DataFrame with OHLCV data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        data = {}

        # Try to load from existing data directory first (much faster)
        data_dir = Path("data/raw")
        for symbol in symbols:
            try:
                # Check if we have cached data
                csv_path = data_dir / f"{symbol}.csv"
                parquet_path = data_dir / f"{symbol}.parquet"

                if parquet_path.exists():
                    df = pd.read_parquet(parquet_path)
                    logger.info(f"Loaded {symbol} from cached parquet file")
                elif csv_path.exists():
                    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                    logger.info(f"Loaded {symbol} from cached CSV file")
                else:
                    # Fall back to pandas_datareader or simple CSV download
                    logger.warning(f"No cached data for {symbol}, using recent data may be delayed")
                    continue

                # Filter to recent data
                df = df[df.index >= start_date]

                # Ensure columns are lowercase
                df.columns = [c.lower() for c in df.columns]

                # Keep only OHLCV
                if all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']):
                    df = df[['open', 'high', 'low', 'close', 'volume']]
                    data[symbol] = df
                    logger.info(f"Loaded {len(df)} bars for {symbol} (from {df.index[0].date()} to {df.index[-1].date()})")
                else:
                    logger.error(f"Missing required columns for {symbol}")

            except Exception as e:
                logger.error(f"Failed to load data for {symbol}: {e}")

        return data

    def generate_signals(self, strategy_info: Dict, market_data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """
        Generate trading signals for a strategy

        Args:
            strategy_info: Strategy information dict
            market_data: Dict mapping symbol to DataFrame

        Returns:
            Dict mapping symbol to signal (-1, 0, 1)
        """
        signals = {}

        try:
            # Execute strategy code to get the function
            local_vars = {}
            exec(strategy_info['code'], {}, local_vars)

            # Find the strategy function (should be the only function defined)
            strategy_func = None
            for var_name, var_value in local_vars.items():
                if callable(var_value) and not var_name.startswith('_'):
                    strategy_func = var_value
                    break

            if strategy_func is None:
                logger.error(f"No strategy function found in code for {strategy_info['id']}")
                return signals

            # Generate signal for each symbol
            for symbol, data in market_data.items():
                try:
                    signal_series = strategy_func(data)

                    # Get the most recent signal
                    if isinstance(signal_series, pd.Series) and len(signal_series) > 0:
                        latest_signal = signal_series.iloc[-1]

                        # Validate signal
                        if pd.isna(latest_signal):
                            latest_signal = 0
                        else:
                            latest_signal = int(np.clip(latest_signal, -1, 1))

                        signals[symbol] = latest_signal
                        logger.debug(f"Strategy {strategy_info['id']}: {symbol} signal = {latest_signal}")
                    else:
                        signals[symbol] = 0
                        logger.warning(f"Strategy {strategy_info['id']}: Invalid signal for {symbol}, defaulting to 0")

                except Exception as e:
                    logger.error(f"Error generating signal for {symbol} with strategy {strategy_info['id']}: {e}")
                    signals[symbol] = 0

        except Exception as e:
            logger.error(f"Error executing strategy {strategy_info['id']}: {e}")

        return signals

    def check_signals_only(self, symbols: List[str]):
        """Check signals without executing trades"""
        logger.info("=" * 80)
        logger.info("SIGNAL CHECK MODE (No Trades)")
        logger.info("=" * 80)

        # Fetch market data
        market_data = self.get_market_data(symbols)

        if not market_data:
            logger.error("No market data available")
            return

        # Generate signals for each strategy
        for strategy_info in self.strategies:
            logger.info(f"\nStrategy #{strategy_info['rank']}: {strategy_info['id']}")
            logger.info(f"Hypothesis: {strategy_info['hypothesis'][:100]}...")

            signals = self.generate_signals(strategy_info, market_data)

            logger.info(f"Signals:")
            for symbol, signal in signals.items():
                signal_str = {-1: "SELL", 0: "HOLD", 1: "BUY"}.get(signal, "UNKNOWN")
                logger.info(f"  {symbol}: {signal_str} ({signal})")

    def execute_paper_trading(self, symbols: List[str]):
        """Execute paper trading for all strategies"""
        logger.info("=" * 80)
        logger.info("PAPER TRADING MODE")
        logger.info("=" * 80)

        # Fetch market data
        market_data = self.get_market_data(symbols)

        if not market_data:
            logger.error("No market data available")
            return

        # Execute trades for each strategy
        for strategy_info in self.strategies:
            logger.info(f"\nProcessing Strategy #{strategy_info['rank']}: {strategy_info['id']}")

            # Generate signals
            signals = self.generate_signals(strategy_info, market_data)

            # Execute trades based on signals
            self._execute_strategy_trades(strategy_info, signals, market_data)

        # Update daily snapshot
        self._record_daily_snapshot()

        # Save tracking data
        self._save_tracking_data()

        logger.info("\nPaper trading execution completed")

    def _execute_strategy_trades(self, strategy_info: Dict, signals: Dict[str, int], market_data: Dict[str, pd.DataFrame]):
        """Execute trades for a single strategy based on signals"""
        strategy_id = strategy_info['id']
        strategy_tracking = self.tracking_data['strategies'][strategy_id]

        # Get current positions for this strategy
        current_positions = {pos['symbol']: pos for pos in strategy_tracking['positions']}

        for symbol, signal in signals.items():
            current_position = current_positions.get(symbol)

            # Get current price
            current_price = market_data[symbol]['close'].iloc[-1]

            if signal == 1 and current_position is None:
                # BUY signal and no position - open long position
                shares = int(strategy_tracking['current_value'] * 0.95 / current_price)  # Use 95% of capital

                if shares > 0:
                    try:
                        # Place paper order
                        order = self.api.submit_order(
                            symbol=symbol,
                            qty=shares,
                            side='buy',
                            type='market',
                            time_in_force='day'
                        )

                        logger.info(f"  BUY {shares} shares of {symbol} @ ${current_price:.2f}")

                        # Record trade
                        trade = {
                            'timestamp': datetime.now().isoformat(),
                            'symbol': symbol,
                            'action': 'buy',
                            'shares': shares,
                            'price': current_price,
                            'order_id': order.id
                        }
                        strategy_tracking['trades'].append(trade)

                        # Add to positions
                        strategy_tracking['positions'].append({
                            'symbol': symbol,
                            'shares': shares,
                            'entry_price': current_price,
                            'entry_date': datetime.now().isoformat()
                        })

                    except Exception as e:
                        logger.error(f"  Failed to BUY {symbol}: {e}")

            elif signal == -1 and current_position is not None:
                # SELL signal and have position - close position
                shares = current_position['shares']

                try:
                    # Place paper order
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=shares,
                        side='sell',
                        type='market',
                        time_in_force='day'
                    )

                    entry_price = current_position['entry_price']
                    pnl = (current_price - entry_price) * shares
                    pnl_pct = (current_price / entry_price - 1) * 100

                    logger.info(f"  SELL {shares} shares of {symbol} @ ${current_price:.2f}")
                    logger.info(f"    Entry: ${entry_price:.2f}, P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")

                    # Record trade
                    trade = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'action': 'sell',
                        'shares': shares,
                        'price': current_price,
                        'entry_price': entry_price,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'order_id': order.id
                    }
                    strategy_tracking['trades'].append(trade)

                    # Remove from positions
                    strategy_tracking['positions'] = [
                        p for p in strategy_tracking['positions']
                        if p['symbol'] != symbol
                    ]

                    # Update current value
                    strategy_tracking['current_value'] += pnl

                except Exception as e:
                    logger.error(f"  Failed to SELL {symbol}: {e}")

            elif signal == 0:
                # HOLD signal
                if current_position:
                    unrealized_pnl = (current_price - current_position['entry_price']) * current_position['shares']
                    logger.debug(f"  HOLD {symbol}: Unrealized P&L: ${unrealized_pnl:.2f}")

    def _record_daily_snapshot(self):
        """Record daily performance snapshot"""
        snapshot = {
            'date': datetime.now().isoformat(),
            'strategies': {}
        }

        for strategy_id, tracking in self.tracking_data['strategies'].items():
            snapshot['strategies'][strategy_id] = {
                'current_value': tracking['current_value'],
                'num_positions': len(tracking['positions']),
                'num_trades': len(tracking['trades']),
                'return_pct': (tracking['current_value'] / tracking['initial_capital'] - 1) * 100
            }

        self.tracking_data['daily_snapshots'].append(snapshot)
        logger.info("\nDaily Snapshot Recorded:")
        for strategy_id, data in snapshot['strategies'].items():
            logger.info(f"  {strategy_id}: ${data['current_value']:,.2f} ({data['return_pct']:+.2f}%)")

    def show_status(self):
        """Display current status and performance"""
        logger.info("=" * 80)
        logger.info("PAPER TRADING STATUS")
        logger.info("=" * 80)

        start_date = datetime.fromisoformat(self.tracking_data['start_date'])
        days_running = (datetime.now() - start_date).days

        logger.info(f"\nStart Date: {start_date.strftime('%Y-%m-%d')}")
        logger.info(f"Days Running: {days_running}")
        logger.info(f"Total Strategies: {len(self.strategies)}")

        # Overall performance
        total_initial = sum(s['initial_capital'] for s in self.tracking_data['strategies'].values())
        total_current = sum(s['current_value'] for s in self.tracking_data['strategies'].values())
        total_return_pct = (total_current / total_initial - 1) * 100

        logger.info(f"\nOVERALL PORTFOLIO:")
        logger.info(f"  Initial Capital: ${total_initial:,.2f}")
        logger.info(f"  Current Value: ${total_current:,.2f}")
        logger.info(f"  Total Return: {total_return_pct:+.2f}%")

        # Individual strategy performance
        logger.info(f"\nINDIVIDUAL STRATEGIES:")
        for strategy_info in self.strategies:
            strategy_id = strategy_info['id']
            tracking = self.tracking_data['strategies'][strategy_id]

            return_pct = (tracking['current_value'] / tracking['initial_capital'] - 1) * 100

            logger.info(f"\n  Strategy #{strategy_info['rank']}: {strategy_id}")
            logger.info(f"    Backtest Return: {strategy_info['backtest_metrics']['total_return']:.2f}%")
            logger.info(f"    Paper Trading Return: {return_pct:+.2f}%")
            logger.info(f"    Current Value: ${tracking['current_value']:,.2f}")
            logger.info(f"    Open Positions: {len(tracking['positions'])}")
            logger.info(f"    Total Trades: {len(tracking['trades'])}")

            if tracking['positions']:
                logger.info(f"    Positions:")
                for pos in tracking['positions']:
                    logger.info(f"      - {pos['symbol']}: {pos['shares']} shares @ ${pos['entry_price']:.2f}")


def main():
    parser = argparse.ArgumentParser(description='Paper Trading for Top 3 Evolved Strategies')
    parser.add_argument('--mode', choices=['check', 'paper'],
                       help='check: Show signals only, paper: Execute paper trades')
    parser.add_argument('--status', action='store_true',
                       help='Show current status and performance')
    parser.add_argument('--capital', type=float, default=10000,
                       help='Capital per strategy in dollars (default: 10000)')
    parser.add_argument('--symbols', nargs='+',
                       default=['AAPL', 'NVDA', 'AMZN', 'GOOGL', 'MSFT', 'TSLA'],
                       help='Symbols to trade (default: AAPL NVDA AMZN GOOGL MSFT TSLA)')

    args = parser.parse_args()

    # Initialize manager
    manager = PaperTradingManager(capital_per_strategy=args.capital)

    if args.status:
        manager.show_status()
    elif args.mode == 'check':
        manager.check_signals_only(args.symbols)
    elif args.mode == 'paper':
        manager.execute_paper_trading(args.symbols)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
