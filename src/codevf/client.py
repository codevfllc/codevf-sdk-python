import os
import logging
import requests
from typing import Optional, Any, Dict
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import __version__
from .exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

from .resources.projects import Projects
from .resources.tasks import Tasks
from .resources.credits import Credits

logger = logging.getLogger(__name__)


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
            # Attempt to parse JSON, but fall back to text if empty or invalid
            data = response.json() if response.content else None
        except ValueError:
            data = response.text

        logger.debug(f"Response: {response.status_code} - {data}")

        if 200 <= response.status_code < 300:
            return data

        error_msg = f"API request failed with status {response.status_code}"
        if isinstance(data, dict) and "message" in data:
            error_msg = data["message"]

        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(error_msg, response.status_code, data)
        elif response.status_code == 404:
            raise NotFoundError(error_msg, response.status_code, data)
        elif response.status_code == 429:
            raise RateLimitError(error_msg, response.status_code, data)
        elif 500 <= response.status_code < 600:
            raise ServerError(error_msg, response.status_code, data)
        else:
            raise APIError(error_msg, response.status_code, data)

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
