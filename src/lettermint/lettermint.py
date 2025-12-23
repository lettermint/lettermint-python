"""Main Lettermint SDK classes."""

from __future__ import annotations

import sys
from typing import Any

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from .client import AsyncLettermintClient, LettermintClient
from .endpoints.email import AsyncEmailEndpoint, EmailEndpoint


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

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    @property
    def email(self) -> EmailEndpoint:
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

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    @property
    def email(self) -> AsyncEmailEndpoint:
        """Access the email endpoint for sending emails asynchronously.

        Returns:
            The async email endpoint instance with fluent builder interface.

        Example:
            >>> await client.email.from_("sender@example.com").to("recipient@example.com").send()
        """
        if self._email is None:
            self._email = AsyncEmailEndpoint(self._client)
        return self._email
