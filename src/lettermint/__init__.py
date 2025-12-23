"""
Lettermint Python SDK
=====================

Official Python SDK for the Lettermint email API.

Basic Usage:
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
    >>> print(response["message_id"])

Async Usage:
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

Webhook Verification:
    >>> from lettermint import Webhook
    >>>
    >>> webhook = Webhook(secret="your-webhook-secret")
    >>> payload = webhook.verify_headers(request.headers, request.body)
"""

from .exceptions import (
    ClientError,
    HttpRequestError,
    InvalidSignatureError,
    JsonDecodeError,
    LettermintError,
    TimeoutError,
    TimestampToleranceError,
    ValidationError,
    WebhookVerificationError,
)
from .lettermint import AsyncLettermint, Lettermint
from .types import EmailAttachment, EmailPayload, EmailStatus, SendEmailResponse
from .webhook import Webhook

__version__ = "1.0.0"

__all__ = [
    # Main clients
    "Lettermint",
    "AsyncLettermint",
    # Webhook
    "Webhook",
    # Exceptions
    "LettermintError",
    "HttpRequestError",
    "ValidationError",
    "ClientError",
    "TimeoutError",
    "WebhookVerificationError",
    "InvalidSignatureError",
    "TimestampToleranceError",
    "JsonDecodeError",
    # Types
    "EmailAttachment",
    "EmailPayload",
    "EmailStatus",
    "SendEmailResponse",
]
