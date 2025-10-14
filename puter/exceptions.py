class PuterError(Exception):
    """Base exception for Puter.js API errors."""
    pass

class PuterAuthError(PuterError):
    """Raised when authentication with Puter.js fails."""
    pass

class PuterAPIError(PuterError):
    """Raised when an API call to Puter.js fails."""
    pass

