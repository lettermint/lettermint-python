"""Base endpoint class for the Lettermint SDK."""

from __future__ import annotations

from ..client import AsyncLettermintClient, LettermintClient


class Endpoint:
    """Base class for synchronous API endpoints.

    Args:
        client: The HTTP client to use for requests.
    """

    def __init__(self, client: LettermintClient) -> None:
        self._client = client


class AsyncEndpoint:
    """Base class for asynchronous API endpoints.

    Args:
        client: The async HTTP client to use for requests.
    """

    def __init__(self, client: AsyncLettermintClient) -> None:
        self._client = client
