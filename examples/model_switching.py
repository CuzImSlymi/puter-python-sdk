#!/usr/bin/env python3
"""
Model Switching Example - Puter Python SDK

This example demonstrates how to switch between different AI models
and compare their responses to the same prompts.
"""

import os

from puter import PuterAI


def main():
    """Demonstrate model switching and comparison."""
    print("🔄 Model Switching Example - Puter Python SDK")
    print("=" * 55)

    username = os.getenv("PUTER_USERNAME", "your_username_here")
    password = os.getenv("PUTER_PASSWORD", "your_password_here")

    if username == "your_username_here":
        print(
            "⚠️  Please set PUTER_USERNAME and PUTER_PASSWORD environment variables"
        )
        return

    try:
        # Initialize client
        client = PuterAI(username=username, password=password)
        client.login()
        print("✅ Logged in successfully!")

        # Get available models
        all_models = client.get_available_models()
        print(f"📋 Total available models: {len(all_models)}")

        # Select some popular models for comparison
        test_models = [
            "gpt-4o",
            "claude-3.5-sonnet",
            "gpt-4",
            "claude-opus-4",
            "gemini-pro",
            "llama-3.1-70b",
        ]

        # Filter to only models that are actually available
        available_test_models = [
            model for model in test_models if model in all_models
        ]

        if not available_test_models:
            # Fallback to first few available models
            available_test_models = all_models[:3]

        print(f"🎯 Testing models: {', '.join(available_test_models)}")

        # Test prompts
        test_prompts = [
            "Explain quantum computing in exactly 2 sentences.",
            "Write a haiku about programming.",
            "What's the capital of Australia?",
            "Solve: What's 15% of 240?",
        ]

        print(
            f"\n💬 Testing {len(test_prompts)} prompts across {len(available_test_models)} models..."
        )
        print("=" * 70)

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n[Prompt {i}] {prompt}")
            print("-" * 50)

            for model in available_test_models:
                try:
                    # Switch to the model
                    success = client.set_model(model)
                    if not success:
                        print(f"❌ {model}: Failed to set model")
                        continue

                    # Clear chat history for fair comparison
                    client.clear_chat_history()

                    # Get response
                    response = client.chat(prompt)

                    # Display response (truncated for readability)
                    display_response = (
                        response[:150] + "..."
                        if len(response) > 150
                        else response
                    )
                    print(f"🤖 {model}:")
                    print(f"   {display_response}")
                    print()

                except Exception as e:
                    print(f"❌ {model}: Error - {e}")
                    print()

        # Demonstrate model-specific chat
        print("\n🎮 Interactive Model Selection")
        print("-" * 40)
        print("Available models:")
        for i, model in enumerate(available_test_models, 1):
            print(f"  {i}. {model}")

        while True:
            try:
                choice = input(
                    f"\nSelect model (1-{len(available_test_models)}) or 'q' to quit: "
                ).strip()

                if choice.lower() in ["q", "quit", "exit"]:
                    break

                model_index = int(choice) - 1
                if 0 <= model_index < len(available_test_models):
                    selected_model = available_test_models[model_index]
                    client.set_model(selected_model)
                    client.clear_chat_history()
                    print(f"✅ Switched to {selected_model}")

                    # Mini chat session
                    while True:
                        user_input = input(
                            f"\n[{selected_model}] You: "
                        ).strip()

                        if user_input.lower() in ["back", "switch"]:
                            break
                        if user_input.lower() in ["quit", "exit", "q"]:
                            return
                        if not user_input:
                            continue

                        response = client.chat(user_input)
                        print(f"[{selected_model}] AI: {response}")
                else:
                    print("❌ Invalid selection")

            except (ValueError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break

        print("\n✨ Model switching demo completed!")
        print("\nKey takeaways:")
        print("• Different models have different strengths")
        print("• Response styles and quality vary between models")
        print("• Use set_model() to switch between models")
        print("• Clear chat history for fair comparisons")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
