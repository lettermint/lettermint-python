"""Custom exceptions for the Lettermint SDK."""

from __future__ import annotations

from typing import Any


class LettermintError(Exception):
    """Base exception for all Lettermint SDK errors."""

    pass


class HttpRequestError(LettermintError):
    """Exception raised for HTTP request errors.

    Attributes:
        status_code: The HTTP status code of the response.
        response_body: The parsed response body, if available.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class ValidationError(HttpRequestError):
    """Exception raised for validation errors (HTTP 422).

    Attributes:
        error_type: The type of validation error from the API.
    """

    def __init__(
        self,
        message: str,
        error_type: str,
        response_body: Any | None = None,
    ) -> None:
        super().__init__(message, 422, response_body)
        self.error_type = error_type


class ClientError(HttpRequestError):
    """Exception raised for client errors (HTTP 400)."""

    def __init__(
        self,
        message: str,
        response_body: Any | None = None,
    ) -> None:
        super().__init__(message, 400, response_body)


class TimeoutError(LettermintError):
    """Exception raised when a request times out."""

    pass


class WebhookVerificationError(LettermintError):
    """Base exception for webhook verification errors."""

    pass


class InvalidSignatureError(WebhookVerificationError):
    """Exception raised when the webhook signature is invalid."""

    pass


class TimestampToleranceError(WebhookVerificationError):
    """Exception raised when the webhook timestamp is outside the tolerance window."""

    pass


class JsonDecodeError(WebhookVerificationError):
    """Exception raised when the webhook payload cannot be decoded as JSON."""

    pass
