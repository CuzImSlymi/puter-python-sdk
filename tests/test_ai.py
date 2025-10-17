"""Tests for the PuterAI class."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from puter import PuterAI, PuterAPIError, PuterAuthError


class TestPuterAIInitialization:
    """Test PuterAI client initialization."""

    def test_init_with_credentials(self):
        """Test initialization with username and password."""
        client = PuterAI(username="test_user", password="test_pass")
        assert client._username == "test_user"
        assert client._password == "test_pass"
        assert client._token is None
        assert client.current_model == "claude-opus-4"
        assert client.chat_history == []

    def test_init_with_token(self):
        """Test initialization with existing token."""
        client = PuterAI(token="existing_token")
        assert client is not None  # Use the client
        assert client._token == "existing_token"
        assert client._username is None
        assert client._password is None

    def test_init_with_config_overrides(self):
        """Test initialization with configuration overrides."""
        client = PuterAI(username="test", password="test", timeout=60, max_retries=5)
        assert client is not None  # Use the client to avoid unused variable
        from puter.config import config

        assert config.timeout == 60
        assert config.max_retries == 5

    def test_available_models_loaded(self, puter_client):
        """Test that available models are loaded on initialization."""
        assert hasattr(puter_client, "available_models")
        assert isinstance(puter_client.available_models, dict)
        assert len(puter_client.available_models) > 0


class TestPuterAIAuthentication:
    """Test PuterAI authentication methods."""

    def test_login_success(self, puter_client, mock_requests, sample_login_response):
        """Test successful login."""
        mock_response = Mock()
        mock_response.json.return_value = sample_login_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        result = puter_client.login()

        assert result is True
        assert puter_client._token == "test_token_12345"
        mock_requests.post.assert_called_once()

    def test_login_failure_invalid_credentials(self, puter_client, mock_requests):
        """Test login failure with invalid credentials."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "proceed": False,
            "error": "Invalid credentials",
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        with pytest.raises(PuterAuthError, match="Login failed"):
            puter_client.login()

    def test_login_no_credentials(self):
        """Test login without credentials raises error."""
        client = PuterAI()
        with pytest.raises(PuterAuthError, match="Username and password must be set"):
            client.login()

    def test_login_network_error(self, puter_client, mock_requests):
        """Test login with network error."""
        mock_requests.post.side_effect = Exception("Network error")

        with pytest.raises(PuterAuthError, match="Login error"):
            puter_client.login()

    @pytest.mark.skip(reason="Async test mocking issues - needs fix")
    @pytest.mark.asyncio
    async def test_async_login_success(self, puter_client, sample_login_response):
        """Test successful async login."""
        with patch("puter.ai.aiohttp.ClientSession") as mock_session_class:
            # Create mock response
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=sample_login_response)
            mock_response.raise_for_status = AsyncMock()

            # Create mock session
            mock_session = AsyncMock()
            mock_session.request = AsyncMock()
            mock_session.request.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.request.return_value.__aexit__ = AsyncMock(return_value=None)

            # Setup session class mock
            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await puter_client.async_login()

            assert result is True
            assert puter_client._token == "test_token_12345"


class TestPuterAIChat:
    """Test PuterAI chat functionality."""

    def test_chat_success(
        self, authenticated_client, mock_requests, sample_chat_response
    ):
        """Test successful chat interaction."""
        mock_response = Mock()
        mock_response.json.return_value = sample_chat_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        response = authenticated_client.chat("Hello!")

        assert response == "Hello! I'm an AI assistant. How can I help you today?"
        assert len(authenticated_client.chat_history) == 2  # User message + AI response

    def test_chat_not_authenticated(self, puter_client):
        """Test chat without authentication raises error."""
        with pytest.raises(PuterAuthError, match="Not authenticated"):
            puter_client.chat("Hello!")

    def test_chat_with_specific_model(
        self, authenticated_client, mock_requests, sample_chat_response
    ):
        """Test chat with a specific model."""
        mock_response = Mock()
        mock_response.json.return_value = sample_chat_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        response = authenticated_client.chat("Hello!", model="gpt-4")

        assert response is not None
        # Verify the correct model was used in the request
        call_args = mock_requests.post.call_args
        payload = call_args[1]["json"]
        assert payload["args"]["model"] == "gpt-4"

    def test_chat_api_error(self, authenticated_client, mock_requests):
        """Test chat with API error."""
        mock_requests.post.side_effect = Exception("API Error")

        with pytest.raises(PuterAPIError):
            authenticated_client.chat("Hello!")

    @pytest.mark.skip(reason="Async test mocking issues - needs fix")
    @pytest.mark.asyncio
    async def test_async_chat_success(self, authenticated_client, sample_chat_response):
        """Test successful async chat."""
        with patch("puter.ai.aiohttp.ClientSession") as mock_session_class:
            # Create mock response
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=sample_chat_response)
            mock_response.raise_for_status = AsyncMock()

            # Create mock session
            mock_session = AsyncMock()
            mock_session.request = AsyncMock()
            mock_session.request.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.request.return_value.__aexit__ = AsyncMock(return_value=None)

            # Setup session class mock
            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            response = await authenticated_client.async_chat("Hello!")

            assert response == "Hello! I'm an AI assistant. How can I help you today?"


