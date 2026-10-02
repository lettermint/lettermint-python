from __future__ import annotations

import json
from typing import get_type_hints

import pytest
import respx
from httpx import Response

from lettermint import AsyncLettermint, HttpRequestError, Lettermint
from lettermint import types as lm_types


@pytest.mark.parametrize(
    "state",
    [{}, {"basic_auth": {"username": " fixture user ", "password": ""}}, {"basic_auth": None}],
)
@pytest.mark.parametrize("asynchronous", [False, True])
@respx.mock
@pytest.mark.asyncio
async def test_webhook_credential_states_keep_bearer_auth(state: dict, asynchronous: bool) -> None:
    create = respx.post("https://api.lettermint.co/v1/webhooks").mock(
        return_value=Response(201, json={"data": {"has_basic_auth": True}})
    )
    update = respx.put("https://api.lettermint.co/v1/webhooks/webhook-id").mock(
        return_value=Response(200, json={"data": {"has_basic_auth": True}})
    )
    payload = {
        "name": "Fixture",
        "url": "https://example.test/hook",
        "events": ["message.sent"],
        **state,
    }
    if asynchronous:
        async with AsyncLettermint.api("fixture-token") as api:
            assert (await api.webhooks.create(payload))["data"]["has_basic_auth"] is True
            assert (await api.webhooks.update("webhook-id", state))["data"][
                "has_basic_auth"
            ] is True
    else:
        with Lettermint.api("fixture-token") as sync_api:
            assert sync_api.webhooks.create(payload)["data"]["has_basic_auth"] is True
            assert sync_api.webhooks.update("webhook-id", state)["data"]["has_basic_auth"] is True
    for route, expected in [(create, payload), (update, state)]:
        request = route.calls.last.request
        assert json.loads(request.content) == expected
        assert request.headers["authorization"] == "Bearer fixture-token"
        assert "x-lettermint-token" not in request.headers


def test_webhook_types_expose_required_read_flag_and_optional_nullable_credentials() -> None:
    for model in [lm_types.WebhookData, lm_types.WebhookListData, lm_types.WebhookSecretData]:
        assert "Required[bool]" in str(get_type_hints(model, include_extras=True)["has_basic_auth"])
    for model in [lm_types.StoreWebhookData, lm_types.UpdateWebhookData]:
        assert "NotRequired" in str(get_type_hints(model, include_extras=True)["basic_auth"])
        assert "has_basic_auth" not in get_type_hints(model, include_extras=True)
    credentials: lm_types.WebhookBasicAuthData = {"username": "fixture", "password": ""}
    assert credentials["password"] == ""


@respx.mock
def test_free_plan_sandbox_keeps_403_response() -> None:
    body = {
        "error": {
            "code": "FEATURE_NOT_AVAILABLE",
            "message": "Sandbox mode is available only on paid plans.",
        }
    }
    respx.post("https://api.lettermint.co/v1/send").mock(return_value=Response(403, json=body))
    with Lettermint.email("fixture-token") as email, pytest.raises(HttpRequestError) as caught:
        email.from_("from@example.test").to("to@example.test").subject("Fixture").send()
    assert caught.value.status_code == 403
    assert caught.value.response_body == body
