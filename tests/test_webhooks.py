"""``webhooks.deliveries.retry`` and the delivery fields: the request, the token and the errors."""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from lettermint import (
    APIError,
    AsyncLettermint,
    ConflictError,
    Lettermint,
    LettermintConfigError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)
from lettermint.types import RetryWebhookDeliveryResponse, WebhookDeliveryData

from .conftest import BASE_URL, SENDING_TOKEN, TEAM_TOKEN, MockAPI

QUEUED = {"message": "Webhook delivery retry queued.", "delivery_id": "dl1"}


def test_retry_posts_without_a_body_with_the_team_token(api: MockAPI, client: Lettermint) -> None:
    api.json(202, QUEUED)
    result: RetryWebhookDeliveryResponse = client.webhooks.deliveries.retry("w1", "dl1")
    assert result == QUEUED
    assert api.last.method == "POST"
    assert str(api.last.url) == f"{BASE_URL}/webhooks/w1/deliveries/dl1/retry"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert "x-lettermint-token" not in api.last.headers
    assert api.last.content == b""
    assert "content-type" not in api.last.headers
    assert "idempotency-key" not in api.last.headers


def test_retry_takes_no_idempotency_key() -> None:
    for cls in (Lettermint, AsyncLettermint):
        client = cls(team_token=TEAM_TOKEN)
        parameters = inspect.signature(client.webhooks.deliveries.retry).parameters
        assert list(parameters) == ["webhook_id", "delivery_id", "timeout"]


def test_retry_needs_the_team_token(api: MockAPI) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(
        LettermintConfigError, match=r"^webhooks\.deliveries\.retry needs team_token"
    ):
        sending_only.webhooks.deliveries.retry("w1", "dl1")
    assert api.requests == []


def test_retry_encodes_and_checks_both_ids(api: MockAPI, client: Lettermint) -> None:
    api.json(202, QUEUED)
    client.webhooks.deliveries.retry("a/b", "c d")
    assert api.last.url.raw_path == b"/v1/webhooks/a%2Fb/deliveries/c%20d/retry"
    with pytest.raises(LettermintConfigError, match=r"^webhooks\.deliveries\.retry: webhookId"):
        client.webhooks.deliveries.retry("", "dl1")
    with pytest.raises(LettermintConfigError, match=r"^webhooks\.deliveries\.retry: deliveryId"):
        client.webhooks.deliveries.retry("w1", "..")
    assert len(api.requests) == 1


def test_a_delivery_that_cannot_be_retried_is_a_conflict(api: MockAPI, client: Lettermint) -> None:
    body = {
        "error": {
            "code": "WEBHOOK_DELIVERY_NOT_RETRYABLE",
            "message": "Only failed deliveries can be retried.",
        }
    }
    api.json(409, body)
    with pytest.raises(ConflictError) as caught:
        client.webhooks.deliveries.retry("w1", "dl1")
    assert isinstance(caught.value, APIError)
    assert (caught.value.status, caught.value.code, caught.value.body) == (
        409,
        "WEBHOOK_DELIVERY_NOT_RETRYABLE",
        body,
    )


@pytest.mark.parametrize(
    ("status", "body", "cls", "code"),
    [
        (404, {"message": "Not found."}, NotFoundError, None),
        (
            403,
            {"error": {"code": "FORBIDDEN", "message": "Forbidden."}},
            PermissionDeniedError,
            "FORBIDDEN",
        ),
        (403, {"message": "This action is unauthorized."}, PermissionDeniedError, None),
        (429, {"message": "Too Many Attempts."}, RateLimitError, None),
        (
            429,
            {"error": {"code": "RATE_LIMITED", "message": "Slow down."}},
            RateLimitError,
            "RATE_LIMITED",
        ),
    ],
)
def test_retry_errors_in_either_body_shape(
    api: MockAPI, client: Lettermint, status: int, body: Any, cls: type[APIError], code: str | None
) -> None:
    api.json(status, body, **{"Retry-After": "7"})
    with pytest.raises(cls) as caught:
        client.webhooks.deliveries.retry("w1", "dl1")
    assert type(caught.value) is cls
    assert (caught.value.status, caught.value.code, caught.value.body) == (status, code, body)
    if cls is RateLimitError:
        assert caught.value.retry_after == 7  # type: ignore[attr-defined]


@pytest.mark.anyio
async def test_async_retry(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(202, QUEUED)
    result: RetryWebhookDeliveryResponse = await aclient.webhooks.deliveries.retry("w1", "dl1")
    assert result == QUEUED
    assert api.last.method == "POST"
    assert str(api.last.url) == f"{BASE_URL}/webhooks/w1/deliveries/dl1/retry"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert api.last.content == b""


@pytest.mark.parametrize("next_retry_at", ["2026-10-18T12:05:00Z", None])
def test_deliveries_carry_next_retry_at(
    api: MockAPI, client: Lettermint, next_retry_at: str | None
) -> None:
    api.json(200, {"id": "dl1", "status": "failed", "next_retry_at": next_retry_at})
    delivery: WebhookDeliveryData = client.webhooks.deliveries.retrieve("w1", "dl1")
    assert delivery["next_retry_at"] == next_retry_at
    api.json(200, {"data": [{"id": "dl1", "next_retry_at": next_retry_at}], "next_cursor": None})
    page = client.webhooks.deliveries.list("w1")
    assert page["data"][0]["next_retry_at"] == next_retry_at
