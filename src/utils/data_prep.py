"""
Data preparation utilities for QuantEvolve
Downloads and prepares market data
"""

import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from typing import List, Optional
from loguru import logger
from datetime import datetime


def download_equity_data(
    symbols: List[str],
    start_date: str,
    end_date: str,
    output_dir: str = "./data/raw"
) -> bool:
    """
    Download equity data from Yahoo Finance

    Args:
        symbols: List of ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_dir: Output directory

    Returns:
        True if successful
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading data for {len(symbols)} symbols from {start_date} to {end_date}")

    success_count = 0

    for symbol in symbols:
        try:
            logger.info(f"Downloading {symbol}...")

            # Download data
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, auto_adjust=False)

            if df.empty:
                logger.warning(f"No data available for {symbol}")
                continue

            # Rename columns to lowercase
            df.columns = df.columns.str.lower()

            # Reset index to make date a column
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'date'}, inplace=True)

            # Ensure date column exists
            if 'date' not in df.columns:
                df.reset_index(inplace=True)
                df.rename(columns={'index': 'date'}, inplace=True)

            # Save to CSV
            output_file = output_path / f"{symbol}.csv"
            df.to_csv(output_file, index=False)

            logger.info(f"  ✓ Saved {len(df)} rows to {output_file}")
            success_count += 1

        except Exception as e:
            logger.error(f"  ✗ Error downloading {symbol}: {e}")

    logger.info(f"Successfully downloaded {success_count}/{len(symbols)} symbols")

    return success_count > 0


def prepare_equity_data(
    assets: List[str],
    start_date: str,
    end_date: str,
    output_dir: str = "./data/raw"
) -> bool:
    """
    Download and prepare equity data

    Args:
        assets: List of asset symbols
        start_date: Start date
        end_date: End date
        output_dir: Output directory

    Returns:
        True if successful
    """
    return download_equity_data(assets, start_date, end_date, output_dir)


def verify_data(data_dir: str, required_symbols: List[str]) -> bool:
    """
    Verify that all required data files exist

    Args:
        data_dir: Data directory
        required_symbols: List of required symbols

    Returns:
        True if all data exists
    """
    data_path = Path(data_dir)

    missing = []

    for symbol in required_symbols:
        csv_file = data_path / f"{symbol}.csv"
        parquet_file = data_path / f"{symbol}.parquet"

        if not csv_file.exists() and not parquet_file.exists():
            missing.append(symbol)

    if missing:
        logger.warning(f"Missing data for: {', '.join(missing)}")
        return False

    logger.info(f"All data files present for {len(required_symbols)} symbols")
    return True


def get_date_range(data_dir: str, symbol: str) -> Optional[tuple]:
    """
    Get date range for a symbol's data

    Args:
        data_dir: Data directory
        symbol: Symbol to check

    Returns:
        (start_date, end_date) tuple or None
    """
    data_path = Path(data_dir)

    csv_file = data_path / f"{symbol}.csv"
    if csv_file.exists():
        try:
            df = pd.read_csv(csv_file, parse_dates=['date'], usecols=['date'])
            return (df['date'].min(), df['date'].max())
        except Exception as e:
            logger.warning(f"Error reading {csv_file}: {e}")

    return None


def create_sample_data(output_dir: str = "./data/raw", days: int = 1000) -> bool:
    """
    Create sample synthetic data for testing

    Args:
        output_dir: Output directory
        days: Number of days to generate

    Returns:
        True if successful
    """
    logger.info(f"Creating {days} days of sample data")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Symbols to generate
    symbols = ['AAPL', 'NVDA', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']

    start_date = pd.Timestamp('2020-01-01')
    dates = pd.date_range(start=start_date, periods=days, freq='D')

    for symbol in symbols:
        # Generate synthetic price data
        np.random.seed(hash(symbol) % (2**32))  # Reproducible per symbol

        # Starting price
        start_price = np.random.uniform(50, 500)

        # Generate returns with momentum and mean reversion
        returns = np.random.normal(0.0005, 0.02, days)

        # Add some momentum
        for i in range(1, len(returns)):
            returns[i] += 0.1 * returns[i-1]

        # Calculate prices
        prices = start_price * (1 + returns).cumprod()

        # Generate OHLCV
        df = pd.DataFrame({
            'date': dates,
            'open': prices * np.random.uniform(0.98, 1.02, days),
            'high': prices * np.random.uniform(1.00, 1.05, days),
            'low': prices * np.random.uniform(0.95, 1.00, days),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        })

        # Ensure OHLC consistency
        df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1)
        df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1)

        # Save
        output_file = output_path / f"{symbol}.csv"
        df.to_csv(output_file, index=False)

        logger.info(f"  ✓ Created {symbol} with {len(df)} rows")

    logger.info(f"Sample data created in {output_dir}")
    return True
