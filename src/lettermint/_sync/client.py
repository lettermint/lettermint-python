# Generated from src/lettermint/_async/client.py by scripts/unasync.py — do not edit.
"""The synchronous client, :class:`Lettermint`."""

from __future__ import annotations

from types import TracebackType
from typing import Any, cast

import httpx
from typing_extensions import Self

from .._core import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, build_config, describe_client
from .._generated.types import AnalyticsQuery, AnalyticsResponse, BlockedFileTypes
from .._transport import Transport
from ..exceptions import LettermintConfigError
from .emails import Emails
from .resources import (
    Domains,
    Messages,
    Projects,
    Routes,
    Stats,
    Suppressions,
    Team,
    Webhooks,
)

__all__ = ["Lettermint"]


class Lettermint:
    """The Lettermint client.

    ::

        lettermint = Lettermint(sending_token=..., team_token=...)
        lettermint = Lettermint("lm_...")  # team or sending token, detected by its prefix

    ``emails`` uses the sending token; every other part uses the team token.
    The client holds no message state, so create it once and share it. Close
    it when you are done, or use it as a context manager::

        with Lettermint(sending_token=token) as lettermint:
            lettermint.emails.send({...})
    """

    #: Send email. Needs ``sending_token``.
    emails: Emails
    #: Sending domains. Needs ``team_token``.
    domains: Domains
    #: Sent and received messages. Needs ``team_token``.
    messages: Messages
    #: Projects and their report forwarding. Needs ``team_token``.
    projects: Projects
    #: Routes of a project. Needs ``team_token``.
    routes: Routes
    #: Sending statistics. Needs ``team_token``.
    stats: Stats
    #: The suppression list. Needs ``team_token``.
    suppressions: Suppressions
    #: The team and its members. Needs ``team_token``.
    team: Team
    #: Webhook endpoints and their deliveries. Needs ``team_token``.
    webhooks: Webhooks

    def __init__(
        self,
        token: str | None = None,
        /,
        *,
        sending_token: str | None = None,
        team_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
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
        if http_client is not None and not isinstance(http_client, httpx.Client):
            raise LettermintConfigError("http_client must be an httpx.Client.")
        client = http_client or httpx.Client(
            follow_redirects=False, timeout=httpx.Timeout(config.timeout)
        )
        self._transport = Transport(config, client, owns_client=http_client is None)
        self.emails = Emails(self._transport)
        self.domains = Domains(self._transport)
        self.messages = Messages(self._transport)
        self.projects = Projects(self._transport)
        self.routes = Routes(self._transport)
        self.stats = Stats(self._transport)
        self.suppressions = Suppressions(self._transport)
        self.team = Team(self._transport)
        self.webhooks = Webhooks(self._transport)

    def ping(self, *, timeout: float | None = None) -> str:
        """Checks the token: ``GET /ping`` returns ``pong``.

        Uses the team token when it is set, otherwise the sending token.
        """
        text = self._transport.request("GET /ping", label="ping", timeout=timeout)
        return cast(str, text).strip()

    def analytics(
        self, query: AnalyticsQuery, *, timeout: float | None = None
    ) -> AnalyticsResponse:
        """Queries email analytics. Needs ``team_token``."""
        return cast(
            AnalyticsResponse,
            self._transport.request(
                "POST /analytics", label="analytics", body=query, timeout=timeout
            ),
        )

    def blocked_file_types(self, *, timeout: float | None = None) -> BlockedFileTypes:
        """The file extensions and MIME types that cannot be attached. Needs ``team_token``."""
        return cast(
            BlockedFileTypes,
            self._transport.request(
                "GET /blocked-file-types", label="blocked_file_types", timeout=timeout
            ),
        )

    def close(self) -> None:
        """Closes the HTTP client, if the SDK created it. Later calls raise ``LettermintConfigError``."""
        self._transport.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return describe_client(type(self).__name__, self._transport.config)

    def __reduce__(self) -> Any:
        raise TypeError(f"{type(self).__name__} cannot be pickled")
