# puter-python-sdk

![Python](https://img.shields.io/badge/python-3.7+-blue.svg) ![License](https://img.shields.io/github/license/CuzImSlymi/puter-python-sdk) ![GitHub stars](https://img.shields.io/github/stars/CuzImSlymi/puter-python-sdk?style=social)

## 🚀 A Powerful Python SDK for Puter.js AI

Seamlessly integrate Puter.js AI models into your Python applications. The `puter-python-sdk` provides a robust and easy-to-use interface to access a wide range of large language models offered by Puter.js, enabling you to build intelligent applications with minimal effort.

Whether you're developing chatbots, content generators, or complex AI-driven workflows, this SDK simplifies the interaction with Puter.js's powerful AI capabilities.

## ✨ Features

-   **Easy Authentication**: Securely log in using your Puter.js username and password.
-   **Flexible Chat Interface**: Engage in dynamic conversations with various AI models.
-   **Comprehensive Model Management**: Effortlessly switch between available AI models to suit your needs.
-   **Automatic Chat History**: Conversation context is automatically maintained for coherent interactions.
-   **Robust Error Handling**: Custom exceptions provide clear and concise error feedback for authentication and API issues.
-   **Developer-Friendly**: Designed with simplicity and developer experience in mind, following Python best practices.

## 📦 Installation

Get started with `puter-python-sdk` in just one command!

### Quick Install (Recommended)

```bash
pip install puter-python-sdk
```

### Development Installation

If you want to contribute or modify the code:

1.  **Clone the Repository**:

    ```bash
    git clone https://github.com/CuzImSlymi/puter-python-sdk.git
    cd puter-python-sdk
    ```

2.  **Install Dependencies**:

    It's highly recommended to use a virtual environment to manage your project dependencies.

    ```bash
    # Create a virtual environment
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    # .\venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate

    # Install required packages
    pip install -r requirements.txt
    ```

3.  **Install the Library**:

    Install the `puter-python-sdk` locally in editable mode (for development) or as a standard package.

    ```bash
    # For development (editable mode)
    pip install -e .

    # Or as a standard package
    pip install .
    ```

## ⚡ Quick Start

Run the `test_puter.py` script to quickly verify your setup and interact with the AI. This script will prompt you for your Puter.js credentials and allow you to chat directly.

```bash
python test_puter.py
```

## 📖 Usage Examples

### Basic Chat Interaction

After installing the library, you can import `PuterAI` and its exceptions into your Python scripts.

```python
from puter import PuterAI, PuterAuthError, PuterAPIError

# Replace with your actual Puter.js credentials
USERNAME = "your_puterjs_username"
PASSWORD = "your_puterjs_password"

try:
    # Initialize the AI client
    puter_ai = PuterAI(username=USERNAME, password=PASSWORD)

    # Log in to Puter.js
    if puter_ai.login():
        print("Login successful!")

        # Start a conversation
        response = puter_ai.chat("Hello, how are you today?")
        print(f"AI: {response}")

        response = puter_ai.chat("What is the capital of France?")
        print(f"AI: {response}")

        # Clear chat history for a fresh start
        puter_ai.clear_chat_history()
        print("Chat history cleared.")

        response = puter_ai.chat("Tell me a short, funny joke.")
        print(f"AI: {response}")

    else:
        print("Login failed. Please check your credentials.")

except PuterAuthError as e:
    print(f"Authentication Error: {e}")
except PuterAPIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"An Unexpected Error Occurred: {e}")
```

### Managing AI Models

Explore and switch between different AI models offered by Puter.js.

```python
from puter import PuterAI

# Assuming puter_ai client is already logged in as shown above
# puter_ai = PuterAI(username=USERNAME, password=PASSWORD)
# puter_ai.login()

# Get a list of all available models
models = puter_ai.get_available_models()
print("Available models:", models)

# Switch to a different model, e.g., gpt-5-nano
if puter_ai.set_model("gpt-5-nano"):
    print(f"Model switched to: {puter_ai.current_model}")
    response = puter_ai.chat("What is the meaning of life, according to GPT-5-nano?")
    print(f"AI: {response}")
else:
    print(f"Failed to switch model.")

# Switch back to claude-opus-4
if puter_ai.set_model("claude-opus-4"):
    print(f"Model switched to: {puter_ai.current_model}")
    response = puter_ai.chat("Tell me a short story about a space-faring cat.")
    print(f"AI: {response}")
```

## 🌐 Available Models

Puter.js supports a variety of AI models. You can find the most up-to-date list and details on the official Puter.js models page [here](https://puter.com/puterai/chat/models).

This SDK now supports a wide range of models by dynamically determining the correct driver based on the model name. You can get a full list of available models by calling the `get_available_models()` method on an authenticated `PuterAI` instance.

## 🚨 Error Handling

The `puter-python-sdk` provides custom exceptions for more granular error management:

-   `puter.PuterError`: The base exception for all library-specific errors.
-   `puter.PuterAuthError`: Raised when authentication with Puter.js fails (e.g., incorrect credentials, network issues during login).
-   `puter.PuterAPIError`: Raised when an API call to Puter.js fails after successful authentication (e.g., invalid model, rate limits, server errors).

## 🤝 Contributing

We welcome contributions! If you have suggestions, bug reports, or want to contribute code, please feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/CuzImSlymi/puter-python-sdk).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
