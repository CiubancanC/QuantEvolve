"""
Test script to verify OpenRouter LLM connection
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.llm_client import create_llm_client, LLMEnsemble
from utils.config_loader import load_config
from utils.logger import setup_logger, get_logger


def test_llm_connection():
    """Test LLM connection to OpenRouter"""

    print("=" * 80)
    print("Testing LLM Connection to OpenRouter")
    print("=" * 80)
    print()

    # Setup
    print("1. Loading configuration...")
    config = load_config()
    print("   ✓ Configuration loaded")
    print()

    print("2. Setting up logger...")
    setup_logger(log_dir='./logs', level='INFO')
    logger = get_logger()
    print("   ✓ Logger configured")
    print()

    print("3. Creating LLM client...")
    llm_config = config.get('llm', {})
    print(f"   - API Key: {llm_config.get('api_key', 'N/A')[:20]}...")
    print(f"   - Small Model: {llm_config.get('small_model')}")
    print(f"   - Large Model: {llm_config.get('large_model')}")

    try:
        client = create_llm_client(llm_config)
        ensemble = LLMEnsemble(client)
        print("   ✓ LLM client created successfully")
        print()
    except Exception as e:
        print(f"   ✗ Error creating client: {e}")
        return False

    # Test fast model
    print("4. Testing small/fast model...")
    test_prompt = "What is momentum trading? Answer in one sentence."

    try:
        response = ensemble.fast_generate(test_prompt)
        print("   ✓ Fast model response received")
        print(f"   Response: {response[:200]}...")
        print()
    except Exception as e:
        print(f"   ✗ Error with fast model: {e}")
        return False

    # Test large model
    print("5. Testing large/thoughtful model...")
    test_prompt = "Explain the theoretical foundation of momentum trading strategies."

    try:
        response = ensemble.thoughtful_generate(test_prompt)
        print("   ✓ Thoughtful model response received")
        print(f"   Response: {response[:200]}...")
        print()
    except Exception as e:
        print(f"   ✗ Error with large model: {e}")
        return False

    # Test with system prompt
    print("6. Testing with system prompt...")
    system_prompt = "You are a quantitative trading expert. Be concise and technical."
    user_prompt = "What is the Sharpe ratio?"

    try:
        response = ensemble.fast_generate(user_prompt, system_prompt=system_prompt)
        print("   ✓ System prompt test successful")
        print(f"   Response: {response[:200]}...")
        print()
    except Exception as e:
        print(f"   ✗ Error with system prompt: {e}")
        return False

    # Success
    print("=" * 80)
    print("✅ All LLM connection tests passed!")
    print("=" * 80)
    print()
    print("Your OpenRouter API key is working correctly.")
    print("Both models (small and large) are accessible.")
    print("You're ready to run QuantEvolve!")
    print()

    return True


if __name__ == "__main__":
    success = test_llm_connection()
    sys.exit(0 if success else 1)
