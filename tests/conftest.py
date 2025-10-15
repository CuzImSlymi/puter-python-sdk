"""Test configuration and fixtures for the Puter Python SDK."""

import pytest
from unittest.mock import Mock, patch
import json
import os


@pytest.fixture
def mock_requests():
    """Mock requests module for testing."""
    with patch('puter.ai.requests') as mock:
        yield mock


@pytest.fixture
def mock_aiohttp():
    """Mock aiohttp module for testing."""
    with patch('puter.ai.aiohttp') as mock:
        yield mock


@pytest.fixture
def sample_login_response():
    """Sample login response for testing."""
    return {
        "proceed": True,
        "token": "test_token_12345",
        "user_id": "test_user",
        "session_id": "test_session"
    }


@pytest.fixture
def sample_chat_response():
    """Sample chat response for testing."""
    return {
        "success": True,
        "result": {
            "message": {
                "content": "Hello! I'm an AI assistant. How can I help you today?"
            }
        }
    }


@pytest.fixture
def sample_models_data():
    """Sample models data for testing."""
    return {
        "gpt-4": "openai-completion",
        "claude-3": "claude",
        "gemini-pro": "google"
    }


@pytest.fixture
def puter_client():
    """Create a PuterAI client instance for testing."""
    from puter import PuterAI
    
    # Use test credentials
    client = PuterAI(username="test_user", password="test_password")
    return client


@pytest.fixture
def authenticated_client(puter_client, mock_requests, sample_login_response):
    """Create an authenticated PuterAI client for testing."""
    # Mock the login response
    mock_response = Mock()
    mock_response.json.return_value = sample_login_response
    mock_response.raise_for_status.return_value = None
    mock_requests.post.return_value = mock_response
    
    # Perform login
    puter_client.login()
    return puter_client


@pytest.fixture
def temp_models_file(tmp_path, sample_models_data):
    """Create a temporary models file for testing."""
    models_file = tmp_path / "available_models.json"
    with open(models_file, 'w') as f:
        json.dump(sample_models_data, f)
    return str(models_file)


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration before each test."""
    from puter.config import config
    
    # Store original values
    original_values = {}
    for attr in dir(config):
        if not attr.startswith('_') and not callable(getattr(config, attr)):
            original_values[attr] = getattr(config, attr)
    
    yield
    
    # Restore original values
    for attr, value in original_values.items():
        setattr(config, attr, value)


@pytest.fixture
def mock_throttler():
    """Mock the async throttler for testing."""
    with patch('puter.ai.Throttler') as mock:
        mock_instance = Mock()
        mock_instance.__aenter__ = Mock(return_value=mock_instance)
        mock_instance.__aexit__ = Mock(return_value=None)
        mock.return_value = mock_instance
        yield mock_instance


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as requiring authentication"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )


# Environment-based test skipping
def pytest_runtest_setup(item):
    """Skip tests based on environment variables."""
    if "integration" in item.keywords:
        if not os.getenv("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled (set RUN_INTEGRATION_TESTS=1 to enable)")
    
    if "network" in item.keywords:
        if not os.getenv("RUN_NETWORK_TESTS"):
            pytest.skip("Network tests disabled (set RUN_NETWORK_TESTS=1 to enable)")
    
    if "auth" in item.keywords:
        if not (os.getenv("PUTER_USERNAME") and os.getenv("PUTER_PASSWORD")):
            pytest.skip("Authentication tests require PUTER_USERNAME and PUTER_PASSWORD environment variables")