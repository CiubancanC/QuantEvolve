"""
Data Agent: Analyzes data schema and generates seed strategies
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from ..utils.llm_client import LLMEnsemble
from ..core.feature_map import Strategy
from .prompts import (
    DATA_AGENT_SYSTEM_PROMPT,
    DATA_AGENT_CATEGORY_PROMPT
)


class DataAgent:
    """
    Data Agent for analyzing data schema and generating seed strategies
    """

    def __init__(self, llm_ensemble: LLMEnsemble):
        """
        Initialize Data Agent

        Args:
            llm_ensemble: LLM ensemble for generation
        """
        self.llm = llm_ensemble
        self.data_schema_prompt = None

    def analyze_data(
        self,
        data_dir: str,
        assets: List[str],
        asset_type: str = "equities"
    ) -> str:
        """
        Analyze data directory and create schema prompt

        Args:
            data_dir: Path to data directory
            assets: List of asset symbols
            asset_type: Type of assets (equities, futures, etc.)

        Returns:
            Data schema prompt
        """
        logger.info(f"Analyzing data for {len(assets)} {asset_type}")

        # Gather data information
        data_path = Path(data_dir)

        data_info = {
            "asset_type": asset_type,
            "assets": assets,
            "data_files": [],
            "date_ranges": {},
            "columns": {},
            "frequency": "daily"
        }

        # Check for data files
        for asset in assets:
            csv_file = data_path / f"{asset}.csv"
            parquet_file = data_path / f"{asset}.parquet"

            if csv_file.exists():
                data_info["data_files"].append(str(csv_file))
                # Try to load and get info
                try:
                    df = pd.read_csv(csv_file, nrows=5)
                    data_info["columns"][asset] = df.columns.tolist()

                    # Get full file for date range
                    df_full = pd.read_csv(csv_file)
                    if 'date' in df_full.columns or 'Date' in df_full.columns:
                        date_col = 'date' if 'date' in df_full.columns else 'Date'
                        data_info["date_ranges"][asset] = {
                            "start": df_full[date_col].min(),
                            "end": df_full[date_col].max(),
                            "count": len(df_full)
                        }
                except Exception as e:
                    logger.warning(f"Could not read {csv_file}: {e}")

            elif parquet_file.exists():
                data_info["data_files"].append(str(parquet_file))
                try:
                    df = pd.read_parquet(parquet_file, nrows=5)
                    data_info["columns"][asset] = df.columns.tolist()

                    df_full = pd.read_parquet(parquet_file)
                    if 'date' in df_full.columns or 'Date' in df_full.columns:
                        date_col = 'date' if 'date' in df_full.columns else 'Date'
                        data_info["date_ranges"][asset] = {
                            "start": df_full[date_col].min(),
                            "end": df_full[date_col].max(),
                            "count": len(df_full)
                        }
                except Exception as e:
                    logger.warning(f"Could not read {parquet_file}: {e}")

        # Create prompt for LLM
        data_description = self._format_data_info(data_info)

        prompt = f"""Analyze the following data and create a comprehensive Data Schema Prompt:

{data_description}

Provide:
1. Data Schema Prompt: A detailed specification for strategy development
2. Available Strategy Categories: List categories that can be derived from this data

Format your response as:

## Data Schema Prompt
[Detailed schema]

