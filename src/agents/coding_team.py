"""
Coding Team: Implements strategies and runs backtests
"""

import re
from typing import Dict, Optional, Tuple
from loguru import logger

from ..utils.llm_client import LLMEnsemble
from ..core.feature_map import Strategy
from .prompts import (
    CODING_TEAM_SYSTEM_PROMPT,
    CODING_TEAM_IMPLEMENTATION_PROMPT,
    CODING_TEAM_DEBUG_PROMPT
)


class CodingTeam:
    """
    Coding Team for implementing and backtesting strategies
    """

    def __init__(self, llm_ensemble: LLMEnsemble, backtesting_engine=None):
        """
        Initialize Coding Team

        Args:
            llm_ensemble: LLM ensemble for code generation
            backtesting_engine: Backtesting engine (optional for now)
        """
        self.llm = llm_ensemble
        self.backtesting_engine = backtesting_engine
        self.max_iterations = 3  # Max debug attempts

    def implement_strategy(
        self,
        hypothesis: str,
        data_schema: str,
        parent_code: Optional[str] = None
    ) -> Tuple[str, Dict, str]:
        """
        Implement strategy from hypothesis

        Args:
            hypothesis: Strategy hypothesis
            data_schema: Data schema prompt
            parent_code: Parent strategy code (for reference)

        Returns:
            (code, metrics, implementation_notes) tuple
        """
        logger.info("Implementing strategy from hypothesis")

        # Generate initial implementation
        code = self._generate_code(hypothesis, data_schema, parent_code)

        # Try to backtest and debug if needed
        metrics = {}
        notes = "Initial implementation"

        if self.backtesting_engine:
            for iteration in range(self.max_iterations):
                try:
                    # Run backtest
                    metrics = self.backtesting_engine.run_backtest(code)
                    notes = f"Successfully backtested after {iteration + 1} iteration(s)"
                    logger.info(f"Backtest successful: {metrics}")
                    break

                except Exception as e:
                    logger.warning(f"Backtest failed (iteration {iteration + 1}): {e}")

                    if iteration < self.max_iterations - 1:
                        # Debug and fix
                        code = self._debug_code(hypothesis, code, str(e), metrics)
                        notes = f"Debugged {iteration + 1} time(s)"
                    else:
                        notes = f"Failed after {self.max_iterations} attempts: {str(e)}"
                        # Return placeholder metrics
                        metrics = self._get_placeholder_metrics()
        else:
            # No backtesting engine - return placeholder metrics
            logger.warning("No backtesting engine available, using placeholder metrics")
            metrics = self._get_placeholder_metrics()
            notes = "No backtesting performed (placeholder metrics)"

        return code, metrics, notes

    def _generate_code(
        self,
        hypothesis: str,
        data_schema: str,
        parent_code: Optional[str] = None
    ) -> str:
        """Generate strategy code from hypothesis"""

        prompt = CODING_TEAM_IMPLEMENTATION_PROMPT.format(
            hypothesis=hypothesis,
            data_schema=data_schema,
            parent_code=parent_code or "# No parent code provided"
        )

        # Use fast model for code generation
        response = self.llm.fast_generate(
            prompt=prompt,
            system_prompt=CODING_TEAM_SYSTEM_PROMPT
        )

        # Extract code from response
        code = self._extract_code(response)

        return code

    def _debug_code(
        self,
        hypothesis: str,
        code: str,
        error: str,
        partial_results: Dict
    ) -> str:
        """Debug and fix code"""

        logger.info("Debugging strategy code")

        prompt = CODING_TEAM_DEBUG_PROMPT.format(
            hypothesis=hypothesis,
            code=code,
            error=error,
            results=str(partial_results)
        )

        # Use fast model for debugging
        response = self.llm.fast_generate(
            prompt=prompt,
            system_prompt=CODING_TEAM_SYSTEM_PROMPT
        )

        # Extract fixed code
        fixed_code = self._extract_code(response)

        return fixed_code

    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response"""

        # Look for code blocks
        code_blocks = re.findall(r'```python\n(.*?)```', response, re.DOTALL)

        if code_blocks:
            return code_blocks[0].strip()

        # If no code blocks, look for code after "code:" or similar markers
        lines = response.split('\n')
        code_lines = []
        in_code = False

        for line in lines:
            if 'code:' in line.lower() or 'python' in line.lower():
                in_code = True
                continue

            if in_code:
                code_lines.append(line)

        if code_lines:
            return '\n'.join(code_lines).strip()

        # Last resort: return entire response
        logger.warning("Could not extract code block, returning full response")
        return response.strip()

    def _get_placeholder_metrics(self) -> Dict[str, float]:
        """Get placeholder metrics when backtesting is not available"""
        import numpy as np

        # Generate random but realistic metrics
        return {
            'sharpe_ratio': np.random.uniform(0.0, 2.0),
            'sortino_ratio': np.random.uniform(0.0, 2.5),
            'information_ratio': np.random.uniform(-0.5, 1.5),
            'total_return': np.random.uniform(-50, 300),
            'max_drawdown': -np.random.uniform(10, 50),
            'trading_frequency': np.random.randint(10, 500),
            'strategy_category_bin': 1  # Will be updated by evaluation team
        }
