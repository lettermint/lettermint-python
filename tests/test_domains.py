"""``domains``: the managed DKIM upgrade and DKIM key rotation."""

from __future__ import annotations

from typing import Any

import pytest

from lettermint import (
    AsyncLettermint,
    Lettermint,
    LettermintConfigError,
    NotFoundError,
    ValidationError,
)
from lettermint.types import DomainDkimTransition, DomainMutationResponse

from .conftest import BASE_URL, SENDING_TOKEN, TEAM_TOKEN, MockAPI

TRANSITION: DomainDkimTransition = {
    "type": "legacy_upgrade",
    "state": "awaiting_dns",
    "completes_after": None,
}

UPGRADING: DomainMutationResponse = {
    "data": {
        "id": "d1",
        "domain": "acme.test",
        "dkim_mode": "legacy_txt",
        "rotation_ready": False,
        "dkim_transition": TRANSITION,
        "status_changed_at": None,
        "dns_records": [
            {
                "id": "r1",
                "type": "CNAME",
                "hostname": "lm1._domainkey",
                "fqdn": "lm1._domainkey.acme.test",
                "content": "lm1.acme-test.dkim.lettermint.test",
                "status": "pending",
                "purpose": "dkim",
                "verification_scope": "migration",
                "required_for_verification": False,
                "verified_at": None,
                "last_checked_at": None,
            }
        ],
        "created_at": "2026-11-01T09:00:00Z",
    },
    "message": "DKIM upgrade started.",
}

# (method, HTTP method, path, status, dkim_transition in the response)
CALLS: list[tuple[str, str, str, int, DomainDkimTransition | None]] = [
    ("start_dkim_upgrade", "POST", "/domains/d1/dkim/upgrade", 202, TRANSITION),
    ("cancel_dkim_upgrade", "DELETE", "/domains/d1/dkim/upgrade", 200, None),
    (
        "activate_dkim_upgrade",
        "POST",
        "/domains/d1/dkim/upgrade/activate",
        200,
        {
            "type": "legacy_upgrade",
            "state": "grace_period",
            "completes_after": "2026-11-03T09:00:00Z",
        },
    ),
    (
        "rotate_dkim_key",
        "POST",
        "/domains/d1/dkim/rotate",
        202,
        {"type": "rotation", "state": "preparing", "completes_after": None},
    ),
]


def response_with(transition: DomainDkimTransition | None) -> DomainMutationResponse:
    return {"data": {**UPGRADING["data"], "dkim_transition": transition}, "message": "OK."}


def assert_team_request(api: MockAPI, method: str, path: str) -> None:
    assert api.last.method == method
    assert str(api.last.url) == f"{BASE_URL}{path}"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert "x-lettermint-token" not in api.last.headers
    assert "idempotency-key" not in api.last.headers


@pytest.mark.parametrize(("name", "method", "path", "status", "transition"), CALLS)
def test_dkim_methods(
    api: MockAPI,
    client: Lettermint,
    name: str,
    method: str,
    path: str,
    status: int,
    transition: DomainDkimTransition | None,
) -> None:
    api.json(status, response_with(transition))
    result: DomainMutationResponse = getattr(client.domains, name)("d1")
    assert result == response_with(transition)
    assert result["data"].get("dkim_transition") == transition
    assert_team_request(api, method, path)
    assert api.last.content == b""
    assert "content-type" not in api.last.headers


def test_start_dkim_upgrade_returns_the_new_records(api: MockAPI, client: Lettermint) -> None:
    api.json(202, UPGRADING)
    result = client.domains.start_dkim_upgrade("d1")
    assert result == UPGRADING
    records = result["data"].get("dns_records", [])
    assert [r["verification_scope"] for r in records] == ["migration"]


def test_a_domain_that_already_uses_managed_dkim(api: MockAPI, client: Lettermint) -> None:
    managed: DomainMutationResponse = {
        "data": {**UPGRADING["data"], "dkim_mode": "managed_cname", "dkim_transition": None},
        "message": "The domain already uses managed DKIM.",
    }
    api.json(200, managed)
    assert client.domains.start_dkim_upgrade("d1") == managed


@pytest.mark.parametrize(
    ("name", "code"),
    [
        ("start_dkim_upgrade", "DKIM_UPGRADE_UNAVAILABLE"),
        ("cancel_dkim_upgrade", "DKIM_UPGRADE_IN_GRACE_PERIOD"),
        ("activate_dkim_upgrade", "DKIM_UPGRADE_NOT_READY"),
        ("rotate_dkim_key", "DKIM_ROTATION_UNAVAILABLE"),
    ],
)
def test_a_domain_in_the_wrong_state_is_a_validation_error(
    api: MockAPI, client: Lettermint, name: str, code: str
) -> None:
    api.json(422, {"error": {"code": code, "message": "Not possible for this domain."}})
    with pytest.raises(ValidationError) as caught:
        getattr(client.domains, name)("d1")
    assert caught.value.status == 422
    assert caught.value.code == code


def test_an_unknown_domain_is_not_found(api: MockAPI, client: Lettermint) -> None:
    api.json(404, {"error": {"code": "RESOURCE_NOT_FOUND", "message": "Not found."}})
    with pytest.raises(NotFoundError) as caught:
        client.domains.rotate_dkim_key("missing")
    assert caught.value.status == 404


@pytest.mark.parametrize("name", [call[0] for call in CALLS])
def test_dkim_methods_need_the_team_token(api: MockAPI, name: str) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(LettermintConfigError, match=rf"^domains\.{name} needs team_token"):
        getattr(sending_only.domains, name)("d1")
    assert api.requests == []


@pytest.mark.parametrize("name", [call[0] for call in CALLS])
def test_domain_ids_are_checked_and_encoded(api: MockAPI, client: Lettermint, name: str) -> None:
    api.json(200, UPGRADING)
    method: Any = getattr(client.domains, name)
    for invalid in ("", ".."):
        with pytest.raises(LettermintConfigError, match=rf"^domains\.{name}: domainId"):
            method(invalid)
    assert api.requests == []
    method("d/1")
    assert api.last.url.raw_path.startswith(b"/v1/domains/d%2F1/dkim/")


@pytest.mark.anyio
@pytest.mark.parametrize(("name", "method", "path", "status", "transition"), CALLS)
async def test_async_dkim_methods(
    api: MockAPI,
    aclient: AsyncLettermint,
    name: str,
    method: str,
    path: str,
    status: int,
    transition: DomainDkimTransition | None,
) -> None:
    api.json(status, response_with(transition))
    assert await getattr(aclient.domains, name)("d1") == response_with(transition)
    assert_team_request(api, method, path)
    assert api.last.content == b""
