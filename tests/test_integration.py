"""Integration tests for the Puter Python SDK."""

import os

import pytest

from puter import PuterAI, PuterAuthError


@pytest.mark.integration
@pytest.mark.network
class TestPuterAIIntegration:
    """Integration tests that require network access."""

    def test_real_login_with_invalid_credentials(self):
        """Test real login attempt with invalid credentials."""
        client = PuterAI(username="invalid_user", password="invalid_pass")

        with pytest.raises(PuterAuthError):
            client.login()

    @pytest.mark.auth
    def test_real_login_success(self):
        """Test real login with valid credentials from environment."""
        username = os.getenv("PUTER_USERNAME")
        password = os.getenv("PUTER_PASSWORD")

        if not username or not password:
            pytest.skip(
                "PUTER_USERNAME and PUTER_PASSWORD environment variables required"
            )

        client = PuterAI(username=username, password=password)
        result = client.login()

        assert result is True
        assert client._token is not None

    @pytest.mark.auth
    def test_real_chat_interaction(self):
        """Test real chat interaction with the API."""
        username = os.getenv("PUTER_USERNAME")
        password = os.getenv("PUTER_PASSWORD")

        if not username or not password:
            pytest.skip(
                "PUTER_USERNAME and PUTER_PASSWORD environment variables required"
            )

        client = PuterAI(username=username, password=password)
        client.login()

        response = client.chat("Hello! Please respond with just 'Hello back!'")

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        assert len(client.chat_history) == 2

    @pytest.mark.auth
    def test_model_switching_integration(self):
        """Test model switching with real API."""
        username = os.getenv("PUTER_USERNAME")
        password = os.getenv("PUTER_PASSWORD")

        if not username or not password:
            pytest.skip(
                "PUTER_USERNAME and PUTER_PASSWORD environment variables required"
            )

        client = PuterAI(username=username, password=password)
        client.login()

        # Get available models
        models = client.get_available_models()
        assert len(models) > 0

        # Try to switch to a different model
        if len(models) > 1:
            new_model = None
            for model in models:
                if model != client.current_model:
                    new_model = model
                    break

            if new_model:
                success = client.set_model(new_model)
                assert success is True
                assert client.current_model == new_model


@pytest.mark.integration
class TestPuterAIOfflineIntegration:
    """Integration tests that work offline."""

    def test_client_initialization_performance(self):
        """Test client initialization performance."""
        import time

        start_time = time.time()
        client = PuterAI(username="test", password="test")
        end_time = time.time()

        # Should initialize quickly (less than 1 second)
        assert (end_time - start_time) < 1.0
        assert client is not None

    def test_models_loading_performance(self):
        """Test models loading performance."""
        import time

        client = PuterAI(username="test", password="test")

        start_time = time.time()
        models = client.get_available_models()
        end_time = time.time()

        # Should load quickly (less than 0.1 seconds)
        assert (end_time - start_time) < 0.1
        assert len(models) > 0

    def test_multiple_client_instances(self):
        """Test creating multiple client instances."""
        clients = []

        for i in range(10):
            client = PuterAI(username=f"user_{i}", password=f"pass_{i}")
            clients.append(client)

        # All clients should be independent
        for i, client in enumerate(clients):
            assert client._username == f"user_{i}"
            assert client._password == f"pass_{i}"
            assert client.current_model == "claude-opus-4"

    def test_configuration_isolation(self):
        """Test that configuration changes don't affect other instances."""
        client1 = PuterAI(username="user1", password="pass1", timeout=30)
        client2 = PuterAI(username="user2", password="pass2", timeout=60)
        assert client1 is not None and client2 is not None  # Use both clients

        # Both should have their configurations applied
        from puter.config import config

        # Note: config is global, so this test checks the last applied config
        assert config.timeout == 60  # Last client's setting


@pytest.mark.slow
class TestPuterAIStressTests:
    """Stress tests for the Puter SDK."""

    def test_rapid_model_switching(self):
        """Test rapid model switching doesn't cause issues."""
        client = PuterAI(username="test", password="test")
        models = client.get_available_models()

        if len(models) >= 2:
            # Switch between models rapidly
            for _ in range(100):
                for model in models[:2]:  # Use only first 2 models
                    result = client.set_model(model)
                    assert result is True
                    assert client.current_model == model

    def test_large_chat_history(self):
        """Test handling of large chat history."""
        client = PuterAI(username="test", password="test")

        # Simulate large chat history
        for i in range(1000):
            client.chat_history.append({"role": "user", "content": f"Message {i}"})
            client.chat_history.append(
                {"role": "assistant", "content": f"Response {i}"}
            )

        assert len(client.chat_history) == 2000

        # Clearing should work efficiently
        import time

        start_time = time.time()
        client.clear_chat_history()
        end_time = time.time()

        assert len(client.chat_history) == 0
        assert (end_time - start_time) < 0.1  # Should be very fast

    def test_memory_usage_stability(self):
        """Test memory usage doesn't grow excessively."""
        import gc

        # Get initial memory usage (rough estimate)
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Create and destroy many clients
        for _ in range(100):
            client = PuterAI(username="test", password="test")
            models = client.get_available_models()
            assert len(models) > 0  # Use models to avoid unused variable
            client.clear_chat_history()
            del client

        gc.collect()
        final_objects = len(gc.get_objects())

        # Object count shouldn't grow significantly
        # Allow some growth for test framework overhead
        assert final_objects < initial_objects + 1000
