"""
Research Agent: Generates hypotheses for trading strategies
"""

from typing import List, Dict, Optional
from loguru import logger

from ..utils.llm_client import LLMEnsemble
from ..core.feature_map import Strategy
from .prompts import (
    RESEARCH_AGENT_SYSTEM_PROMPT,
    RESEARCH_AGENT_HYPOTHESIS_PROMPT,
    format_strategy_info,
    format_insights
)


class ResearchAgent:
    """
    Research Agent for generating trading strategy hypotheses
    """

    def __init__(self, llm_ensemble: LLMEnsemble):
        """
        Initialize Research Agent

        Args:
            llm_ensemble: LLM ensemble for generation
        """
        self.llm = llm_ensemble

    def generate_hypothesis(
        self,
        parent: Strategy,
        cousins: List[Strategy],
        data_schema: str,
        insights: List[Dict],
        generation: int
    ) -> str:
        """
        Generate new trading strategy hypothesis

        Args:
            parent: Parent strategy
            cousins: Cousin strategies
            data_schema: Data schema prompt
            insights: Accumulated insights
            generation: Current generation number

        Returns:
            Hypothesis text
        """
        logger.info(f"Generating hypothesis (gen {generation})")

        # Format parent information
        parent_info = format_strategy_info(parent, include_code=True)

        # Format cousin information (without code to save tokens)
        cousins_info = "\n\n".join([
            format_strategy_info(cousin, include_code=False)
            for cousin in cousins[:5]  # Limit to 5 cousins
        ])

        # Format insights
        insights_text = format_insights(insights, max_insights=50)

        # Create prompt
        prompt = RESEARCH_AGENT_HYPOTHESIS_PROMPT.format(
            parent_info=parent_info,
            cousins_info=cousins_info,
            data_schema=data_schema,
            insights=insights_text,
            generation=generation
        )

        # Generate hypothesis using large (thoughtful) model
        hypothesis = self.llm.thoughtful_generate(
            prompt=prompt,
            system_prompt=RESEARCH_AGENT_SYSTEM_PROMPT
        )

        logger.info(f"Generated hypothesis: {hypothesis[:100]}...")

        return hypothesis
