"""Puter Python SDK for accessing free AI models through Puter.js."""

from .ai import PuterAI
from .config import PuterConfig
from .config import config
from .exceptions import PuterAPIError
from .exceptions import PuterAuthError
from .exceptions import PuterError

__version__ = "0.5.0"
__all__ = [
    "PuterAI",
    "PuterError",
    "PuterAuthError",
    "PuterAPIError",
    "config",
    "PuterConfig",
]
