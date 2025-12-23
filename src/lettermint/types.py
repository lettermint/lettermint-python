"""Type definitions for the Lettermint SDK."""

from __future__ import annotations

from typing import Literal, TypedDict


class EmailAttachment(TypedDict, total=False):
    """Attachment for an email message.

    Attributes:
        filename: The filename of the attachment.
        content: The base64-encoded content of the attachment.
        content_id: Optional Content-ID for inline attachments.
    """

    filename: str
    content: str
    content_id: str


class EmailPayload(TypedDict, total=False):
    """Payload for sending an email.

    Attributes:
        from_: The sender's email address (RFC 5322 format supported).
        to: List of recipient email addresses.
        subject: The email subject line.
        html: HTML content of the email body.
        text: Plain text content of the email body.
        cc: List of CC email addresses.
        bcc: List of BCC email addresses.
        reply_to: List of Reply-To email addresses.
        headers: Custom email headers.
        attachments: List of file attachments.
        route: Route identifier for the email.
        metadata: Custom metadata key-value pairs.
        tag: Tag for categorizing the email.
    """

    # Note: 'from' is a reserved keyword in Python, so the API uses 'from' but we document as from_
    from_: str
    to: list[str]
    subject: str
    html: str
    text: str
    cc: list[str]
    bcc: list[str]
    reply_to: list[str]
    headers: dict[str, str]
    attachments: list[EmailAttachment]
    route: str
    metadata: dict[str, str]
    tag: str


EmailStatus = Literal[
    "pending",
    "queued",
    "processed",
    "delivered",
    "soft_bounced",
    "hard_bounced",
    "failed",
]


class SendEmailResponse(TypedDict):
    """Response from the send email API.

    Attributes:
        message_id: The unique message identifier.
        status: The current status of the message.
    """

    message_id: str
    status: EmailStatus
