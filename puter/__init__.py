"""Puter Python SDK for accessing free AI models through Puter.js."""

from .ai import PuterAI
from .config import PuterConfig, config
from .exceptions import PuterAPIError, PuterAuthError, PuterError

__version__ = "0.5.0"
__all__ = [
    "PuterAI",
    "PuterError",
    "PuterAuthError",
    "PuterAPIError",
    "config",
    "PuterConfig",
]
