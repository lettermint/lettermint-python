"""Webhook signature verification for the Lettermint SDK."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

from .exceptions import (
    InvalidSignatureError,
    JsonDecodeError,
    TimestampToleranceError,
    WebhookVerificationError,
)

SIGNATURE_HEADER = "X-Lettermint-Signature"
DELIVERY_HEADER = "X-Lettermint-Delivery"
DEFAULT_TOLERANCE = 300  # 5 minutes


class Webhook:
    """Webhook signature verifier for Lettermint webhooks.

    Verifies webhook signatures using HMAC-SHA256 and validates timestamps
    to prevent replay attacks.

    Args:
        secret: The webhook signing secret.
        tolerance: Maximum allowed time difference in seconds. Defaults to 300 (5 minutes).

    Raises:
        ValueError: If secret is empty.

    Example:
        >>> from lettermint import Webhook
        >>>
        >>> webhook = Webhook(secret="your-webhook-secret")
        >>> payload = webhook.verify_headers(request.headers, request.body)
        >>> print(payload["event"])
    """

    def __init__(self, secret: str, tolerance: int = DEFAULT_TOLERANCE) -> None:
        if not secret:
            raise ValueError("Webhook secret cannot be empty")
        self._secret = secret
        self._tolerance = tolerance

    def verify(
        self,
        payload: str,
        signature: str,
        timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Verify a webhook signature and return the decoded payload.

        Args:
            payload: The raw request body as a string.
            signature: The signature header value (format: t={timestamp},v1={hash}).
            timestamp: Optional timestamp from delivery header for cross-validation.

        Returns:
            The decoded webhook payload as a dictionary.

        Raises:
            WebhookVerificationError: If signature format is invalid or timestamps mismatch.
            InvalidSignatureError: If signature doesn't match.
            TimestampToleranceError: If timestamp is outside tolerance window.
            JsonDecodeError: If payload is not valid JSON.

        Example:
            >>> payload = webhook.verify(
            ...     payload=request_body,
            ...     signature=request.headers["X-Lettermint-Signature"],
            ... )
        """
        parsed = self._parse_signature(signature)
        signature_timestamp = parsed["timestamp"]
        expected_signature = parsed["signature"]

        if timestamp is not None and timestamp != signature_timestamp:
            raise WebhookVerificationError(
                "Timestamp mismatch between signature and delivery headers"
            )

        self._validate_timestamp(signature_timestamp)

        signed_content = f"{signature_timestamp}.{payload}"
        computed_signature = hmac.new(
            self._secret.encode(),
            signed_content.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(computed_signature, expected_signature):
            raise InvalidSignatureError("Signature verification failed")

        try:
            data: dict[str, Any] = json.loads(payload)
        except json.JSONDecodeError as e:
            raise JsonDecodeError(f"Failed to decode webhook payload: {e}") from e

        return data

    def verify_headers(
        self,
        headers: dict[str, str],
        payload: str,
    ) -> dict[str, Any]:
        """Verify a webhook using HTTP headers and return the decoded payload.

        Args:
            headers: HTTP headers from the request (case-insensitive).
            payload: The raw request body as a string.

        Returns:
            The decoded webhook payload as a dictionary.

        Raises:
            WebhookVerificationError: If required headers are missing or verification fails.
            InvalidSignatureError: If signature doesn't match.
            TimestampToleranceError: If timestamp is outside tolerance window.
            JsonDecodeError: If payload is not valid JSON.

        Example:
            >>> payload = webhook.verify_headers(
            ...     headers=dict(request.headers),
            ...     payload=request.body,
            ... )
        """
        normalized_headers = self._normalize_headers(headers)

        signature = normalized_headers.get(SIGNATURE_HEADER.lower())
        timestamp_str = normalized_headers.get(DELIVERY_HEADER.lower())

        if signature is None:
            raise WebhookVerificationError(f"Missing signature header: {SIGNATURE_HEADER}")

        if timestamp_str is None:
            raise WebhookVerificationError(f"Missing delivery header: {DELIVERY_HEADER}")

        try:
            timestamp = int(timestamp_str)
        except ValueError:
            raise WebhookVerificationError(
                f"Invalid timestamp format in {DELIVERY_HEADER} header"
            ) from None

        return self.verify(payload, signature, timestamp)

    @staticmethod
    def verify_signature(
        payload: str,
        signature: str,
        secret: str,
        timestamp: int | None = None,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> dict[str, Any]:
        """Static convenience method to verify a webhook signature.

        Args:
            payload: The raw request body as a string.
            signature: The signature header value (format: t={timestamp},v1={hash}).
            secret: The webhook signing secret.
            timestamp: Optional timestamp from delivery header for cross-validation.
            tolerance: Maximum allowed time difference in seconds. Defaults to 300.

        Returns:
            The decoded webhook payload as a dictionary.

        Raises:
            ValueError: If secret is empty.
            WebhookVerificationError: If signature format is invalid or timestamps mismatch.
            InvalidSignatureError: If signature doesn't match.
            TimestampToleranceError: If timestamp is outside tolerance window.
            JsonDecodeError: If payload is not valid JSON.

        Example:
            >>> payload = Webhook.verify_signature(
            ...     payload=request_body,
            ...     signature=request.headers["X-Lettermint-Signature"],
            ...     secret="your-webhook-secret",
            ... )
        """
        webhook = Webhook(secret, tolerance)
        return webhook.verify(payload, signature, timestamp)

    def _parse_signature(self, signature: str) -> dict[str, Any]:
        """Parse the signature header into timestamp and signature hash."""
        parts = signature.split(",")

        parsed_timestamp: int | None = None
        parsed_signature: str | None = None

        for part in parts:
            key_value = part.split("=", 1)
            if len(key_value) != 2:
                continue

            key, value = key_value

            if key == "t":
                try:
                    parsed_timestamp = int(value)
                except ValueError:
                    continue
            elif key == "v1":
                parsed_signature = value

        if parsed_timestamp is None or parsed_signature is None:
            raise WebhookVerificationError(
                "Invalid signature format. Expected format: t={timestamp},v1={signature}"
            )

        return {
            "timestamp": parsed_timestamp,
            "signature": parsed_signature,
        }

    def _validate_timestamp(self, timestamp: int) -> None:
        """Validate that the timestamp is within the tolerance window."""
        current_time = int(time.time())
        difference = abs(current_time - timestamp)

        if difference > self._tolerance:
            raise TimestampToleranceError(
                f"Timestamp outside tolerance window. "
                f"Difference: {difference} seconds, Tolerance: {self._tolerance} seconds"
            )

    def _normalize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Normalize headers to lowercase keys."""
        return {key.lower(): value for key, value in headers.items()}
