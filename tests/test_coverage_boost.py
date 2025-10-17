"""Additional tests to boost code coverage."""

import json
import os
from unittest.mock import Mock, patch

import pytest

from puter import PuterAI, PuterAPIError, PuterAuthError


class TestCoverageBoost:
    """Additional tests to improve code coverage."""

    def test_ai_init_with_all_params(self):
        """Test PuterAI initialization with all parameters."""
        client = PuterAI(
            username="test",
            password="test",
            token="existing_token",
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
            backoff_factor=3.0,
        )
        assert client._username == "test"
        assert client._password == "test"
        assert client._token == "existing_token"

    def test_models_file_loading(self):
        """Test models file loading logic."""
        client = PuterAI(username="test", password="test")
        # Test the models are loaded from file
        assert hasattr(client, "available_models")
        assert isinstance(client.available_models, dict)

    def test_get_driver_for_unknown_model(self):
        """Test driver selection for unknown models."""
        client = PuterAI(username="test", password="test")
        driver = client._get_driver_for_model("completely-unknown-model")
        assert driver == "openai-completion"  # Default driver

    def test_clear_chat_history_empty(self):
        """Test clearing already empty chat history."""
        client = PuterAI(username="test", password="test")
        assert client.chat_history == []
        client.clear_chat_history()
        assert client.chat_history == []

    def test_auth_headers_generation(self):
        """Test auth headers generation with token."""
        client = PuterAI(username="test", password="test")
        client._token = "test_token_123"
        headers = client._get_auth_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_123"
        assert headers["Content-Type"] == "application/json"

    def test_set_model_with_same_model(self):
        """Test setting the same model that's already active."""
        client = PuterAI(username="test", password="test")
        current_model = client.current_model
        result = client.set_model(current_model)
        assert result is True
        assert client.current_model == current_model

    def test_login_with_missing_credentials(self):
        """Test login with only username or password."""
        client = PuterAI(username="test", password=None)
        with pytest.raises(PuterAuthError):
            client.login()

        client = PuterAI(username=None, password="test")
        with pytest.raises(PuterAuthError):
            client.login()

    @patch("puter.ai.requests.post")
    def test_login_retry_logic(self, mock_post):
        """Test login retry logic on failure."""
        client = PuterAI(username="test", password="test")

        # First call fails, second succeeds
        mock_response = Mock()
        mock_response.json.return_value = {
            "proceed": True,
            "token": "test_token",
        }
        mock_response.raise_for_status.return_value = None

        mock_post.side_effect = [
            Exception("Network error"),  # First attempt fails
            mock_response,  # Second attempt succeeds
        ]

        result = client.login()
        assert result is True
        assert mock_post.call_count == 2

    @patch("puter.ai.requests.post")
    def test_chat_error_handling(self, mock_post):
        """Test chat error handling."""
        client = PuterAI(username="test", password="test")
        client._token = "test_token"

        # Simulate API error
        mock_post.side_effect = Exception("API Error")

        with pytest.raises(PuterAPIError):
            client.chat("Hello")

    def test_available_models_json_file_path(self):
        """Test that the models JSON file exists."""
        models_file = os.path.join(
            os.path.dirname(__file__), "..", "puter", "available_models.json"
        )
        assert os.path.exists(models_file), "Models file should exist"

        with open(models_file) as f:
            models_data = json.load(f)

        assert isinstance(models_data, dict)
        assert len(models_data) > 0

    def test_config_update_in_init(self):
        """Test that config is updated during initialization."""
        from puter.config import config

        original_timeout = config.timeout

        try:
            client = PuterAI(username="test", password="test", timeout=999)
            assert client is not None  # Use the client
            assert config.timeout == 999
        finally:
            config.update(timeout=original_timeout)

    def test_models_list_conversion(self):
        """Test models list conversion."""
        client = PuterAI(username="test", password="test")
        models_list = client.get_available_models()
        assert isinstance(models_list, list)
        assert len(models_list) > 0
        assert all(isinstance(model, str) for model in models_list)

    @patch("puter.ai.requests.post")
    def test_login_with_invalid_response(self, mock_post):
        """Test login with invalid JSON response."""
        client = PuterAI(username="test", password="test")

        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(PuterAuthError):
            client.login()

    def test_token_only_initialization(self):
        """Test initialization with token only."""
        client = PuterAI(token="existing_token_123")
        assert client._token == "existing_token_123"
        assert client._username is None
        assert client._password is None
