#!/usr/bin/env python3
"""
Fix timezone issues in downloaded stock data.

This script detects and fixes timezone-related issues in CSV files that can cause
"Cannot compare tz-naive and tz-aware timestamps" errors during backtesting.

The script:
1. Scans all CSV files in the data directory
2. Detects timezone-aware timestamps
3. Converts all timestamps to timezone-naive (local time)
4. Creates backups before modifying files
5. Reports all changes made

Usage:
    python scripts/fix_timezone_issues.py
    python scripts/fix_timezone_issues.py --data-dir data/raw --backup
"""

import argparse
import os
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Tuple


def detect_timezone_issue(csv_path: str) -> bool:
    """
    Check if a CSV file has timezone-aware timestamps.

    Args:
        csv_path: Path to CSV file

    Returns:
        True if timezone issues detected, False otherwise
    """
    try:
        df = pd.read_csv(csv_path)

        # Check if Date column exists
        if 'Date' not in df.columns:
            return False

        # Try to parse the first date to check for timezone
        first_date = str(df['Date'].iloc[0])

        # Check for timezone indicators (+ or - followed by time offset)
        if '+' in first_date or ('-' in first_date and ':' in first_date.split('-')[-1]):
            return True

        return False

    except Exception as e:
        print(f"  Error checking {csv_path}: {e}")
        return False


def fix_timezone_in_file(csv_path: str, create_backup: bool = True) -> Tuple[bool, str]:
    """
    Fix timezone issues in a single CSV file.

    Args:
        csv_path: Path to CSV file
        create_backup: Whether to create a backup before modifying

    Returns:
        Tuple of (success, message)
    """
    try:
        # Create backup if requested
        if create_backup:
            backup_path = f"{csv_path}.bak"
            shutil.copy2(csv_path, backup_path)

        # Read CSV
        df = pd.read_csv(csv_path)

        if 'Date' not in df.columns:
            return False, "No Date column found"

        # Parse dates with timezone awareness, then convert to UTC and remove tz
        df['Date'] = pd.to_datetime(df['Date'], utc=True)

        # Convert to timezone-naive (remove timezone info, keeping UTC time)
        df['Date'] = df['Date'].dt.tz_localize(None)

        # Save back to CSV
        df.to_csv(csv_path, index=False)

        return True, f"Fixed {len(df)} rows"

    except Exception as e:
        return False, f"Error: {e}"


def fix_all_files(data_dir: str, create_backup: bool = True) -> dict:
    """
    Fix timezone issues in all CSV files in a directory.

    Args:
        data_dir: Directory containing CSV files
        create_backup: Whether to create backups

    Returns:
        Dictionary with results
    """
    results = {
        'total': 0,
        'fixed': 0,
        'skipped': 0,
        'errors': 0,
        'files': []
    }

    # Find all CSV files
    csv_files = list(Path(data_dir).glob('*.csv'))
    results['total'] = len(csv_files)

    print(f"\nScanning {len(csv_files)} CSV files in {data_dir}...")
    print(f"{'='*70}\n")

    for csv_file in csv_files:
        csv_path = str(csv_file)
        filename = csv_file.name

        print(f"Checking {filename}...", end=' ')

        # Check if file has timezone issues
        has_issue = detect_timezone_issue(csv_path)

        if not has_issue:
            print("✓ No timezone issues")
            results['skipped'] += 1
            results['files'].append({
                'file': filename,
                'status': 'skipped',
                'message': 'No timezone issues'
            })
            continue

        print("⚠ Timezone issue detected - fixing...", end=' ')

        # Fix the file
        success, message = fix_timezone_in_file(csv_path, create_backup)

        if success:
            print(f"✓ {message}")
            results['fixed'] += 1
            results['files'].append({
                'file': filename,
                'status': 'fixed',
                'message': message
            })
        else:
            print(f"✗ {message}")
            results['errors'] += 1
            results['files'].append({
                'file': filename,
                'status': 'error',
                'message': message
            })

    return results


def print_summary(results: dict, backup_created: bool):
    """Print summary of operations."""
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total files scanned: {results['total']}")
    print(f"✓ Fixed: {results['fixed']}")
    print(f"- Skipped (no issues): {results['skipped']}")
    print(f"✗ Errors: {results['errors']}")

    if backup_created and results['fixed'] > 0:
        print(f"\n💾 Backups created with .bak extension")

    if results['fixed'] > 0:
        print(f"\n✓ Timezone issues fixed! Data is now ready for backtesting.")
    elif results['skipped'] == results['total']:
        print(f"\n✓ All files already clean - no fixes needed!")

    print(f"{'='*70}\n")


def verify_fixes(data_dir: str) -> bool:
    """
    Verify that all timezone issues have been resolved.

    Args:
        data_dir: Directory containing CSV files

    Returns:
        True if all files are clean, False otherwise
    """
    csv_files = list(Path(data_dir).glob('*.csv'))

    print(f"\nVerifying fixes in {len(csv_files)} files...")

    issues_found = False
    for csv_file in csv_files:
        if detect_timezone_issue(str(csv_file)):
            print(f"  ✗ {csv_file.name} still has timezone issues")
            issues_found = True

    if not issues_found:
        print(f"  ✓ All files verified - no timezone issues remaining\n")
        return True
    else:
        print(f"  ✗ Some files still have issues\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Fix timezone issues in stock data CSV files"
    )
    parser.add_argument(
        "--data-dir",
        default="data/raw",
        help="Directory containing CSV files (default: data/raw)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backups before modifying files (default: True)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create backups (use with caution)"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only check for issues without fixing"
    )

    args = parser.parse_args()

    # Handle backup flag
    create_backup = args.backup and not args.no_backup

    print(f"\n{'='*70}")
    print("TIMEZONE FIX UTILITY")
    print(f"{'='*70}")
    print(f"Data directory: {args.data_dir}")
    print(f"Create backups: {create_backup}")
    print(f"{'='*70}")

    # Check if directory exists
    if not os.path.exists(args.data_dir):
        print(f"\n✗ Error: Directory '{args.data_dir}' not found")
        return 1

    # Verify-only mode
    if args.verify_only:
        print("\nRunning in verify-only mode (no changes will be made)\n")
        csv_files = list(Path(args.data_dir).glob('*.csv'))
        issues_found = False

        for csv_file in csv_files:
            filename = csv_file.name
            has_issue = detect_timezone_issue(str(csv_file))

            if has_issue:
                print(f"  ⚠ {filename} has timezone issues")
                issues_found = True
            else:
                print(f"  ✓ {filename} is clean")

        if issues_found:
            print(f"\n⚠ Timezone issues detected. Run without --verify-only to fix.")
            return 1
        else:
            print(f"\n✓ All files are clean!")
            return 0

    # Fix files
    results = fix_all_files(args.data_dir, create_backup)

    # Print summary
    print_summary(results, create_backup)

    # Verify fixes
    if results['fixed'] > 0:
        verify_fixes(args.data_dir)

    return 0 if results['errors'] == 0 else 1


if __name__ == "__main__":
    exit(main())
