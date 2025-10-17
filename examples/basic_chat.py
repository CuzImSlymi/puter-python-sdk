#!/usr/bin/env python3
"""Basic Chat Example - Puter Python SDK.

This example demonstrates the simplest way to chat with AI models using the
Puter SDK.
Perfect for getting started with the library.
"""

import os

from puter import PuterAI


def main():
    """Demonstrate basic chat functionality."""
    print("🤖 Basic Chat Example - Puter Python SDK")
    print("=" * 50)

    # Initialize the client
    print("Initializing Puter AI client...")

    # You can set credentials via environment variables or pass them directly
    username = os.getenv("PUTER_USERNAME", "your_username_here")
    password = os.getenv("PUTER_PASSWORD", "your_password_here")

    if username == "your_username_here":
        print("⚠️  Please set your Puter.js credentials!")
        print("Either set environment variables:")
        print("   export PUTER_USERNAME='your_username'")
        print("   export PUTER_PASSWORD='your_password'")
        print("Or modify this script to include your credentials.")
        return

    try:
        # Create client and login
        client = PuterAI(username=username, password=password)
        print("Logging in...")
        client.login()
        print("✅ Successfully logged in!")

        # Show available models
        models = client.get_available_models()
        print(f"📋 Available models: {len(models)} models")
        print(f"🎯 Current model: {client.current_model}")

        # Simple chat examples
        examples = [
            "Hello! What can you help me with?",
            "What's the weather like in a poetic way?",
            "Explain quantum computing in simple terms.",
            "Write a short joke about programming.",
        ]

        print("\n💬 Starting chat examples...")
        print("-" * 30)

        for i, prompt in enumerate(examples, 1):
            print(f"\n[Example {i}]")
            print(f"User: {prompt}")

            # Send message and get response
            response = client.chat(prompt)
            print(
                f"AI: {response[:200]}{'...' if len(response) > 200 else ''}"
            )

        # Interactive mode
        print("\n🎮 Interactive mode - Type 'quit' to exit")
        print("-" * 40)

        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                break

            if not user_input:
                continue

            try:
                response = client.chat(user_input)
                print(f"AI: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")

        print("\n👋 Thanks for trying the Puter Python SDK!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify your Puter.js credentials")
        print("3. Make sure you have the latest SDK version")


if __name__ == "__main__":
    main()
