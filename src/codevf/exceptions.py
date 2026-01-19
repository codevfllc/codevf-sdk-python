from typing import Optional, Any

class CodeVFError(Exception):
    """Base exception for all CodeVF SDK errors."""
    pass


class APIConnectionError(CodeVFError):
    """Raised when communication with the API fails (network issues)."""
    pass


class APIError(CodeVFError):
    """Raised when the API returns a non-success status code."""

    def __init__(self, message: str, status_code: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthenticationError(APIError):
    """Raised when API Key is invalid or missing (401/403)."""
    pass


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded (429)."""
    pass


class ServerError(APIError):
    """Raised when the API encounters an internal error (5xx)."""
    pass
