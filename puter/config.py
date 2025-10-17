"""Configuration settings for the Puter AI SDK."""

import os
from typing import Any, Dict


class PuterConfig:
    """Configuration class for Puter AI SDK."""

    def __init__(self):
        """Initialize configuration with default values."""
        # API Configuration
        self.api_base = os.getenv("PUTER_API_BASE", "https://api.puter.com")
        self.login_url = os.getenv("PUTER_LOGIN_URL", "https://puter.com/login")

        # Request Configuration
        self.timeout = int(os.getenv("PUTER_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("PUTER_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("PUTER_RETRY_DELAY", "1.0"))
        self.backoff_factor = float(os.getenv("PUTER_BACKOFF_FACTOR", "2.0"))

        # Rate Limiting
        self.rate_limit_requests = int(os.getenv("PUTER_RATE_LIMIT_REQUESTS", "10"))
        self.rate_limit_period = int(os.getenv("PUTER_RATE_LIMIT_PERIOD", "60"))

        # Default Headers
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://puter.com",
            "Referer": "https://puter.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }

    def update(self, **kwargs):
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not attr.startswith("_") and not callable(getattr(self, attr))
        }


# Global configuration instance
config = PuterConfig()
