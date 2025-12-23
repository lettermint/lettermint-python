"""HTTP client implementations for the Lettermint SDK."""

from __future__ import annotations

import platform
from importlib.metadata import version
from typing import Any

import httpx

from .exceptions import (
    ClientError,
    HttpRequestError,
    TimeoutError,
    ValidationError,
)

DEFAULT_BASE_URL = "https://api.lettermint.co/v1"
DEFAULT_TIMEOUT = 30.0


class LettermintClient:
    """Synchronous HTTP client for the Lettermint API.

    Args:
        api_token: API token for authentication.
        base_url: Base URL for the API. Defaults to https://api.lettermint.co/v1.
        timeout: Request timeout in seconds. Defaults to 30.0.
    """

    def __init__(
        self,
        api_token: str,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_token = api_token
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"Lettermint/{version('lettermint')} (Python; python {platform.python_version()})",
                "x-lettermint-token": self._api_token,
            },
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> LettermintClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle the HTTP response and raise appropriate exceptions."""
        if response.is_success:
            return response.json()

        try:
            response_body = response.json()
        except Exception:
            response_body = None

        if response.status_code == 422:
            error_type = (
                response_body.get("error", "ValidationError")
                if isinstance(response_body, dict)
                else "ValidationError"
            )
            raise ValidationError(
                f"Validation error: {error_type}",
                error_type,
                response_body,
            )

        if response.status_code == 400:
            error_message = (
                response_body.get("error", "Unknown client error")
                if isinstance(response_body, dict)
                else "Unknown client error"
            )
            raise ClientError(f"Client error: {error_message}", response_body)

        raise HttpRequestError(
            f"HTTP error {response.status_code} {response.reason_phrase}",
            response.status_code,
            response_body,
        )

    def get(
        self,
        path: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a GET request to the API.

        Args:
            path: API endpoint path.
            params: Query parameters.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = self._client.get(path, params=params, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e

    def post(
        self,
        path: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a POST request to the API.

        Args:
            path: API endpoint path.
            data: Request payload to be JSON-encoded.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = self._client.post(path, json=data, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e

    def put(
        self,
        path: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a PUT request to the API.

        Args:
            path: API endpoint path.
            data: Request payload to be JSON-encoded.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = self._client.put(path, json=data, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e

    def delete(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a DELETE request to the API.

        Args:
            path: API endpoint path.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = self._client.delete(path, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e


class AsyncLettermintClient:
    """Asynchronous HTTP client for the Lettermint API.

    Args:
        api_token: API token for authentication.
        base_url: Base URL for the API. Defaults to https://api.lettermint.co/v1.
        timeout: Request timeout in seconds. Defaults to 30.0.
    """

    def __init__(
        self,
        api_token: str,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_token = api_token
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"Lettermint/{version('lettermint')} (Python; python {platform.python_version()})",
                "x-lettermint-token": self._api_token,
            },
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncLettermintClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle the HTTP response and raise appropriate exceptions."""
        if response.is_success:
            return response.json()

        try:
            response_body = response.json()
        except Exception:
            response_body = None

        if response.status_code == 422:
            error_type = (
                response_body.get("error", "ValidationError")
                if isinstance(response_body, dict)
                else "ValidationError"
            )
            raise ValidationError(
                f"Validation error: {error_type}",
                error_type,
                response_body,
            )

        if response.status_code == 400:
            error_message = (
                response_body.get("error", "Unknown client error")
                if isinstance(response_body, dict)
                else "Unknown client error"
            )
            raise ClientError(f"Client error: {error_message}", response_body)

        raise HttpRequestError(
            f"HTTP error {response.status_code} {response.reason_phrase}",
            response.status_code,
            response_body,
        )

    async def get(
        self,
        path: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a GET request to the API.

        Args:
            path: API endpoint path.
            params: Query parameters.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = await self._client.get(path, params=params, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e

    async def post(
        self,
        path: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a POST request to the API.

        Args:
            path: API endpoint path.
            data: Request payload to be JSON-encoded.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = await self._client.post(path, json=data, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e

    async def put(
        self,
        path: str,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a PUT request to the API.

        Args:
            path: API endpoint path.
            data: Request payload to be JSON-encoded.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = await self._client.put(path, json=data, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e

    async def delete(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a DELETE request to the API.

        Args:
            path: API endpoint path.
            headers: Additional request headers.

        Returns:
            The parsed JSON response.

        Raises:
            HttpRequestError: On HTTP errors.
            TimeoutError: On request timeout.
        """
        try:
            response = await self._client.delete(path, headers=headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout after {self._timeout}s") from e
