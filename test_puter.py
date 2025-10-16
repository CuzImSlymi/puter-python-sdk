"""Test script for Puter Python SDK."""

from puter import PuterAI, PuterAPIError, PuterAuthError


def main():
    """Test the Puter AI SDK interactively."""
    print("\n--- Puter.js AI Python SDK Test Script ---")
    print("This script allows you to interact with Puter.js AI models.")
    print(
        "Your credentials are used only for this session and are not stored."
    )

    username = input("Enter your Puter.js Username: ")
    password = input("Enter your Puter.js Password: ")

    try:
        # Initialize the AI client
        client = PuterAI(username=username, password=password)
        print("Attempting to log in...")

        # Attempt to log in
        if client.login():
            print("Login successful!")
            print(f"Currently using model: {client.current_model}")
            print(
                "Type 'exit' to quit, '/model <name>' to change model, '/clear' to clear chat history."
            )
            print("Type '/models' to see available models.")

            while True:
                user_input = input(f"\nYou [{client.current_model}]> ")

                if user_input.lower() == "exit":
                    print("Exiting chat. Goodbye!")
                    break
                elif user_input.lower().startswith("/model "):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) > 1:
                        new_model = parts[1]
                        if client.set_model(new_model):
                            print(
                                f"Model successfully changed to: {client.current_model}"
                            )
                        else:
                            print(
                                f"Error: Model '{new_model}' not found. Available models: {', '.join(client.get_available_models())}"
                            )
                    else:
                        print(
                            f"Current model: {client.current_model}. Use '/model <name>' to change."
                        )
                elif user_input.lower() == "/clear":
                    client.clear_chat_history()
                    print("Chat history cleared.")
                elif user_input.lower() == "/models":
                    print("Available models:")
                    for model in client.get_available_models():
                        print(f"- {model}")
                elif (
                    user_input.strip()
                ):  # Only call AI if user input is not empty and not a command
                    try:
                        response = client.chat(user_input)
                        print(f"AI: {response}")
                    except PuterAPIError as e:
                        print(f"AI chat error: {e}")

        else:
            print("Login failed. Please check your credentials.")

    except PuterAuthError as e:
        print(f"Authentication Error: {e}")
    except Exception as e:
        print(f"An Unexpected Error Occurred: {e}")


if __name__ == "__main__":
    main()
