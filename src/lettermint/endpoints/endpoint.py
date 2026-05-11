"""Base endpoint class for the Lettermint SDK."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..client import AsyncLettermintClient, LettermintClient


class Endpoint:
    """Base class for synchronous API endpoints.

    Args:
        client: The HTTP client to use for requests.
    """

    def __init__(self, client: LettermintClient) -> None:
        self._client = client

    def __enter__(self) -> Endpoint:
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.close()

    def _path(self, path: str, **parameters: str) -> str:
        for key, value in parameters.items():
            path = path.replace(f"{{{key}}}", quote(value, safe=""))
        return path


class AsyncEndpoint:
    """Base class for asynchronous API endpoints.

    Args:
        client: The async HTTP client to use for requests.
    """

    def __init__(self, client: AsyncLettermintClient) -> None:
        self._client = client

    async def __aenter__(self) -> AsyncEndpoint:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.close()

    def _path(self, path: str, **parameters: str) -> str:
        for key, value in parameters.items():
            path = path.replace(f"{{{key}}}", quote(value, safe=""))
        return path
