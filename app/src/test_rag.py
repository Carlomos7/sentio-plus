#!/usr/bin/env python3
"""Simple test script to verify LLM functionality."""

import sys
from pathlib import Path

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import get_settings
from src.services.llm import LLMClient
from src.services.rag import RAGService
from src.services.vector_store import VectorStore


def test_basic_query():
    """Test basic rag query method."""
    print("=" * 60)
    print("Test 1: Basic query() method")
    print("=" * 60)

    settings = get_settings()
    
    # printing settings
    #print("Settings:", settings.model_dump())
    
    client = LLMClient(
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
    store = VectorStore(
        client_type=settings.chroma_client_type,
        collection_name=settings.chroma_collection_name,
        persist_path=settings.chroma_persist_path,
        host='localhost',
        port=8001,
    )

    ingestDocs = ["I fell off the map.", "This is the best game I ever played."]
    ids = ["com.Google_Maps_1", "com.Death_RPG_1"]
    metadata = [{"app_name": "Google_Maps"}, {"app_name": "Death_RPG"}]
    store.clear()
    store.add_documents(ingestDocs, metadata, ids)

    rag = RAGService(
        llm=client,
        vector_store=store,
        top_k=5,
        threshold=1.2,
    )


    prompt = "What do people think of my mapping app?"
    print(f"Prompt: {prompt}\n")

    try:
        response = rag.query(prompt)
        print(response)
        assert len(response["sources"]) >= 1
        #assert response["selected_sources"] == ["Google_Maps"]
        assert "Google_Maps" in response["selected_sources"]
        print("✓ Basic invoke() test passed!")
        return True
    except Exception as e:
        print(f"✗ Basic invoke() test failed: {e}\n")
        import traceback

        traceback.print_exc()
        return False

'''
def test_generate_with_system_prompt():
    """Test generate method with system prompt."""
    print("=" * 60)
    print("Test 2: generate() method with system prompt")
    print("=" * 60)

    settings = get_settings()
    client = LLMClient(
        provider=settings.llm_provider,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        aws_region=settings.aws_region,
    )

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

    settings = get_settings()
    client = LLMClient(
        provider=settings.llm_provider,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        aws_region=settings.aws_region,
    )

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
'''

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAG Functionality Test")
    print("=" * 60 + "\n")

    settings = get_settings()
    print(f"Provider: {settings.llm_provider.value}")
    print(f"Model: {settings.llm_model}")
    print(f"Base URL: {settings.llm_base_url}")
    print(f"Temperature: {settings.llm_temperature}")
    print(f"Max Tokens: {settings.llm_max_tokens}\n")

    results = []

    # Run tests
    results.append(("Basic query()", test_basic_query()))

    '''
    print("\n")
    results.append(
        ("generate() with system prompt", test_generate_with_system_prompt())
    )
    print("\n")
    results.append(
        ("generate() without system prompt", test_generate_without_system_prompt())
    )
    '''

    # Summary
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