## Available Strategy Categories
1. Category Name: Description
2. ...
"""

        # Get schema from LLM
        logger.info("Generating data schema prompt")
        response = self.llm.thoughtful_generate(
            prompt=prompt,
            system_prompt=DATA_AGENT_SYSTEM_PROMPT
        )

        self.data_schema_prompt = response
        logger.info("Data schema prompt generated")

        return response

    def _format_data_info(self, data_info: Dict[str, Any]) -> str:
        """Format data information for prompt"""
        lines = [
            f"Asset Type: {data_info['asset_type']}",
            f"Assets: {', '.join(data_info['assets'])}",
            f"Frequency: {data_info['frequency']}",
            "",
            "Available Data:"
        ]

        for asset in data_info['assets']:
            if asset in data_info['columns']:
                cols = data_info['columns'][asset]
                lines.append(f"  {asset}:")
                lines.append(f"    Columns: {', '.join(cols)}")

                if asset in data_info['date_ranges']:
                    dr = data_info['date_ranges'][asset]
                    lines.append(f"    Date Range: {dr['start']} to {dr['end']} ({dr['count']} rows)")

        return "\n".join(lines)

    def generate_seed_strategy(
        self,
        category: str,
        generation: int = 0,
        island_id: int = 0
    ) -> Strategy:
        """
        Generate a seed strategy for a category

        Args:
            category: Strategy category
            generation: Generation number
            island_id: Island ID

        Returns:
            Seed strategy
        """
        logger.info(f"Generating seed strategy for category: {category}")

        if not self.data_schema_prompt:
            raise ValueError("Data schema not analyzed yet. Call analyze_data() first.")

        # Create prompt
        prompt = DATA_AGENT_CATEGORY_PROMPT.format(category=category)
        prompt += f"\n\n## Data Schema\n{self.data_schema_prompt}"

        # Generate strategy
        response = self.llm.thoughtful_generate(
            prompt=prompt,
            system_prompt=DATA_AGENT_SYSTEM_PROMPT
        )

        # Parse response (basic parsing - extract code and hypothesis)
        hypothesis, code = self._parse_strategy_response(response, category)

        # Create strategy object
        strategy = Strategy(
            hypothesis=hypothesis,
            code=code,
            metrics={
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0,
                'information_ratio': 0.0,
                'total_return': 0.0,
                'max_drawdown': 0.0,
                'trading_frequency': 0,
                'strategy_category_bin': self._category_to_bin(category)
            },
            analysis=f"Seed strategy for {category}",
            generation=generation,
            island_id=island_id
        )

        logger.info(f"Generated seed strategy for {category}")

        return strategy

    def _parse_strategy_response(self, response: str, category: str) -> tuple[str, str]:
        """
        Parse strategy response from LLM

        Args:
            response: LLM response
            category: Strategy category

        Returns:
            (hypothesis, code) tuple
        """
        # Simple parsing - look for code blocks
        hypothesis = ""
        code = ""

        lines = response.split('\n')
        in_code_block = False
        code_lines = []

        for line in lines:
            if '```python' in line.lower():
                in_code_block = True
                continue
            elif '```' in line and in_code_block:
                in_code_block = False
                continue

            if in_code_block:
                code_lines.append(line)
            elif not code and ('hypothesis' in line.lower() or 'description' in line.lower()):
                # Start capturing hypothesis
                hypothesis = line

        code = '\n'.join(code_lines) if code_lines else f"# Placeholder for {category} strategy\n"

        if not hypothesis:
            hypothesis = f"Baseline {category} strategy"

        return hypothesis, code

    def _category_to_bin(self, category: str) -> int:
        """
        Convert category name to binary bin

        Args:
            category: Category name

        Returns:
            Binary bin index
        """
        # Simple hash-based mapping
        # In practice, should have predefined mapping
        categories = [
            "Momentum/Trend",
            "Mean-Reversion",
            "Volatility",
            "Volume/Liquidity",
            "Breakout/Pattern",
            "Correlation/Pairs",
            "Risk/Allocation",
            "Seasonal/Calendar Effects"
        ]

        # Binary encoding
        bin_val = 0
        for i, cat in enumerate(categories):
            if cat.lower() in category.lower() or category.lower() in cat.lower():
                bin_val |= (1 << i)

        return bin_val if bin_val > 0 else 1  # Default to 1 if no match

    def generate_all_seed_strategies(
        self,
        categories: List[str],
        include_benchmark: bool = True
    ) -> List[Strategy]:
        """
        Generate seed strategies for all categories

        Args:
            categories: List of strategy categories
            include_benchmark: Whether to include a buy-and-hold benchmark

        Returns:
            List of seed strategies
        """
        strategies = []

        for i, category in enumerate(categories):
            strategy = self.generate_seed_strategy(
                category=category,
                generation=0,
                island_id=i
            )
            strategies.append(strategy)

        # Add benchmark if requested
        if include_benchmark:
            benchmark = self.generate_seed_strategy(
                category="Buy-and-Hold Benchmark",
                generation=0,
                island_id=len(categories)
            )
            strategies.append(benchmark)

        logger.info(f"Generated {len(strategies)} seed strategies")

        return strategies
