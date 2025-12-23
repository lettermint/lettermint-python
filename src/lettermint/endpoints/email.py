"""Email endpoint for the Lettermint SDK."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ..types import SendEmailResponse
from .endpoint import AsyncEndpoint, Endpoint

if TYPE_CHECKING:
    from ..client import AsyncLettermintClient, LettermintClient


class EmailEndpoint(Endpoint):
    """Synchronous endpoint for sending emails.

    Provides a fluent builder interface for composing and sending emails.

    Example:
        >>> client = Lettermint(api_token="your-token")
        >>> response = (
        ...     client.email
        ...     .from_("sender@example.com")
        ...     .to("recipient@example.com")
        ...     .subject("Hello!")
        ...     .html("<h1>Welcome!</h1>")
        ...     .send()
        ... )
        >>> print(response["message_id"])
    """

    def __init__(self, client: LettermintClient) -> None:
        super().__init__(client)
        self._payload: dict[str, Any] = {}
        self._idempotency_key: str | None = None

    def _reset(self) -> None:
        """Reset the payload and idempotency key after sending."""
        self._payload = {}
        self._idempotency_key = None

    def headers(self, headers: dict[str, str]) -> Self:
        """Set custom headers for the email.

        Args:
            headers: Dictionary of custom header key-value pairs.

        Returns:
            The current instance for method chaining.

        Example:
            >>> client.email.headers({"X-Custom-Header": "value"})
        """
        self._payload["headers"] = headers
        return self

    def idempotency_key(self, key: str) -> Self:
        """Set the idempotency key for the request.

        This helps prevent duplicate email sends when retrying failed requests.
        If you provide the same idempotency key for multiple requests, only the
        first one will be processed.

        Args:
            key: A unique string to identify this request.

        Returns:
            The current instance for method chaining.

        Example:
            >>> client.email.idempotency_key("unique-id-123")
        """
        self._idempotency_key = key
        return self

    def from_(self, email: str) -> Self:
        """Set the sender email address.

        Supports RFC 5322 addresses, e.g., "John Doe <john@example.com>".

        Note: This method is named `from_` because `from` is a reserved keyword
        in Python.

        Args:
            email: The sender's email address.

        Returns:
            The current instance for method chaining.

        Example:
            >>> client.email.from_("John Doe <john@example.com>")
        """
        self._payload["from"] = email
        return self

    def to(self, *emails: str) -> Self:
        """Set one or more recipient email addresses.

        Args:
            *emails: One or more recipient email addresses.

        Returns:
            The current instance for method chaining.

        Example:
            >>> client.email.to("user1@example.com", "user2@example.com")
        """
        self._payload["to"] = list(emails)
        return self

    def subject(self, subject: str) -> Self:
        """Set the subject of the email.

        Args:
            subject: The subject line.

        Returns:
            The current instance for method chaining.
        """
        self._payload["subject"] = subject
        return self

    def html(self, html: str | None) -> Self:
        """Set the HTML body of the email.

        Args:
            html: The HTML content for the email body.

        Returns:
            The current instance for method chaining.
        """
        if html is not None:
            self._payload["html"] = html
        return self

    def text(self, text: str | None) -> Self:
        """Set the plain text body of the email.

        Args:
            text: The plain text content for the email body.

        Returns:
            The current instance for method chaining.
        """
        if text is not None:
            self._payload["text"] = text
        return self

    def cc(self, *emails: str) -> Self:
        """Set one or more CC email addresses.

        Args:
            *emails: Email addresses to be CC'd.

        Returns:
            The current instance for method chaining.
        """
        self._payload["cc"] = list(emails)
        return self

    def bcc(self, *emails: str) -> Self:
        """Set one or more BCC email addresses.

        Args:
            *emails: Email addresses to be BCC'd.

        Returns:
            The current instance for method chaining.
        """
        self._payload["bcc"] = list(emails)
        return self

    def reply_to(self, *emails: str) -> Self:
        """Set one or more Reply-To email addresses.

        Args:
            *emails: Reply-To email addresses.

        Returns:
            The current instance for method chaining.
        """
        self._payload["reply_to"] = list(emails)
        return self

    def route(self, route: str) -> Self:
        """Set the routing key for the email.

        Args:
            route: The routing key.

        Returns:
            The current instance for method chaining.
        """
        self._payload["route"] = route
        return self

    def attach(
        self,
        filename: str,
        content: str,
        content_id: str | None = None,
    ) -> Self:
        """Attach a file to the email.

        Args:
            filename: The attachment filename.
            content: The base64-encoded file content.
            content_id: Optional Content-ID for inline attachments.

        Returns:
            The current instance for method chaining.

        Example:
            >>> # Regular attachment
            >>> client.email.attach("document.pdf", base64_content)
            >>> # Inline image
            >>> client.email.attach("logo.png", base64_content, "logo@example.com")
        """
        if "attachments" not in self._payload:
            self._payload["attachments"] = []

        attachment: dict[str, str] = {
            "filename": filename,
            "content": content,
        }
        if content_id is not None:
            attachment["content_id"] = content_id

        self._payload["attachments"].append(attachment)
        return self

    def metadata(self, metadata: dict[str, str]) -> Self:
        """Set metadata for the email.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            The current instance for method chaining.

        Example:
            >>> client.email.metadata({"campaign_id": "123", "user_id": "456"})
        """
        self._payload["metadata"] = metadata
        return self

    def tag(self, tag: str) -> Self:
        """Set the tag for the email.

        Args:
            tag: A string to categorize the email.

        Returns:
            The current instance for method chaining.

        Example:
            >>> client.email.tag("welcome-campaign")
        """
        self._payload["tag"] = tag
        return self

    def send(self) -> SendEmailResponse:
        """Send the composed email.

        Returns:
            The API response containing the message ID and status.

        Raises:
            HttpRequestError: On HTTP errors.
            ValidationError: On validation errors (422).
            ClientError: On client errors (400).
            TimeoutError: On request timeout.

        Example:
            >>> response = client.email.from_("sender@example.com").to("recipient@example.com").subject("Hello").send()
            >>> print(response["message_id"])
        """
        headers: dict[str, str] | None = None
        if self._idempotency_key is not None:
            headers = {"Idempotency-Key": self._idempotency_key}

        try:
            response: SendEmailResponse = self._client.post(
                "/send",
                data=self._payload,
                headers=headers,
            )
            return response
        finally:
            self._reset()


class AsyncEmailEndpoint(AsyncEndpoint):
    """Asynchronous endpoint for sending emails.

    Provides a fluent builder interface for composing and sending emails.

    Example:
        >>> async with AsyncLettermint(api_token="your-token") as client:
        ...     response = await (
        ...         client.email
        ...         .from_("sender@example.com")
        ...         .to("recipient@example.com")
        ...         .subject("Hello!")
        ...         .html("<h1>Welcome!</h1>")
        ...         .send()
        ...     )
        ...     print(response["message_id"])
    """

    def __init__(self, client: AsyncLettermintClient) -> None:
        super().__init__(client)
        self._payload: dict[str, Any] = {}
        self._idempotency_key: str | None = None

    def _reset(self) -> None:
        """Reset the payload and idempotency key after sending."""
        self._payload = {}
        self._idempotency_key = None

    def headers(self, headers: dict[str, str]) -> Self:
        """Set custom headers for the email.

        Args:
            headers: Dictionary of custom header key-value pairs.

        Returns:
            The current instance for method chaining.
        """
        self._payload["headers"] = headers
        return self

    def idempotency_key(self, key: str) -> Self:
        """Set the idempotency key for the request.

        This helps prevent duplicate email sends when retrying failed requests.

        Args:
            key: A unique string to identify this request.

        Returns:
            The current instance for method chaining.
        """
        self._idempotency_key = key
        return self

    def from_(self, email: str) -> Self:
        """Set the sender email address.

        Supports RFC 5322 addresses, e.g., "John Doe <john@example.com>".

        Args:
            email: The sender's email address.

        Returns:
            The current instance for method chaining.
        """
        self._payload["from"] = email
        return self

    def to(self, *emails: str) -> Self:
        """Set one or more recipient email addresses.

        Args:
            *emails: One or more recipient email addresses.

        Returns:
            The current instance for method chaining.
        """
        self._payload["to"] = list(emails)
        return self

    def subject(self, subject: str) -> Self:
        """Set the subject of the email.

        Args:
            subject: The subject line.

        Returns:
            The current instance for method chaining.
        """
        self._payload["subject"] = subject
        return self

    def html(self, html: str | None) -> Self:
        """Set the HTML body of the email.

        Args:
            html: The HTML content for the email body.

        Returns:
            The current instance for method chaining.
        """
        if html is not None:
            self._payload["html"] = html
        return self

    def text(self, text: str | None) -> Self:
        """Set the plain text body of the email.

        Args:
            text: The plain text content for the email body.

        Returns:
            The current instance for method chaining.
        """
        if text is not None:
            self._payload["text"] = text
        return self

    def cc(self, *emails: str) -> Self:
        """Set one or more CC email addresses.

        Args:
            *emails: Email addresses to be CC'd.

        Returns:
            The current instance for method chaining.
        """
        self._payload["cc"] = list(emails)
        return self

    def bcc(self, *emails: str) -> Self:
        """Set one or more BCC email addresses.

        Args:
            *emails: Email addresses to be BCC'd.

        Returns:
            The current instance for method chaining.
        """
        self._payload["bcc"] = list(emails)
        return self

    def reply_to(self, *emails: str) -> Self:
        """Set one or more Reply-To email addresses.

        Args:
            *emails: Reply-To email addresses.

        Returns:
            The current instance for method chaining.
        """
        self._payload["reply_to"] = list(emails)
        return self

    def route(self, route: str) -> Self:
        """Set the routing key for the email.

        Args:
            route: The routing key.

        Returns:
            The current instance for method chaining.
        """
        self._payload["route"] = route
        return self

    def attach(
        self,
        filename: str,
        content: str,
        content_id: str | None = None,
    ) -> Self:
        """Attach a file to the email.

        Args:
            filename: The attachment filename.
            content: The base64-encoded file content.
            content_id: Optional Content-ID for inline attachments.

        Returns:
            The current instance for method chaining.
        """
        if "attachments" not in self._payload:
            self._payload["attachments"] = []

        attachment: dict[str, str] = {
            "filename": filename,
            "content": content,
        }
        if content_id is not None:
            attachment["content_id"] = content_id

        self._payload["attachments"].append(attachment)
        return self

    def metadata(self, metadata: dict[str, str]) -> Self:
        """Set metadata for the email.

        Args:
            metadata: Dictionary of metadata key-value pairs.

        Returns:
            The current instance for method chaining.
        """
        self._payload["metadata"] = metadata
        return self

    def tag(self, tag: str) -> Self:
        """Set the tag for the email.

        Args:
            tag: A string to categorize the email.

        Returns:
            The current instance for method chaining.
        """
        self._payload["tag"] = tag
        return self

    async def send(self) -> SendEmailResponse:
        """Send the composed email asynchronously.

        Returns:
            The API response containing the message ID and status.

        Raises:
            HttpRequestError: On HTTP errors.
            ValidationError: On validation errors (422).
            ClientError: On client errors (400).
            TimeoutError: On request timeout.
        """
        headers: dict[str, str] | None = None
        if self._idempotency_key is not None:
            headers = {"Idempotency-Key": self._idempotency_key}

        try:
            response: SendEmailResponse = await self._client.post(
                "/send",
                data=self._payload,
                headers=headers,
            )
            return response
        finally:
            self._reset()
