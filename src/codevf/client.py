import os
import requests
from typing import Optional, Any, Dict, Union
from urllib.parse import urljoin

from .exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


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
    ):
        """
        Initialize the CodeVF Client.

        Args:
            api_key: The API key for authentication. If not provided,
                     looks for CODEVF_API_KEY environment variable.
            base_url: The base URL for the API. Defaults to production URL.
            timeout: Request timeout in seconds.
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
        self._configure_session()

    def _configure_session(self):
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "codevf-python-sdk/0.1.0",
        })

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            # Attempt to parse JSON, but fall back to text if empty or invalid
            data = response.json() if response.content else None
        except ValueError:
            data = response.text

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
        return self.request("GET", path, params=params)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", path, data=data)

    def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", path, data=data)

    def patch(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PATCH", path, data=data)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)

    def close(self):
        """Close the underlying session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
