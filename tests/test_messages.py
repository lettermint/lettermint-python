"""``messages.resend``: the request, both tokens, idempotency and the errors of the endpoint."""

from __future__ import annotations

import pytest

from lettermint import (
    APIError,
    AsyncLettermint,
    Lettermint,
    LettermintConfigError,
    LettermintValidationError,
    RateLimitError,
)
from lettermint.types import PendingSendMailResponse

from .conftest import BASE_URL, SENDING_TOKEN, TEAM_TOKEN, MockAPI

ACCEPTED = {"message_id": "m2", "status": "pending"}


def test_resend_without_a_body_resends_to_every_recipient(api: MockAPI, client: Lettermint) -> None:
    api.json(202, ACCEPTED)
    result: PendingSendMailResponse = client.messages.resend("m1")
    assert result == ACCEPTED
    assert api.last.method == "POST"
    assert str(api.last.url) == f"{BASE_URL}/messages/m1/resend"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert "x-lettermint-token" not in api.last.headers
    assert api.last.content == b""
    assert "content-type" not in api.last.headers
    assert "idempotency-key" not in api.last.headers


def test_resend_to_chosen_recipients(api: MockAPI, client: Lettermint) -> None:
    api.json(202, ACCEPTED)
    client.messages.resend("m1", {"recipients": ["jane@example.test", "john@example.test"]})
    assert api.last.headers["content-type"] == "application/json"
    assert api.body() == {"recipients": ["jane@example.test", "john@example.test"]}


def test_resend_with_an_empty_body_sends_an_empty_object(api: MockAPI, client: Lettermint) -> None:
    api.json(202, ACCEPTED)
    client.messages.resend("m1", {})
    assert api.body() == {}


def test_resend_takes_an_idempotency_key(api: MockAPI, client: Lettermint) -> None:
    api.json(202, ACCEPTED)
    client.messages.resend("m1", idempotency_key="resend-m1")
    assert api.last.headers["idempotency-key"] == "resend-m1"
    client.messages.resend("m1", {"recipients": ["jane@example.test"]}, idempotency_key="k2")
    assert api.last.headers["idempotency-key"] == "k2"
    assert api.body() == {"recipients": ["jane@example.test"]}
    with pytest.raises(LettermintValidationError) as caught:
        client.messages.resend("m1", idempotency_key="")
    assert caught.value.field == "idempotency_key"
    assert len(api.requests) == 2


def test_resend_encodes_and_checks_the_message_id(api: MockAPI, client: Lettermint) -> None:
    api.json(202, ACCEPTED)
    client.messages.resend("a/b c")
    assert api.last.url.raw_path == b"/v1/messages/a%2Fb%20c/resend"
    with pytest.raises(LettermintConfigError, match=r"^messages\.resend: messageId must be"):
        client.messages.resend("")
    assert len(api.requests) == 1


def test_resend_accepts_the_sending_token(api: MockAPI) -> None:
    api.json(202, ACCEPTED)
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    sending_only.messages.resend("m1")
    assert api.last.headers["x-lettermint-token"] == SENDING_TOKEN
    assert "authorization" not in api.last.headers


def test_resend_of_a_message_whose_content_is_gone_is_an_api_error(
    api: MockAPI, client: Lettermint
) -> None:
    body = {
        "error": {
            "code": "MESSAGE_CONTENT_UNAVAILABLE",
            "message": "The content of this message is no longer retained.",
        }
    }
    api.json(410, body)
    with pytest.raises(APIError) as caught:
        client.messages.resend("m1")
    assert type(caught.value) is APIError
    assert (caught.value.status, caught.value.code, caught.value.body) == (
        410,
        "MESSAGE_CONTENT_UNAVAILABLE",
        body,
    )


def test_resend_limit_is_a_rate_limit_error(api: MockAPI, client: Lettermint) -> None:
    api.json(
        429,
        {"error": {"code": "RESEND_LIMIT_REACHED", "message": "Resend limit reached."}},
    )
    with pytest.raises(RateLimitError) as caught:
        client.messages.resend("m1")
    assert caught.value.code == "RESEND_LIMIT_REACHED"


@pytest.mark.anyio
async def test_async_resend(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(202, ACCEPTED)
    result: PendingSendMailResponse = await aclient.messages.resend(
        "m1", {"recipients": ["jane@example.test"]}, idempotency_key="resend-m1"
    )
    assert result == ACCEPTED
    assert str(api.last.url) == f"{BASE_URL}/messages/m1/resend"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert api.last.headers["idempotency-key"] == "resend-m1"
    assert api.body() == {"recipients": ["jane@example.test"]}
    await aclient.messages.resend("m1")
    assert api.last.content == b""
