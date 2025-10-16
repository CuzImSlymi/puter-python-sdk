# Architecture Documentation - Puter Python SDK

This document explains the internal architecture and design decisions of the Puter Python SDK.

## Overview

The Puter Python SDK is designed as a lightweight, extensible wrapper around the Puter.js AI API. It provides both synchronous and asynchronous interfaces for accessing multiple AI models through a unified API.

## Design Principles

### 1. Simplicity
- **Minimal learning curve** - developers can start with basic usage
- **Sensible defaults** - works out of the box with minimal configuration
- **Clear API** - intuitive method names and parameters

### 2. Reliability
- **Robust error handling** - comprehensive exception hierarchy
- **Retry logic** - automatic retry with exponential backoff
- **Rate limiting** - built-in protection against API limits

### 3. Performance
- **Async support** - non-blocking operations for concurrent usage
- **Connection pooling** - efficient resource utilization
- **Configurable timeouts** - prevent hanging requests

### 4. Extensibility
- **Configuration system** - easily customizable behavior
- **Plugin-ready** - designed for future extensions
- **Model abstraction** - supports new models without code changes

## Core Components

### 1. PuterAI Class (`puter/ai.py`)

The main client class that handles all interactions with the Puter.js API.

```python
class PuterAI:
    def __init__(self, username, password, token, **config_overrides)
    def login(self) -> bool
    def async_login(self) -> bool
    def chat(self, prompt: str, model: Optional[str] = None) -> str
    def async_chat(self, prompt: str, model: Optional[str] = None) -> str
    def get_available_models(self) -> List[str]
    def set_model(self, model_name: str) -> bool
    def clear_chat_history(self)
```

**Key Features:**
- Maintains conversation history automatically
- Supports both sync and async operations
- Handles authentication and token management
- Provides model switching capabilities

### 2. Configuration System (`puter/config.py`)

Centralized configuration management with environment variable support.

```python
class PuterConfig:
    # API Configuration
    api_base: str
    login_url: str

    # Request Configuration
    timeout: int
    max_retries: int
    retry_delay: float
    backoff_factor: float

    # Rate Limiting
    rate_limit_requests: int
    rate_limit_period: int

    # Default Headers
    headers: Dict[str, str]
```

**Features:**
- Environment variable integration
- Runtime configuration updates
- Client-specific overrides
- Validation and type safety

### 3. Exception Hierarchy (`puter/exceptions.py`)

Structured error handling for different failure scenarios.

```
PuterError (Base)
├── PuterAuthError (Authentication failures)
└── PuterAPIError (API call failures)
```

### 4. Model Registry (`puter/available_models.json`)

Static registry of supported AI models and their configurations.

```json
{
  "gpt-4": "openai-completion",
  "claude-3.5-sonnet": "claude",
  "gemini-pro": "google-completion"
}
```

## Request Flow

### Synchronous Flow

```
User Request
    ↓
PuterAI.chat()
    ↓
_retry_request()
    ↓
Authentication Check
    ↓
Request Building
    ↓
HTTP Request (with retries)
    ↓
Response Parsing
    ↓
History Update
    ↓
Return Response
```

### Asynchronous Flow

```
User Request
    ↓
PuterAI.async_chat()
    ↓
Rate Limiter (Throttler)
    ↓
_async_retry_request()
    ↓
Authentication Check
    ↓
Async HTTP Request
    ↓
Response Parsing
    ↓
History Update
    ↓
Return Response
```

## Error Handling Strategy

### 1. Retry Logic

The SDK implements exponential backoff for transient failures:

```python
for attempt in range(max_retries + 1):
    try:
        response = make_request()
        return response
    except TransientError:
        if attempt < max_retries:
            delay = retry_delay * (backoff_factor ** attempt)
            time.sleep(delay)
        else:
            raise
```

### 2. Exception Mapping

Different error types are mapped to appropriate exceptions:

- **Network errors** → `PuterAPIError`
- **Authentication failures** → `PuterAuthError`
- **Invalid responses** → `PuterAPIError`
- **Timeouts** → `PuterAPIError`

### 3. Graceful Degradation

The SDK attempts to provide useful information even when things go wrong:

- **Debug information** in error messages
- **Partial responses** when possible
- **Fallback mechanisms** for configuration

