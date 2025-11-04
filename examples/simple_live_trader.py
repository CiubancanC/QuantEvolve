#!/usr/bin/env python3
"""
Simple Live Trading Script for QuantEvolve Strategy

This script:
1. Downloads latest market data
2. Generates trading signals
3. Prints what trades you should make
4. (Optional) Can execute trades automatically with Alpaca

USAGE:
  python3 examples/simple_live_trader.py --mode check    # Just check signals
  python3 examples/simple_live_trader.py --mode paper    # Paper trading
  python3 examples/simple_live_trader.py --mode live     # REAL MONEY (careful!)
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import argparse


def download_recent_data(symbol, days=60):
    """Download recent stock data"""
    try:
        data = yf.download(symbol, period=f'{days}d', progress=False)
        if len(data) == 0:
            print(f"  ✗ No data for {symbol}")
            return None

        # Handle MultiIndex columns (yfinance sometimes returns these)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Normalize column names
        data.columns = data.columns.str.lower()

        # Ensure we have required columns
        required = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required):
            print(f"  ✗ Missing columns for {symbol}")
            return None

        return data

    except Exception as e:
        print(f"  ✗ Error downloading {symbol}: {e}")
        return None


def generate_signals_wrapper(data):
    """
    Wrapper to import and run the strategy
    This way the strategy code stays clean
    """
    try:
        # Import the best strategy
        from exported_strategies.strat_734877525 import generate_signals
        signals = generate_signals(data.copy())
        return signals
    except Exception as e:
        print(f"  ✗ Error generating signals: {e}")
        return None


def check_signals_for_stocks(symbols):
    """
    Check what the strategy says to do for each stock

    Returns:
        dict: {symbol: {'signal': 1/0/-1, 'price': float, 'data': DataFrame}}
    """
    print(f"\n{'='*80}")
    print(f"CHECKING SIGNALS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    results = {}

    for symbol in symbols:
        print(f"Checking {symbol}...")

        # Download data
        data = download_recent_data(symbol)
        if data is None:
            continue

        # Generate signals
        signals = generate_signals_wrapper(data)
        if signals is None:
            continue

        # Get latest signal
        latest_signal = signals.iloc[-1]
        latest_price = data['close'].iloc[-1]

        results[symbol] = {
            'signal': latest_signal,
            'price': latest_price,
            'data': data
        }

        # Print signal
        if latest_signal == 1:
            print(f"  🟢 BUY {symbol} at ${latest_price:.2f}")
        elif latest_signal == -1:
            print(f"  🔴 SELL {symbol} at ${latest_price:.2f}")
        else:
            print(f"  ⚪ HOLD {symbol} - no action at ${latest_price:.2f}")

    return results


def calculate_position_size(capital, num_positions, price, max_pct=0.1):
    """
    Calculate how many shares to buy

    Args:
        capital: Total portfolio value
        num_positions: Number of positions to split capital across
        price: Current stock price
        max_pct: Maximum % of capital per position (default 10%)

    Returns:
        int: Number of shares to buy
    """
    # Equal weight across positions
    position_value = capital / num_positions

    # Don't exceed max position size
    max_position_value = capital * max_pct
    position_value = min(position_value, max_position_value)

    # Calculate shares
    shares = int(position_value / price)

    return shares


def print_trading_plan(results, capital=10000):
    """
    Print a trading plan based on signals

    Args:
        results: Output from check_signals_for_stocks()
        capital: How much money you have to invest
    """
    print(f"\n{'='*80}")
    print(f"TRADING PLAN")
    print(f"{'='*80}\n")

    buy_signals = [s for s, r in results.items() if r['signal'] == 1]
    sell_signals = [s for s, r in results.items() if r['signal'] == -1]
    hold_signals = [s for s, r in results.items() if r['signal'] == 0]

    print(f"Portfolio Capital: ${capital:,.2f}")
    print(f"\nSignals:")
    print(f"  🟢 BUY:  {len(buy_signals)}")
    print(f"  🔴 SELL: {len(sell_signals)}")
    print(f"  ⚪ HOLD: {len(hold_signals)}")

    if buy_signals:
        print(f"\n{'─'*80}")
        print("BUY ORDERS:")
        print(f"{'─'*80}")

        num_positions = len(buy_signals)
        for symbol in buy_signals:
            price = results[symbol]['price']
            shares = calculate_position_size(capital, num_positions, price)
            value = shares * price

            print(f"\n  {symbol}:")
            print(f"    Current Price: ${price:.2f}")
            print(f"    Shares to Buy: {shares}")
            print(f"    Total Cost:    ${value:,.2f}")
            print(f"    % of Capital:  {(value/capital)*100:.1f}%")

    if sell_signals:
        print(f"\n{'─'*80}")
        print("SELL ORDERS:")
        print(f"{'─'*80}")

        for symbol in sell_signals:
            price = results[symbol]['price']
            print(f"\n  {symbol}:")
            print(f"    Current Price: ${price:.2f}")
            print(f"    Action: SELL ALL shares")

    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print("""
