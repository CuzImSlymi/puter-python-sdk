# Puter Python SDK

A lightweight Python SDK for interacting with Puter.js AI chat completion services.

## Features

- **Dynamic Model Fetching**: Retrieves available models directly from the Puter API.
- **Unified Driver Routing**: Uses the unified `ai-chat` endpoint.
- **Intelligent Model Resolution**: Automatically maps short names (e.g., `claude-fable-5`) to full API paths.
- **Session History**: Context window is managed automatically.

## Installation

```bash
pip install .
```

## Quick Start

Run the interactive test CLI:

```bash
python test_puter.py
```

### Basic Chat Example

```python
from puter import PuterAI

# Initialize and login
client = PuterAI(username="your_username", password="your_password")
client.login()

# Switch to a specific model
client.set_model("claude-fable-5")

# Send messages (history is handled automatically)
response = client.chat("Hello!")
print(f"AI: {response}")
```

### Multimodal Chat Example

```python
# Send a prompt along with local image paths or URLs
response = client.chat(
    prompt="Describe this image",
    images=["path/to/image.png"]
)
print(response)
```

## Error Handling

Custom exceptions:
- `PuterAuthError`: Authentication failures.
- `PuterAPIError`: API or rate-limit failures (e.g., 402 balance exhausted).

## License

MIT
