from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import get_args, get_origin, get_type_hints

import pytest
import respx
from httpx import Response
from typing_extensions import NotRequired, Required

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
    def field_hint(model: type, field: str):
        selected = type(
            "SelectedField", (), {"__annotations__": {field: model.__annotations__[field]}}
        )
        return get_type_hints(selected, globalns=vars(lm_types), include_extras=True)[field]

    for model in [lm_types.WebhookData, lm_types.WebhookListData, lm_types.WebhookSecretData]:
        hint = field_hint(model, "has_basic_auth")
        assert get_origin(hint) is Required and get_args(hint) == (bool,)
    for model in [lm_types.StoreWebhookData, lm_types.UpdateWebhookData]:
        hint = field_hint(model, "basic_auth")
        assert get_origin(hint) is NotRequired
        assert set(get_args(get_args(hint)[0])) == {lm_types.WebhookBasicAuthData, type(None)}
        assert "has_basic_auth" not in model.__annotations__
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


@pytest.mark.parametrize("model", ["WebhookData", "WebhookListData", "WebhookSecretData"])
def test_old_typed_webhook_fixtures_need_safe_read_flag(tmp_path: Path, model: str) -> None:
    value = {
        "id": "fixture",
        "scope": "route",
        "project_ids": [],
        "route_ids": [],
        "route_id": None,
        "name": "Fixture",
        "url": "https://example.test/hook",
        "events": [],
        "enabled": True,
        "last_called_at": None,
        "created_at": "",
        "updated_at": "",
        "delivery_mode_filter": "both",
    }
    if model != "WebhookListData":
        value["include_machine_events"] = False
    if model == "WebhookSecretData":
        value["secret"] = "synthetic-signing-secret"
    caller = tmp_path / "old_caller.py"
    environment = {**os.environ, "MYPYPATH": str(Path(__file__).resolve().parents[1] / "src")}
    command = [
        sys.executable,
        "-m",
        "mypy",
        "--python-version",
        "3.10",
        "--follow-imports=silent",
        "--no-incremental",
        "--cache-dir",
        str(tmp_path / "mypy-cache"),
        str(caller),
    ]
    caller.write_text(f"from lettermint.types import {model}\nfixture: {model} = {value!r}\n")
    old = subprocess.run(command, env=environment, capture_output=True, text=True, check=False)
    assert (
        old.returncode == 1
        and f'Missing key "has_basic_auth" for TypedDict "{model}"' in old.stdout
    )
    assert "Found 1 error" in old.stdout
    value["has_basic_auth"] = False
    caller.write_text(f"from lettermint.types import {model}\nfixture: {model} = {value!r}\n")
    migrated = subprocess.run(command, env=environment, capture_output=True, text=True, check=False)
    assert migrated.returncode == 0, migrated.stdout + migrated.stderr
