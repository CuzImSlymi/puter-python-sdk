"""Tests for the configuration module."""

import os
from unittest.mock import patch

from puter.config import PuterConfig, config


class TestPuterConfig:
    """Test PuterConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        cfg = PuterConfig()

        assert cfg.api_base == "https://api.puter.com"
        assert cfg.login_url == "https://puter.com/login"
        assert cfg.timeout == 30
        assert cfg.max_retries == 3
        assert cfg.retry_delay == 1.0
        assert cfg.backoff_factor == 2.0
        assert cfg.rate_limit_requests == 10
        assert cfg.rate_limit_period == 60
        assert isinstance(cfg.headers, dict)

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "PUTER_API_BASE": "https://custom.api.com",
                "PUTER_TIMEOUT": "60",
                "PUTER_MAX_RETRIES": "5",
                "PUTER_RETRY_DELAY": "2.0",
                "PUTER_BACKOFF_FACTOR": "3.0",
                "PUTER_RATE_LIMIT_REQUESTS": "20",
                "PUTER_RATE_LIMIT_PERIOD": "120",
            },
        ):
            cfg = PuterConfig()

            assert cfg.api_base == "https://custom.api.com"
            assert cfg.timeout == 60
            assert cfg.max_retries == 5
            assert cfg.retry_delay == 2.0
            assert cfg.backoff_factor == 3.0
            assert cfg.rate_limit_requests == 20
            assert cfg.rate_limit_period == 120

    def test_update_method(self):
        """Test configuration update method."""
        cfg = PuterConfig()
        # original_timeout = cfg.timeout

        cfg.update(timeout=120, max_retries=10)

        assert cfg.timeout == 120
        assert cfg.max_retries == 10
        # Other values should remain unchanged
        assert cfg.api_base == "https://api.puter.com"

    def test_update_invalid_attribute(self):
        """Test update with invalid attribute (should be ignored)."""
        cfg = PuterConfig()

        # This should not raise an error, but should be ignored
        cfg.update(invalid_attribute="test")

        # Should not create the attribute
        assert not hasattr(cfg, "invalid_attribute")

    def test_to_dict_method(self):
        """Test conversion to dictionary."""
        cfg = PuterConfig()
        cfg_dict = cfg.to_dict()

        assert isinstance(cfg_dict, dict)
        assert "api_base" in cfg_dict
        assert "timeout" in cfg_dict
        assert "headers" in cfg_dict
        # Private attributes and methods should not be included
        assert not any(key.startswith("_") for key in cfg_dict.keys())

    def test_headers_structure(self):
        """Test that headers have the expected structure."""
        cfg = PuterConfig()

        assert isinstance(cfg.headers, dict)
        assert "Accept" in cfg.headers
        assert "User-Agent" in cfg.headers
        assert "Origin" in cfg.headers
        assert "Referer" in cfg.headers


class TestGlobalConfig:
    """Test the global config instance."""

    def test_global_config_exists(self):
        """Test that global config instance exists."""
        assert config is not None
        assert isinstance(config, PuterConfig)

    def test_global_config_modification(self):
        """Test modifying global config."""
        original_timeout = config.timeout

        try:
            config.update(timeout=999)
            assert config.timeout == 999
        finally:
            # Reset to original value
            config.update(timeout=original_timeout)

    def test_config_immutable_during_import(self):
        """Test that config behaves consistently during imports."""
        # Import the config again
        from puter.config import config as config2

        # Should be the same instance
        assert config is config2
        assert config.timeout == config2.timeout
