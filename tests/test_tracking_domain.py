"""``projects.tracking_domain``: the custom tracking domain of a project."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from lettermint import (
    AsyncLettermint,
    Lettermint,
    LettermintConfigError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from lettermint.types import (
    ProjectTrackingDomain,
    ProjectTrackingDomainMutationResponse,
    ProjectTrackingDomainVerificationResponse,
    UpdateProjectTrackingDomainData,
)

from .conftest import BASE_URL, SENDING_TOKEN, TEAM_TOKEN, MockAPI

PATH = "/projects/p1/tracking-domain"

TRACKING_DOMAIN: ProjectTrackingDomain = {
    "domain": "track.acme.test",
    "verified": False,
    "active": False,
    "verified_at": None,
    "last_verification_at": None,
    "cname_target": "track.lettermint.test",
}

UPDATED: ProjectTrackingDomainMutationResponse = {
    "data": TRACKING_DOMAIN,
    "message": "Tracking domain updated.",
}

VERIFIED: ProjectTrackingDomainVerificationResponse = {
    "data": {
        "domain": "track.acme.test",
        "verified": True,
        "verified_at": "2026-11-20T09:00:00Z",
        "expected_cname": "track.lettermint.test",
        "found_cname": "track.lettermint.test",
        "temporary_error": False,
    },
    "message": "Tracking domain verified.",
}

NOT_VERIFIED: ProjectTrackingDomainVerificationResponse = {
    "data": {
        "domain": "track.acme.test",
        "verified": False,
        "verified_at": None,
        "expected_cname": "track.lettermint.test",
        "found_cname": None,
        "temporary_error": False,
    },
    "message": "No CNAME record found for track.acme.test.",
}


def assert_team_request(api: MockAPI, method: str, path: str) -> None:
    assert api.last.method == method
    assert str(api.last.url) == f"{BASE_URL}{path}"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert "x-lettermint-token" not in api.last.headers
    assert "idempotency-key" not in api.last.headers


def test_retrieve(api: MockAPI, client: Lettermint) -> None:
    api.json(200, TRACKING_DOMAIN)
    result: ProjectTrackingDomain = client.projects.tracking_domain.retrieve("p1")
    assert result == TRACKING_DOMAIN
    assert_team_request(api, "GET", PATH)
    assert api.last.content == b""


def test_retrieve_without_a_custom_domain(api: MockAPI, client: Lettermint) -> None:
    none: ProjectTrackingDomain = {**TRACKING_DOMAIN, "domain": None}
    api.json(200, none)
    assert client.projects.tracking_domain.retrieve("p1")["domain"] is None


def test_update(api: MockAPI, client: Lettermint) -> None:
    api.json(200, UPDATED)
    body: UpdateProjectTrackingDomainData = {"domain": "track.acme.test"}
    result: ProjectTrackingDomainMutationResponse = client.projects.tracking_domain.update(
        "p1", body
    )
    assert result == UPDATED
    assert result["data"]["cname_target"] == "track.lettermint.test"
    assert_team_request(api, "PUT", PATH)
    assert api.last.headers["content-type"] == "application/json"
    assert api.body() == {"domain": "track.acme.test"}


def test_delete_returns_none(api: MockAPI, client: Lettermint) -> None:
    api.respond(lambda request: httpx.Response(204))
    delete: Any = client.projects.tracking_domain.delete
    assert delete("p1") is None
    assert_team_request(api, "DELETE", PATH)
    assert api.last.content == b""


def test_verify(api: MockAPI, client: Lettermint) -> None:
    api.json(200, VERIFIED)
    result: ProjectTrackingDomainVerificationResponse = client.projects.tracking_domain.verify("p1")
    assert result == VERIFIED
    assert_team_request(api, "POST", f"{PATH}/verify")
    assert api.last.content == b""
    assert "content-type" not in api.last.headers


def test_a_failed_check_is_a_validation_error_with_the_verification(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(422, NOT_VERIFIED)
    with pytest.raises(ValidationError) as caught:
        client.projects.tracking_domain.verify("p1")
    assert caught.value.status == 422
    assert caught.value.message == "No CNAME record found for track.acme.test."
    assert caught.value.body == NOT_VERIFIED
    assert caught.value.body["data"]["temporary_error"] is False


def test_an_invalid_domain_is_a_validation_error(api: MockAPI, client: Lettermint) -> None:
    body = {
        "message": "The domain field must be a valid domain.",
        "errors": {"domain": ["The domain field must be a valid domain."]},
    }
    api.json(422, body)
    with pytest.raises(ValidationError) as caught:
        client.projects.tracking_domain.update("p1", {"domain": "not a domain"})
    assert caught.value.errors == body["errors"]


def test_a_plan_without_custom_tracking_domains_is_forbidden(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(403, {"message": "Your plan does not include custom tracking domains."})
    with pytest.raises(PermissionDeniedError) as caught:
        client.projects.tracking_domain.update("p1", {"domain": "track.acme.test"})
    assert caught.value.status == 403


def test_an_unknown_project_is_not_found(api: MockAPI, client: Lettermint) -> None:
    api.json(404, {"error": {"code": "RESOURCE_NOT_FOUND", "message": "Not found."}})
    with pytest.raises(NotFoundError):
        client.projects.tracking_domain.retrieve("missing")


CALLS: list[tuple[str, Any]] = [
    ("retrieve", lambda t, i: t.retrieve(i)),
    ("update", lambda t, i: t.update(i, {"domain": "track.acme.test"})),
    ("delete", lambda t, i: t.delete(i)),
    ("verify", lambda t, i: t.verify(i)),
]


@pytest.mark.parametrize(("label", "call"), CALLS)
def test_tracking_domain_needs_the_team_token(api: MockAPI, label: str, call: Any) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(
        LettermintConfigError, match=rf"^projects\.tracking_domain\.{label} needs team_token"
    ):
        call(sending_only.projects.tracking_domain, "p1")
    assert api.requests == []


@pytest.mark.parametrize(("label", "call"), CALLS)
def test_project_ids_are_checked_and_encoded(
    api: MockAPI, client: Lettermint, label: str, call: Any
) -> None:
    api.json(200, {})
    for invalid in ("", ".."):
        with pytest.raises(
            LettermintConfigError, match=rf"^projects\.tracking_domain\.{label}: projectId"
        ):
            call(client.projects.tracking_domain, invalid)
    assert api.requests == []
    if label == "delete":
        api.respond(lambda request: httpx.Response(204))
    call(client.projects.tracking_domain, "p/1")
    assert api.last.url.raw_path.startswith(b"/v1/projects/p%2F1/tracking-domain")


@pytest.mark.anyio
async def test_async_tracking_domain(api: MockAPI, aclient: AsyncLettermint) -> None:
    tracking_domain = aclient.projects.tracking_domain
    api.json(200, TRACKING_DOMAIN)
    assert await tracking_domain.retrieve("p1") == TRACKING_DOMAIN
    assert_team_request(api, "GET", PATH)
    api.json(200, UPDATED)
    assert await tracking_domain.update("p1", {"domain": "track.acme.test"}) == UPDATED
    assert_team_request(api, "PUT", PATH)
    assert api.body() == {"domain": "track.acme.test"}
    api.json(200, VERIFIED)
    assert await tracking_domain.verify("p1") == VERIFIED
    assert_team_request(api, "POST", f"{PATH}/verify")
    api.json(422, NOT_VERIFIED)
    with pytest.raises(ValidationError) as caught:
        await tracking_domain.verify("p1")
    assert caught.value.body == NOT_VERIFIED
    api.respond(lambda request: httpx.Response(204))
    delete: Any = tracking_domain.delete
    assert await delete("p1") is None
    assert_team_request(api, "DELETE", PATH)
