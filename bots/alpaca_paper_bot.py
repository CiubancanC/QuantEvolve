#!/usr/bin/env python3
"""
QuantEvolve Alpaca Paper Trading Bot

This bot:
1. Runs daily at market close (4:00 PM ET)
2. Generates signals using your evolved strategy
3. Executes trades automatically in Alpaca paper account
4. Logs all trades and performance
5. Sends you daily reports

Setup:
    pip install alpaca-trade-api pandas yfinance loguru

Usage:
    python3 bots/alpaca_paper_bot.py --run-once      # Test run
    python3 bots/alpaca_paper_bot.py --daemon        # Run continuously
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from loguru import logger
import argparse


class AlpacaPaperBot:
    """
    Automated paper trading bot for Alpaca
    """

    def __init__(
        self,
        api_key=None,
        secret_key=None,
        initial_capital=100000,
        symbols=None,
        max_position_pct=0.10,  # Max 10% per position
        max_total_exposure=0.80,  # Max 80% invested
        stop_loss_pct=0.05,  # 5% stop loss
        log_dir="logs/paper_trading"
    ):
        """
        Initialize the paper trading bot

        Args:
            api_key: Alpaca API key (or set ALPACA_API_KEY env var)
            secret_key: Alpaca secret key (or set ALPACA_SECRET_KEY env var)
            initial_capital: Starting capital
            symbols: List of symbols to trade
            max_position_pct: Max % of capital per position
            max_total_exposure: Max % of capital invested
            stop_loss_pct: Stop loss percentage
            log_dir: Directory for logs
        """
        # API credentials
        self.api_key = api_key or os.environ.get('ALPACA_API_KEY')
        self.secret_key = secret_key or os.environ.get('ALPACA_SECRET_KEY')

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "Alpaca API keys not found! Set ALPACA_API_KEY and ALPACA_SECRET_KEY "
                "environment variables or pass them to constructor."
            )

        # Trading parameters
        self.initial_capital = initial_capital
        self.symbols = symbols or ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'META', 'NVDA']
        self.max_position_pct = max_position_pct
        self.max_total_exposure = max_total_exposure
        self.stop_loss_pct = stop_loss_pct

        # Logging
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set up logger
        log_file = self.log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
        logger.add(log_file, rotation="1 day", retention="90 days")

        # Initialize Alpaca API
        self.api = None
        self._init_alpaca()

        # Trade tracking
        self.trades_file = self.log_dir / "trades.jsonl"
        self.performance_file = self.log_dir / "performance.jsonl"

        # Position tracking (for 3-day hold)
        self.positions_db = self.log_dir / "positions_tracker.json"
        self.load_positions_tracker()

        logger.info("="*80)
        logger.info("QuantEvolve Paper Trading Bot Initialized")
        logger.info("="*80)
        logger.info(f"Symbols: {', '.join(self.symbols)}")
        logger.info(f"Max position size: {self.max_position_pct*100:.1f}%")
        logger.info(f"Max exposure: {self.max_total_exposure*100:.1f}%")
        logger.info(f"Stop loss: {self.stop_loss_pct*100:.1f}%")
        logger.info("="*80)

    def _init_alpaca(self):
        """Initialize Alpaca API connection"""
        try:
            import alpaca_trade_api as tradeapi

            self.api = tradeapi.REST(
                self.api_key,
                self.secret_key,
                'https://paper-api.alpaca.markets',  # PAPER trading
                api_version='v2'
            )

            # Test connection
            account = self.api.get_account()
            logger.info(f"✓ Connected to Alpaca (PAPER)")
            logger.info(f"  Account: {account.account_number}")
            logger.info(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
            logger.info(f"  Cash: ${float(account.cash):,.2f}")

        except ImportError:
            logger.error("alpaca-trade-api not installed!")
            logger.error("Run: pip install alpaca-trade-api")
            raise

        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            raise

    def load_positions_tracker(self):
        """Load position tracker from disk"""
        if self.positions_db.exists():
            with open(self.positions_db, 'r') as f:
                self.open_positions = json.load(f)
        else:
            self.open_positions = {}
        logger.info(f"Loaded {len(self.open_positions)} open positions from tracker")

    def save_positions_tracker(self):
        """Save position tracker to disk"""
        with open(self.positions_db, 'w') as f:
            json.dump(self.open_positions, f, indent=2)

    def get_market_data(self, symbol, days=60):
        """Download recent market data"""
        try:
            data = yf.download(symbol, period=f'{days}d', progress=False)
            if len(data) == 0:
                logger.warning(f"No data for {symbol}")
                return None

            # Handle MultiIndex
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data.columns = data.columns.str.lower()

            # Verify required columns
            required = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required):
                logger.warning(f"Missing columns for {symbol}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error downloading {symbol}: {e}")
            return None

    def generate_signals(self, symbol):
        """
        Generate trading signals for a symbol

        Returns:
            tuple: (signal, price, data) where signal is -1/0/1
        """
        # Get market data
        data = self.get_market_data(symbol)
        if data is None:
            return 0, None, None

        try:
            # Import strategy
            from exported_strategies.strat_734877525 import generate_signals

            # Generate signals
            signals = generate_signals(data.copy())

            # Get latest signal and price
            latest_signal = signals.iloc[-1]
            latest_price = data['close'].iloc[-1]

            return latest_signal, latest_price, data

        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {e}")
            return 0, None, None

    def calculate_position_size(self, price):
        """
        Calculate position size based on available capital and risk limits

        Args:
            price: Current stock price

        Returns:
            int: Number of shares to buy
        """
        # Get account info
        account = self.api.get_account()
        cash = float(account.cash)
        portfolio_value = float(account.portfolio_value)

        # Calculate max position value
        max_position_value = portfolio_value * self.max_position_pct

        # Don't use all cash (keep some reserve)
        max_cash_to_use = cash * self.max_total_exposure

        # Position size is minimum of constraints
        position_value = min(max_position_value, max_cash_to_use)

        # Calculate shares
        shares = int(position_value / price)

        return shares

    def check_stop_losses(self):
        """Check and execute stop losses on open positions"""
        logger.info("Checking stop losses...")

        for symbol, position_info in list(self.open_positions.items()):
            try:
                # Get current price
                _, current_price, _ = self.generate_signals(symbol)
                if current_price is None:
                    continue

                entry_price = position_info['entry_price']
                loss_pct = (entry_price - current_price) / entry_price

                if loss_pct > self.stop_loss_pct:
                    logger.warning(f"🛑 STOP LOSS triggered on {symbol}: {loss_pct*100:.2f}%")
                    logger.warning(f"   Entry: ${entry_price:.2f}, Current: ${current_price:.2f}")

                    # Close position
                    self.close_position(symbol, reason="stop_loss")

            except Exception as e:
                logger.error(f"Error checking stop loss for {symbol}: {e}")

    def check_exit_dates(self):
        """Check if any positions need to be exited (3-day hold)"""
        logger.info("Checking exit dates...")

        today = datetime.now().date()

        for symbol, position_info in list(self.open_positions.items()):
            entry_date = datetime.fromisoformat(position_info['entry_date']).date()
            days_held = (today - entry_date).days

            if days_held >= 3:
                logger.info(f"📅 Exiting {symbol} after {days_held} days (3-day hold)")
                self.close_position(symbol, reason="3_day_exit")

    def close_position(self, symbol, reason="manual"):
        """Close a position"""
        try:
            # Get current position from Alpaca
            position = self.api.get_position(symbol)
            shares = int(position.qty)
            current_price = float(position.current_price)

            # Submit sell order
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='sell',
                type='market',
                time_in_force='day'
            )

            # Calculate P&L
            entry_price = self.open_positions[symbol]['entry_price']
            pnl = (current_price - entry_price) * shares
            pnl_pct = (current_price / entry_price - 1) * 100

            logger.info(f"✓ SELL {shares} shares of {symbol} at ${current_price:.2f}")
            logger.info(f"  Reason: {reason}")
            logger.info(f"  Entry: ${entry_price:.2f}, Exit: ${current_price:.2f}")
            logger.info(f"  P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")

            # Log trade
            self.log_trade({
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': 'SELL',
                'shares': shares,
                'price': current_price,
                'reason': reason,
                'entry_price': entry_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })

            # Remove from tracker
            del self.open_positions[symbol]
            self.save_positions_tracker()

        except Exception as e:
            logger.error(f"Error closing position in {symbol}: {e}")

    def execute_buy_signal(self, symbol, signal, price):
        """Execute a buy order"""
        try:
            # Calculate position size
            shares = self.calculate_position_size(price)

            if shares == 0:
                logger.warning(f"Cannot buy {symbol}: position size = 0")
                return

            # Submit buy order
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='buy',
                type='market',
                time_in_force='day'
            )

            logger.info(f"✓ BUY {shares} shares of {symbol} at ${price:.2f}")
            logger.info(f"  Total value: ${shares * price:,.2f}")

            # Track position
            self.open_positions[symbol] = {
                'entry_date': datetime.now().isoformat(),
                'entry_price': price,
                'shares': shares,
                'signal': signal
            }
            self.save_positions_tracker()

            # Log trade
            self.log_trade({
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': 'BUY',
                'shares': shares,
                'price': price,
                'signal': signal
            })

        except Exception as e:
            logger.error(f"Error buying {symbol}: {e}")

    def log_trade(self, trade_data):
        """Log trade to file"""
        with open(self.trades_file, 'a') as f:
            f.write(json.dumps(trade_data) + '\n')

    def log_performance(self):
        """Log daily performance metrics"""
        try:
            account = self.api.get_account()

            performance = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'equity': float(account.equity),
                'long_market_value': float(account.long_market_value),
                'num_positions': len(self.open_positions),
                'positions': list(self.open_positions.keys())
            }

            # Calculate return
            total_return = (performance['portfolio_value'] / self.initial_capital - 1) * 100

            logger.info("="*80)
            logger.info("DAILY PERFORMANCE")
            logger.info("="*80)
            logger.info(f"Portfolio Value: ${performance['portfolio_value']:,.2f}")
            logger.info(f"Cash: ${performance['cash']:,.2f}")
            logger.info(f"Invested: ${performance['long_market_value']:,.2f}")
            logger.info(f"Total Return: {total_return:+.2f}%")
            logger.info(f"Open Positions: {performance['num_positions']}")
            if performance['positions']:
                logger.info(f"  {', '.join(performance['positions'])}")
            logger.info("="*80)

            # Save to file
            with open(self.performance_file, 'a') as f:
                f.write(json.dumps(performance) + '\n')

        except Exception as e:
            logger.error(f"Error logging performance: {e}")

    def run_daily_cycle(self):
        """
        Run the complete daily trading cycle

        1. Check stop losses
        2. Check 3-day exits
        3. Generate new signals
        4. Execute trades
        5. Log performance
        """
        logger.info("\n" + "="*80)
        logger.info(f"DAILY TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80 + "\n")

        # Step 1: Check stop losses
        self.check_stop_losses()

        # Step 2: Check 3-day exits
        self.check_exit_dates()

        # Step 3: Generate signals and execute trades
        logger.info("Checking signals for all symbols...")

        for symbol in self.symbols:
            logger.info(f"\nAnalyzing {symbol}...")

            # Generate signal
            signal, price, data = self.generate_signals(symbol)

            if price is None:
                logger.warning(f"  Skipping {symbol} - no data")
                continue

            # Check if we already have a position
            has_position = symbol in self.open_positions

            # Execute based on signal
            if signal == 1 and not has_position:
                logger.info(f"  🟢 BUY signal at ${price:.2f}")
                self.execute_buy_signal(symbol, signal, price)

            elif signal == 0 and has_position:
                logger.info(f"  🔴 EXIT signal at ${price:.2f}")
                self.close_position(symbol, reason="exit_signal")

            else:
                if has_position:
                    entry_price = self.open_positions[symbol]['entry_price']
                    pnl_pct = (price / entry_price - 1) * 100
                    logger.info(f"  ⚪ HOLD - Current P&L: {pnl_pct:+.2f}%")
                else:
                    logger.info(f"  ⚪ No action at ${price:.2f}")

        # Step 4: Log performance
        self.log_performance()

        logger.info("\n✓ Daily cycle complete\n")

    def run_daemon(self, check_interval=3600):
        """
        Run bot as a daemon (continuously)

        Args:
            check_interval: Seconds between checks (default 1 hour)
        """
        logger.info("Starting daemon mode...")
        logger.info(f"Will run daily cycle at 4:30 PM ET")
        logger.info(f"Checking every {check_interval/60:.0f} minutes")

        last_run_date = None

        while True:
            try:
                now = datetime.now()

                # Check if it's 4:30 PM ET (market close)
                # For testing, you might want to change this
                if now.hour == 16 and now.minute >= 30:
                    # Only run once per day
                    if now.date() != last_run_date:
                        logger.info("Market closed, running daily cycle...")
                        self.run_daily_cycle()
                        last_run_date = now.date()

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down bot...")
                break

            except Exception as e:
                logger.error(f"Error in daemon loop: {e}")
                time.sleep(check_interval)


def main():
    parser = argparse.ArgumentParser(description='QuantEvolve Alpaca Paper Trading Bot')

    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run one trading cycle and exit (for testing)'
    )

    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run continuously as a daemon'
    )

    parser.add_argument(
        '--initial-capital',
        type=float,
        default=100000,
        help='Initial capital (default: 100000)'
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        default=['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'META', 'NVDA'],
        help='Symbols to trade'
    )

    args = parser.parse_args()

    # Create bot
    bot = AlpacaPaperBot(
        initial_capital=args.initial_capital,
        symbols=args.symbols
    )

    # Run based on mode
    if args.run_once:
        logger.info("Running single cycle (test mode)")
        bot.run_daily_cycle()

    elif args.daemon:
        logger.info("Running as daemon")
        bot.run_daemon()

    else:
        logger.info("No mode specified. Use --run-once or --daemon")
        logger.info("Example: python3 bots/alpaca_paper_bot.py --run-once")


if __name__ == '__main__':
    main()
