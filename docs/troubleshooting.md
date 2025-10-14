# Troubleshooting Guide - Puter Python SDK

This guide helps you resolve common issues when using the Puter Python SDK.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Authentication Problems](#authentication-problems)
- [API Call Errors](#api-call-errors)
- [Performance Issues](#performance-issues)
- [Configuration Problems](#configuration-problems)
- [Common Error Messages](#common-error-messages)
- [Debugging Tips](#debugging-tips)
- [Getting Help](#getting-help)

## Installation Issues

### ImportError: No module named 'puter'

**Problem:** SDK not installed or not in Python path.

**Solutions:**
```bash
# Install the SDK
pip install puter-python-sdk

# Upgrade to latest version
pip install --upgrade puter-python-sdk

# Install in development mode
pip install -e .

# Check installation
python -c "import puter; print(puter.__version__)"
```

### ModuleNotFoundError: No module named 'aiohttp'

**Problem:** Missing dependencies for async functionality.

**Solutions:**
```bash
# Install missing dependencies
pip install aiohttp asyncio-throttle

# Or reinstall the SDK
pip uninstall puter-python-sdk
pip install puter-python-sdk
```

### Permission Errors During Installation

**Problem:** Insufficient permissions to install packages.

**Solutions:**
```bash
# Install for current user only
pip install --user puter-python-sdk

# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install puter-python-sdk
```

## Authentication Problems

### PuterAuthError: Username and password must be set

**Problem:** Missing credentials.

**Solutions:**
```python
# Method 1: Direct credentials
client = PuterAI(username="your_username", password="your_password")

# Method 2: Environment variables
import os
os.environ['PUTER_USERNAME'] = 'your_username'
os.environ['PUTER_PASSWORD'] = 'your_password'
client = PuterAI()

# Method 3: Check if credentials are set
if not os.getenv('PUTER_USERNAME'):
    print("Please set PUTER_USERNAME environment variable")
```

### PuterAuthError: Login failed. Please check your credentials.

**Problem:** Invalid username or password.

**Solutions:**
1. **Verify credentials** on [puter.com](https://puter.com)
2. **Check for typos** in username/password
3. **Try creating a new account** if needed
4. **Check network connectivity**

```python
# Test credentials manually
try:
    client = PuterAI(username="your_username", password="your_password")
    success = client.login()
    if success:
        print("✅ Login successful!")
    else:
        print("❌ Login failed - check credentials")
except Exception as e:
    print(f"❌ Error: {e}")
```

### Token Authentication Issues

**Problem:** Token-based authentication not working.

**Solutions:**
```python
# Check token validity
client = PuterAI(token="your_token")
try:
    response = client.chat("test")
    print("✅ Token is valid")
except PuterAuthError:
    print("❌ Token is invalid or expired")
    # Re-authenticate with username/password
```

## API Call Errors

### PuterAPIError: Request failed after X attempts

**Problem:** API calls consistently failing.

**Common causes:**
- Network connectivity issues
- API server temporarily down
- Rate limiting
- Invalid request format

**Solutions:**
```python
# Increase retry attempts and timeout
client = PuterAI(
    username="user",
    password="pass",
    timeout=60,        # Longer timeout
    max_retries=10,    # More retries
    retry_delay=2.0    # Longer delay between retries
)

# Check network connectivity
import requests
try:
    response = requests.get("https://api.puter.com", timeout=10)
    print(f"API server status: {response.status_code}")
except requests.RequestException as e:
    print(f"Network error: {e}")
```

### Empty or Invalid Responses

**Problem:** AI returns empty responses or error messages.

**Solutions:**
```python
# Check if prompt is appropriate
prompt = "Your question here"
if len(prompt.strip()) == 0:
    print("❌ Empty prompt")

# Try different models
models_to_try = ["gpt-4", "claude-3.5-sonnet", "gpt-3.5-turbo"]
for model in models_to_try:
    try:
        client.set_model(model)
        response = client.chat(prompt)
        if response and not response.startswith("No content"):
            print(f"✅ Success with {model}: {response[:100]}...")
            break
    except Exception as e:
        print(f"❌ {model} failed: {e}")
```

### Rate Limiting Issues

**Problem:** Too many requests causing errors.

**Solutions:**
```python
# Reduce rate limit
client = PuterAI(
    username="user",
    password="pass",
    rate_limit_requests=5,   # Fewer requests
    rate_limit_period=60     # per minute
)

# Add manual delays
import time
for prompt in prompts:
    response = client.chat(prompt)
    time.sleep(2)  # Wait 2 seconds between requests
```

## Performance Issues

### Slow Response Times

**Problem:** API calls taking too long.

**Solutions:**
```python
# Use async for concurrent requests
import asyncio

async def fast_processing():
    client = PuterAI(username="user", password="pass")
    await client.async_login()
    
    # Process multiple requests concurrently
    tasks = [client.async_chat(prompt) for prompt in prompts]
    responses = await asyncio.gather(*tasks)
    return responses

responses = asyncio.run(fast_processing())
```

### Memory Usage Issues

**Problem:** High memory usage with long conversations.

**Solutions:**
```python
# Clear chat history periodically
if len(client.chat_history) > 20:  # Keep only recent messages
    client.clear_chat_history()

# Or keep only last N messages
def trim_history(client, max_messages=10):
    if len(client.chat_history) > max_messages:
        client.chat_history = client.chat_history[-max_messages:]

# Use for each conversation
trim_history(client, 10)
```

## Configuration Problems

### Environment Variables Not Working

**Problem:** Environment variables not being read.

**Solutions:**
```python
# Check if environment variables are set
import os
print(f"Username: {os.getenv('PUTER_USERNAME', 'Not set')}")
print(f"Password: {os.getenv('PUTER_PASSWORD', 'Not set')}")

# Set environment variables in Python
os.environ['PUTER_USERNAME'] = 'your_username'
os.environ['PUTER_PASSWORD'] = 'your_password'

# Verify configuration loading
from puter import config
print(f"API Base: {config.api_base}")
print(f"Timeout: {config.timeout}")
```

### Configuration Not Taking Effect

**Problem:** Configuration changes not being applied.

**Solutions:**
```python
# Update global configuration
from puter import config
config.update(timeout=60, max_retries=5)

# Or use client-specific configuration
client = PuterAI(
    username="user",
    password="pass",
    timeout=60,
    max_retries=5
)

# Verify configuration
print(f"Client timeout: {config.timeout}")
```

## Common Error Messages

### "No content in AI response"

**Possible causes:**
- Model doesn't support the request format
- API response format changed
- Network issues during response parsing

**Solutions:**
```python
# Try different models
client.set_model("gpt-4")
response = client.chat("Hello")

# Check raw response (for debugging)
import requests
# Manual API call to debug response format
```

### "Not authenticated. Please login first."

**Causes:**
- Forgot to call `login()`
- Token expired
- Network issues during authentication

**Solutions:**
```python
# Always call login after initialization
client = PuterAI(username="user", password="pass")
client.login()  # Don't forget this!

# Check authentication status
try:
    client.chat("test")
    print("✅ Authenticated")
except PuterAuthError:
    print("❌ Not authenticated - calling login()")
    client.login()
```

### "Model not found" or set_model() returns False

**Causes:**
- Model name misspelled
- Model not available
- Model was removed from service

**Solutions:**
```python
# Check available models
models = client.get_available_models()
print(f"Available models: {len(models)}")

# Search for model
target_model = "gpt-4"
if target_model in models:
    client.set_model(target_model)
else:
    # Find similar models
    similar = [m for m in models if "gpt" in m.lower()]
    print(f"Similar models: {similar}")
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('puter')

# Your SDK code here
client = PuterAI(username="user", password="pass")
```

### Inspect Network Traffic

```python
import requests

# Create session to inspect requests
session = requests.Session()

# Add request/response hooks for debugging
def log_request(request):
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")

def log_response(response):
    print(f"Response: {response.status_code}")
    print(f"Content: {response.text[:200]}...")

# You can monkey-patch or use debugging proxies
```

### Test with Minimal Example

```python
# Minimal test case
from puter import PuterAI

def minimal_test():
    try:
        client = PuterAI(username="your_username", password="your_password")
        print("1. ✅ Client created")
        
        success = client.login()
        print(f"2. {'✅' if success else '❌'} Login: {success}")
        
        models = client.get_available_models()
        print(f"3. ✅ Models loaded: {len(models)}")
        
        response = client.chat("Hello")
        print(f"4. ✅ Chat response: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error at step: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run test
success = minimal_test()
print(f"Overall result: {'✅ PASS' if success else '❌ FAIL'}")
```

### Check System Information

```python
import sys
import platform

def system_info():
    print("System Information:")
    print(f"  Python version: {sys.version}")
    print(f"  Platform: {platform.platform()}")
    print(f"  Architecture: {platform.architecture()}")
    
    try:
        import puter
        print(f"  Puter SDK version: {puter.__version__}")
    except ImportError:
        print("  Puter SDK: Not installed")
    
    # Check dependencies
    deps = ['requests', 'aiohttp', 'asyncio_throttle']
    for dep in deps:
        try:
            __import__(dep)
            print(f"  {dep}: ✅ Installed")
        except ImportError:
            print(f"  {dep}: ❌ Missing")

system_info()
```

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Try the minimal test example** above
3. **Check the [examples](../examples/)** for similar use cases
4. **Search [existing issues](https://github.com/CuzImSlymi/puter-python-sdk/issues)**

### When Reporting Issues

Include this information:

```python
# System information
import sys, platform
import puter

print("=== System Information ===")
print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Puter SDK: {puter.__version__}")

# Error reproduction
print("\n=== Error Reproduction ===")
try:
    # Your minimal code that reproduces the error
    pass
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
```

### Support Channels

- **GitHub Issues**: [Report bugs](https://github.com/CuzImSlymi/puter-python-sdk/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/CuzImSlymi/puter-python-sdk/discussions)
- **Email**: justin@slymi.org for private inquiries

### Useful Resources

- [API Documentation](api.md)
- [Examples](../examples/)
- [Contributing Guide](../CONTRIBUTING.md)
- [Puter.js Documentation](https://puter.com/docs)

## Frequently Asked Questions

### Q: Can I use multiple models in the same conversation?

A: Yes, but each model switch creates a separate conversation context:

```python
client.chat("Hello")  # Using default model
client.set_model("gpt-4")  
client.chat("Continue conversation")  # GPT-4 sees full history

# To start fresh with new model:
client.clear_chat_history()
client.set_model("claude-3.5-sonnet")
client.chat("New conversation")  # Clean slate
```

### Q: How do I handle long conversations without hitting limits?

A: Manage conversation history strategically:

```python
def smart_history_management(client, new_prompt):
    # Keep only essential context
    if len(client.chat_history) > 20:
        # Keep first 2 and last 10 messages
        important_start = client.chat_history[:2]
        recent_context = client.chat_history[-10:]
        client.chat_history = important_start + recent_context
    
    return client.chat(new_prompt)
```

### Q: Is there a way to stream responses?

A: Currently, the SDK doesn't support streaming, but you can simulate it:

```python
import time

def simulate_streaming(response, delay=0.05):
    """Simulate streaming by printing response word by word."""
    words = response.split()
    for word in words:
        print(word, end=' ', flush=True)
        time.sleep(delay)
    print()  # New line at end

response = client.chat("Tell me a story")
simulate_streaming(response)
```

### Q: How do I save and restore conversations?

A: Use JSON serialization:

```python
import json
from datetime import datetime

# Save conversation
def save_conversation(client, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "model": client.current_model,
        "history": client.chat_history
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filename

# Load conversation
def load_conversation(client, filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    
    client.set_model(data["model"])
    client.chat_history = data["history"]
    
    return data["timestamp"]

# Usage
filename = save_conversation(client)
# Later...
timestamp = load_conversation(client, filename)
print(f"Restored conversation from {timestamp}")
```

Remember: When in doubt, start with the minimal test example and gradually add complexity to isolate the issue! 🔍