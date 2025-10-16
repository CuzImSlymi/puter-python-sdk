#!/usr/bin/env python3
"""
Simple Chatbot Example - Puter Python SDK

A basic interactive chatbot with personality and conversation management.
Perfect for building customer service bots, assistants, or companions.
"""

import json
import os
from datetime import datetime

from puter import PuterAI

class SimpleChatbot:
    """A simple chatbot with personality and memory."""

    def __init__(
        self, name="Puter Assistant", personality="helpful and friendly"
    ):
        self.name = name
        self.personality = personality
        self.client = None
        self.conversation_history = []
        self.user_name = None

    def initialize(self, username=None, password=None):
        """Initialize the AI client."""
        username = username or os.getenv("PUTER_USERNAME")
        password = password or os.getenv("PUTER_PASSWORD")

        if not username or not password:
            raise ValueError("Please provide Puter.js credentials")

        self.client = PuterAI(username=username, password=password)
        self.client.login()

        # Set personality with system message
        personality_prompt = """You are {self.name}, a {self.personality} AI assistant.
        Key traits:
        - Always be helpful and positive
        - Remember context from our conversation
        - Ask follow-up questions when appropriate
        - Provide practical, actionable advice
        - Use a warm, conversational tone

        Keep responses concise but informative. If you don't know something, admit it honestly."""

        # Send personality setup (this will be remembered in chat history)
        self.client.chat(personality_prompt)
        print(f"✅ {self.name} is ready to chat!")

    def chat(self, message):
        """Send a message and get response."""
        if not self.client:
            raise RuntimeError(
                "Chatbot not initialized. Call initialize() first."
            )

        # Add timestamp and user context
        context_message = (
            f"[{datetime.now().strftime('%H:%M')}] User: {message}"
        )

        # Get AI response
        response = self.client.chat(context_message)

        # Store conversation
        self.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "user": message,
                "bot": response,
            }
        )

        return response

    def get_conversation_summary(self):
        """Get a summary of the conversation."""
        if not self.conversation_history:
            return "No conversation yet."

        summary_prompt = """Please provide a brief summary of our conversation so far.
        Focus on the main topics discussed and any important information shared.
        Keep it to 2-3 sentences."""

        return self.client.chat(summary_prompt)

    def save_conversation(self, filename=None):
        """Save conversation to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"

        data = {
            "bot_name": self.name,
            "personality": self.personality,
            "user_name": self.user_name,
            "start_time": (
                self.conversation_history[0]["timestamp"]
                if self.conversation_history
                else None
            ),
            "conversation": self.conversation_history,
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        return filename

    def clear_memory(self):
        """Clear conversation history."""
        self.client.clear_chat_history()
        self.conversation_history = []
        print("🧹 Conversation history cleared!")

def main():
    """Run the interactive chatbot."""
    print("🤖 Simple Chatbot - Puter Python SDK")
    print("=" * 45)

    try:
        # Initialize chatbot
        bot = SimpleChatbot(
            name="Buddy", personality="friendly, witty, and knowledgeable"
        )

        print("Initializing chatbot...")
        bot.initialize()

        # Get user's name
        user_name = input("What's your name? ").strip()
        if user_name:
            bot.user_name = user_name
            greeting = bot.chat(
                f"Hi! My name is {user_name}. Nice to meet you!"
            )
            print(f"\n{bot.name}: {greeting}")
        else:
            greeting = bot.chat(
                "Hello! I'm ready to help. What would you like to talk about?"
            )
            print(f"\n{bot.name}: {greeting}")

        print(f"\n💬 Start chatting with {bot.name}!")
        print("Commands: 'help', 'summary', 'save', 'clear', 'quit'")
        print("-" * 50)

        while True:
            try:
                user_input = input(f"\n{user_name or 'You'}: ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() == "quit":
                    # Farewell message
                    farewell = bot.chat(
                        "The user is saying goodbye. Please say a nice farewell message."
                    )
                    print(f"\n{bot.name}: {farewell}")
                    break

                elif user_input.lower() == "help":
                    print("\n🆘 Available commands:")
                    print("• 'summary' - Get conversation summary")
                    print("• 'save' - Save conversation to file")
                    print("• 'clear' - Clear conversation memory")
                    print("• 'quit' - End conversation")
                    continue

                elif user_input.lower() == "summary":
                    summary = bot.get_conversation_summary()
                    print(f"\n📋 Conversation Summary:\n{summary}")
                    continue

                elif user_input.lower() == "save":
                    filename = bot.save_conversation()
                    print(f"💾 Conversation saved to {filename}")
                    continue

                elif user_input.lower() == "clear":
                    bot.clear_memory()
                    continue

                # Regular chat
                response = bot.chat(user_input)
                print(f"\n{bot.name}: {response}")

            except KeyboardInterrupt:
                print(
                    f"\n\n{bot.name}: Goodbye! It was nice chatting with you! 👋"
                )
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Type 'help' for available commands or 'quit' to exit.")

        # Save conversation on exit
        if bot.conversation_history:
            save_choice = (
                input("\nWould you like to save this conversation? (y/n): ")
                .strip()
                .lower()
            )
            if save_choice in ["y", "yes"]:
                filename = bot.save_conversation()
                print(f"💾 Conversation saved to {filename}")

        print("\n✨ Thanks for using the Puter chatbot!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("• Set PUTER_USERNAME and PUTER_PASSWORD environment variables")
        print("• A stable internet connection")
        print("• Valid Puter.js credentials")

if __name__ == "__main__":
    main()
