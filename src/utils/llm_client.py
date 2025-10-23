"""
OpenRouter API Client for QuantEvolve
Provides interface to LLM models through OpenRouter API
"""

import os
from typing import Dict, List, Optional, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        small_model: Optional[str] = None,
        large_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        timeout: int = 120
    ):
        """
        Initialize OpenRouter client

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            small_model: Fast model for quick responses (defaults to env var)
            large_model: Large model for thoughtful analysis (defaults to env var)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided")

        self.small_model = small_model or os.getenv("SMALL_MODEL", "qwen/qwen3-30b-a3b-instruct-2507")
        self.large_model = large_model or os.getenv("LARGE_MODEL", "qwen/qwen3-next-80b-a3b-instruct")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/quantevolve/quantevolve",
            "X-Title": "QuantEvolve"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def _make_request(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make API request with retry logic

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            API response dictionary
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        use_large_model: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send chat completion request

        Args:
            messages: Conversation messages
            use_large_model: If True, use large model; otherwise use small model
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Generated text response
        """
        model = self.large_model if use_large_model else self.small_model

        logger.info(f"Calling {model} with {len(messages)} messages")

        response = self._make_request(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        content = response["choices"][0]["message"]["content"]

        # Log usage stats if available
        if "usage" in response:
            usage = response["usage"]
            logger.debug(
                f"Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                f"Completion: {usage.get('completion_tokens', 0)}, "
                f"Total: {usage.get('total_tokens', 0)}"
            )

        return content

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_large_model: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from a single prompt

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            use_large_model: If True, use large model
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Generated text response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return self.chat(
            messages=messages,
            use_large_model=use_large_model,
            temperature=temperature,
            max_tokens=max_tokens
        )


class LLMEnsemble:
    """
    Ensemble of small and large models
    Mimics the paper's approach: Qwen3-30B-A3B-Instruct-2507 (fast) + Qwen3-Next-80B-A3B-Instruct (thoughtful)
    """

    def __init__(self, client: OpenRouterClient):
        """
        Initialize LLM ensemble

        Args:
            client: OpenRouter client instance
        """
        self.client = client

    def fast_generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using small, fast model"""
        return self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            use_large_model=False
        )

    def thoughtful_generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using large, thoughtful model"""
        return self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            use_large_model=True
        )

    def ensemble_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        combine_strategy: str = "large"
    ) -> str:
        """
        Generate using both models and combine

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            combine_strategy: How to combine outputs ('large', 'small', 'both')

        Returns:
            Combined or selected response
        """
        if combine_strategy == "small":
            return self.fast_generate(prompt, system_prompt)
        elif combine_strategy == "large":
            return self.thoughtful_generate(prompt, system_prompt)
        elif combine_strategy == "both":
            # Get both responses and ask large model to synthesize
            fast_response = self.fast_generate(prompt, system_prompt)

            synthesis_prompt = f"""You have two analyses of the same question.
Please synthesize them into a single, comprehensive response.

Original Question:
{prompt}

Fast Analysis:
{fast_response}

Please provide the synthesized response:"""

            return self.thoughtful_generate(synthesis_prompt, system_prompt)
        else:
            raise ValueError(f"Unknown combine_strategy: {combine_strategy}")


def create_llm_client(config: Optional[Dict[str, Any]] = None) -> OpenRouterClient:
    """
    Factory function to create LLM client from config

    Args:
        config: Configuration dictionary (defaults to env vars)

    Returns:
        Configured OpenRouter client
    """
    if config is None:
        config = {}

    return OpenRouterClient(
        api_key=config.get("api_key"),
        small_model=config.get("small_model"),
        large_model=config.get("large_model"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4000),
        timeout=config.get("timeout", 120)
    )
