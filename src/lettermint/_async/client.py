"""The asynchronous client, :class:`AsyncLettermint`."""

from __future__ import annotations

from types import TracebackType
from typing import Any, cast

import httpx
from typing_extensions import Self

from .._core import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, build_config, describe_client
from .._generated.types import AnalyticsQuery, AnalyticsResponse, BlockedFileTypes
from .._transport import AsyncTransport
from ..exceptions import LettermintConfigError
from .emails import AsyncEmails
from .resources import (
    AsyncDomains,
    AsyncMessages,
    AsyncProjects,
    AsyncRoutes,
    AsyncStats,
    AsyncSuppressions,
    AsyncTeam,
    AsyncWebhooks,
)

__all__ = ["AsyncLettermint"]


class AsyncLettermint:
    """The Lettermint client.

    ::

        lettermint = AsyncLettermint(sending_token=..., team_token=...)
        lettermint = AsyncLettermint("lm_...")  # team or sending token, detected by its prefix

    ``emails`` uses the sending token; every other part uses the team token.
    The client holds no message state, so create it once and share it. Close
    it when you are done, or use it as a context manager::

        async with AsyncLettermint(sending_token=token) as lettermint:
            await lettermint.emails.send({...})
    """

    #: Send email. Needs ``sending_token``.
    emails: AsyncEmails
    #: Sending domains. Needs ``team_token``.
    domains: AsyncDomains
    #: Sent and received messages. Needs ``team_token``.
    messages: AsyncMessages
    #: Projects and their report forwarding. Needs ``team_token``.
    projects: AsyncProjects
    #: Routes of a project. Needs ``team_token``.
    routes: AsyncRoutes
    #: Sending statistics. Needs ``team_token``.
    stats: AsyncStats
    #: The suppression list. Needs ``team_token``.
    suppressions: AsyncSuppressions
    #: The team and its members. Needs ``team_token``.
    team: AsyncTeam
    #: Webhook endpoints and their deliveries. Needs ``team_token``.
    webhooks: AsyncWebhooks

    def __init__(
        self,
        token: str | None = None,
        /,
        *,
        sending_token: str | None = None,
        team_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Creates a client.

        Args:
            token: A token string; ``lm_team_...`` is a team token, any other
                ``lm_...`` token a sending token. Other formats raise
                :class:`~lettermint.LettermintConfigError`.
            sending_token: A project sending token, sent as ``x-lettermint-token``.
            team_token: A team API token, sent as ``Authorization: Bearer``.
            base_url: The API base URL.
            timeout: Seconds for each request, covering the response headers and body.
            http_client: An ``httpx`` client to send requests with, for example
                for a proxy. The SDK never follows redirects and does not close
                a client it did not create.
        """
        config = build_config(token, sending_token, team_token, base_url, timeout)
        if http_client is not None and not isinstance(http_client, httpx.AsyncClient):
            raise LettermintConfigError("http_client must be an httpx.AsyncClient.")
        client = http_client or httpx.AsyncClient(
            follow_redirects=False, timeout=httpx.Timeout(config.timeout)
        )
        self._transport = AsyncTransport(config, client, owns_client=http_client is None)
        self.emails = AsyncEmails(self._transport)
        self.domains = AsyncDomains(self._transport)
        self.messages = AsyncMessages(self._transport)
        self.projects = AsyncProjects(self._transport)
        self.routes = AsyncRoutes(self._transport)
        self.stats = AsyncStats(self._transport)
        self.suppressions = AsyncSuppressions(self._transport)
        self.team = AsyncTeam(self._transport)
        self.webhooks = AsyncWebhooks(self._transport)

    async def ping(self, *, timeout: float | None = None) -> str:
        """Checks the token: ``GET /ping`` returns ``pong``.

        Uses the team token when it is set, otherwise the sending token.
        """
        text = await self._transport.request("GET /ping", label="ping", timeout=timeout)
        return cast(str, text).strip()

    async def analytics(
        self, query: AnalyticsQuery, *, timeout: float | None = None
    ) -> AnalyticsResponse:
        """Queries email analytics. Needs ``team_token``."""
        return cast(
            AnalyticsResponse,
            await self._transport.request(
                "POST /analytics", label="analytics", body=query, timeout=timeout
            ),
        )

    async def blocked_file_types(self, *, timeout: float | None = None) -> BlockedFileTypes:
        """The file extensions and MIME types that cannot be attached. Needs ``team_token``."""
        return cast(
            BlockedFileTypes,
            await self._transport.request(
                "GET /blocked-file-types", label="blocked_file_types", timeout=timeout
            ),
        )

    async def close(self) -> None:
        """Closes the HTTP client, if the SDK created it. Later calls raise ``LettermintConfigError``."""
        await self._transport.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    def __repr__(self) -> str:
        return describe_client(type(self).__name__, self._transport.config)

    def __reduce__(self) -> Any:
        raise TypeError(f"{type(self).__name__} cannot be pickled")
