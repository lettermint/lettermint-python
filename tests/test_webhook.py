"""Tests for webhook verification."""

import hashlib
import hmac
import json
import time

import pytest

from lettermint import Webhook
from lettermint.exceptions import (
    InvalidSignatureError,
    JsonDecodeError,
    TimestampToleranceError,
    WebhookVerificationError,
)


def generate_valid_signature(
    payload: str, secret: str, timestamp: int | None = None
) -> tuple[str, int]:
    """Generate a valid signature for testing."""
    ts = timestamp or int(time.time())
    signed_content = f"{ts}.{payload}"
    signature = hmac.new(
        secret.encode(),
        signed_content.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"t={ts},v1={signature}", ts


class TestWebhook:
    """Tests for the Webhook class."""

    def test_verify_valid_signature(self, webhook_secret: str) -> None:
        """Test verifying a valid webhook signature."""
        payload = json.dumps({"event": "email.delivered", "data": {"message_id": "123"}})
        signature, timestamp = generate_valid_signature(payload, webhook_secret)

        webhook = Webhook(secret=webhook_secret)
        result = webhook.verify(payload, signature)

        assert result["event"] == "email.delivered"
        assert result["data"]["message_id"] == "123"

    def test_verify_with_timestamp_validation(self, webhook_secret: str) -> None:
        """Test verifying signature with cross-validated timestamp."""
        payload = json.dumps({"event": "email.delivered"})
        signature, timestamp = generate_valid_signature(payload, webhook_secret)

        webhook = Webhook(secret=webhook_secret)
        result = webhook.verify(payload, signature, timestamp)

        assert result["event"] == "email.delivered"

    def test_verify_headers(self, webhook_secret: str) -> None:
        """Test verifying webhook using headers."""
        payload = json.dumps({"event": "email.delivered"})
        signature, timestamp = generate_valid_signature(payload, webhook_secret)

        headers = {
            "X-Lettermint-Signature": signature,
            "X-Lettermint-Delivery": str(timestamp),
        }

        webhook = Webhook(secret=webhook_secret)
        result = webhook.verify_headers(headers, payload)

        assert result["event"] == "email.delivered"

    def test_verify_headers_case_insensitive(self, webhook_secret: str) -> None:
        """Test that header names are case-insensitive."""
        payload = json.dumps({"event": "email.delivered"})
        signature, timestamp = generate_valid_signature(payload, webhook_secret)

        headers = {
            "x-lettermint-signature": signature,
            "x-lettermint-delivery": str(timestamp),
        }

        webhook = Webhook(secret=webhook_secret)
        result = webhook.verify_headers(headers, payload)

        assert result["event"] == "email.delivered"

    def test_static_verify_signature(self, webhook_secret: str) -> None:
        """Test static convenience method."""
        payload = json.dumps({"event": "email.delivered"})
        signature, _ = generate_valid_signature(payload, webhook_secret)

        result = Webhook.verify_signature(payload, signature, webhook_secret)

        assert result["event"] == "email.delivered"

    def test_invalid_signature(self, webhook_secret: str) -> None:
        """Test that invalid signatures are rejected."""
        payload = json.dumps({"event": "email.delivered"})
        timestamp = int(time.time())
        invalid_signature = f"t={timestamp},v1=invalidsignaturehash"

        webhook = Webhook(secret=webhook_secret)
        with pytest.raises(InvalidSignatureError, match="Signature verification failed"):
            webhook.verify(payload, invalid_signature)

    def test_tampered_payload(self, webhook_secret: str) -> None:
        """Test that tampered payloads are rejected."""
        original_payload = json.dumps({"event": "email.delivered"})
        signature, _ = generate_valid_signature(original_payload, webhook_secret)

        tampered_payload = json.dumps({"event": "email.bounced"})

        webhook = Webhook(secret=webhook_secret)
        with pytest.raises(InvalidSignatureError):
            webhook.verify(tampered_payload, signature)

    def test_wrong_secret(self, webhook_secret: str) -> None:
        """Test that wrong secrets are rejected."""
        payload = json.dumps({"event": "email.delivered"})
        signature, _ = generate_valid_signature(payload, webhook_secret)

        webhook = Webhook(secret="wrong-secret")
        with pytest.raises(InvalidSignatureError):
            webhook.verify(payload, signature)

    def test_timestamp_too_old(self, webhook_secret: str) -> None:
        """Test that old timestamps are rejected."""
        payload = json.dumps({"event": "email.delivered"})
        old_timestamp = int(time.time()) - 600  # 10 minutes ago
        signature, _ = generate_valid_signature(payload, webhook_secret, old_timestamp)

        webhook = Webhook(secret=webhook_secret, tolerance=300)
        with pytest.raises(TimestampToleranceError, match="Timestamp outside tolerance"):
            webhook.verify(payload, signature)

    def test_timestamp_in_future(self, webhook_secret: str) -> None:
        """Test that future timestamps are rejected."""
        payload = json.dumps({"event": "email.delivered"})
        future_timestamp = int(time.time()) + 600  # 10 minutes in future
        signature, _ = generate_valid_signature(payload, webhook_secret, future_timestamp)

        webhook = Webhook(secret=webhook_secret, tolerance=300)
        with pytest.raises(TimestampToleranceError):
            webhook.verify(payload, signature)

    def test_custom_tolerance(self, webhook_secret: str) -> None:
        """Test custom timestamp tolerance."""
        payload = json.dumps({"event": "email.delivered"})
        old_timestamp = int(time.time()) - 400  # 6.67 minutes ago
        signature, _ = generate_valid_signature(payload, webhook_secret, old_timestamp)

        # Default tolerance (300s) should reject
        webhook_default = Webhook(secret=webhook_secret)
        with pytest.raises(TimestampToleranceError):
            webhook_default.verify(payload, signature)

        # Custom tolerance (600s) should accept
        webhook_custom = Webhook(secret=webhook_secret, tolerance=600)
        result = webhook_custom.verify(payload, signature)
        assert result["event"] == "email.delivered"

    def test_invalid_signature_format(self, webhook_secret: str) -> None:
        """Test that invalid signature format is rejected."""
        payload = json.dumps({"event": "email.delivered"})

        webhook = Webhook(secret=webhook_secret)

        # Missing timestamp
        with pytest.raises(WebhookVerificationError, match="Invalid signature format"):
            webhook.verify(payload, "v1=somehash")

        # Missing signature hash
        with pytest.raises(WebhookVerificationError, match="Invalid signature format"):
            webhook.verify(payload, "t=12345")

        # Completely invalid
        with pytest.raises(WebhookVerificationError, match="Invalid signature format"):
            webhook.verify(payload, "garbage")

    def test_timestamp_mismatch(self, webhook_secret: str) -> None:
        """Test timestamp mismatch between signature and delivery header."""
        payload = json.dumps({"event": "email.delivered"})
        signature, timestamp = generate_valid_signature(payload, webhook_secret)

        webhook = Webhook(secret=webhook_secret)
        with pytest.raises(WebhookVerificationError, match="Timestamp mismatch"):
            webhook.verify(payload, signature, timestamp + 1)

    def test_missing_signature_header(self, webhook_secret: str) -> None:
        """Test missing signature header."""
        payload = json.dumps({"event": "email.delivered"})

        headers = {
            "X-Lettermint-Delivery": "12345",
        }

        webhook = Webhook(secret=webhook_secret)
        with pytest.raises(WebhookVerificationError, match="Missing signature header"):
            webhook.verify_headers(headers, payload)

    def test_missing_delivery_header(self, webhook_secret: str) -> None:
        """Test missing delivery header."""
        payload = json.dumps({"event": "email.delivered"})
        signature, _ = generate_valid_signature(payload, webhook_secret)

        headers = {
            "X-Lettermint-Signature": signature,
        }

        webhook = Webhook(secret=webhook_secret)
        with pytest.raises(WebhookVerificationError, match="Missing delivery header"):
            webhook.verify_headers(headers, payload)

    def test_invalid_json_payload(self, webhook_secret: str) -> None:
        """Test invalid JSON payload."""
        payload = "not valid json {"
        timestamp = int(time.time())
        signed_content = f"{timestamp}.{payload}"
        signature = hmac.new(
            webhook_secret.encode(),
            signed_content.encode(),
            hashlib.sha256,
        ).hexdigest()
        signature_header = f"t={timestamp},v1={signature}"

        webhook = Webhook(secret=webhook_secret)
        with pytest.raises(JsonDecodeError, match="Failed to decode webhook payload"):
            webhook.verify(payload, signature_header)

    def test_empty_secret_raises_error(self) -> None:
        """Test that empty secret raises ValueError."""
        with pytest.raises(ValueError, match="Webhook secret cannot be empty"):
            Webhook(secret="")

    def test_complex_payload(self, webhook_secret: str) -> None:
        """Test verification with complex nested payload."""
        payload_data = {
            "event": "email.delivered",
            "data": {
                "message_id": "msg_123",
                "recipient": "user@example.com",
                "metadata": {"campaign_id": "456", "user_id": "789"},
                "timestamps": {"sent_at": 1700000000, "delivered_at": 1700000010},
            },
        }
        payload = json.dumps(payload_data)
        signature, _ = generate_valid_signature(payload, webhook_secret)

        webhook = Webhook(secret=webhook_secret)
        result = webhook.verify(payload, signature)

        assert result == payload_data
