"""Sending email: :class:`AsyncEmails` and the immutable :class:`AsyncEmailBuilder`."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from .._core import auth_header
from .._emails import BaseEmailBuilder, EmailMessage, check_message, initial_message
from .._generated.types import SendBatchMailResponse, SendMailResponse
from ..exceptions import LettermintValidationError
from .resources import AsyncResource

__all__ = ["AsyncEmailBuilder", "AsyncEmails"]


class AsyncEmailBuilder(BaseEmailBuilder):
    """An immutable email builder, created by ``lettermint.emails.compose()``.

    Every setter returns a new builder and leaves this one unchanged, so a base
    builder can be shared and reused safely::

        welcome = lettermint.emails.compose().from_("Acme <hello@acme.com>").subject("Welcome")
        await welcome.to("jane@example.com").html("<p>Hi Jane</p>").send()
    """

    __slots__ = ()

    async def send(
        self, *, idempotency_key: str | None = None, timeout: float | None = None
    ) -> SendMailResponse:
        """Sends a snapshot of this email. The builder is unchanged and can be sent again."""
        emails = cast(AsyncEmails, self._emails)
        return await emails.send(
            cast(EmailMessage, self._message), idempotency_key=idempotency_key, timeout=timeout
        )


class AsyncEmails(AsyncResource):
    """Sends email with the project sending token (``x-lettermint-token``).

    Holds no message state: every call sends exactly what it is given.
    """

    async def send(
        self,
        message: EmailMessage,
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> SendMailResponse:
        """Sends one email, given in the API's wire format (``reply_to``, ``scheduled_at``, ...)."""
        auth_header(self._transport.config, "emails.send", "sending")
        body = check_message(message)
        return cast(
            SendMailResponse,
            await self._request(
                "POST /send",
                "emails.send",
                body=body,
                idempotency_key=idempotency_key,
                timeout=timeout,
            ),
        )

    async def send_batch(
        self,
        messages: Sequence[EmailMessage | AsyncEmailBuilder],
        *,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> SendBatchMailResponse:
        """Sends up to 500 emails in one request. Accepts messages and builders."""
        auth_header(self._transport.config, "emails.send_batch", "sending")
        if not isinstance(messages, (list, tuple)):
            raise LettermintValidationError(
                "send_batch() takes a list of messages.", field="messages"
            )
        body: list[Any] = [
            check_message(message, f"messages[{index}]") for index, message in enumerate(messages)
        ]
        return cast(
            SendBatchMailResponse,
            await self._request(
                "POST /send/batch",
                "emails.send_batch",
                body=body,
                idempotency_key=idempotency_key,
                timeout=timeout,
            ),
        )

    def compose(self, message: EmailMessage | None = None) -> AsyncEmailBuilder:
        """Starts an immutable email builder, empty or from ``message``."""
        auth_header(self._transport.config, "emails.compose", "sending")
        return AsyncEmailBuilder(self, None if message is None else initial_message(message))

    async def ping(self, *, timeout: float | None = None) -> str:
        """Checks the sending token: ``GET /ping`` returns ``pong``."""
        text = await self._request("GET /ping", "emails.ping", auth="sending", timeout=timeout)
        return cast(str, text).strip()
