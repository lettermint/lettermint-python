"""Verification of Lettermint webhook deliveries."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from collections.abc import Iterable, Mapping
from typing import Any, NoReturn, TypeAlias

from typing_extensions import Buffer, NotRequired, Required, TypedDict

from ._core import Secret
from ._emails import as_bytes
from ._generated.types import WebhookEvent
from .exceptions import LettermintConfigError, WebhookVerificationError, WebhookVerificationReason

__all__ = ["Webhook", "WebhookHeaders", "WebhookPayload"]

SIGNATURE_HEADER = "x-lettermint-signature"
DELIVERY_HEADER = "x-lettermint-delivery"
DEFAULT_TOLERANCE = 300
_PRINTABLE_ASCII = re.compile(r"[\x20-\x7e]*")
_DIGITS = re.compile(r"[0-9]+")
_HEX_SHA256 = re.compile(r"[0-9a-fA-F]{64}")
_MAX_SAFE_INTEGER = 2**53 - 1

#: Request headers: any mapping (``dict``, Django ``request.headers``, Flask,
#: Starlette, ``http.client`` messages, ``httpx.Headers``) or an iterable of
#: ``(name, value)`` pairs, such as the raw ASGI headers. Names are
#: case-insensitive; values may be ``str``, ``bytes`` or a list of them.
WebhookHeaders: TypeAlias = Mapping[Any, Any] | Iterable[tuple[Any, Any]]


class WebhookPayload(TypedDict):
    """A verified webhook delivery. The API may send more keys; they are kept."""

    #: The delivery id.
    id: NotRequired[str]
    #: The event name, for example ``message.delivered``. Unknown events pass through as strings.
    event: Required[WebhookEvent]
    #: When the event occurred, ISO 8601.
    timestamp: NotRequired[str]
    data: Required[dict[str, Any]]


def _fail(reason: WebhookVerificationReason, message: str) -> NoReturn:
    raise WebhookVerificationError(reason, message)


def _text(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("latin-1")
    return None


def _read_header(headers: WebhookHeaders, name: str) -> list[str | None]:
    """Every value of header ``name`` (case-insensitive); ``None`` for a value of another type."""
    if isinstance(headers, (str, bytes, bytearray)):
        raise TypeError(
            "Webhook.verify() takes the request headers (a mapping or (name, value) pairs); "
            "use verify_signature() for a signature header value"
        )
    pairs: Iterable[Any]
    if isinstance(headers, Mapping) or hasattr(headers, "items"):
        multi = getattr(headers, "multi_items", None)  # httpx.Headers joins duplicates in items()
        pairs = multi() if callable(multi) else headers.items()
    else:
        pairs = headers
    values: list[str | None] = []
    for pair in pairs:
        try:
            key, value = pair
        except (TypeError, ValueError):
            continue
        key_text = _text(key)
        if key_text is None or key_text.lower() != name:
            continue
        for item in value if isinstance(value, (list, tuple)) else [value]:
            if item is not None:
                values.append(_text(item))
    return values


def _parse_signature(header: str) -> tuple[str, list[bytes]]:
    def malformed(detail: str) -> NoReturn:
        _fail("signature_header_malformed", f"The signature header is malformed: {detail}.")

    if not _PRINTABLE_ASCII.fullmatch(header):
        malformed("it contains non-ASCII or control characters")
    timestamp: str | None = None
    signatures: list[bytes] = []
    for part in header.split(","):
        entry = part.strip()
        key, separator, value = entry.partition("=")
        if not separator:
            continue
        if key == "t":
            if timestamp is not None:
                malformed("it has more than one timestamp")
            if not _DIGITS.fullmatch(value) or len(value) > 16 or int(value) > _MAX_SAFE_INTEGER:
                malformed("the timestamp is not a number of seconds")
            timestamp = value
        elif key == "v1" and _HEX_SHA256.fullmatch(value):
            signatures.append(bytes.fromhex(value))
    if timestamp is None:
        malformed("the timestamp (t=) is missing")
    if not signatures:
        malformed("no v1 signature is present")
    return timestamp, signatures


def _body_bytes(body: object) -> bytes:
    binary = None if isinstance(body, str) else as_bytes(body)
    if isinstance(body, str):
        data = body.encode("utf-8")
    elif binary is not None:
        data = binary
    else:
        _fail("body_invalid", "Pass the raw request body (str or bytes), not parsed JSON.")
    if not data:
        _fail("body_invalid", "The raw request body is empty.")
    return data


class Webhook:
    """Verifies Lettermint webhook deliveries.

    The signature is HMAC-SHA256 over ``"<t>." + raw body`` with the
    endpoint's signing secret (``whsec_...``, used as is), compared in
    constant time. Any ``v1`` signature in the header may match.

    ::

        webhook = Webhook(os.environ["LETTERMINT_WEBHOOK_SECRET"])
        event = webhook.verify(request.body, request.headers)
    """

    __slots__ = ("_secret", "_tolerance")

    def __init__(self, secret: str, tolerance: int = DEFAULT_TOLERANCE) -> None:
        """
        Args:
            secret: The webhook's signing secret, including the ``whsec_`` prefix.
            tolerance: Maximum difference between the signed timestamp and the
                current time, in seconds, in either direction. ``0`` accepts
                only the current second; it does not disable the check.
        """
        if not isinstance(secret, str) or not secret:
            raise LettermintConfigError("The webhook signing secret must be a non-empty string.")
        if isinstance(tolerance, bool) or not isinstance(tolerance, int) or tolerance < 0:
            raise LettermintConfigError("tolerance must be a non-negative whole number of seconds.")
        self._secret = Secret(secret)
        self._tolerance = tolerance

    @property
    def tolerance(self) -> int:
        """The timestamp tolerance in seconds."""
        return self._tolerance

    def verify(self, raw_body: str | Buffer, headers: WebhookHeaders) -> WebhookPayload:
        """Verifies a delivery from its raw body and request headers; returns the payload.

        Requires ``X-Lettermint-Signature`` and ``X-Lettermint-Delivery``, which
        must equal the signed timestamp.

        Raises:
            WebhookVerificationError: The delivery is not genuine. Its ``reason``
                says why.
        """
        signatures = _read_header(headers, SIGNATURE_HEADER)
        if not signatures:
            _fail("signature_header_missing", "The X-Lettermint-Signature header is missing.")
        if len(signatures) > 1 or signatures[0] is None:
            _fail(
                "signature_header_malformed",
                "The request has more than one X-Lettermint-Signature header.",
            )
        deliveries = _read_header(headers, DELIVERY_HEADER)
        if not deliveries:
            _fail("delivery_header_missing", "The X-Lettermint-Delivery header is missing.")
        if len(deliveries) > 1 or deliveries[0] is None:
            _fail(
                "delivery_timestamp_mismatch",
                "The request has more than one X-Lettermint-Delivery header.",
            )
        return self.verify_signature(raw_body, signatures[0], deliveries[0])

    def verify_signature(
        self, raw_body: str | Buffer, signature_header: str, timestamp: str | int | None = None
    ) -> WebhookPayload:
        """Verifies the raw body against an ``X-Lettermint-Signature`` value.

        For setups where the headers are not at hand. When ``timestamp`` (the
        ``X-Lettermint-Delivery`` value) is given, it must equal the signed
        timestamp.

        Raises:
            WebhookVerificationError: The delivery is not genuine.
        """
        if not isinstance(signature_header, str) or not signature_header.strip():
            _fail("signature_header_missing", "The X-Lettermint-Signature header is missing.")
        signed_at, candidates = _parse_signature(signature_header)
        if timestamp is not None and str(timestamp).strip() != signed_at:
            _fail(
                "delivery_timestamp_mismatch",
                "The X-Lettermint-Delivery header does not match the signed timestamp.",
            )
        body = _body_bytes(raw_body)
        if abs(int(time.time()) - int(signed_at)) > self._tolerance:
            _fail(
                "timestamp_out_of_tolerance",
                "The signed timestamp is outside the allowed tolerance.",
            )
        key = self._secret.reveal().encode("utf-8")
        expected = hmac.new(key, signed_at.encode("ascii") + b"." + body, hashlib.sha256).digest()
        matched = False
        for candidate in candidates:
            matched |= hmac.compare_digest(candidate, expected)
        if not matched:
            _fail("signature_mismatch", "The webhook signature does not match.")
        try:
            payload = json.loads(body.decode("utf-8"))
        except ValueError:
            _fail("payload_invalid", "The webhook payload is not valid JSON.")
        if not isinstance(payload, dict):
            _fail("payload_invalid", "The webhook payload is not a JSON object.")
        return payload  # type: ignore[return-value]

    def __repr__(self) -> str:
        return f"Webhook(tolerance={self._tolerance})"

    def __reduce__(self) -> NoReturn:
        raise TypeError("Webhook verifiers cannot be pickled; they hold the signing secret")
