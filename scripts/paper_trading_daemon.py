#!/usr/bin/env python3
"""
Paper Trading Daemon - Automated Long-Running Process

This daemon runs continuously and automatically executes paper trading for your
top 3 evolved strategies. It handles:
- Market hours detection (US equities: Mon-Fri 9:30 AM - 4 PM ET)
- Daily trade execution (default: 3:30 PM ET, 30 min before close)
- Automatic report generation
- Error recovery and retry logic
- Health monitoring and status updates
- Graceful shutdown

Usage:
    # Start the daemon
    python3 scripts/paper_trading_daemon.py start

    # Stop the daemon
    python3 scripts/paper_trading_daemon.py stop

    # Check status
    python3 scripts/paper_trading_daemon.py status

    # Run in foreground (for testing)
    python3 scripts/paper_trading_daemon.py run
"""

import os
import sys
import json
import signal
import time
import atexit
import logging
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Optional
import pytz

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Setup logging
log_dir = Path("logs/daemon")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "paper_trading_daemon.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PaperTradingDaemon:
    """Long-running daemon for automated paper trading"""

    def __init__(self,
                 trade_time: str = "15:30",  # 3:30 PM ET (30 min before close)
                 check_interval: int = 300,   # Check every 5 minutes
                 run_duration_days: int = 30):
        """
        Initialize daemon

        Args:
            trade_time: Time to execute daily trades (HH:MM in ET)
            check_interval: Seconds between status checks
            run_duration_days: Total days to run (default 30 for 1 month)
        """
        self.trade_time = self._parse_time(trade_time)
        self.check_interval = check_interval
        self.run_duration_days = run_duration_days
        self.timezone = pytz.timezone('America/New_York')

        # State management
        self.state_file = Path("results/paper_trading/daemon_state.json")
        self.state = self._load_state()

        # PID file for daemon management
        self.pid_file = Path("results/paper_trading/daemon.pid")

        # Shutdown flag
        self.shutdown_requested = False

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Register cleanup
        atexit.register(self._cleanup)

        logger.info("Paper Trading Daemon initialized")
        logger.info(f"Trade execution time: {trade_time} ET")
        logger.info(f"Check interval: {check_interval} seconds")
        logger.info(f"Run duration: {run_duration_days} days")

    def _parse_time(self, time_str: str) -> dt_time:
        """Parse time string HH:MM to time object"""
        hour, minute = map(int, time_str.split(':'))
        return dt_time(hour, minute)

    def _load_state(self) -> dict:
        """Load daemon state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                logger.info(f"Loaded existing state: Started {state.get('start_time')}")
                return state

        state = {
            'start_time': datetime.now(self.timezone).isoformat(),
            'last_trade_date': None,
            'total_trading_days': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'errors': [],
            'status': 'initializing'
        }
        self._save_state(state)
        return state

    def _save_state(self, state: Optional[dict] = None):
        """Save daemon state to file"""
        if state is None:
            state = self.state

        state['last_update'] = datetime.now().isoformat()

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True

    def _cleanup(self):
        """Cleanup on exit"""
        logger.info("Cleaning up...")
        if self.pid_file.exists():
            self.pid_file.unlink()
        self._save_state()

    def _write_pid(self):
        """Write PID file"""
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def _is_market_open(self) -> bool:
        """Check if US equity markets are currently open"""
        now = datetime.now(self.timezone)

        # Check if weekday (0=Monday, 6=Sunday)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False

        # Check market hours (9:30 AM - 4:00 PM ET)
        market_open = dt_time(9, 30)
        market_close = dt_time(16, 0)

        current_time = now.time()

        is_open = market_open <= current_time <= market_close

        if is_open:
            logger.debug(f"Markets are OPEN (current time: {current_time})")
        else:
            logger.debug(f"Markets are CLOSED (current time: {current_time})")

        return is_open

    def _should_trade_now(self) -> bool:
        """Check if it's time to execute daily trades"""
        now = datetime.now(self.timezone)
        current_date = now.date().isoformat()

        # Check if we already traded today
        if self.state['last_trade_date'] == current_date:
            logger.debug(f"Already traded today ({current_date})")
            return False

        # Check if markets are open
        if not self._is_market_open():
            logger.debug("Markets closed, cannot trade")
            return False

        # Check if it's past our designated trade time
        current_time = now.time()
        if current_time >= self.trade_time:
            logger.info(f"Time to trade! Current: {current_time}, Target: {self.trade_time}")
            return True

        logger.debug(f"Not yet trade time. Current: {current_time}, Target: {self.trade_time}")
        return False

    def _execute_daily_trades(self):
        """Execute daily paper trading"""
        logger.info("=" * 80)
        logger.info("EXECUTING DAILY PAPER TRADES")
        logger.info("=" * 80)

        try:
            # Import here to avoid circular dependencies
            from paper_trading_top3 import PaperTradingManager

            # Initialize manager
            manager = PaperTradingManager(capital_per_strategy=10000)

            # Define symbols
            symbols = ['AAPL', 'NVDA', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']

            # Execute trades
            manager.execute_paper_trading(symbols)

            # Update state
            self.state['last_trade_date'] = datetime.now(self.timezone).date().isoformat()
            self.state['total_trading_days'] += 1
            self.state['successful_trades'] += 1
            self.state['status'] = 'running'
            self._save_state()

            logger.info("✓ Daily trading execution completed successfully")

            # Generate report
            self._generate_report()

            return True

        except Exception as e:
            logger.error(f"✗ Failed to execute daily trades: {e}", exc_info=True)

            # Update state with error
            self.state['failed_trades'] += 1
            self.state['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'type': 'trade_execution'
            })
            self._save_state()

            return False

    def _generate_report(self):
        """Generate daily performance report"""
        try:
            logger.info("Generating daily performance report...")

            import subprocess
            result = subprocess.run(
                ['python3', 'scripts/generate_paper_trading_report.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info("✓ Report generated successfully")

                # Save markdown version
                report_dir = Path("results/paper_trading/daily_reports")
                report_dir.mkdir(parents=True, exist_ok=True)

                report_file = report_dir / f"report_{datetime.now().strftime('%Y%m%d')}.md"

                result_md = subprocess.run(
                    ['python3', 'scripts/generate_paper_trading_report.py', '--format', 'markdown'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result_md.returncode == 0:
                    with open(report_file, 'w') as f:
                        f.write(result_md.stdout)
                    logger.info(f"✓ Saved report to {report_file}")

            else:
                logger.error(f"✗ Report generation failed: {result.stderr}")

        except Exception as e:
            logger.error(f"✗ Failed to generate report: {e}")

    def _should_continue_running(self) -> bool:
        """Check if daemon should continue running"""
        start_time = datetime.fromisoformat(self.state['start_time'])
        # Ensure timezone-aware
        if start_time.tzinfo is None:
            start_time = self.timezone.localize(start_time)
        elapsed_days = (datetime.now(self.timezone) - start_time).days

        if elapsed_days >= self.run_duration_days:
            logger.info(f"Reached run duration of {self.run_duration_days} days. Shutting down.")
            return False

        if self.shutdown_requested:
            logger.info("Shutdown requested by signal.")
            return False

        return True

    def _print_status(self):
        """Print current daemon status"""
        now = datetime.now(self.timezone)
        start_time = datetime.fromisoformat(self.state['start_time'])
        # Ensure start_time is timezone-aware
        if start_time.tzinfo is None:
            start_time = self.timezone.localize(start_time)
        elapsed = now - start_time

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"DAEMON STATUS - {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info("=" * 80)
        logger.info(f"Status: {self.state['status']}")
        logger.info(f"Uptime: {elapsed.days} days, {elapsed.seconds // 3600} hours")
        logger.info(f"Last trade: {self.state['last_trade_date'] or 'None'}")
        logger.info(f"Total trading days: {self.state['total_trading_days']}")
        logger.info(f"Successful trades: {self.state['successful_trades']}")
        logger.info(f"Failed trades: {self.state['failed_trades']}")
        logger.info(f"Markets: {'OPEN' if self._is_market_open() else 'CLOSED'}")

        # Calculate next trade time
        if self._is_market_open() and now.time() < self.trade_time:
            next_trade = now.replace(hour=self.trade_time.hour, minute=self.trade_time.minute)
            time_until = next_trade - now
            logger.info(f"Next trade in: {time_until.seconds // 3600}h {(time_until.seconds % 3600) // 60}m")
        elif self.state['last_trade_date'] != now.date().isoformat():
            logger.info(f"Waiting for market open and {self.trade_time}")
        else:
            logger.info("Trading completed for today")

        logger.info("=" * 80)
        logger.info("")

    def run(self):
        """Main daemon loop"""
        logger.info("=" * 80)
        logger.info("PAPER TRADING DAEMON STARTING")
        logger.info("=" * 80)

        self._write_pid()
        self.state['status'] = 'running'
        self._save_state()

        iteration = 0
        status_print_interval = 12  # Print status every ~1 hour (12 * 5 min)

        try:
            while self._should_continue_running():
                iteration += 1

                # Print status periodically
                if iteration % status_print_interval == 1:
                    self._print_status()

                # Check if we should trade
                if self._should_trade_now():
                    self._execute_daily_trades()

                # Sleep before next check
                logger.debug(f"Sleeping for {self.check_interval} seconds...")
                time.sleep(self.check_interval)

            # Final status
            self.state['status'] = 'completed'
            self._save_state()

            logger.info("=" * 80)
            logger.info("DAEMON COMPLETED SUCCESSFULLY")
            logger.info(f"Total trading days: {self.state['total_trading_days']}")
            logger.info(f"Success rate: {self.state['successful_trades']}/{self.state['successful_trades'] + self.state['failed_trades']}")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Daemon error: {e}", exc_info=True)
            self.state['status'] = 'error'
            self.state['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'type': 'daemon_crash'
            })
            self._save_state()
            raise


def check_daemon_status():
    """Check if daemon is running and print status"""
    pid_file = Path("results/paper_trading/daemon.pid")
    state_file = Path("results/paper_trading/daemon_state.json")

    if not pid_file.exists():
        print("Daemon is NOT running")
        print("(No PID file found)")
        return False

    # Read PID
    with open(pid_file, 'r') as f:
        pid = int(f.read().strip())

    # Check if process exists
    try:
        os.kill(pid, 0)  # Doesn't actually kill, just checks if process exists
        is_running = True
    except OSError:
        is_running = False

    if is_running:
        print(f"Daemon IS running (PID: {pid})")

        # Load and print state
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)

            print("\nCurrent Status:")
            print(f"  State: {state.get('status', 'unknown')}")
            print(f"  Started: {state.get('start_time', 'unknown')}")
            print(f"  Last trade: {state.get('last_trade_date', 'None')}")
            print(f"  Trading days: {state.get('total_trading_days', 0)}")
            print(f"  Successful: {state.get('successful_trades', 0)}")
            print(f"  Failed: {state.get('failed_trades', 0)}")

            if state.get('errors'):
                print(f"\nRecent errors: {len(state['errors'])}")
                for err in state['errors'][-3:]:
                    print(f"  - {err['timestamp']}: {err['error'][:60]}")

        return True
    else:
        print(f"Daemon is NOT running")
        print(f"(Stale PID file found: {pid})")
        pid_file.unlink()
        return False


def stop_daemon():
    """Stop the running daemon"""
    pid_file = Path("results/paper_trading/daemon.pid")

    if not pid_file.exists():
        print("Daemon is not running (no PID file)")
        return

    with open(pid_file, 'r') as f:
        pid = int(f.read().strip())

    try:
        print(f"Stopping daemon (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)

        # Wait for process to terminate
        for i in range(10):
            try:
                os.kill(pid, 0)
                print("Waiting for graceful shutdown...")
                time.sleep(1)
            except OSError:
                print("✓ Daemon stopped successfully")
                return

        print("Warning: Daemon didn't stop gracefully, force killing...")
        os.kill(pid, signal.SIGKILL)
        print("✓ Daemon force killed")

    except OSError as e:
        print(f"Error stopping daemon: {e}")
        if pid_file.exists():
            pid_file.unlink()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Paper Trading Daemon')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'run'],
                       help='start: Start as background daemon, stop: Stop daemon, status: Check status, run: Run in foreground')
    parser.add_argument('--trade-time', default='15:30',
                       help='Daily trade execution time (HH:MM in ET, default: 15:30)')
    parser.add_argument('--check-interval', type=int, default=300,
                       help='Seconds between checks (default: 300 = 5 min)')
    parser.add_argument('--duration', type=int, default=30,
                       help='Total days to run (default: 30)')

    args = parser.parse_args()

    if args.command == 'status':
        check_daemon_status()

    elif args.command == 'stop':
        stop_daemon()

    elif args.command == 'run':
        # Run in foreground
        daemon = PaperTradingDaemon(
            trade_time=args.trade_time,
            check_interval=args.check_interval,
            run_duration_days=args.duration
        )
        daemon.run()

    elif args.command == 'start':
        # Check if already running
        if check_daemon_status():
            print("\nDaemon is already running. Stop it first with: python3 scripts/paper_trading_daemon.py stop")
            sys.exit(1)

        # Fork to background
        print("Starting daemon in background...")

        pid = os.fork()
        if pid > 0:
            # Parent process
            print(f"✓ Daemon started with PID: {pid}")
            print("\nMonitor with:")
            print("  python3 scripts/paper_trading_daemon.py status")
            print("  tail -f logs/daemon/paper_trading_daemon.log")
            print("\nStop with:")
            print("  python3 scripts/paper_trading_daemon.py stop")
            sys.exit(0)

        # Child process (daemon)
        os.setsid()  # Create new session

        # Redirect stdout/stderr to log file
        sys.stdout.flush()
        sys.stderr.flush()

        daemon = PaperTradingDaemon(
            trade_time=args.trade_time,
            check_interval=args.check_interval,
            run_duration_days=args.duration
        )
        daemon.run()


if __name__ == '__main__':
    main()
