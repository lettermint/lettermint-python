"""Exceptions of the Lettermint SDK.

Every exception the SDK raises is a :class:`LettermintError`. No exception
carries request headers, API tokens or the underlying HTTP library's request
object, and none is chained to an ``httpx`` exception.
"""

from __future__ import annotations

from typing import Any, Literal, TypeAlias

__all__ = [
    "APIConnectionError",
    "APIError",
    "APITimeoutError",
    "AuthenticationError",
    "ConflictError",
    "LettermintConfigError",
    "LettermintError",
    "LettermintValidationError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "RedirectError",
    "ServerError",
    "UnexpectedResponseError",
    "ValidationError",
    "WebhookVerificationError",
    "WebhookVerificationReason",
]


def _rebuild(
    cls: type[LettermintError], args: tuple[Any, ...], state: dict[str, Any]
) -> LettermintError:
    error = cls.__new__(cls)
    error.args = args
    error.__dict__.update(state)
    return error


class LettermintError(Exception):
    """Base class of every exception the SDK raises."""

    def __reduce__(self) -> tuple[Any, ...]:
        # Exceptions travel between processes (multiprocessing, Celery). The
        # keyword-only constructors below would break the default pickling.
        return (_rebuild, (type(self), self.args, dict(self.__dict__)))


class LettermintConfigError(LettermintError):
    """The client was configured or called incorrectly.

    For example a missing or unrecognised token, a token that the called
    method cannot use, an invalid option or an invalid path parameter. Raised
    before any request is made.
    """


class LettermintValidationError(LettermintError):
    """The SDK rejected a request before sending it, for example invalid tags.

    Unlike :class:`ValidationError`, the API never saw this request.
    """

    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        #: The offending field, for example ``tags`` or ``messages[2].tags``.
        self.field = field


class APIError(LettermintError):
    """The API answered with an error status (4xx or 5xx) and a JSON or empty body.

    Subclasses cover the common statuses; any other 4xx is a plain ``APIError``.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int,
        code: str | None = None,
        details: Any = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        #: The API's error message, or the HTTP reason phrase.
        self.message = message
        #: The HTTP status code.
        self.status = status
        #: Machine-readable error code from ``{"error": {"code"}}`` or a string ``error``.
        self.code = code
        #: Additional context from ``{"error": {"details"}}``, if the API sent any.
        self.details = details
        #: The decoded JSON error body, or ``None`` for an empty body.
        self.body = body

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status={self.status!r}, code={self.code!r}, message={self.message!r})"


class AuthenticationError(APIError):
    """HTTP 401: the token is missing, invalid or revoked."""


class PermissionDeniedError(APIError):
    """HTTP 403: the token may not perform this action, or the plan lacks the feature."""


class NotFoundError(APIError):
    """HTTP 404: the resource does not exist or is not visible to the token."""


class ConflictError(APIError):
    """HTTP 409: the request conflicts with the current state.

    For example an ``Idempotency-Key`` reused with a different body.
    """


class ValidationError(APIError):
    """HTTP 422: the API rejected the request data."""

    def __init__(
        self,
        message: str,
        *,
        status: int,
        code: str | None = None,
        details: Any = None,
        body: Any = None,
        errors: dict[str, list[str]] | None = None,
    ) -> None:
        super().__init__(message, status=status, code=code, details=details, body=body)
        #: Field errors from the ``{"message", "errors"}`` body, when the API sent them.
        self.errors = errors


class RateLimitError(APIError):
    """HTTP 429: too many requests."""

    def __init__(
        self,
        message: str,
        *,
        status: int,
        code: str | None = None,
        details: Any = None,
        body: Any = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status=status, code=code, details=details, body=body)
        #: Seconds to wait, from the ``Retry-After`` header (seconds or an HTTP date).
        self.retry_after = retry_after


class ServerError(APIError):
    """HTTP 5xx with a JSON or empty body."""


class APITimeoutError(LettermintError):
    """The request did not complete within the timeout.

    The timeout covers the whole request: connecting, sending, the response
    headers and the body. The API may still have processed the request.
    """

    def __init__(self, timeout: float) -> None:
        super().__init__(f"The request to the Lettermint API timed out after {timeout:g} seconds.")
        #: The timeout in seconds.
        self.timeout = timeout


class APIConnectionError(LettermintError):
    """The request could not be sent or the connection failed (DNS, TLS, refused, reset).

    The message names the underlying error. The exception is not chained to
    it, because HTTP library exceptions hold the request and its headers.
    """


class UnexpectedResponseError(LettermintError):
    """The response could not be decoded.

    An empty or non-JSON body where JSON was expected, or an error status
    with a non-JSON body such as a proxy's HTML error page.
    """

    def __init__(self, message: str, *, status: int, body: str) -> None:
        super().__init__(message)
        #: The HTTP status code.
        self.status = status
        #: The first 200 characters of the response body.
        self.body_excerpt = body if len(body) <= 200 else body[:200] + "…"


class RedirectError(LettermintError):
    """The API answered with a redirect (3xx).

    Redirects are never followed, so tokens are never sent to another location.
    """

    def __init__(self, status: int) -> None:
        super().__init__(
            f"The Lettermint API answered with a redirect (HTTP {status}). "
            "Redirects are not followed; check the base_url option."
        )
        #: The HTTP status code.
        self.status = status


#: Why a webhook delivery failed verification.
WebhookVerificationReason: TypeAlias = Literal[
    "signature_header_missing",
    "signature_header_malformed",
    "delivery_header_missing",
    "delivery_timestamp_mismatch",
    "timestamp_out_of_tolerance",
    "signature_mismatch",
    "body_invalid",
    "payload_invalid",
]


class WebhookVerificationError(LettermintError):
    """A webhook delivery could not be verified. Reject the request; do not process its payload."""

    def __init__(self, reason: WebhookVerificationReason, message: str) -> None:
        super().__init__(message)
        #: A machine-readable reason.
        self.reason: WebhookVerificationReason = reason