class TestPuterAIModels:
    """Test PuterAI model management."""

    def test_get_available_models(self, puter_client):
        """Test getting available models."""
        models = puter_client.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(model, str) for model in models)

    def test_set_model_success(self, puter_client):
        """Test successfully setting a model."""
        available_models = puter_client.get_available_models()
        if available_models:
            model_name = available_models[0]
            result = puter_client.set_model(model_name)
            assert result is True
            assert puter_client.current_model == model_name

    def test_set_model_invalid(self, puter_client):
        """Test setting an invalid model."""
        result = puter_client.set_model("invalid-model-name")
        assert result is False
        assert puter_client.current_model == "claude-opus-4"  # Should remain unchanged

    def test_get_driver_for_model(self, puter_client):
        """Test getting driver for a model."""
        # Test with known model
        driver = puter_client._get_driver_for_model("claude-opus-4")
        assert driver == "claude"

        # Test with unknown model (should return default)
        driver = puter_client._get_driver_for_model("unknown-model")
        assert driver == "openai-completion"


class TestPuterAIChatHistory:
    """Test PuterAI chat history management."""

    def test_clear_chat_history(self, authenticated_client):
        """Test clearing chat history."""
        # Add some mock history
        authenticated_client.chat_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        authenticated_client.clear_chat_history()
        assert authenticated_client.chat_history == []

    def test_chat_history_accumulation(
        self, authenticated_client, mock_requests, sample_chat_response
    ):
        """Test that chat history accumulates correctly."""
        mock_response = Mock()
        mock_response.json.return_value = sample_chat_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        # Send multiple messages
        authenticated_client.chat("First message")
        authenticated_client.chat("Second message")

        assert (
            len(authenticated_client.chat_history) == 4
        )  # 2 user + 2 assistant messages
        assert authenticated_client.chat_history[0]["role"] == "user"
        assert authenticated_client.chat_history[1]["role"] == "assistant"


class TestPuterAIRetryLogic:
    """Test PuterAI retry logic and error handling."""

    def test_retry_on_network_error(
        self, puter_client, mock_requests, sample_login_response
    ):
        """Test retry logic on network errors."""
        # First call fails, second succeeds
        mock_response = Mock()
        mock_response.json.return_value = sample_login_response
        mock_response.raise_for_status.return_value = None

        mock_requests.post.side_effect = [
            Exception("Network error"),  # First attempt fails
            mock_response,  # Second attempt succeeds
        ]

        result = puter_client.login()
        assert result is True
        assert mock_requests.post.call_count == 2

    def test_retry_exhausted(self, puter_client, mock_requests):
        """Test behavior when all retries are exhausted."""
        mock_requests.post.side_effect = Exception("Persistent error")

        with pytest.raises(PuterAuthError, match="Login error"):
            puter_client.login()


class TestPuterAIConfiguration:
    """Test PuterAI configuration handling."""

    def test_auth_headers(self, authenticated_client):
        """Test authentication headers generation."""
        headers = authenticated_client._get_auth_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_12345"
        assert "Content-Type" in headers

    def test_auth_headers_not_authenticated(self, puter_client):
        """Test auth headers when not authenticated."""
        with pytest.raises(PuterAuthError, match="Not authenticated"):
            puter_client._get_auth_headers()
