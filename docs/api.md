# API Reference - Puter Python SDK

Complete API documentation for the Puter Python SDK v0.3.0.

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [PuterAI Class](#puterai-class)
- [Configuration](#configuration)
- [Exceptions](#exceptions)
- [Examples](#examples)

## Installation

```bash
pip install puter-python-sdk
```

## Authentication

The SDK supports multiple authentication methods:

### Method 1: Direct Credentials

```python
from puter import PuterAI

client = PuterAI(username="your_username", password="your_password")
client.login()
```

### Method 2: Environment Variables

```bash
export PUTER_USERNAME="your_username"
export PUTER_PASSWORD="your_password"
```

```python
from puter import PuterAI

client = PuterAI()  # Automatically uses environment variables
client.login()
```

### Method 3: Token-based Authentication

```python
from puter import PuterAI

client = PuterAI(token="your_existing_token")
# No need to call login() with token
```

## PuterAI Class

The main class for interacting with Puter.js AI models.

### Constructor

```python
PuterAI(username=None, password=None, token=None, **config_overrides)
```

**Parameters:**
- `username` (str, optional): Your Puter.js username
- `password` (str, optional): Your Puter.js password
- `token` (str, optional): Existing authentication token
- `**config_overrides`: Configuration overrides (see [Configuration](#configuration))

**Example:**
```python
# Basic initialization
client = PuterAI(username="user", password="pass")

# With configuration overrides
client = PuterAI(
    username="user",
    password="pass",
    timeout=60,
    max_retries=5,
    rate_limit_requests=20
)
```

### Methods

#### `login() -> bool`

Authenticate with Puter.js using username and password.

**Returns:**
- `bool`: True if login successful, False otherwise

**Raises:**
- `PuterAuthError`: If credentials are invalid or missing

**Example:**
```python
client = PuterAI(username="user", password="pass")
if client.login():
    print("Successfully logged in!")
else:
    print("Login failed")
```

#### `async_login() -> bool`

Async version of login method.

**Returns:**
- `bool`: True if login successful, False otherwise

**Raises:**
- `PuterAuthError`: If credentials are invalid or missing

**Example:**
```python
import asyncio

async def main():
    client = PuterAI(username="user", password="pass")
    if await client.async_login():
        print("Successfully logged in!")

asyncio.run(main())
```

#### `chat(prompt: Optional[str] = None, model: Optional[str] = None, *, images: Optional[Sequence] = None, content_parts: Optional[Sequence[dict]] = None) -> str`

Send a chat or multimodal message to the AI model and get a response.

**Parameters:**
- `prompt` (str, optional): The user's message. May be omitted when using `images` or `content_parts`
- `model` (str, optional): Model to use for this chat. Defaults to `current_model`
- `images` (sequence, optional): Image inputs to attach. Each item may be a file path, `bytes`, a file-like object, an HTTP(S)/data URL, a tuple of `(data, mime_type)`, or a pre-built payload dictionary (`{"type": "image_url", ...}`)
- `content_parts` (sequence of dict, optional): Fully custom content payload overriding both `prompt` and `images`

**Returns:**
- `str`: The AI's response

**Raises:**
- `ValueError`: If no content is provided or an image input is invalid
- `PuterAPIError`: If the API call fails
- `PuterAuthError`: If not authenticated

**Example:**
```python
client = PuterAI(username="user", password="pass")
client.login()

# Basic chat
response = client.chat("Hello, how are you?")
print(response)

# Chat with specific model
response = client.chat("Explain quantum computing", model="gpt-4")
print(response)

# Vision chat with a local image
response = client.chat(
    "List every ingredient you see in this dish",
    images=["/tmp/dinner.jpg"],
)
print(response)

# Custom multimodal payload (content_parts overrides prompt/images)
response = client.chat(
    content_parts=[
        {"type": "text", "text": "Transcribe this audio clip."},
        {"type": "input_audio", "audio": {"id": "file_audio_123"}},
    ],
)
print(response)
```

#### `async_chat(prompt: Optional[str] = None, model: Optional[str] = None, *, images: Optional[Sequence] = None, content_parts: Optional[Sequence[dict]] = None) -> str`

Async version of the chat method with multimodal support.

**Parameters:**
- `prompt` (str, optional): The user's message. May be omitted when using `images` or `content_parts`
- `model` (str, optional): The model to use for this chat
- `images` (sequence, optional): Image inputs handled the same way as in `chat`
- `content_parts` (sequence of dict, optional): Fully custom content payload overriding `prompt` and `images`

**Returns:**
- `str`: The AI's response

**Raises:**
- `ValueError`: If no content is provided or an image input is invalid
- `PuterAPIError`: If the API call fails
- `PuterAuthError`: If not authenticated

**Example:**
```python
import asyncio

async def main():
    client = PuterAI(username="user", password="pass")
    await client.async_login()

    # Single async chat
    response = await client.async_chat("What is AI?")
    print(response)

    # Async vision request
    response = await client.async_chat(
        "What is in this bowl?",
        images=["https://example.com/food.jpg"],
    )
    print(response)

    # Multiple concurrent multimodal chats
    tasks = [
        client.async_chat("Summarize", images=["/tmp/report.png"]),
        client.async_chat(content_parts=[
            {"type": "text", "text": "Count the objects"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
        ]),
        client.async_chat("What is machine learning?"),
    ]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        print(response)

asyncio.run(main())
```

#### `get_available_models() -> List[str]`

Get list of all available AI model names.

**Returns:**
- `List[str]`: List of available model names

**Example:**
```python
client = PuterAI(username="user", password="pass")
models = client.get_available_models()
print(f"Available models: {len(models)}")
for model in models[:5]:  # Show first 5
    print(f"  • {model}")
```

#### `set_model(model_name: str) -> bool`

Set the current AI model for subsequent chats.

**Parameters:**
- `model_name` (str): Name of the model to set

**Returns:**
- `bool`: True if model was set successfully, False if model not found

**Example:**
```python
client = PuterAI(username="user", password="pass")
client.login()

# Check current model
print(f"Current model: {client.current_model}")

# Switch to different model
if client.set_model("gpt-4"):
    print("Successfully switched to GPT-4")
else:
    print("Model not found")

print(f"New current model: {client.current_model}")
```

#### `clear_chat_history()`

Clear the current conversation history.

**Example:**
```python
client = PuterAI(username="user", password="pass")
client.login()

client.chat("Hello!")
client.chat("How are you?")
print(f"History length: {len(client.chat_history)}")  # 4 messages

client.clear_chat_history()
print(f"History length: {len(client.chat_history)}")  # 0 messages
```

### Properties

#### `current_model: str`

The currently selected AI model.

**Example:**
```python
client = PuterAI()
print(client.current_model)  # "claude-opus-4" (default)
```

#### `chat_history: List[Dict[str, Any]]`

The conversation history as a list of message dictionaries.

**Example:**
```python
client = PuterAI(username="user", password="pass")
client.login()

client.chat("Hello!")
print(client.chat_history)
# [
#   {"role": "user", "content": "Hello!"},
#   {"role": "assistant", "content": "Hello! How can I help you today?"}
# ]
```

#### `available_models: Dict[str, str]`

Dictionary mapping model names to their driver types.

**Example:**
```python
client = PuterAI()
print(f"Total models: {len(client.available_models)}")
print(f"GPT-4 driver: {client.available_models.get('gpt-4', 'Not found')}")
```

## Configuration

The SDK provides flexible configuration options through the `config` object and environment variables.

### Configuration Class

```python
from puter import config, PuterConfig

# View current configuration
print(f"API Base: {config.api_base}")
print(f"Timeout: {config.timeout}")
print(f"Max Retries: {config.max_retries}")

# Update configuration
config.update(timeout=60, max_retries=5)

# Create custom configuration
custom_config = PuterConfig()
custom_config.update(timeout=120)
```

### Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `api_base` | `PUTER_API_BASE` | `https://api.puter.com` | Puter API base URL |
| `login_url` | `PUTER_LOGIN_URL` | `https://puter.com/login` | Login endpoint URL |
| `timeout` | `PUTER_TIMEOUT` | `30` | Request timeout in seconds |
| `max_retries` | `PUTER_MAX_RETRIES` | `3` | Maximum retry attempts |
| `retry_delay` | `PUTER_RETRY_DELAY` | `1.0` | Initial retry delay in seconds |
| `backoff_factor` | `PUTER_BACKOFF_FACTOR` | `2.0` | Exponential backoff multiplier |
| `rate_limit_requests` | `PUTER_RATE_LIMIT_REQUESTS` | `10` | Requests per rate limit period |
| `rate_limit_period` | `PUTER_RATE_LIMIT_PERIOD` | `60` | Rate limit period in seconds |

### Environment Variable Configuration

```bash
# Set environment variables
export PUTER_USERNAME="your_username"
export PUTER_PASSWORD="your_password"
export PUTER_TIMEOUT="60"
export PUTER_MAX_RETRIES="5"
export PUTER_RATE_LIMIT_REQUESTS="20"
export PUTER_RATE_LIMIT_PERIOD="60"
```

### Client-Specific Configuration

```python
# Override configuration per client
client = PuterAI(
    username="user",
    password="pass",
    timeout=90,                    # 90 second timeout
    max_retries=10,               # 10 retry attempts
    rate_limit_requests=50,       # 50 requests
    rate_limit_period=3600        # per hour
)
```

## Exceptions

The SDK defines custom exceptions for better error handling.

### Exception Hierarchy

```
PuterError (base exception)
├── PuterAuthError (authentication errors)
└── PuterAPIError (API call errors)
```

### PuterError

Base exception class for all Puter SDK errors.

```python
from puter.exceptions import PuterError

try:
    # SDK operations
    pass
except PuterError as e:
    print(f"Puter SDK error: {e}")
```

### PuterAuthError

Raised for authentication-related errors.

**Common causes:**
- Invalid username/password
- Missing credentials
- Token expired
- Network issues during login

```python
from puter.exceptions import PuterAuthError

try:
    client = PuterAI(username="invalid", password="invalid")
    client.login()
except PuterAuthError as e:
    print(f"Authentication failed: {e}")
```

### PuterAPIError

Raised for API call errors.

**Common causes:**
- Network connectivity issues
- API server errors
- Rate limiting
- Invalid requests

```python
from puter.exceptions import PuterAPIError

try:
    response = client.chat("Hello")
except PuterAPIError as e:
    print(f"API error: {e}")
```

### Error Handling Best Practices

```python
from puter import PuterAI
from puter.exceptions import PuterAuthError, PuterAPIError
import time

def robust_chat(client, prompt, max_retries=3):
    """Robust chat with comprehensive error handling."""

    for attempt in range(max_retries):
        try:
            return client.chat(prompt)

        except PuterAuthError as e:
            print(f"Authentication error: {e}")
            # Re-authentication might be needed
            return None

        except PuterAPIError as e:
            print(f"API error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return None

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    return None

# Usage
client = PuterAI(username="user", password="pass")
client.login()

response = robust_chat(client, "Hello, world!")
if response:
    print(response)
else:
    print("Failed to get response after retries")
```

## Examples

### Basic Usage

```python
from puter import PuterAI

# Initialize and login
client = PuterAI(username="your_username", password="your_password")
client.login()

# Simple chat
response = client.chat("What is artificial intelligence?")
print(response)

# Multi-turn conversation
client.chat("I'm learning about Python programming.")
response = client.chat("Can you give me some tips for beginners?")
print(response)
```

### Model Switching

```python
from puter import PuterAI

client = PuterAI(username="user", password="pass")
client.login()

# Get available models
models = client.get_available_models()
print(f"Available models: {len(models)}")

# Try the same question with different models
question = "Explain quantum computing in simple terms."

for model in ["gpt-4", "claude-3.5-sonnet", "gemini-pro"]:
    if model in models:
        client.set_model(model)
        client.clear_chat_history()  # Fresh conversation
        response = client.chat(question)
        print(f"\n{model}:")
        print(response[:200] + "...")
```

### Async Operations

```python
import asyncio
from puter import PuterAI

async def concurrent_chats():
    client = PuterAI(username="user", password="pass")
    await client.async_login()

    # Run multiple chats concurrently
    questions = [
        "What is machine learning?",
        "What is deep learning?",
        "What is neural network?",
        "What is artificial intelligence?"
    ]

    tasks = [client.async_chat(q) for q in questions]
    responses = await asyncio.gather(*tasks)

    for question, response in zip(questions, responses):
        print(f"Q: {question}")
        print(f"A: {response[:100]}...\n")

# Run async function
asyncio.run(concurrent_chats())
```

### Configuration Examples

```python
from puter import PuterAI, config

# Method 1: Global configuration
config.update(
    timeout=60,
    max_retries=5,
    rate_limit_requests=20
)

client = PuterAI(username="user", password="pass")

# Method 2: Client-specific configuration
client = PuterAI(
    username="user",
    password="pass",
    timeout=120,           # 2 minute timeout
    max_retries=10,        # More retries
    rate_limit_requests=100  # Higher rate limit
)
```

### Error Handling

```python
from puter import PuterAI
from puter.exceptions import PuterAuthError, PuterAPIError

try:
    client = PuterAI(username="user", password="pass")
    client.login()

    response = client.chat("Hello!")
    print(response)

except PuterAuthError as e:
    print(f"Authentication failed: {e}")
    # Handle auth error (retry login, check credentials, etc.)

except PuterAPIError as e:
    print(f"API call failed: {e}")
    # Handle API error (retry, fallback, etc.)

except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other errors
```

## Rate Limiting

The SDK includes built-in rate limiting to respect API limits:

```python
from puter import PuterAI

# Create client with custom rate limiting
client = PuterAI(
    username="user",
    password="pass",
    rate_limit_requests=5,   # 5 requests
    rate_limit_period=10     # per 10 seconds
)

client.login()

# Requests will be automatically throttled
for i in range(10):
    response = client.chat(f"Question {i+1}")
    print(f"Response {i+1}: {response[:50]}...")
```

For more examples, see the [examples/](../examples/) directory.
