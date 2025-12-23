"""Tests for the HTTP client."""

import pytest
import respx
from httpx import Response

from lettermint.client import AsyncLettermintClient, LettermintClient
from lettermint.exceptions import (
    ClientError,
    HttpRequestError,
    TimeoutError,
    ValidationError,
)


class TestLettermintClientSync:
    """Tests for the synchronous HTTP client."""

    @respx.mock
    def test_get_request(self) -> None:
        """Test GET request."""
        route = respx.get("https://api.lettermint.co/v1/test").mock(
            return_value=Response(200, json={"result": "success"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            result = client.get("/test")
            assert result == {"result": "success"}
            assert route.called
            assert route.calls.last.request.headers["x-lettermint-token"] == "test-token"
        finally:
            client.close()

    @respx.mock
    def test_post_request(self) -> None:
        """Test POST request."""
        route = respx.post("https://api.lettermint.co/v1/test").mock(
            return_value=Response(200, json={"result": "created"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            result = client.post("/test", data={"key": "value"})
            assert result == {"result": "created"}

            import json

            body = json.loads(route.calls.last.request.content)
            assert body == {"key": "value"}
        finally:
            client.close()

    @respx.mock
    def test_put_request(self) -> None:
        """Test PUT request."""
        route = respx.put("https://api.lettermint.co/v1/test").mock(
            return_value=Response(200, json={"result": "updated"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            result = client.put("/test", data={"key": "value"})
            assert result == {"result": "updated"}
        finally:
            client.close()

    @respx.mock
    def test_delete_request(self) -> None:
        """Test DELETE request."""
        route = respx.delete("https://api.lettermint.co/v1/test").mock(
            return_value=Response(200, json={"result": "deleted"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            result = client.delete("/test")
            assert result == {"result": "deleted"}
        finally:
            client.close()

    @respx.mock
    def test_custom_base_url(self) -> None:
        """Test custom base URL."""
        route = respx.get("https://custom.api.com/v2/test").mock(
            return_value=Response(200, json={"result": "success"})
        )

        client = LettermintClient(api_token="test-token", base_url="https://custom.api.com/v2")
        try:
            client.get("/test")
            assert route.called
        finally:
            client.close()

    @respx.mock
    def test_additional_headers(self) -> None:
        """Test additional request headers."""
        route = respx.get("https://api.lettermint.co/v1/test").mock(
            return_value=Response(200, json={"result": "success"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            client.get("/test", headers={"X-Custom": "header"})
            assert route.calls.last.request.headers["X-Custom"] == "header"
        finally:
            client.close()

    @respx.mock
    def test_validation_error_422(self) -> None:
        """Test 422 validation error handling."""
        respx.post("https://api.lettermint.co/v1/test").mock(
            return_value=Response(422, json={"error": "DailyLimitExceeded"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            with pytest.raises(ValidationError) as exc_info:
                client.post("/test", data={})

            assert exc_info.value.status_code == 422
            assert exc_info.value.error_type == "DailyLimitExceeded"
            assert exc_info.value.response_body == {"error": "DailyLimitExceeded"}
        finally:
            client.close()

    @respx.mock
    def test_client_error_400(self) -> None:
        """Test 400 client error handling."""
        respx.post("https://api.lettermint.co/v1/test").mock(
            return_value=Response(400, json={"error": "Bad request"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            with pytest.raises(ClientError) as exc_info:
                client.post("/test", data={})

            assert exc_info.value.status_code == 400
        finally:
            client.close()

    @respx.mock
    def test_http_error_500(self) -> None:
        """Test 500 server error handling."""
        respx.get("https://api.lettermint.co/v1/test").mock(
            return_value=Response(500, json={"error": "Internal server error"})
        )

        client = LettermintClient(api_token="test-token")
        try:
            with pytest.raises(HttpRequestError) as exc_info:
                client.get("/test")

            assert exc_info.value.status_code == 500
        finally:
            client.close()

    def test_context_manager(self) -> None:
        """Test context manager usage."""
        with LettermintClient(api_token="test-token") as client:
            assert client._api_token == "test-token"


class TestAsyncLettermintClient:
    """Tests for the asynchronous HTTP client."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_request_async(self) -> None:
        """Test async GET request."""
        route = respx.get("https://api.lettermint.co/v1/test").mock(
            return_value=Response(200, json={"result": "success"})
        )

        async with AsyncLettermintClient(api_token="test-token") as client:
            result = await client.get("/test")
            assert result == {"result": "success"}
            assert route.called

    @respx.mock
    @pytest.mark.asyncio
    async def test_post_request_async(self) -> None:
        """Test async POST request."""
        route = respx.post("https://api.lettermint.co/v1/test").mock(
            return_value=Response(200, json={"result": "created"})
        )

        async with AsyncLettermintClient(api_token="test-token") as client:
            result = await client.post("/test", data={"key": "value"})
            assert result == {"result": "created"}

    @respx.mock
    @pytest.mark.asyncio
    async def test_error_handling_async(self) -> None:
        """Test async error handling."""
        respx.get("https://api.lettermint.co/v1/test").mock(
            return_value=Response(422, json={"error": "ValidationError"})
        )

        async with AsyncLettermintClient(api_token="test-token") as client:
            with pytest.raises(ValidationError):
                await client.get("/test")
