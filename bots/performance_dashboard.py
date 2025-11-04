#!/usr/bin/env python3
"""
Performance Dashboard for Paper Trading Bot

Analyzes logs and generates performance reports
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger


class PerformanceDashboard:
    """Analyze paper trading performance"""

    def __init__(self, log_dir="logs/paper_trading"):
        self.log_dir = Path(log_dir)
        self.trades_file = self.log_dir / "trades.jsonl"
        self.performance_file = self.log_dir / "performance.jsonl"

    def load_trades(self):
        """Load all trades from log"""
        if not self.trades_file.exists():
            return pd.DataFrame()

        trades = []
        with open(self.trades_file, 'r') as f:
            for line in f:
                trades.append(json.loads(line))

        if not trades:
            return pd.DataFrame()

        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def load_performance(self):
        """Load daily performance snapshots"""
        if not self.performance_file.exists():
            return pd.DataFrame()

        performance = []
        with open(self.performance_file, 'r') as f:
            for line in f:
                performance.append(json.loads(line))

        if not performance:
            return pd.DataFrame()

        df = pd.DataFrame(performance)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def calculate_metrics(self):
        """Calculate all performance metrics"""
        trades_df = self.load_trades()
        perf_df = self.load_performance()

        if trades_df.empty and perf_df.empty:
            print("No trading data found yet!")
            return None

        metrics = {}

        # From trades
        if not trades_df.empty:
            # Filter completed trades (buy + sell pairs)
            sell_trades = trades_df[trades_df['action'] == 'SELL'].copy()

            if not sell_trades.empty:
                metrics['total_trades'] = len(sell_trades)
                metrics['profitable_trades'] = (sell_trades['pnl'] > 0).sum()
                metrics['losing_trades'] = (sell_trades['pnl'] < 0).sum()
                metrics['win_rate'] = metrics['profitable_trades'] / metrics['total_trades'] * 100

                metrics['total_pnl'] = sell_trades['pnl'].sum()
                metrics['avg_pnl'] = sell_trades['pnl'].mean()
                metrics['avg_pnl_pct'] = sell_trades['pnl_pct'].mean()

                metrics['best_trade'] = sell_trades.loc[sell_trades['pnl'].idxmax()]
                metrics['worst_trade'] = sell_trades.loc[sell_trades['pnl'].idxmin()]

                # Profit factor
                profits = sell_trades[sell_trades['pnl'] > 0]['pnl'].sum()
                losses = abs(sell_trades[sell_trades['pnl'] < 0]['pnl'].sum())
                metrics['profit_factor'] = profits / losses if losses > 0 else float('inf')

        # From performance snapshots
        if not perf_df.empty:
            latest = perf_df.iloc[-1]
            first = perf_df.iloc[0]

            initial_capital = first['portfolio_value']
            current_value = latest['portfolio_value']

            metrics['initial_capital'] = initial_capital
            metrics['current_value'] = current_value
            metrics['total_return_pct'] = (current_value / initial_capital - 1) * 100

            # Calculate daily returns
            perf_df = perf_df.sort_values('timestamp')
            perf_df['daily_return'] = perf_df['portfolio_value'].pct_change()

            if len(perf_df) > 1:
                returns = perf_df['daily_return'].dropna()

                # Sharpe ratio (annualized)
                if len(returns) > 0 and returns.std() > 0:
                    metrics['sharpe_ratio'] = (returns.mean() / returns.std()) * np.sqrt(252)
                else:
                    metrics['sharpe_ratio'] = 0

                # Max drawdown
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                metrics['max_drawdown_pct'] = drawdown.min() * 100

                # Days trading
                days = (perf_df['timestamp'].max() - perf_df['timestamp'].min()).days
                metrics['days_trading'] = days

                # Annualized return
                if days > 0:
                    years = days / 365.25
                    metrics['annualized_return_pct'] = ((current_value / initial_capital) ** (1/years) - 1) * 100
                else:
                    metrics['annualized_return_pct'] = 0

        return metrics

    def print_report(self):
        """Print formatted performance report"""
        metrics = self.calculate_metrics()

        if metrics is None:
            return

        print("\n" + "="*80)
        print("PAPER TRADING PERFORMANCE REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Portfolio summary
        if 'current_value' in metrics:
            print("\nPORTFOLIO SUMMARY")
            print("-"*80)
            print(f"Initial Capital:      ${metrics['initial_capital']:>15,.2f}")
            print(f"Current Value:        ${metrics['current_value']:>15,.2f}")
            print(f"Total P&L:            ${metrics['current_value'] - metrics['initial_capital']:>15,.2f}")
            print(f"Total Return:         {metrics['total_return_pct']:>15.2f}%")

            if 'annualized_return_pct' in metrics:
                print(f"Annualized Return:    {metrics['annualized_return_pct']:>15.2f}%")

            if 'days_trading' in metrics:
                print(f"Days Trading:         {metrics['days_trading']:>15}")

        # Trading statistics
        if 'total_trades' in metrics:
            print("\nTRADING STATISTICS")
            print("-"*80)
            print(f"Total Trades:         {metrics['total_trades']:>15}")
            print(f"Profitable Trades:    {metrics['profitable_trades']:>15}")
            print(f"Losing Trades:        {metrics['losing_trades']:>15}")
            print(f"Win Rate:             {metrics['win_rate']:>15.2f}%")
            print(f"\nAverage P&L:          ${metrics['avg_pnl']:>15,.2f}")
            print(f"Average P&L %:        {metrics['avg_pnl_pct']:>15.2f}%")
            print(f"Total P&L:            ${metrics['total_pnl']:>15,.2f}")
            print(f"Profit Factor:        {metrics['profit_factor']:>15.2f}")

        # Risk metrics
        if 'sharpe_ratio' in metrics:
            print("\nRISK METRICS")
            print("-"*80)
            print(f"Sharpe Ratio:         {metrics['sharpe_ratio']:>15.2f}")
            print(f"Max Drawdown:         {metrics['max_drawdown_pct']:>15.2f}%")

        # Best/worst trades
        if 'best_trade' in metrics:
            print("\nBEST TRADE")
            print("-"*80)
            best = metrics['best_trade']
            print(f"  {best['symbol']}: ${best['pnl']:,.2f} ({best['pnl_pct']:+.2f}%)")
            print(f"  Entry: ${best['entry_price']:.2f}, Exit: ${best['price']:.2f}")
            print(f"  Date: {best['timestamp'].strftime('%Y-%m-%d')}")

            print("\nWORST TRADE")
            print("-"*80)
            worst = metrics['worst_trade']
            print(f"  {worst['symbol']}: ${worst['pnl']:,.2f} ({worst['pnl_pct']:+.2f}%)")
            print(f"  Entry: ${worst['entry_price']:.2f}, Exit: ${worst['price']:.2f}")
            print(f"  Date: {worst['timestamp'].strftime('%Y-%m-%d')}")

        # Comparison to backtest
        print("\n" + "="*80)
        print("COMPARISON TO BACKTEST")
        print("="*80)
        print("Backtest (2020-2022):")
        print("  Total Return: 422.52%")
        print("  Sharpe Ratio: 2.811")
        print("  Max Drawdown: -2.25%")
        print("  Win Rate: 48.66%")

        if 'total_return_pct' in metrics and 'sharpe_ratio' in metrics:
            print(f"\nPaper Trading (Current):")
            print(f"  Total Return: {metrics.get('total_return_pct', 0):.2f}%")
            print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"  Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
            print(f"  Win Rate: {metrics.get('win_rate', 0):.2f}%")

        print("\n" + "="*80)

    def export_csv(self):
        """Export trades to CSV for analysis"""
        trades_df = self.load_trades()

        if not trades_df.empty:
            output_file = self.log_dir / "trades_export.csv"
            trades_df.to_csv(output_file, index=False)
            print(f"\n✓ Trades exported to: {output_file}")

        perf_df = self.load_performance()

        if not perf_df.empty:
            output_file = self.log_dir / "performance_export.csv"
            perf_df.to_csv(output_file, index=False)
            print(f"✓ Performance exported to: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Paper Trading Performance Dashboard')
    parser.add_argument(
        '--log-dir',
        default='logs/paper_trading',
        help='Directory containing trading logs'
    )
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export data to CSV'
    )

    args = parser.parse_args()

    dashboard = PerformanceDashboard(args.log_dir)
    dashboard.print_report()

    if args.export:
        dashboard.export_csv()


if __name__ == '__main__':
    main()
