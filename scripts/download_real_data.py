#!/usr/bin/env python3
"""
Download real historical stock data using yfinance (Yahoo Finance).

This script downloads historical price data for a list of stock symbols
and saves them in the format expected by QuantEvolve.

Usage:
    python scripts/download_real_data.py
    python scripts/download_real_data.py --symbols AAPL MSFT GOOGL --start 2020-01-01 --end 2024-12-31
"""

import argparse
import os
from datetime import datetime
from pathlib import Path
import yfinance as yf
import pandas as pd
from typing import List


def download_stock_data(
    symbol: str,
    start_date: str,
    end_date: str,
    output_dir: str
) -> bool:
    """
    Download historical data for a single stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        start_date: Start date in YYYY-MM-DD format, or 'max' for all available data
        end_date: End date in YYYY-MM-DD format
        output_dir: Directory to save CSV files

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Downloading {symbol}...")

        # Download data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        if start_date == 'max':
            # Download all available data
            df = ticker.history(period='max')
        else:
            df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            print(f"  ✗ No data found for {symbol}")
            return False

        # Rename columns to match expected format (lowercase)
        df.columns = [col.lower() for col in df.columns]

        # Reset index to make date a column
        df.reset_index(inplace=True)
        df.rename(columns={'date': 'Date'}, inplace=True)

        # FIX TIMEZONE ISSUES: Convert to timezone-naive to prevent backtest errors
        # yfinance returns timezone-aware timestamps which cause comparison errors
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)

        # Select only the columns we need
        df = df[['Date', 'open', 'high', 'low', 'close', 'volume']]

        # Save to CSV
        output_path = os.path.join(output_dir, f"{symbol}.csv")
        df.to_csv(output_path, index=False)

        print(f"  ✓ Saved {len(df)} days of data to {output_path}")
        print(f"    Date range: {df['Date'].min()} to {df['Date'].max()}")

        return True

    except Exception as e:
        print(f"  ✗ Error downloading {symbol}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download real historical stock data using Yahoo Finance"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA"],
        help="Stock symbols to download (default: AAPL MSFT GOOGL AMZN META TSLA)"
    )
    parser.add_argument(
        "--start",
        default="2020-01-01",
        help="Start date (YYYY-MM-DD or 'max' for all available data, default: 2020-01-01)"
    )
    parser.add_argument(
        "--end",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date (YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--output",
        default="data/raw",
        help="Output directory (default: data/raw)"
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"DOWNLOADING REAL HISTORICAL STOCK DATA")
    print(f"{'='*60}")
    print(f"Symbols: {', '.join(args.symbols)}")
    print(f"Date range: {args.start} to {args.end}")
    print(f"Output directory: {args.output}")
    print(f"{'='*60}\n")

    # Download data for each symbol
    successful = 0
    failed = 0

    for symbol in args.symbols:
        if download_stock_data(symbol, args.start, args.end, args.output):
            successful += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"DOWNLOAD COMPLETE")
    print(f"{'='*60}")
    print(f"✓ Successful: {successful}/{len(args.symbols)}")
    if failed > 0:
        print(f"✗ Failed: {failed}/{len(args.symbols)}")
    print(f"{'='*60}\n")

    if successful > 0:
        print(f"Data saved to: {args.output}")
        print(f"\nTo run training with real data:")
        print(f"  python3 -m src.main --generations 5")
        print(f"\nTo run training with sample data:")
        print(f"  python3 -m src.main --sample-data --generations 5")


if __name__ == "__main__":
    main()
