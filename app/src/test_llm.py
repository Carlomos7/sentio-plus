#!/usr/bin/env python3
"""Simple test script to verify LLM functionality."""

import sys
from pathlib import Path

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import get_settings
from src.services.llm import LLMClient

settings = get_settings()

print("Provider:", settings.llm_provider)
print("Region:", settings.aws_region)
print("Access key loaded:", bool(settings.aws_access_key_id))


def make_client() -> LLMClient:
    """Factory for LLMClient with explicit AWS credentials (Option 1)."""
    return LLMClient(
        provider=settings.llm_provider,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        aws_region=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def test_basic_invoke():
    """Test basic LLM invoke method."""
    print("=" * 60)
    print("Test 1: Basic invoke() method")
    print("=" * 60)

    client = make_client()

    print(f"\nModel Info: {client.get_model_info()}\n")

    prompt = "Say hello and tell me what 2+2 equals in one sentence."
    print(f"Prompt: {prompt}\n")

    try:
        response = client.invoke(prompt)
        print(f"Response: {response}\n")
        print("✓ Basic invoke() test passed!")
        return True
    except Exception as e:
        print(f"✗ Basic invoke() test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_generate_with_system_prompt():
    """Test generate method with system prompt."""
    print("=" * 60)
    print("Test 2: generate() method with system prompt")
    print("=" * 60)

    client = make_client()

    system_prompt = (
        "You are a helpful math tutor. Always explain your reasoning step by step."
    )
    user_prompt = "What is 15 * 7?"

    print(f"\nSystem Prompt: {system_prompt}")
    print(f"User Prompt: {user_prompt}\n")

    try:
        response = client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )
        print(f"Response: {response}\n")
        print("✓ generate() with system prompt test passed!")
        return True
    except Exception as e:
        print(f"✗ generate() with system prompt test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_generate_without_system_prompt():
    """Test generate method without system prompt."""
    print("=" * 60)
    print("Test 3: generate() method without system prompt")
    print("=" * 60)

    client = make_client()

    user_prompt = "Write a haiku about coding."
    print(f"\nUser Prompt: {user_prompt}\n")

    try:
        response = client.generate(prompt=user_prompt)
        print(f"Response: {response}\n")
        print("✓ generate() without system prompt test passed!")
        return True
    except Exception as e:
        print(f"✗ generate() without system prompt test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LLM Functionality Test")
    print("=" * 60 + "\n")

    print(f"Provider: {settings.llm_provider.value}")
    print(f"Model: {settings.llm_model}")
    print(f"Base URL: {settings.llm_base_url}")
    print(f"Temperature: {settings.llm_temperature}")
    print(f"Max Tokens: {settings.llm_max_tokens}\n")

    results = []

    results.append(("Basic invoke()", test_basic_invoke()))
    print("\n")
    results.append(("generate() with system prompt", test_generate_with_system_prompt()))
    print("\n")
    results.append(("generate() without system prompt", test_generate_without_system_prompt()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
