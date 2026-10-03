"""Requests, decoding, errors, redirects, timeouts and cancellation, for both clients."""

from __future__ import annotations

import email.utils
import socket
import threading
import time
from collections.abc import AsyncIterator, Iterator
from typing import Any

import anyio
import httpx
import pytest

from lettermint import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncLettermint,
    AuthenticationError,
    ConflictError,
    Lettermint,
    LettermintConfigError,
    LettermintError,
    LettermintValidationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    RedirectError,
    ServerError,
    UnexpectedResponseError,
    ValidationError,
)

from .conftest import BASE_URL, MESSAGE, SENDING_TOKEN, TEAM_TOKEN, MockAPI

HTML_502 = (
    "<html><head><title>502 Bad Gateway</title></head><body><h1>502 Bad Gateway</h1></body></html>"
)


def assert_detached(error: BaseException) -> None:
    """No chained exception (which could hold the httpx request), no token anywhere."""
    assert error.__cause__ is None
    assert error.__context__ is None
    for text in (str(error), repr(error), repr(vars(error))):
        assert SENDING_TOKEN not in text
        assert TEAM_TOKEN not in text


# ---------------------------------------------------------------- headers and tokens


def test_emails_use_the_sending_token_only(api: MockAPI, client: Lettermint) -> None:
    api.json(202, {"message_id": "m1", "status": "pending"})
    client.emails.send(MESSAGE)
    assert api.last.method == "POST"
    assert str(api.last.url) == f"{BASE_URL}/send"
    assert api.last.headers["x-lettermint-token"] == SENDING_TOKEN
    assert "authorization" not in api.last.headers
    assert api.last.headers["content-type"] == "application/json"


def test_team_api_uses_the_team_token_only(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"data": [], "next_cursor": None})
    client.domains.list()
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert "x-lettermint-token" not in api.last.headers


def test_ping_prefers_the_team_token(api: MockAPI) -> None:
    api.respond(lambda request: httpx.Response(200, text=" pong\n"))
    both = Lettermint(
        sending_token=SENDING_TOKEN,
        team_token=TEAM_TOKEN,
        base_url=BASE_URL,
        http_client=api.sync_client(),
    )
    assert both.ping() == "pong"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert both.emails.ping() == "pong"
    assert api.last.headers["x-lettermint-token"] == SENDING_TOKEN
    assert "authorization" not in api.last.headers
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    sending_only.ping()
    assert api.last.headers["x-lettermint-token"] == SENDING_TOKEN


def test_reschedule_and_cancel_accept_either_token(api: MockAPI) -> None:
    api.json(200, {"message_id": "m1", "status": "canceled", "scheduled_at": None})
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    sending_only.messages.cancel("m1")
    assert api.last.headers["x-lettermint-token"] == SENDING_TOKEN
    sending_only.messages.reschedule("m1", {"scheduled_at": "2026-10-20T09:00:00Z"})
    assert api.last.method == "PATCH"
    team = Lettermint(
        sending_token=SENDING_TOKEN,
        team_token=TEAM_TOKEN,
        base_url=BASE_URL,
        http_client=api.sync_client(),
    )
    team.messages.cancel("m1")
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"


