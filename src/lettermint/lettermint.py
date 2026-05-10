"""Main Lettermint SDK classes."""

from __future__ import annotations

import sys
from typing import Any

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from .client import AsyncLettermintClient, LettermintClient
from .endpoints.api import (
    AsyncDomainsEndpoint,
    AsyncMessagesEndpoint,
    AsyncProjectsEndpoint,
    AsyncRoutesEndpoint,
    AsyncStatsEndpoint,
    AsyncSuppressionsEndpoint,
    AsyncTeamEndpoint,
    AsyncWebhooksEndpoint,
    DomainsEndpoint,
    MessagesEndpoint,
    ProjectsEndpoint,
    RoutesEndpoint,
    StatsEndpoint,
    SuppressionsEndpoint,
    TeamEndpoint,
    WebhooksEndpoint,
)
from .endpoints.email import AsyncEmailEndpoint, EmailEndpoint


class _EmailAccessor:
    def __get__(self, instance: Lettermint | None, owner: type[Lettermint]) -> Any:
        if instance is None:
            return owner._email_client
        return instance._email_endpoint()


class _AsyncEmailAccessor:
    def __get__(
        self,
        instance: AsyncLettermint | None,
        owner: type[AsyncLettermint],
    ) -> Any:
        if instance is None:
            return owner._email_client
        return instance._email_endpoint()


class ApiClient:
    """Synchronous client for the full Lettermint API."""

    def __init__(
        self,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = LettermintClient(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
            auth_scheme="bearer",
        )
        self.domains = DomainsEndpoint(self._client)
        self.messages = MessagesEndpoint(self._client)
        self.projects = ProjectsEndpoint(self._client)
        self.routes = RoutesEndpoint(self._client)
        self.stats = StatsEndpoint(self._client)
        self.suppressions = SuppressionsEndpoint(self._client)
        self.team = TeamEndpoint(self._client)
        self.webhooks = WebhooksEndpoint(self._client)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def ping(self) -> str:
        return self._client.get_raw("/ping").strip()


class AsyncApiClient:
    """Asynchronous client for the full Lettermint API."""

    def __init__(
        self,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = AsyncLettermintClient(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
            auth_scheme="bearer",
        )
        self.domains = AsyncDomainsEndpoint(self._client)
        self.messages = AsyncMessagesEndpoint(self._client)
        self.projects = AsyncProjectsEndpoint(self._client)
        self.routes = AsyncRoutesEndpoint(self._client)
        self.stats = AsyncStatsEndpoint(self._client)
        self.suppressions = AsyncSuppressionsEndpoint(self._client)
        self.team = AsyncTeamEndpoint(self._client)
        self.webhooks = AsyncWebhooksEndpoint(self._client)

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def ping(self) -> str:
        return (await self._client.get_raw("/ping")).strip()


class Lettermint:
    """Synchronous Lettermint SDK client.

    The main entry point for interacting with the Lettermint API.

    Args:
        api_token: Your Lettermint API token.
        base_url: Custom base URL for the API. Defaults to https://api.lettermint.co/v1.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Example:
        >>> from lettermint import Lettermint
        >>>
        >>> client = Lettermint(api_token="your-api-token")
        >>>
        >>> response = (
        ...     client.email
        ...     .from_("sender@example.com")
        ...     .to("recipient@example.com")
        ...     .subject("Hello from Python!")
        ...     .html("<h1>Welcome!</h1>")
        ...     .send()
        ... )
        >>>
        >>> print(response["message_id"])

    Example with context manager:
        >>> with Lettermint(api_token="your-api-token") as client:
        ...     response = client.email.from_("sender@example.com").to("recipient@example.com").subject("Hello").send()
    """

    email = _EmailAccessor()

    def __init__(
        self,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = LettermintClient(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
        )
        self._email: EmailEndpoint | None = None

    @classmethod
    def _email_client(
        cls,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> EmailEndpoint:
        client = LettermintClient(api_token=api_token, base_url=base_url, timeout=timeout)
        return EmailEndpoint(client)

    @classmethod
    def api(
        cls,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> ApiClient:
        return ApiClient(api_token, base_url=base_url, timeout=timeout)

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _email_endpoint(self) -> EmailEndpoint:
        """Access the email endpoint for sending emails.

        Returns:
            The email endpoint instance with fluent builder interface.

        Example:
            >>> client.email.from_("sender@example.com").to("recipient@example.com").send()
        """
        if self._email is None:
            self._email = EmailEndpoint(self._client)
        return self._email


class AsyncLettermint:
    """Asynchronous Lettermint SDK client.

    The main entry point for interacting with the Lettermint API asynchronously.

    Args:
        api_token: Your Lettermint API token.
        base_url: Custom base URL for the API. Defaults to https://api.lettermint.co/v1.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Example:
        >>> from lettermint import AsyncLettermint
        >>>
        >>> async with AsyncLettermint(api_token="your-api-token") as client:
        ...     response = await (
        ...         client.email
        ...         .from_("sender@example.com")
        ...         .to("recipient@example.com")
        ...         .subject("Hello from Python!")
        ...         .html("<h1>Welcome!</h1>")
        ...         .send()
        ...     )
        ...     print(response["message_id"])
    """

    email = _AsyncEmailAccessor()

    def __init__(
        self,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = AsyncLettermintClient(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
        )
        self._email: AsyncEmailEndpoint | None = None

    @classmethod
    def _email_client(
        cls,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> AsyncEmailEndpoint:
        client = AsyncLettermintClient(api_token=api_token, base_url=base_url, timeout=timeout)
        return AsyncEmailEndpoint(client)

    @classmethod
    def api(
        cls,
        api_token: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> AsyncApiClient:
        return AsyncApiClient(api_token, base_url=base_url, timeout=timeout)

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _email_endpoint(self) -> AsyncEmailEndpoint:
        """Access the email endpoint for sending emails asynchronously.

        Returns:
            The async email endpoint instance with fluent builder interface.

        Example:
            >>> await client.email.from_("sender@example.com").to("recipient@example.com").send()
        """
        if self._email is None:
            self._email = AsyncEmailEndpoint(self._client)
        return self._email
