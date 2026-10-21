"""``team.invites``: the requests, the token, the bodies and the errors."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from lettermint import (
    AsyncLettermint,
    ConflictError,
    Lettermint,
    LettermintConfigError,
    ValidationError,
)
from lettermint.types import (
    CreateTeamInviteData,
    ListTeamInvitesResponse,
    MessageResponse,
    TeamInviteData,
    UpdateTeamInviteData,
)

from .conftest import BASE_URL, SENDING_TOKEN, TEAM_TOKEN, MockAPI

INVITE: TeamInviteData = {
    "id": "i1",
    "email": "jane@acme.test",
    "role": {"id": "r1", "name": "Member"},
    "project_access": {"scope": "selected", "projects": [{"id": "p1", "name": "Production"}]},
    "created_at": "2026-10-20T09:00:00Z",
}

NEW_INVITE: CreateTeamInviteData = {
    "email": "jane@acme.test",
    "role_id": "r1",
    "project_access": {"scope": "selected", "project_ids": ["p1"]},
}

RBAC_CONFLICT = {"error": {"code": "stale_resource", "message": "The role changed."}}


def assert_team_request(api: MockAPI, method: str, path: str) -> None:
    assert api.last.method == method
    assert str(api.last.url) == f"{BASE_URL}{path}"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert "x-lettermint-token" not in api.last.headers
    assert "idempotency-key" not in api.last.headers


def test_list_invites(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"data": [INVITE], "next_cursor": "c2"})
    page: ListTeamInvitesResponse = client.team.invites.list({"page": {"size": 10}})
    assert page["data"] == [INVITE]
    assert page["next_cursor"] == "c2"
    assert_team_request(api, "GET", "/team/invites?page%5Bsize%5D=10")


def test_iterate_invites_follows_the_cursor(api: MockAPI, client: Lettermint) -> None:
    second = {**INVITE, "id": "i2"}
    pages = {
        None: {"data": [INVITE], "next_cursor": "c2"},
        "c2": {"data": [second], "next_cursor": None},
    }
    api.respond(
        lambda request: httpx.Response(200, json=pages[request.url.params.get("page[cursor]")])
    )
    invites: list[TeamInviteData] = list(client.team.invites.iterate({"page": {"size": 1}}))
    assert invites == [INVITE, second]
    assert [r.url.params.get("page[cursor]") for r in api.requests] == [None, "c2"]
    assert all(r.url.params["page[size]"] == "1" for r in api.requests)


def test_retrieve_invite(api: MockAPI, client: Lettermint) -> None:
    api.json(200, INVITE)
    invite: TeamInviteData = client.team.invites.retrieve("i1")
    assert invite == INVITE
    assert_team_request(api, "GET", "/team/invites/i1")
    assert api.last.content == b""


def test_create_invite_sends_the_body(api: MockAPI, client: Lettermint) -> None:
    api.json(201, INVITE)
    invite: TeamInviteData = client.team.invites.create(NEW_INVITE)
    assert invite == INVITE
    assert_team_request(api, "POST", "/team/invites")
    assert api.last.headers["content-type"] == "application/json"
    assert api.body() == NEW_INVITE


def test_create_invite_with_access_to_all_projects(api: MockAPI, client: Lettermint) -> None:
    api.json(201, INVITE)
    body: CreateTeamInviteData = {
        "email": "jane@acme.test",
        "role_id": "r1",
        "project_access": {"scope": "all"},
    }
    client.team.invites.create(body)
    assert api.body() == body


def test_update_invite_replaces_it(api: MockAPI, client: Lettermint) -> None:
    api.json(200, INVITE)
    body: UpdateTeamInviteData = {
        "email": "john@acme.test",
        "role_id": "r2",
        "project_access": {"scope": "all"},
    }
    invite: TeamInviteData = client.team.invites.update("i1", body)
    assert invite == INVITE
    assert_team_request(api, "PUT", "/team/invites/i1")
    assert api.body() == body


def test_revoke_invite(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "Invite revoked."})
    result: MessageResponse = client.team.invites.revoke("i1")
    assert result == {"message": "Invite revoked."}
    assert_team_request(api, "DELETE", "/team/invites/i1")
    assert api.last.content == b""


def test_invites_need_the_team_token(api: MockAPI) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(LettermintConfigError, match=r"^team\.invites\.list needs team_token"):
        sending_only.team.invites.list()
    with pytest.raises(LettermintConfigError, match=r"^team\.invites\.iterate needs team_token"):
        sending_only.team.invites.iterate()
    with pytest.raises(LettermintConfigError, match=r"^team\.invites\.create needs team_token"):
        sending_only.team.invites.create(NEW_INVITE)
    assert api.requests == []


@pytest.mark.parametrize(
    ("call", "label"),
    [
        (lambda c, i: c.team.invites.retrieve(i), "retrieve"),
        (lambda c, i: c.team.invites.update(i, NEW_INVITE), "update"),
        (lambda c, i: c.team.invites.revoke(i), "revoke"),
    ],
)
def test_invite_ids_are_checked_and_encoded(
    api: MockAPI, client: Lettermint, call: Any, label: str
) -> None:
    api.json(200, INVITE)
    for invalid in ("", ".."):
        with pytest.raises(LettermintConfigError, match=rf"^team\.invites\.{label}: inviteId"):
            call(client, invalid)
    assert api.requests == []
    call(client, "a/b")
    assert api.last.url.raw_path == b"/v1/team/invites/a%2Fb"


def test_an_invite_conflict_is_a_conflict_error(api: MockAPI, client: Lettermint) -> None:
    api.json(409, RBAC_CONFLICT)
    with pytest.raises(ConflictError) as caught:
        client.team.invites.update("i1", NEW_INVITE)
    assert (caught.value.status, caught.value.code, caught.value.body) == (
        409,
        "stale_resource",
        RBAC_CONFLICT,
    )


def test_an_invalid_invite_is_a_validation_error(api: MockAPI, client: Lettermint) -> None:
    body = {
        "message": "The team has no free seat.",
        "errors": {"email": ["The team has no free seat."]},
    }
    api.json(422, body)
    with pytest.raises(ValidationError) as caught:
        client.team.invites.create(NEW_INVITE)
    assert caught.value.status == 422
    assert caught.value.errors == {"email": ["The team has no free seat."]}


@pytest.mark.anyio
async def test_async_invites(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(201, INVITE)
    invite: TeamInviteData = await aclient.team.invites.create(NEW_INVITE)
    assert invite == INVITE
    assert_team_request(api, "POST", "/team/invites")
    assert api.body() == NEW_INVITE
    api.json(200, {"data": [INVITE], "next_cursor": None})
    assert [item async for item in aclient.team.invites.iterate()] == [INVITE]
    assert_team_request(api, "GET", "/team/invites")
    api.json(200, {"message": "Invite revoked."})
    assert await aclient.team.invites.revoke("i1") == {"message": "Invite revoked."}
    assert_team_request(api, "DELETE", "/team/invites/i1")
