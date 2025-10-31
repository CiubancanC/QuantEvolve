#!/usr/bin/env python3
"""
Simulate trading with the best strategy from evolution
Shows realistic P&L over the 10-year training period
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import numpy as np
from loguru import logger
import pickle
from datetime import datetime

# Import our modules
from backtesting.improved_backtest import ImprovedBacktestEngine
from core.evolutionary_database import EvolutionaryDatabase


def load_best_strategy(results_dir="results/final"):
    """Load the best performing strategy from the evolutionary database"""
    db_path = Path(results_dir) / "evolutionary_database.pkl"

    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return None

    with open(db_path, 'rb') as f:
        db = pickle.load(f)

    # Get all strategies and sort by combined score
    all_strategies = db.feature_map.get_all_strategies()
    all_strategies.sort(key=lambda s: s.combined_score, reverse=True)

    if not all_strategies:
        logger.error("No strategies found in database")
        return None

    return all_strategies[0]


def simulate_trading(
    strategy,
    initial_capital=100000,
    data_dir="data/raw_5years_backup",
    symbols=None
):
    """
    Simulate trading with realistic P&L tracking

    Args:
        strategy: Strategy object from database
        initial_capital: Starting capital ($)
        data_dir: Directory with price data
        symbols: List of symbols to trade (None = all available)

    Returns:
        Dictionary with simulation results
    """
    logger.info("=" * 80)
    logger.info("TRADING SIMULATION - 10 Year Period")
    logger.info("=" * 80)
    logger.info(f"Strategy: {strategy.strategy_id}")
    logger.info(f"Initial Capital: ${initial_capital:,.2f}")
    logger.info("")

    # Initialize backtest engine
    engine = ImprovedBacktestEngine(
        data_dir=data_dir,
        initial_capital=initial_capital,
        per_share_commission=0.0075,
        min_commission=1.00,
        volume_slippage=True
    )

    # Get symbols to trade
    if symbols is None:
        symbols = engine.symbols

    logger.info(f"Trading symbols: {', '.join(symbols)}")
    logger.info("")

    # Load all data
    all_data = {}
    date_ranges = {}

    for symbol in symbols:
        data = engine.load_data(symbol)
        if data is not None and len(data) > 0:
            all_data[symbol] = data
            date_ranges[symbol] = (data.index[0], data.index[-1])
            logger.info(f"  {symbol}: {len(data)} days ({data.index[0].date()} to {data.index[-1].date()})")

    if not all_data:
        logger.error("No data loaded!")
        return None

    logger.info("")

    # Execute strategy code to get signal generator
    namespace = engine._create_strategy_namespace()

    try:
        exec(strategy.code, namespace)
    except Exception as e:
        logger.error(f"Failed to execute strategy code: {e}")
        return None

    if 'generate_signals' not in namespace:
        logger.error("Strategy missing generate_signals function")
        return None

    generate_signals = namespace['generate_signals']

    # Run simulation for each symbol
    logger.info("=" * 80)
    logger.info("PER-SYMBOL RESULTS")
    logger.info("=" * 80)
    logger.info("")

    symbol_results = {}

    for symbol, data in all_data.items():
        logger.info(f"Simulating {symbol}...")

        try:
            # Generate signals
            signals = generate_signals(data.copy())

            if not isinstance(signals, pd.Series):
                signals = pd.Series(signals, index=data.index)

            signals = engine._validate_signals(signals, data)

            # Calculate returns
            returns = engine._calculate_returns(data, signals)

            if returns is None or len(returns) == 0:
                logger.warning(f"  No valid returns for {symbol}")
                continue

            # Calculate cumulative portfolio value
            cumulative_returns = (1 + returns).cumprod()
            final_value = initial_capital * cumulative_returns.iloc[-1]
            profit = final_value - initial_capital
            profit_pct = (final_value / initial_capital - 1) * 100

            # Calculate metrics
            sharpe = engine._calculate_sharpe(returns)
            max_dd = engine._calculate_max_drawdown(cumulative_returns)

            # Count trades
            num_trades = (signals.diff().abs() > 0).sum()

            # Track daily P&L
            daily_pnl = returns * initial_capital

            symbol_results[symbol] = {
                'final_value': final_value,
                'profit': profit,
                'profit_pct': profit_pct,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_dd,
                'num_trades': num_trades,
                'cumulative_returns': cumulative_returns,
                'daily_pnl': daily_pnl,
                'returns': returns
            }

            logger.info(f"  Final Value: ${final_value:,.2f}")
            logger.info(f"  Profit/Loss: ${profit:,.2f} ({profit_pct:+.2f}%)")
            logger.info(f"  Sharpe Ratio: {sharpe:.3f}")
            logger.info(f"  Max Drawdown: {max_dd:.2f}%")
            logger.info(f"  Number of Trades: {num_trades}")
            logger.info("")

        except Exception as e:
            logger.error(f"  Error simulating {symbol}: {e}")
            continue

    if not symbol_results:
        logger.error("No successful simulations!")
        return None

    # Combine results (portfolio approach)
    logger.info("=" * 80)
    logger.info("PORTFOLIO RESULTS (Equal Weight Across Symbols)")
    logger.info("=" * 80)
    logger.info("")

    # Combine returns with equal weighting
    all_returns = [res['returns'] for res in symbol_results.values()]
    combined_returns = pd.concat(all_returns, axis=1).mean(axis=1)

    # Calculate portfolio metrics
    portfolio_cumulative = (1 + combined_returns).cumprod()
    portfolio_final_value = initial_capital * portfolio_cumulative.iloc[-1]
    portfolio_profit = portfolio_final_value - initial_capital
    portfolio_profit_pct = (portfolio_final_value / initial_capital - 1) * 100

    portfolio_sharpe = engine._calculate_sharpe(combined_returns)
    portfolio_max_dd = engine._calculate_max_drawdown(portfolio_cumulative)

    total_trades = sum(res['num_trades'] for res in symbol_results.values())
    avg_trades_per_symbol = total_trades / len(symbol_results)

    # Daily P&L for portfolio
    portfolio_daily_pnl = combined_returns * initial_capital

    # Calculate some additional stats
    winning_days = (combined_returns > 0).sum()
    losing_days = (combined_returns < 0).sum()
    win_rate = winning_days / (winning_days + losing_days) * 100 if (winning_days + losing_days) > 0 else 0

    best_day = combined_returns.max() * 100
    worst_day = combined_returns.min() * 100
    avg_daily_return = combined_returns.mean() * 100

    logger.info(f"Initial Capital: ${initial_capital:,.2f}")
    logger.info(f"Final Portfolio Value: ${portfolio_final_value:,.2f}")
    logger.info(f"Total Profit/Loss: ${portfolio_profit:,.2f}")
    logger.info(f"Total Return: {portfolio_profit_pct:+.2f}%")
    logger.info("")
    logger.info(f"Performance Metrics:")
    logger.info(f"  Sharpe Ratio: {portfolio_sharpe:.3f}")
    logger.info(f"  Max Drawdown: {portfolio_max_dd:.2f}%")
    logger.info(f"  Win Rate: {win_rate:.2f}%")
    logger.info(f"  Best Day: {best_day:+.2f}%")
    logger.info(f"  Worst Day: {worst_day:+.2f}%")
    logger.info(f"  Avg Daily Return: {avg_daily_return:+.4f}%")
    logger.info("")
    logger.info(f"Trading Activity:")
    logger.info(f"  Total Trades: {total_trades}")
    logger.info(f"  Avg Trades/Symbol: {avg_trades_per_symbol:.1f}")
    logger.info(f"  Trading Days: {len(combined_returns)}")
    logger.info("")

    # Time analysis
    start_date = combined_returns.index[0]
    end_date = combined_returns.index[-1]

    # Ensure timezone-naive for date arithmetic
    if hasattr(start_date, 'tz') and start_date.tz is not None:
        start_date = start_date.tz_localize(None)
    if hasattr(end_date, 'tz') and end_date.tz is not None:
        end_date = end_date.tz_localize(None)

    years = (end_date - start_date).days / 365.25
    annualized_return = ((portfolio_final_value / initial_capital) ** (1 / years) - 1) * 100

    logger.info(f"Time Period:")
    logger.info(f"  Start: {start_date.date()}")
    logger.info(f"  End: {end_date.date()}")
    logger.info(f"  Duration: {years:.2f} years")
    logger.info(f"  Annualized Return: {annualized_return:+.2f}%")
    logger.info("")

    # Show strategy hypothesis
    logger.info("=" * 80)
    logger.info("STRATEGY DETAILS")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Strategy ID: {strategy.strategy_id}")
    logger.info(f"Generation: {strategy.generation}")
    logger.info("")
    logger.info("Hypothesis:")
    logger.info(strategy.hypothesis)
    logger.info("")

    return {
        'initial_capital': initial_capital,
        'final_value': portfolio_final_value,
        'profit': portfolio_profit,
        'profit_pct': portfolio_profit_pct,
        'sharpe_ratio': portfolio_sharpe,
        'max_drawdown': portfolio_max_dd,
        'win_rate': win_rate,
        'total_trades': total_trades,
        'years': years,
        'annualized_return': annualized_return,
        'symbol_results': symbol_results,
        'portfolio_returns': combined_returns,
        'portfolio_cumulative': portfolio_cumulative,
        'portfolio_daily_pnl': portfolio_daily_pnl,
        'start_date': start_date,
        'end_date': end_date,
        'strategy': strategy
    }


def save_simulation_report(results, output_file="simulation_report.txt"):
    """Save detailed simulation report to file"""
    if results is None:
        return

    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("QUANTEVOLVE TRADING SIMULATION REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")

        f.write("PORTFOLIO SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Initial Capital:        ${results['initial_capital']:>15,.2f}\n")
        f.write(f"Final Portfolio Value:  ${results['final_value']:>15,.2f}\n")
        f.write(f"Total Profit/Loss:      ${results['profit']:>15,.2f}\n")
        f.write(f"Total Return:           {results['profit_pct']:>15.2f}%\n")
        f.write(f"Annualized Return:      {results['annualized_return']:>15.2f}%\n")
        f.write("\n")

        f.write("PERFORMANCE METRICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Sharpe Ratio:           {results['sharpe_ratio']:>15.3f}\n")
        f.write(f"Max Drawdown:           {results['max_drawdown']:>15.2f}%\n")
        f.write(f"Win Rate:               {results['win_rate']:>15.2f}%\n")
        f.write("\n")

        f.write("TRADING ACTIVITY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Trades:           {results['total_trades']:>15}\n")
        f.write(f"Period:                 {results['start_date'].date()} to {results['end_date'].date()}\n")
        f.write(f"Duration:               {results['years']:>15.2f} years\n")
        f.write("\n")

        f.write("PER-SYMBOL RESULTS\n")
        f.write("-" * 80 + "\n")
        for symbol, res in results['symbol_results'].items():
            f.write(f"\n{symbol}:\n")
            f.write(f"  Profit/Loss:     ${res['profit']:>12,.2f} ({res['profit_pct']:+.2f}%)\n")
            f.write(f"  Sharpe Ratio:    {res['sharpe_ratio']:>12.3f}\n")
            f.write(f"  Max Drawdown:    {res['max_drawdown']:>12.2f}%\n")
            f.write(f"  Trades:          {res['num_trades']:>12}\n")

        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("STRATEGY DETAILS\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nStrategy ID: {results['strategy'].strategy_id}\n")
        f.write(f"Generation: {results['strategy'].generation}\n")
        f.write(f"\nHypothesis:\n{results['strategy'].hypothesis}\n")
        f.write("\n")

    logger.info(f"Report saved to: {output_file}")


def main():
    """Run the trading simulation"""
    logger.info("Loading best strategy from evolutionary database...")

    # Load best strategy
    best_strategy = load_best_strategy()

    if best_strategy is None:
        logger.error("Failed to load strategy!")
        return

    logger.info(f"Loaded strategy: {best_strategy.strategy_id}")
    logger.info(f"Combined Score: {best_strategy.combined_score:.3f}")
    logger.info(f"Sharpe Ratio: {best_strategy.metrics.get('sharpe_ratio', 0):.3f}")
    logger.info("")

    # Run simulation
    results = simulate_trading(
        strategy=best_strategy,
        initial_capital=100000,  # $100k starting capital
        data_dir="data/raw_5years_backup"
    )

    if results is None:
        logger.error("Simulation failed!")
        return

    # Save report
    save_simulation_report(results, "simulation_report.txt")

    logger.info("")
    logger.info("=" * 80)
    logger.info("SIMULATION COMPLETE!")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"If you had invested $100,000 using this strategy,")
    logger.info(f"you would have: ${results['final_value']:,.2f}")
    logger.info(f"Profit: ${results['profit']:,.2f} ({results['profit_pct']:+.2f}%)")
    logger.info("")


if __name__ == "__main__":
    main()
