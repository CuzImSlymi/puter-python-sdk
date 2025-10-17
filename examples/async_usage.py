#!/usr/bin/env python3
"""Async Usage Example - Puter Python SDK.

This example demonstrates how to use the async/await features of the Puter SDK
for better performance in concurrent applications.
"""

import asyncio
import os
import time

from puter import PuterAI


async def async_chat_example():
    """Demonstrate async chat functionality."""
    print("🚀 Async Chat Example")
    print("=" * 30)

    username = os.getenv("PUTER_USERNAME", "your_username_here")
    password = os.getenv("PUTER_PASSWORD", "your_password_here")

    if username == "your_username_here":
        print(
            "⚠️  Please set PUTER_USERNAME and PUTER_PASSWORD environment variables"
        )
        return

    try:
        # Create client
        client = PuterAI(username=username, password=password)

        # Async login
        print("Logging in asynchronously...")
        await client.async_login()
        print("✅ Logged in!")

        # Single async chat
        print("\n💬 Single async chat:")
        response = await client.async_chat(
            "Explain async programming in Python briefly."
        )
        print(f"Response: {response[:150]}...")

        # Multiple concurrent chats
        print("\n🔄 Running multiple concurrent chats...")

        prompts = [
            "What is artificial intelligence?",
            "Explain machine learning in one sentence.",
            "What is the difference between AI and ML?",
            "Name three benefits of AI.",
            "What are some AI applications?",
        ]

        start_time = time.time()

        # Run all chats concurrently
        tasks = [client.async_chat(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks)

        end_time = time.time()

        print(
            f"\n⚡ Completed {len(prompts)} chats in {end_time - start_time:.2f} seconds"
        )

        for i, (prompt, response) in enumerate(zip(prompts, responses), 1):
            print(f"\n[{i}] {prompt}")
            print(f"Response: {response[:100]}...")

    except Exception as e:
        print(f"❌ Error: {e}")


async def rate_limited_example():
    """Demonstrate rate limiting in action."""
    print("\n🛡️ Rate Limiting Example")
    print("=" * 30)

    username = os.getenv("PUTER_USERNAME", "your_username_here")
    password = os.getenv("PUTER_PASSWORD", "your_password_here")

    if username == "your_username_here":
        return

    try:
        # Create client with custom rate limiting
        client = PuterAI(
            username=username,
            password=password,
            rate_limit_requests=3,  # Only 3 requests
            rate_limit_period=10,  # per 10 seconds
        )

        await client.async_login()

        print("Making rapid requests (rate limited to 3/10s)...")

        for i in range(5):
            start = time.time()
            response = await client.async_chat(
                f"Quick question #{i+1}: What's 2+2?"
            )
            elapsed = time.time() - start
            print(f"Request {i+1}: {elapsed:.2f}s - {response[:50]}...")

    except Exception as e:
        print(f"❌ Error: {e}")


async def error_handling_example():
    """Demonstrate robust error handling with async operations."""
    print("\n🔧 Error Handling Example")
    print("=" * 30)

    try:
        # Test with invalid credentials
        client = PuterAI(username="invalid", password="invalid")

        print("Testing login with invalid credentials...")
        await client.async_login()

    except Exception as e:
        print(f"✅ Caught expected error: {type(e).__name__}: {e}")

    try:
        # Test unauthenticated chat
        client = PuterAI()
        await client.async_chat("This should fail")

    except Exception as e:
        print(f"✅ Caught expected error: {type(e).__name__}: {e}")


async def main():
    """Run all async examples."""
    print("🚀 Puter Python SDK - Async Examples")
    print("=" * 50)

    await async_chat_example()
    await rate_limited_example()
    await error_handling_example()

    print("\n✨ All async examples completed!")
    print("Key benefits of async:")
    print("• Better performance for multiple requests")
    print("• Built-in rate limiting")
    print("• Non-blocking operations")
    print("• Proper resource management")


if __name__ == "__main__":
    asyncio.run(main())
