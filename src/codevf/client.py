import logging
import os
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import __version__
from .exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    AttachmentLimitExceededError,
    AttachmentTooLargeError,
    BadRequestError,
    IdempotencyConflictError,
    InsufficientCreditsError,
    InvalidMetadataError,
    InvalidModeError,
    InvalidTagError,
    MaxCreditsExceededError,
    NotFoundError,
    PayloadTooLargeError,
    RateLimitError,
    ServerError,
)

from .resources.credits import Credits
from .resources.projects import Projects
from .resources.tags import Tags
from .resources.tasks import Tasks

logger = logging.getLogger(__name__)

ERROR_CODE_EXCEPTION_MAP: Mapping[str, type[APIError]] = {
    "invalid_mode": InvalidModeError,
    "invalid_tag": InvalidTagError,
    "invalid_metadata": InvalidMetadataError,
    "max_credits_exceeded": MaxCreditsExceededError,
    "attachment_limit_exceeded": AttachmentLimitExceededError,
    "attachment_too_large": AttachmentTooLargeError,
    "idempotency_conflict": IdempotencyConflictError,
    "insufficient_credits": InsufficientCreditsError,
    "token_expired": AuthenticationError,
    "rate_limit_exceeded": RateLimitError,
}


class CodeVFClient:
    """
    Synchronous client for the CodeVF API.
    """

    DEFAULT_BASE_URL = "https://codevf.com/api/v1/"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """
        Initialize the CodeVF Client.

        Args:
            api_key: The API key for authentication. If not provided,
                     looks for CODEVF_API_KEY environment variable.
            base_url: The base URL for the API. Defaults to production URL.
            timeout: Request timeout in seconds.
            max_retries: Number of retries for transient errors (502, 503, 504).
        """
        self.api_key = api_key or os.environ.get("CODEVF_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key must be provided via argument or CODEVF_API_KEY environment variable."
            )

        self.base_url = base_url or self.DEFAULT_BASE_URL
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.timeout = timeout
        self.session = requests.Session()
        self._configure_session(max_retries)

        # Initialize resources
        self.projects = Projects(self)
        self.tasks = Tasks(self)
        self.credits = Credits(self)
        self.tags = Tags(self)

    def _configure_session(self, max_retries: int) -> None:
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": f"codevf-python-sdk/{__version__}",
        })

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            data = response.json() if response.content else None
        except ValueError:
            data = response.text

        logger.debug(f"Response: {response.status_code} - {data}")

        if 200 <= response.status_code < 300:
            return data

        message, code, status = self._extract_error_payload(data, response.status_code)
        exc_class = self._resolve_exception_class(status, code)
        raise exc_class(message, status, data)

    @staticmethod
    def _extract_error_payload(data: Any, fallback_status: int) -> tuple[str, Optional[str], int]:
        message = f"API request failed with status {fallback_status}"
        error_code: Optional[str] = None
        status = fallback_status

        if isinstance(data, dict):
            error_value = data.get("error")
            if isinstance(error_value, dict):
                error_code = error_value.get("code")
                message = error_value.get("message", message)
                status = error_value.get("status", fallback_status) or fallback_status

            elif isinstance(error_value, str):
                message = error_value
                status = data.get("status", fallback_status) or fallback_status

            elif "message" in data:
                message = data["message"]

        elif isinstance(data, str) and data:
            message = data

        try:
            status = int(status)
        except (TypeError, ValueError):
            status = fallback_status

        return message, error_code, status

    @staticmethod
    def _resolve_exception_class(status_code: int, error_code: Optional[str]) -> type[APIError]:
        normalized_error = (error_code or "").lower()

        if status_code in (401, 403):
            return AuthenticationError
        if status_code == 404:
            return NotFoundError
        if status_code == 429:
            return RateLimitError
        if status_code == 413:
            return PayloadTooLargeError
        if 500 <= status_code < 600:
            return ServerError

        base_exception: type[APIError]
        if status_code == 400:
            base_exception = BadRequestError
        else:
            base_exception = APIError

        return ERROR_CODE_EXCEPTION_MAP.get(normalized_error, base_exception)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make a raw request to the API.
        """
        url = urljoin(self.base_url, path.lstrip("/"))
        
        logger.debug(f"Request: {method} {url} - Params: {params} - Data: {data}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Connection error: {str(e)}") from e

        return self._handle_response(response)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a GET request."""
        return self.request("GET", path, params=params)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a POST request."""
        return self.request("POST", path, data=data)

    def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a PUT request."""
        return self.request("PUT", path, data=data)

    def patch(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a PATCH request."""
        return self.request("PATCH", path, data=data)

    def delete(self, path: str) -> Any:
        """Execute a DELETE request."""
        return self.request("DELETE", path)

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> "CodeVFClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
