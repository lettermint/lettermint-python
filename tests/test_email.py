"""Tests for the email endpoint."""

import asyncio
import json

import pytest
import respx
from httpx import Response

from lettermint import AsyncLettermint, Lettermint
from lettermint.exceptions import ClientError, ValidationError


class TestEmailEndpointSync:
    """Tests for the synchronous email endpoint."""

    @respx.mock
    def test_send_basic_email(self, api_token: str) -> None:
        """Test sending a basic email with required fields."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(
                200,
                json={"message_id": "msg_123", "status": "pending"},
            )
        )

        with Lettermint(api_token=api_token) as client:
            response = (
                client.email.from_("sender@example.com")
                .to("recipient@example.com")
                .subject("Test Subject")
                .send()
            )

        assert response["message_id"] == "msg_123"
        assert response["status"] == "pending"
        assert route.called

        request = route.calls.last.request
        assert request.headers["x-lettermint-token"] == api_token

    @respx.mock
    def test_send_with_multiple_recipients(self, api_token: str) -> None:
        """Test sending email with multiple recipients."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to(
                "recipient1@example.com", "recipient2@example.com"
            ).subject("Test").send()

        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["to"] == ["recipient1@example.com", "recipient2@example.com"]

    @respx.mock
    def test_send_with_html_and_text(self, api_token: str) -> None:
        """Test sending email with HTML and text content."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).html("<h1>Hello</h1>").text("Hello").send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["html"] == "<h1>Hello</h1>"
        assert body["text"] == "Hello"

    @respx.mock
    def test_send_with_cc_and_bcc(self, api_token: str) -> None:
        """Test sending email with CC and BCC recipients."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject("Test").cc(
                "cc1@example.com", "cc2@example.com"
            ).bcc("bcc@example.com").send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["cc"] == ["cc1@example.com", "cc2@example.com"]
        assert body["bcc"] == ["bcc@example.com"]

    @respx.mock
    def test_send_with_reply_to(self, api_token: str) -> None:
        """Test sending email with Reply-To addresses."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).reply_to("reply@example.com").send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["reply_to"] == ["reply@example.com"]

    @respx.mock
    def test_send_with_attachments(self, api_token: str) -> None:
        """Test sending email with attachments."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).attach("document.pdf", "base64content").attach(
                "logo.png", "base64image", "logo@example.com", "image/png"
            ).send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert len(body["attachments"]) == 2
        assert body["attachments"][0] == {"filename": "document.pdf", "content": "base64content"}
        assert body["attachments"][1] == {
            "filename": "logo.png",
            "content": "base64image",
            "content_id": "logo@example.com",
            "content_type": "image/png",
        }

    @respx.mock
    def test_send_with_custom_headers(self, api_token: str) -> None:
        """Test sending email with custom headers."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).headers(
                {
                    "Message-ID": "<ticket-123@example.com>",
                    "X-LM-Preserve-Message-ID": "true",
                }
            ).send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["headers"] == {
            "Message-ID": "<ticket-123@example.com>",
            "X-LM-Preserve-Message-ID": "true",
        }

    @respx.mock
    def test_send_with_idempotency_key(self, api_token: str) -> None:
        """Test sending email with idempotency key."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).idempotency_key("unique-key-123").send()

        request = route.calls.last.request
        assert request.headers["Idempotency-Key"] == "unique-key-123"

    @respx.mock
    def test_send_with_metadata_and_tag(self, api_token: str) -> None:
        """Test sending email with metadata and tag."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).metadata({"campaign_id": "123"}).tag("welcome").tags(
                [{"name": "campaign", "value": "welcome-v2"}]
            ).settings({"track_opens": False, "track_clicks": True, "tls": "enforced"}).send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["metadata"] == {"campaign_id": "123"}
        assert body["tag"] == "welcome"
        assert body["tags"] == [{"name": "campaign", "value": "welcome-v2"}]
        assert body["settings"] == {
            "track_opens": False,
            "track_clicks": True,
            "tls": "enforced",
        }

    @respx.mock
    def test_send_with_route(self, api_token: str) -> None:
        """Test sending email with route."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).route("my-route").send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["route"] == "my-route"

    @respx.mock
    def test_validation_error(self, api_token: str) -> None:
        """Test handling validation errors (422)."""
        respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(422, json={"error": "DailyLimitExceeded"})
        )

        with Lettermint(api_token=api_token) as client, pytest.raises(ValidationError) as exc_info:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).send()

        assert exc_info.value.status_code == 422
        assert exc_info.value.error_type == "DailyLimitExceeded"

    @respx.mock
    def test_client_error(self, api_token: str) -> None:
        """Test handling client errors (400)."""
        respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(400, json={"error": "Invalid request"})
        )

        with Lettermint(api_token=api_token) as client, pytest.raises(ClientError) as exc_info:
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Test"
            ).send()

        assert exc_info.value.status_code == 400

    @respx.mock
    def test_rfc_5322_addresses(self, api_token: str) -> None:
        """Test RFC 5322 format email addresses."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            client.email.from_("John Doe <john@example.com>").to(
                "Jane Doe <jane@example.com>"
            ).subject("Test").send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["from"] == "John Doe <john@example.com>"
        assert body["to"] == ["Jane Doe <jane@example.com>"]

    @respx.mock
    def test_payload_reset_after_send(self, api_token: str) -> None:
        """Test that payload is reset after sending."""
        respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        with Lettermint(api_token=api_token) as client:
            # First send
            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "First"
            ).tag("first").send()

            # Second send should not include tag from first send
            route = respx.post("https://api.lettermint.co/v1/send").mock(
                return_value=Response(200, json={"message_id": "msg_456", "status": "pending"})
            )

            client.email.from_("sender@example.com").to("recipient@example.com").subject(
                "Second"
            ).send()

        import json

        body = json.loads(route.calls.last.request.content)
        assert "tag" not in body


class TestEmailEndpointAsync:
    """Tests for the asynchronous email endpoint."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_send_basic_email_async(self, api_token: str) -> None:
        """Test sending a basic email asynchronously."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(
                200,
                json={"message_id": "msg_123", "status": "pending"},
            )
        )

        async with AsyncLettermint(api_token=api_token) as client:
            response = await (
                client.email.from_("sender@example.com")
                .to("recipient@example.com")
                .subject("Test Subject")
                .send()
            )

        assert response["message_id"] == "msg_123"
        assert response["status"] == "pending"
        assert route.called

    @respx.mock
    @pytest.mark.asyncio
    async def test_send_with_all_options_async(self, api_token: str) -> None:
        """Test sending email with all options asynchronously."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            return_value=Response(200, json={"message_id": "msg_123", "status": "pending"})
        )

        async with AsyncLettermint(api_token=api_token) as client:
            await (
                client.email.from_("sender@example.com")
                .to("recipient@example.com")
                .subject("Test")
                .html("<h1>Hello</h1>")
                .text("Hello")
                .cc("cc@example.com")
                .bcc("bcc@example.com")
                .reply_to("reply@example.com")
                .headers(
                    {
                        "Message-ID": "<ticket-123@example.com>",
                        "X-LM-Preserve-Message-ID": "true",
                    }
                )
                .attach("file.pdf", "base64content", None, "application/pdf")
                .metadata({"key": "value"})
                .tag("campaign")
                .settings({"track_opens": False, "tls": "enforced"})
                .route("my-route")
                .idempotency_key("unique-key")
                .send()
            )

        import json

        body = json.loads(route.calls.last.request.content)
        assert body["from"] == "sender@example.com"
        assert body["to"] == ["recipient@example.com"]
        assert body["subject"] == "Test"
        assert body["html"] == "<h1>Hello</h1>"
        assert body["text"] == "Hello"
        assert body["cc"] == ["cc@example.com"]
        assert body["bcc"] == ["bcc@example.com"]
        assert body["reply_to"] == ["reply@example.com"]
        assert body["headers"] == {
            "Message-ID": "<ticket-123@example.com>",
            "X-LM-Preserve-Message-ID": "true",
        }
        assert body["attachments"] == [
            {
                "filename": "file.pdf",
                "content": "base64content",
                "content_type": "application/pdf",
            }
        ]
        assert body["metadata"] == {"key": "value"}
        assert body["tag"] == "campaign"
        assert body["route"] == "my-route"
        assert body["settings"] == {"track_opens": False, "tls": "enforced"}

        request = route.calls.last.request
        assert request.headers["Idempotency-Key"] == "unique-key"

    @respx.mock
    @pytest.mark.asyncio
    async def test_send_batch_with_idempotency_key_async(self, api_token: str) -> None:
        """Test an asynchronous batch idempotency key."""
        route = respx.post("https://api.lettermint.co/v1/send/batch").mock(
            return_value=Response(200, json=[{"message_id": "msg_123", "status": "pending"}])
        )
        payload = [
            {
                "from": "sender@example.com",
                "to": ["recipient@example.com"],
                "subject": "Test",
            }
        ]

        async with AsyncLettermint(api_token=api_token) as client:
            await client.email.idempotency_key("batch-key").send_batch(payload)

        assert route.calls.last.request.headers["Idempotency-Key"] == "batch-key"

    @respx.mock
    @pytest.mark.asyncio
    async def test_deferred_async_sends_use_payload_snapshots(self, api_token: str) -> None:
        """Deferred async send coroutines must not share later builder mutations."""
        route = respx.post("https://api.lettermint.co/v1/send").mock(
            side_effect=[
                Response(200, json={"message_id": "msg_1", "status": "pending"}),
                Response(200, json={"message_id": "msg_2", "status": "pending"}),
            ]
        )

        async with AsyncLettermint(api_token=api_token) as client:
            first = (
                client.email.from_("sender@example.com")
                .to("first@example.com")
                .subject("First")
                .attach("secret.pdf", "base64secret")
                .metadata({"invoice": "123"})
                .idempotency_key("first-key")
                .send()
            )
            second = (
                client.email.from_("sender@example.com")
                .to("second@example.com")
                .subject("Second")
                .send()
            )

            await asyncio.gather(first, second)

        first_request = route.calls[0].request
        second_request = route.calls[1].request
        first_body = json.loads(first_request.content)
        second_body = json.loads(second_request.content)

        assert first_body["to"] == ["first@example.com"]
        assert first_body["attachments"] == [{"filename": "secret.pdf", "content": "base64secret"}]
        assert first_body["metadata"] == {"invoice": "123"}
        assert first_request.headers["Idempotency-Key"] == "first-key"

        assert second_body["to"] == ["second@example.com"]
        assert "attachments" not in second_body
        assert "metadata" not in second_body
        assert "Idempotency-Key" not in second_request.headers