def test_a_missing_token_is_a_config_error_that_names_the_option(api: MockAPI) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(
        LettermintConfigError,
        match=r"^domains\.list needs team_token; pass Lettermint\(team_token=\.\.\.\)\.$",
    ):
        sending_only.domains.list()
    with pytest.raises(LettermintConfigError, match=r"domains\.iterate needs team_token"):
        sending_only.domains.iterate()
    team_only = Lettermint(TEAM_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(LettermintConfigError, match=r"emails\.send needs sending_token"):
        team_only.emails.send(MESSAGE)
    with pytest.raises(LettermintConfigError, match=r"emails\.compose needs sending_token"):
        team_only.emails.compose()
    with pytest.raises(LettermintConfigError, match=r"emails\.ping needs sending_token"):
        team_only.emails.ping()
    assert api.requests == []


# ---------------------------------------------------------------- paths and bodies


def test_path_parameters_are_encoded(api: MockAPI, client: Lettermint) -> None:
    client.domains.retrieve("a/b c?d")
    assert api.last.url.raw_path == b"/v1/domains/a%2Fb%20c%3Fd"


@pytest.mark.parametrize("value", ["", ".", "..", None, 42])
def test_invalid_path_parameters_are_rejected_before_the_request(
    api: MockAPI, client: Lettermint, value: Any
) -> None:
    with pytest.raises(
        LettermintConfigError,
        match=r'domains\.retrieve: domainId must be a non-empty string other than "\." and "\.\."',
    ):
        client.domains.retrieve(value)
    with pytest.raises(LettermintConfigError, match=r"webhooks\.deliveries\.iterate: webhookId"):
        client.webhooks.deliveries.iterate(value)
    assert api.requests == []


def test_a_body_that_is_not_json_is_rejected(api: MockAPI, client: Lettermint) -> None:
    with pytest.raises(
        LettermintValidationError,
        match=r"domains\.create: the request body cannot be encoded as JSON",
    ):
        client.domains.create({"domain": float("nan")})  # type: ignore[typeddict-item]
    assert api.requests == []


# ---------------------------------------------------------------- decoding


def test_204_returns_none(api: MockAPI, client: Lettermint) -> None:
    api.respond(lambda request: httpx.Response(204))
    delete: Any = client.projects.report_forwarding.delete
    assert delete("p1") is None


def test_text_endpoints_return_strings(api: MockAPI, client: Lettermint) -> None:
    api.respond(
        lambda request: httpx.Response(
            200, text="<p>Hi</p>", headers={"content-type": "text/html; charset=UTF-8"}
        )
    )
    assert client.messages.html("m1") == "<p>Hi</p>"
    api.respond(
        lambda request: httpx.Response(
            200,
            content="Grüße".encode("latin-1"),
            headers={"content-type": "text/plain; charset=ISO-8859-1"},
        )
    )
    assert client.messages.text("m1") == "Grüße"
    api.respond(lambda request: httpx.Response(200, content=b"Received: x\r\n"))
    assert client.messages.source("m1") == "Received: x\r\n"


def test_unknown_enum_values_and_fields_are_kept(api: MockAPI, client: Lettermint) -> None:
    api.json(
        202,
        {"message_id": "m1", "status": "some_future_status", "some_future_field": {"nested": [1]}},
    )
    # The status of a send is a discriminator (Literal), but the raw value is kept.
    result: dict[str, Any] = dict(client.emails.send(MESSAGE))
    assert result["status"] == "some_future_status"
    assert result["some_future_field"] == {"nested": [1]}


@pytest.mark.parametrize(
    ("response", "status", "message"),
    [
        (
            httpx.Response(202, headers={"content-type": "application/json"}),
            202,
            "an empty body where JSON was expected",
        ),
        (httpx.Response(202, text="  \n"), 202, "an empty body where JSON was expected"),
        (httpx.Response(200, text="pong"), 200, "a body that is not valid JSON"),
        (
            httpx.Response(
                502, text=HTML_502, headers={"content-type": "text/html; charset=UTF-8"}
            ),
            502,
            r"HTTP 502 and a body that is not JSON \(text/html\)",
        ),
        (httpx.Response(101), 101, "unexpected HTTP status 101"),
    ],
)
def test_unexpected_responses_are_typed(
    api: MockAPI, client: Lettermint, response: httpx.Response, status: int, message: str
) -> None:
    api.respond(lambda request: response)
    with pytest.raises(UnexpectedResponseError, match=message) as caught:
        client.emails.send(MESSAGE)
    assert caught.value.status == status
    assert_detached(caught.value)


def test_unexpected_response_keeps_a_short_excerpt(api: MockAPI, client: Lettermint) -> None:
    api.respond(lambda request: httpx.Response(502, text="x" * 500))
    with pytest.raises(UnexpectedResponseError) as caught:
        client.emails.send(MESSAGE)
    assert caught.value.body_excerpt == "x" * 200 + "…"


@pytest.mark.parametrize(
    ("status", "cls"),
    [
        (400, APIError),
        (401, AuthenticationError),
        (403, PermissionDeniedError),
        (404, NotFoundError),
        (409, ConflictError),
        (410, APIError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, ServerError),
        (503, ServerError),
    ],
)
def test_api_errors_map_to_classes(
    api: MockAPI, client: Lettermint, status: int, cls: type[APIError]
) -> None:
    body = {
        "error": {"code": "some_code", "message": "Something went wrong", "details": {"field": "x"}}
    }
    api.json(status, body)
    with pytest.raises(cls) as caught:
        client.emails.send(MESSAGE)
    error = caught.value
    assert type(error) is cls
    assert isinstance(error, APIError) and isinstance(error, LettermintError)
    assert (error.status, error.code, error.message, error.details, error.body) == (
        status,
        "some_code",
        "Something went wrong",
        {"field": "x"},
        body,
    )
    assert str(error) == "Something went wrong"
    assert_detached(error)


def test_laravel_validation_errors(api: MockAPI, client: Lettermint) -> None:
    body = {"message": "The to field is required.", "errors": {"to": ["The to field is required."]}}
    api.json(422, body)
    with pytest.raises(ValidationError) as caught:
        client.emails.send(MESSAGE)
    assert caught.value.message == "The to field is required."
    assert caught.value.errors == {"to": ["The to field is required."]}
    assert caught.value.code is None


def test_string_error_codes_and_reason_phrase_fallback(api: MockAPI, client: Lettermint) -> None:
    api.json(400, {"error": "DailyLimitExceeded"})
    with pytest.raises(APIError) as caught:
        client.emails.send(MESSAGE)
    assert (caught.value.code, caught.value.message) == ("DailyLimitExceeded", "Bad Request")
    api.respond(lambda request: httpx.Response(500))
    with pytest.raises(ServerError) as server:
        client.emails.send(MESSAGE)
    assert (server.value.message, server.value.body) == ("Internal Server Error", None)


def test_retry_after_seconds_and_http_dates(api: MockAPI, client: Lettermint) -> None:
    api.json(429, {"message": "Too Many Attempts."}, **{"Retry-After": "17"})
    with pytest.raises(RateLimitError) as caught:
        client.emails.send(MESSAGE)
    assert caught.value.retry_after == 17
    later = email.utils.formatdate(time.time() + 120, usegmt=True)
    api.json(429, {}, **{"Retry-After": later})
    with pytest.raises(RateLimitError) as dated:
        client.emails.send(MESSAGE)
    assert dated.value.retry_after is not None and 115 <= dated.value.retry_after <= 121
    api.json(429, {}, **{"Retry-After": "soon"})
    with pytest.raises(RateLimitError) as unparsable:
        client.emails.send(MESSAGE)
    assert unparsable.value.retry_after is None


def test_errors_survive_pickling(api: MockAPI, client: Lettermint) -> None:
    import pickle

    api.json(429, {"message": "slow down"}, **{"Retry-After": "3"})
    with pytest.raises(RateLimitError) as caught:
        client.emails.send(MESSAGE)
    copy = pickle.loads(pickle.dumps(caught.value))
    assert (type(copy), copy.status, copy.retry_after, str(copy)) == (
        RateLimitError,
        429,
        3,
        "slow down",
    )


# ---------------------------------------------------------------- redirects


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_redirects_are_never_followed(api: MockAPI, status: int) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "foreign.test":
            return httpx.Response(202, json={"message_id": "captured", "status": "pending"})
        return httpx.Response(status, headers={"Location": "https://foreign.test/v1/send"})

    api.respond(handler)
    # Even a client configured to follow redirects does not follow them for the SDK.
    client = Lettermint(
        sending_token=SENDING_TOKEN,
        team_token=TEAM_TOKEN,
        base_url=BASE_URL,
        http_client=api.sync_client(follow_redirects=True),
    )
    with pytest.raises(RedirectError) as caught:
        client.emails.send(MESSAGE)
    assert caught.value.status == status
    with pytest.raises(RedirectError):
        client.ping()
    assert {request.url.host for request in api.requests} == {"api.lettermint.test"}
    assert_detached(caught.value)


@pytest.mark.anyio
async def test_async_redirects_are_never_followed(api: MockAPI) -> None:
    api.respond(
        lambda request: httpx.Response(307, headers={"Location": "https://foreign.test/v1/ping"})
    )
    client = AsyncLettermint(
        TEAM_TOKEN, base_url=BASE_URL, http_client=api.async_client(follow_redirects=True)
    )
    with pytest.raises(RedirectError) as caught:
        await client.ping()
    assert caught.value.status == 307
    assert len(api.requests) == 1


# ---------------------------------------------------------------- connection errors


def test_connection_errors_are_wrapped_without_the_request(
    api: MockAPI, client: Lettermint
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            f"refused, header was {request.headers['x-lettermint-token']}", request=request
        )

    api.respond(handler)
    with pytest.raises(APIConnectionError) as caught:
        client.emails.send(MESSAGE)
    assert (
        str(caught.value)
        == "emails.send: could not reach the Lettermint API (ConnectError: refused, header was [redacted])"
    )
    assert_detached(caught.value)


@pytest.mark.anyio
async def test_async_connection_errors_are_wrapped_without_the_request(
    api: MockAPI, aclient: AsyncLettermint
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.RemoteProtocolError("Server disconnected", request=request)

    api.respond(handler)
    with pytest.raises(
        APIConnectionError, match="RemoteProtocolError: Server disconnected"
    ) as caught:
        await aclient.domains.list()
    assert_detached(caught.value)


def _closed_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_a_refused_connection_is_a_connection_error() -> None:
    client = Lettermint(SENDING_TOKEN, base_url=f"http://127.0.0.1:{_closed_port()}/v1", timeout=5)
    with pytest.raises(APIConnectionError) as caught:
        client.emails.ping()
    assert_detached(caught.value)
    client.close()


@pytest.mark.anyio
async def test_async_refused_connection_is_a_connection_error() -> None:
    async with AsyncLettermint(
        SENDING_TOKEN, base_url=f"http://127.0.0.1:{_closed_port()}/v1", timeout=5
    ) as client:
        with pytest.raises(APIConnectionError) as caught:
            await client.emails.ping()
    assert_detached(caught.value)


def test_exceptions_from_application_hooks_propagate_unchanged(api: MockAPI) -> None:
    def hook(request: httpx.Request) -> None:
        raise KeyError("from the application")

    client = Lettermint(
        SENDING_TOKEN,
        base_url=BASE_URL,
        http_client=api.sync_client(event_hooks={"request": [hook]}),
    )
    with pytest.raises(KeyError, match="from the application"):
        client.emails.ping()


# ---------------------------------------------------------------- timeouts


class SlowStream(httpx.SyncByteStream, httpx.AsyncByteStream):
    """A body that arrives in small pieces, each well within httpx's read timeout."""

    def __init__(self, pieces: int, delay: float) -> None:
        self.pieces = pieces
        self.delay = delay

    def __iter__(self) -> Iterator[bytes]:
        yield b'{"message_id": "m1",'
        for _ in range(self.pieces):
            time.sleep(self.delay)
            yield b" "
        yield b'"status": "pending"}'

    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b'{"message_id": "m1",'
        for _ in range(self.pieces):
            await anyio.sleep(self.delay)
            yield b" "
        yield b'"status": "pending"}'


def test_the_timeout_covers_a_slow_body(api: MockAPI) -> None:
    api.respond(lambda request: httpx.Response(202, stream=SlowStream(pieces=40, delay=0.05)))
    client = Lettermint(
        SENDING_TOKEN, base_url=BASE_URL, timeout=0.5, http_client=api.sync_client()
    )
    started = time.monotonic()
    with pytest.raises(APITimeoutError) as caught:
        client.emails.send(MESSAGE)
    assert time.monotonic() - started < 1.5
    assert caught.value.timeout == 0.5
    assert str(caught.value) == "The request to the Lettermint API timed out after 0.5 seconds."
    assert_detached(caught.value)


def test_the_timeout_covers_slow_headers(api: MockAPI) -> None:
    released = threading.Event()

    def handler(request: httpx.Request) -> httpx.Response:
        released.wait(5)
        return httpx.Response(202, json={"message_id": "m1", "status": "pending"})

    api.respond(handler)
    client = Lettermint(
        SENDING_TOKEN, base_url=BASE_URL, timeout=0.3, http_client=api.sync_client()
    )
    started = time.monotonic()
    with pytest.raises(APITimeoutError):
        client.emails.send(MESSAGE)
    assert time.monotonic() - started < 1.5
    released.set()


def test_a_per_call_timeout_overrides_the_client_timeout(api: MockAPI) -> None:
    api.respond(lambda request: httpx.Response(202, stream=SlowStream(pieces=4, delay=0.05)))
    client = Lettermint(
        SENDING_TOKEN, base_url=BASE_URL, timeout=0.05, http_client=api.sync_client()
    )
    assert client.emails.send(MESSAGE, timeout=5)["message_id"] == "m1"
    with pytest.raises(LettermintConfigError, match="timeout must be a positive number"):
        client.emails.send(MESSAGE, timeout=-1)


@pytest.mark.anyio
async def test_async_timeout_covers_a_slow_body(api: MockAPI) -> None:
    api.respond(lambda request: httpx.Response(202, stream=SlowStream(pieces=40, delay=0.05)))
    client = AsyncLettermint(
        SENDING_TOKEN, base_url=BASE_URL, timeout=0.5, http_client=api.async_client()
    )
    started = time.monotonic()
    with pytest.raises(APITimeoutError) as caught:
        await client.emails.send(MESSAGE)
    assert time.monotonic() - started < 1.5
    assert_detached(caught.value)


@pytest.mark.anyio
async def test_async_cancellation_is_not_converted(api: MockAPI) -> None:
    started = anyio.Event()

    async def handler(request: httpx.Request) -> httpx.Response:
        started.set()
        await anyio.sleep(10)
        return httpx.Response(200, text="pong")

    api.respond(handler)
    client = AsyncLettermint(TEAM_TOKEN, base_url=BASE_URL, http_client=api.async_client())
    outcome: list[str] = []

    async def ping() -> None:
        try:
            await client.ping()
        except LettermintError:
            outcome.append("sdk error")
            raise
        except BaseException:
            outcome.append("cancelled")
            raise

    async with anyio.create_task_group() as group:
        group.start_soon(ping)
        await started.wait()
        group.cancel_scope.cancel()
    assert outcome == ["cancelled"]


# ---------------------------------------------------------------- idempotency


def test_idempotency_keys_are_per_call(api: MockAPI, client: Lettermint) -> None:
    api.json(202, {"message_id": "m1", "status": "pending"})
    client.emails.send(MESSAGE, idempotency_key="key-1")
    assert api.last.headers["idempotency-key"] == "key-1"
    client.emails.send(MESSAGE)
    assert "idempotency-key" not in api.last.headers
    client.messages.process("m1", idempotency_key="process-1")
    assert api.last.headers["idempotency-key"] == "process-1"


@pytest.mark.parametrize("key", ["", "a\nb", "a\rb", "a\0b", 42])
def test_invalid_idempotency_keys_are_rejected(api: MockAPI, client: Lettermint, key: Any) -> None:
    with pytest.raises(LettermintValidationError) as caught:
        client.emails.send(MESSAGE, idempotency_key=key)
    assert caught.value.field == "idempotency_key"
    assert api.requests == []


def test_no_automatic_retries(api: MockAPI, client: Lettermint) -> None:
    api.json(503, {"message": "down"})
    with pytest.raises(ServerError):
        client.emails.send(MESSAGE, idempotency_key="k")
    assert len(api.requests) == 1
