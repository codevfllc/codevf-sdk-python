from __future__ import annotations

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


class BadRequestError(APIError):
    """Raised when the server rejects a request with HTTP 400."""
    pass


class InvalidModeError(APIError):
    """Raised when the provided mode is invalid."""
    pass


class InvalidTagError(APIError):
    """Raised when the provided tagId is unknown or inactive."""
    pass


class InvalidMetadataError(APIError):
    """Raised when metadata contains disallowed keys or nested values."""
    pass


class MaxCreditsExceededError(APIError):
    """Raised when the maxCredits field is insufficient after multipliers."""
    pass


class AttachmentLimitExceededError(APIError):
    """Raised when more than five attachments are submitted."""
    pass


class AttachmentTooLargeError(APIError):
    """Raised when an attachment exceeds the supported size limits."""
    pass


class IdempotencyConflictError(APIError):
    """Raised when an idempotency key is re-used by a different API key."""
    pass


class InsufficientCreditsError(APIError):
    """Raised when the account lacks enough credits for the requested task."""
    pass


class InvalidSchemaError(APIError):
    """Raised when the provided responseSchema is invalid JSON Schema."""
    pass


class PayloadTooLargeError(APIError):
    """Raised when the JSON body exceeds 150KB."""
    pass
