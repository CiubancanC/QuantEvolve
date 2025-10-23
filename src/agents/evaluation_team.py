"""
Evaluation Team: Analyzes strategies and extracts insights
"""

import re
from typing import Dict, List
from loguru import logger

from ..utils.llm_client import LLMEnsemble
from .prompts import (
    EVALUATION_TEAM_SYSTEM_PROMPT,
    EVALUATION_TEAM_ANALYSIS_PROMPT,
    EVALUATION_TEAM_INSIGHT_CURATION_PROMPT
)


class EvaluationTeam:
    """
    Evaluation Team for analyzing strategies and extracting insights
    """

    def __init__(self, llm_ensemble: LLMEnsemble):
        """
        Initialize Evaluation Team

        Args:
            llm_ensemble: LLM ensemble for analysis
        """
        self.llm = llm_ensemble

    def analyze_strategy(
        self,
        hypothesis: str,
        code: str,
        metrics: Dict[str, float],
        quantstats_output: str = "N/A"
    ) -> Dict:
        """
        Analyze strategy and extract insights

        Args:
            hypothesis: Strategy hypothesis
            code: Strategy code
            metrics: Backtest metrics
            quantstats_output: QuantStats analysis output

        Returns:
            Analysis dictionary with insights and categorization
        """
        logger.info("Analyzing strategy")

        # Format metrics for display
        metrics_str = self._format_metrics(metrics)

        # Create analysis prompt
        prompt = EVALUATION_TEAM_ANALYSIS_PROMPT.format(
            hypothesis=hypothesis,
            code=code,
            metrics=metrics_str,
            quantstats_output=quantstats_output
        )

        # Use large (thoughtful) model for analysis
        response = self.llm.thoughtful_generate(
            prompt=prompt,
            system_prompt=EVALUATION_TEAM_SYSTEM_PROMPT
        )

        # Parse analysis
        analysis = self._parse_analysis(response, metrics)

        logger.info(f"Analysis complete. Category bin: {analysis['category_bin']}")

        return analysis

    def curate_insights(
        self,
        insights: List[Dict],
        island_category: str,
        max_insights: int = 100
    ) -> List[Dict]:
        """
        Curate accumulated insights

        Args:
            insights: List of insights to curate
            island_category: Island category for context
            max_insights: Maximum number of insights to keep

        Returns:
            Curated list of insights
        """
        logger.info(f"Curating {len(insights)} insights for {island_category}")

        if len(insights) <= max_insights:
            return insights

        # Format insights for curation
        insights_text = "\n\n".join([
            f"[Gen {i.get('generation', '?')}] {i.get('content', i.get('insight', ''))}"
            for i in insights
        ])

        # Create curation prompt
        prompt = EVALUATION_TEAM_INSIGHT_CURATION_PROMPT.format(
            num_insights=len(insights),
            insights=insights_text,
            island_category=island_category,
            max_insights=max_insights
        )

        # Use large model for curation
        response = self.llm.thoughtful_generate(
            prompt=prompt,
            system_prompt=EVALUATION_TEAM_SYSTEM_PROMPT
        )

        # Parse curated insights
        curated = self._parse_curated_insights(response)

        logger.info(f"Curated to {len(curated)} insights")

        return curated

    def _format_metrics(self, metrics: Dict[str, float]) -> str:
        """Format metrics for display"""
        lines = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if 'ratio' in key.lower():
                    lines.append(f"- {key}: {value:.3f}")
                elif 'return' in key.lower() or 'drawdown' in key.lower():
                    lines.append(f"- {key}: {value:.2f}%")
                else:
                    lines.append(f"- {key}: {value}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _parse_analysis(self, response: str, metrics: Dict) -> Dict:
        """Parse analysis response into structured format"""

        analysis = {
            'full_text': response,
            'hypothesis_quality': 'Unknown',
            'implementation_fidelity': 'Unknown',
            'insights': [],
            'recommendations': [],
            'category_bin': metrics.get('strategy_category_bin', 1)
        }

        # Extract insights
        insights_match = re.search(
            r'(?:insights?|learnings?)[:|\n]+(.*?)(?:recommendations?|$)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if insights_match:
            insights_text = insights_match.group(1)
            # Split by numbers or bullets
            insights = re.findall(r'(?:^|\n)\s*[\d\-\*]+[\.\)]\s*(.+?)(?=\n\s*[\d\-\*]+|$)', insights_text, re.DOTALL)
            analysis['insights'] = [i.strip() for i in insights if i.strip()]

        # Extract recommendations
        rec_match = re.search(
            r'recommendations?[:|\n]+(.*?)$',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if rec_match:
            rec_text = rec_match.group(1)
            recommendations = re.findall(r'(?:^|\n)\s*[\d\-\*]+[\.\)]\s*(.+?)(?=\n\s*[\d\-\*]+|$)', rec_text, re.DOTALL)
            analysis['recommendations'] = [r.strip() for r in recommendations if r.strip()]

        # Extract category from "Strategy Categorization" section
        cat_match = re.search(
            r'categor[iy].*?[:|\n]+.*?(?:binary|encoding|bin).*?[:\s]+(\d+)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if cat_match:
            try:
                analysis['category_bin'] = int(cat_match.group(1))
            except ValueError:
                pass

        # Extract quality ratings
        if 'excellent' in response.lower():
            analysis['hypothesis_quality'] = 'Excellent'
        elif 'good' in response.lower():
            analysis['hypothesis_quality'] = 'Good'
        elif 'fair' in response.lower():
            analysis['hypothesis_quality'] = 'Fair'
        elif 'poor' in response.lower():
            analysis['hypothesis_quality'] = 'Poor'

        return analysis

    def _parse_curated_insights(self, response: str) -> List[Dict]:
        """Parse curated insights from response"""

        insights = []

        # Look for structured insights
        # Format: "Theme: ...\nInsight: ...\nSupporting Evidence: ...\nActionability: ..."
        insight_blocks = re.split(r'\n\s*(?=Theme|Category|Insight\s*\d+)', response)

        for block in insight_blocks:
            if len(block.strip()) < 20:
                continue

            insight = {
                'content': block.strip(),
                'theme': 'General',
                'actionability': 'Medium'
            }

            # Extract theme
            theme_match = re.search(r'(?:theme|category):\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if theme_match:
                insight['theme'] = theme_match.group(1).strip()

            # Extract main insight content
            content_match = re.search(r'insight:\s*(.+?)(?:\n\n|supporting|actionability|$)', block, re.IGNORECASE | re.DOTALL)
            if content_match:
                insight['content'] = content_match.group(1).strip()

            insights.append(insight)

        # If no structured format found, split by numbers
        if not insights:
            numbered = re.findall(r'(?:^|\n)\s*\d+[\.\)]\s*(.+?)(?=\n\s*\d+|$)', response, re.DOTALL)
            insights = [{'content': i.strip(), 'theme': 'General', 'actionability': 'Medium'} for i in numbered if i.strip()]

        return insights