## Rate Limiting Implementation

### Algorithm

Uses token bucket algorithm via `asyncio-throttle`:

```python
self._throttler = Throttler(
    rate_limit=requests_per_period,
    period=period_in_seconds
)

async with self._throttler:
    # Make API request
    pass
```

### Benefits

- **Prevents API abuse** - respects service limits
- **Smooth traffic** - distributes requests over time
- **Configurable** - adjustable per use case

## Authentication Flow

### Initial Authentication

```
1. User provides credentials
2. SDK makes login request to Puter.js
3. Receives authentication token
4. Stores token for subsequent requests
5. Adds token to request headers
```

### Token Management

- **Automatic inclusion** in API requests
- **No automatic refresh** - user must handle expiration
- **Secure storage** - only in memory, not persisted

## Conversation Management

### History Structure

```python
chat_history = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"},
    {"role": "assistant", "content": "I'm doing well!"}
]
```

### Memory Management

- **Automatic growth** - history grows with conversation
- **Manual cleanup** - `clear_chat_history()` method
- **No automatic trimming** - user controls memory usage

## Model Abstraction

### Driver System

Different AI providers use different APIs, abstracted via drivers:

```python
def _get_driver_for_model(self, model_name: str) -> str:
    return self.available_models.get(model_name, "openai-completion")
```

### Request Format

Unified request format regardless of underlying model:

```python
payload = {
    "interface": "puter-chat-completion",
    "driver": driver,
    "method": "complete",
    "args": {
        "messages": messages,
        "model": model,
        "temperature": 0.7,
        "max_tokens": 4096
    }
}
```

## Performance Considerations

### Async Architecture

- **Non-blocking I/O** - uses aiohttp for async requests
- **Concurrent requests** - multiple operations in parallel
- **Resource pooling** - efficient connection reuse

### Memory Optimization

- **Lazy loading** - models loaded on demand
- **Minimal dependencies** - only essential packages
- **Efficient serialization** - optimized JSON handling

### Network Optimization

- **Connection reuse** - HTTP keep-alive
- **Compression** - gzip encoding when available
- **Timeouts** - prevents hanging connections

## Security Considerations

### Credential Handling

- **Environment variables** - secure credential storage
- **No persistence** - credentials not saved to disk
- **Memory safety** - tokens cleared on client destruction

### Request Security

- **HTTPS only** - all API calls encrypted
- **Header sanitization** - safe header construction
- **Input validation** - parameter checking

## Testing Strategy

### Test Categories

1. **Unit Tests** - individual method testing
2. **Integration Tests** - end-to-end API flows
3. **Async Tests** - concurrent operation validation
4. **Error Tests** - failure scenario handling

### Test Structure

```
tests/
├── test_auth.py          # Authentication tests
├── test_chat.py          # Chat functionality
├── test_config.py        # Configuration tests
├── test_errors.py        # Error handling tests
└── test_async.py         # Async operation tests
```

## Future Enhancements

### Planned Features

1. **Streaming responses** - real-time response chunks
2. **Function calling** - structured AI interactions
3. **Plugin system** - extensible functionality
4. **Caching layer** - response caching for efficiency
5. **Metrics collection** - usage analytics

### Extensibility Points

- **Custom drivers** - support for new AI providers
- **Middleware system** - request/response processing
- **Event hooks** - lifecycle event handling
- **Custom serializers** - alternative data formats

## Dependencies

### Core Dependencies

- **requests** - HTTP client for sync operations
- **aiohttp** - HTTP client for async operations
- **asyncio-throttle** - rate limiting implementation

### Development Dependencies

- **pytest** - testing framework
- **black** - code formatting
- **flake8** - linting
- **mypy** - type checking

## Deployment Considerations

### Installation

- **PyPI distribution** - standard pip installation
- **Minimal dependencies** - fast installation
- **Cross-platform** - Windows, macOS, Linux support

### Configuration

- **Environment variables** - production configuration
- **Config files** - structured configuration (future)
- **Runtime updates** - dynamic configuration changes

### Monitoring

- **Error logging** - structured error information
- **Performance metrics** - request timing and success rates
- **Usage tracking** - API call statistics (future)

This architecture provides a solid foundation for the current functionality while remaining flexible enough to support future enhancements and use cases.
