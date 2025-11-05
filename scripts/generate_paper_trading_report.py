#!/usr/bin/env python3
"""
Generate Paper Trading Performance Report

Analyzes paper trading results and generates markdown/console reports
showing performance metrics, comparisons to backtests, and trade history.

Usage:
    python3 scripts/generate_paper_trading_report.py
    python3 scripts/generate_paper_trading_report.py --format markdown > report.md
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import pandas as pd


def load_tracking_data() -> Dict:
    """Load paper trading tracking data"""
    tracking_file = Path("results/paper_trading/tracking.json")

    if not tracking_file.exists():
        print("No paper trading data found. Run paper trading first.")
        return None

    with open(tracking_file, 'r') as f:
        return json.load(f)


def calculate_performance_metrics(tracking_data: Dict) -> Dict:
    """Calculate performance metrics for each strategy"""
    metrics = {}

    for strategy_id, data in tracking_data['strategies'].items():
        initial = data['initial_capital']
        current = data['current_value']
        total_return_pct = (current / initial - 1) * 100

        # Calculate from daily snapshots
        daily_returns = []
        for i, snapshot in enumerate(tracking_data['daily_snapshots']):
            if strategy_id in snapshot['strategies']:
                daily_returns.append(snapshot['strategies'][strategy_id]['return_pct'])

        # Calculate metrics
        if len(daily_returns) > 1:
            returns_series = pd.Series(daily_returns)
            daily_changes = returns_series.diff().dropna()

            sharpe = (daily_changes.mean() / daily_changes.std() * (252 ** 0.5)) if daily_changes.std() > 0 else 0
            max_dd = min(daily_changes.cumsum()) if len(daily_changes) > 0 else 0
        else:
            sharpe = 0
            max_dd = 0

        metrics[strategy_id] = {
            'rank': data['rank'],
            'initial_capital': initial,
            'current_value': current,
            'total_return_pct': total_return_pct,
            'num_trades': len(data['trades']),
            'num_positions': len(data['positions']),
            'sharpe_ratio_estimate': sharpe,
            'max_drawdown_estimate': max_dd,
            'recent_trades': data['trades'][-5:] if len(data['trades']) > 0 else []
        }

    return metrics


def generate_console_report(tracking_data: Dict, metrics: Dict):
    """Generate console-formatted report"""
    start_date = datetime.fromisoformat(tracking_data['start_date'])
    days_running = (datetime.now() - start_date).days

    print("\n" + "=" * 80)
    print(" PAPER TRADING PERFORMANCE REPORT ".center(80, "="))
    print("=" * 80)

    print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Trading Started: {start_date.strftime('%Y-%m-%d')}")
    print(f"Days Running: {days_running}")
    print(f"Trading Days Recorded: {len(tracking_data['daily_snapshots'])}")

    # Overall portfolio performance
    total_initial = sum(m['initial_capital'] for m in metrics.values())
    total_current = sum(m['current_value'] for m in metrics.values())
    total_return_pct = (total_current / total_initial - 1) * 100

    print(f"\n{'OVERALL PORTFOLIO':=^80}")
    print(f"  Initial Capital:     ${total_initial:>12,.2f}")
    print(f"  Current Value:       ${total_current:>12,.2f}")
    print(f"  Total Return:        {total_return_pct:>12.2f}%")
    print(f"  Total Trades:        {sum(m['num_trades'] for m in metrics.values()):>12,}")
    print(f"  Open Positions:      {sum(m['num_positions'] for m in metrics.values()):>12,}")

    # Individual strategy performance
    print(f"\n{'STRATEGY PERFORMANCE':=^80}")

    for strategy_id in sorted(metrics.keys(), key=lambda x: metrics[x]['rank']):
        m = metrics[strategy_id]
        data = tracking_data['strategies'][strategy_id]

        print(f"\n  Strategy #{m['rank']}: {strategy_id}")
        print(f"  {'-' * 76}")

        # Backtest vs Paper Trading
        backtest_metrics = None
        # We'd need to load this from the evolutionary database
        # For now, just show paper trading results

        print(f"    Paper Trading Return:  {m['total_return_pct']:>10.2f}%")
        print(f"    Current Value:         ${m['current_value']:>10,.2f}")
        print(f"    Total Trades:          {m['num_trades']:>10,}")
        print(f"    Open Positions:        {m['num_positions']:>10,}")

        if m['num_positions'] > 0:
            print(f"\n    Current Positions:")
            for pos in data['positions']:
                print(f"      • {pos['symbol']}: {pos['shares']} shares @ ${pos['entry_price']:.2f}")

        if len(m['recent_trades']) > 0:
            print(f"\n    Recent Trades (last 5):")
            for trade in m['recent_trades'][-5:]:
                timestamp = datetime.fromisoformat(trade['timestamp']).strftime('%Y-%m-%d')
                action = trade['action'].upper()
                symbol = trade['symbol']
                shares = trade['shares']
                price = trade['price']

                if action == 'SELL' and 'pnl_pct' in trade:
                    pnl_pct = trade['pnl_pct']
                    print(f"      • {timestamp}: {action:4} {shares:>4} {symbol:5} @ ${price:>7.2f} (P&L: {pnl_pct:>+6.2f}%)")
                else:
                    print(f"      • {timestamp}: {action:4} {shares:>4} {symbol:5} @ ${price:>7.2f}")

    print("\n" + "=" * 80)


def generate_markdown_report(tracking_data: Dict, metrics: Dict) -> str:
    """Generate markdown-formatted report"""
    start_date = datetime.fromisoformat(tracking_data['start_date'])
    days_running = (datetime.now() - start_date).days

    md = []
    md.append("# Paper Trading Performance Report\n")
    md.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    md.append(f"**Trading Started**: {start_date.strftime('%Y-%m-%d')}  ")
    md.append(f"**Days Running**: {days_running}  ")
    md.append(f"**Trading Days**: {len(tracking_data['daily_snapshots'])}  \n")

    # Overall performance
    total_initial = sum(m['initial_capital'] for m in metrics.values())
    total_current = sum(m['current_value'] for m in metrics.values())
    total_return_pct = (total_current / total_initial - 1) * 100

    md.append("## Overall Portfolio\n")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append(f"| Initial Capital | ${total_initial:,.2f} |")
    md.append(f"| Current Value | ${total_current:,.2f} |")
    md.append(f"| Total Return | {total_return_pct:+.2f}% |")
    md.append(f"| Total Trades | {sum(m['num_trades'] for m in metrics.values())} |")
    md.append(f"| Open Positions | {sum(m['num_positions'] for m in metrics.values())} |\n")

    # Individual strategies
    md.append("## Strategy Performance\n")

    for strategy_id in sorted(metrics.keys(), key=lambda x: metrics[x]['rank']):
        m = metrics[strategy_id]
        data = tracking_data['strategies'][strategy_id]

        md.append(f"### Strategy #{m['rank']}: `{strategy_id}`\n")

        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Paper Trading Return | {m['total_return_pct']:+.2f}% |")
        md.append(f"| Current Value | ${m['current_value']:,.2f} |")
        md.append(f"| Total Trades | {m['num_trades']} |")
        md.append(f"| Open Positions | {m['num_positions']} |\n")

        if m['num_positions'] > 0:
            md.append("**Current Positions**:\n")
            for pos in data['positions']:
                md.append(f"- {pos['symbol']}: {pos['shares']} shares @ ${pos['entry_price']:.2f}")
            md.append("")

        if len(m['recent_trades']) > 0:
            md.append("**Recent Trades**:\n")
            for trade in m['recent_trades'][-5:]:
                timestamp = datetime.fromisoformat(trade['timestamp']).strftime('%Y-%m-%d')
                action = trade['action'].upper()
                if action == 'SELL' and 'pnl_pct' in trade:
                    pnl_pct = trade['pnl_pct']
                    md.append(f"- {timestamp}: {action} {trade['shares']} {trade['symbol']} @ ${trade['price']:.2f} (P&L: {pnl_pct:+.2f}%)")
                else:
                    md.append(f"- {timestamp}: {action} {trade['shares']} {trade['symbol']} @ ${trade['price']:.2f}")
            md.append("")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description='Generate Paper Trading Performance Report')
    parser.add_argument('--format', choices=['console', 'markdown'], default='console',
                       help='Output format (default: console)')

    args = parser.parse_args()

    # Load data
    tracking_data = load_tracking_data()
    if tracking_data is None:
        return

    # Calculate metrics
    metrics = calculate_performance_metrics(tracking_data)

    # Generate report
    if args.format == 'markdown':
        print(generate_markdown_report(tracking_data, metrics))
    else:
        generate_console_report(tracking_data, metrics)


if __name__ == '__main__':
    main()