1. Review the signals above
2. Check that the prices look reasonable
3. Decide how much capital to deploy
4. Execute trades in your brokerage account
5. Set a reminder to check again at market close tomorrow
6. Strategy holds for 3 days, then exits

NOTES:
- This is just a suggestion, not financial advice
- Always verify signals yourself
- Start small while learning
- Use stop losses (5% recommended)
    """)


def alpaca_paper_trading(results, capital=10000):
    """
    Execute trades on Alpaca paper trading account

    REQUIRES:
        pip install alpaca-trade-api
        Alpaca account with API keys
    """
    try:
        import alpaca_trade_api as tradeapi
    except ImportError:
        print("\n✗ Alpaca API not installed. Run: pip install alpaca-trade-api")
        return

    # Get API keys from environment
    api_key = os.environ.get('ALPACA_API_KEY')
    secret_key = os.environ.get('ALPACA_SECRET_KEY')

    if not api_key or not secret_key:
        print("\n✗ Alpaca API keys not found!")
        print("Set environment variables:")
        print("  export ALPACA_API_KEY='your_key'")
        print("  export ALPACA_SECRET_KEY='your_secret'")
        print("\nGet keys from: https://alpaca.markets")
        return

    # Connect to Alpaca (PAPER trading)
    api = tradeapi.REST(
        api_key,
        secret_key,
        'https://paper-api.alpaca.markets',  # PAPER trading!
        api_version='v2'
    )

    # Get account info
    account = api.get_account()
    print(f"\n✓ Connected to Alpaca (PAPER trading)")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"  Cash Available:  ${float(account.cash):,.2f}")

    # Execute BUY orders
    buy_signals = [s for s, r in results.items() if r['signal'] == 1]
    if buy_signals:
        print(f"\nExecuting {len(buy_signals)} BUY orders...")

        num_positions = len(buy_signals)
        for symbol in buy_signals:
            price = results[symbol]['price']
            shares = calculate_position_size(
                float(account.cash),
                num_positions,
                price
            )

            if shares > 0:
                try:
                    order = api.submit_order(
                        symbol=symbol,
                        qty=shares,
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    print(f"  ✓ BUY {shares} shares of {symbol} (${shares*price:.2f})")
                except Exception as e:
                    print(f"  ✗ Failed to buy {symbol}: {e}")

    # Execute SELL orders
    sell_signals = [s for s, r in results.items() if r['signal'] == -1]
    if sell_signals:
        print(f"\nExecuting {len(sell_signals)} SELL orders...")

        for symbol in sell_signals:
            try:
                # Get current position
                position = api.get_position(symbol)
                shares = int(position.qty)

                # Sell all shares
                order = api.submit_order(
                    symbol=symbol,
                    qty=shares,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
                print(f"  ✓ SELL {shares} shares of {symbol}")
            except Exception as e:
                # No position or error
                print(f"  ⚪ No position in {symbol} or error: {e}")


def main():
    parser = argparse.ArgumentParser(description='QuantEvolve Live Trader')
    parser.add_argument(
        '--mode',
        choices=['check', 'paper', 'live'],
        default='check',
        help='Trading mode: check (signals only), paper (Alpaca paper), live (REAL MONEY)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=10000,
        help='Portfolio capital in dollars (default: 10000)'
    )

    args = parser.parse_args()

    # Stocks to trade (same as training data)
    SYMBOLS = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'META', 'NVDA']

    # Check signals
    results = check_signals_for_stocks(SYMBOLS)

    if not results:
        print("\n✗ No signals generated. Check your data connection.")
        return

    # Execute based on mode
    if args.mode == 'check':
        print_trading_plan(results, args.capital)

    elif args.mode == 'paper':
        alpaca_paper_trading(results, args.capital)

    elif args.mode == 'live':
        print("\n" + "!"*80)
        print("LIVE TRADING MODE")
        print("!"*80)
        response = input("\nAre you SURE you want to trade with REAL MONEY? (type 'YES' to confirm): ")

        if response == 'YES':
            print("\nLive trading not implemented yet. Use paper mode first!")
            print("When ready, modify this script to use live API endpoint.")
        else:
            print("\nCancelled. Stay safe!")


if __name__ == '__main__':
    main()
