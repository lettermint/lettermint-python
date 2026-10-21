"""``team.invites``, the team role methods and ``team.members.remove`` with the project filter."""

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
    CreateTeamRoleData,
    ListTeamInvitesResponse,
    MessageResponse,
    TeamInviteData,
    TeamRoleData,
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


ROLE: TeamRoleData = {
    "id": "r1",
    "name": "Support",
    "description": "Handles customer questions",
    "system_key": None,
    "permissions": ["support:manage"],
    "assignable": True,
}

NEW_ROLE: CreateTeamRoleData = {
    "name": "Support",
    "description": "Handles customer questions",
    "permissions": ["support:manage"],
}


@pytest.mark.parametrize("description", ["Handles customer questions", None])
def test_retrieve_role_parses_the_description(
    api: MockAPI, client: Lettermint, description: str | None
) -> None:
    api.json(200, {**ROLE, "description": description})
    role: TeamRoleData = client.team.retrieve_role("r1")
    assert role["description"] == description
    assert role == {**ROLE, "description": description}
    assert_team_request(api, "GET", "/team/roles/r1")
    assert api.last.content == b""


def test_a_role_without_a_description_still_parses(api: MockAPI, client: Lettermint) -> None:
    legacy = {key: value for key, value in ROLE.items() if key != "description"}
    api.json(200, {"data": [legacy]})
    assert "description" not in client.team.roles()["data"][0]


def test_create_role_sends_the_body(api: MockAPI, client: Lettermint) -> None:
    api.json(201, ROLE)
    role: TeamRoleData = client.team.create_role(NEW_ROLE)
    assert role == ROLE
    assert_team_request(api, "POST", "/team/roles")
    assert api.last.headers["content-type"] == "application/json"
    assert api.body() == NEW_ROLE
    client.team.create_role({"name": "Support", "permissions": ["support:manage"]})
    assert api.body() == {"name": "Support", "permissions": ["support:manage"]}
    client.team.create_role({**NEW_ROLE, "description": None})
    assert api.body() == {**NEW_ROLE, "description": None}


def test_update_role_replaces_it(api: MockAPI, client: Lettermint) -> None:
    api.json(200, ROLE)
    role: TeamRoleData = client.team.update_role("r1", NEW_ROLE)
    assert role == ROLE
    assert_team_request(api, "PUT", "/team/roles/r1")
    assert api.body() == NEW_ROLE


def test_delete_role_without_a_replacement_sends_no_query(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "Role deleted."})
    result: MessageResponse = client.team.delete_role("r1")
    assert result == {"message": "Role deleted."}
    assert_team_request(api, "DELETE", "/team/roles/r1")
    assert api.last.url.query == b""
    assert api.last.content == b""
    client.team.delete_role("r1", {})
    assert api.last.url.query == b""
    client.team.delete_role("r1", {"replacement_role_id": None})
    assert api.last.url.query == b""


def test_delete_role_with_a_replacement(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "Role deleted."})
    client.team.delete_role("r1", {"replacement_role_id": "r2"})
    assert_team_request(api, "DELETE", "/team/roles/r1?replacement_role_id=r2")
    assert api.last.url.params["replacement_role_id"] == "r2"


@pytest.mark.parametrize(
    "body", [{"name": "Support copy"}, {"name": "Support copy", "description": None}]
)
def test_duplicate_role(api: MockAPI, client: Lettermint, body: Any) -> None:
    api.json(201, {**ROLE, "id": "r2", "name": "Support copy"})
    role: TeamRoleData = client.team.duplicate_role("r1", body)
    assert (role["id"], role["name"]) == ("r2", "Support copy")
    assert_team_request(api, "POST", "/team/roles/r1/duplicate")
    assert api.body() == body


@pytest.mark.parametrize(
    ("call", "label"),
    [
        (lambda c, i: c.team.retrieve_role(i), "retrieve_role"),
        (lambda c, i: c.team.update_role(i, NEW_ROLE), "update_role"),
        (lambda c, i: c.team.delete_role(i), "delete_role"),
        (lambda c, i: c.team.duplicate_role(i, {"name": "Copy"}), "duplicate_role"),
    ],
)
def test_role_ids_are_checked_and_encoded(
    api: MockAPI, client: Lettermint, call: Any, label: str
) -> None:
    api.json(200, ROLE)
    for invalid in ("", ".."):
        with pytest.raises(LettermintConfigError, match=rf"^team\.{label}: roleId"):
            call(client, invalid)
    assert api.requests == []
    call(client, "a/b")
    assert api.last.url.raw_path.startswith(b"/v1/team/roles/a%2Fb")


def test_role_methods_need_the_team_token(api: MockAPI) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(LettermintConfigError, match=r"^team\.create_role needs team_token"):
        sending_only.team.create_role(NEW_ROLE)
    with pytest.raises(LettermintConfigError, match=r"^team\.delete_role needs team_token"):
        sending_only.team.delete_role("r1")
    assert api.requests == []


def test_a_role_conflict_is_a_conflict_error(api: MockAPI, client: Lettermint) -> None:
    body = {"error": {"code": "built_in_role_immutable", "message": "Built-in roles are fixed."}}
    api.json(409, body)
    with pytest.raises(ConflictError) as caught:
        client.team.update_role("r1", NEW_ROLE)
    assert (caught.value.status, caught.value.code, caught.value.body) == (
        409,
        "built_in_role_immutable",
        body,
    )


def test_a_role_still_in_use_is_a_validation_error(api: MockAPI, client: Lettermint) -> None:
    body = {
        "message": "A replacement role is required.",
        "errors": {"replacement_role_id": ["A replacement role is required."]},
    }
    api.json(422, body)
    with pytest.raises(ValidationError) as caught:
        client.team.delete_role("r1")
    assert caught.value.errors == body["errors"]


@pytest.mark.anyio
async def test_async_roles(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(201, ROLE)
    role: TeamRoleData = await aclient.team.create_role(NEW_ROLE)
    assert role == ROLE
    assert_team_request(api, "POST", "/team/roles")
    assert api.body() == NEW_ROLE
    api.json(200, {"message": "Role deleted."})
    await aclient.team.delete_role("r1", {"replacement_role_id": "r2"})
    assert_team_request(api, "DELETE", "/team/roles/r1?replacement_role_id=r2")
    api.json(201, ROLE)
    await aclient.team.duplicate_role("r1", {"name": "Copy"})
    assert_team_request(api, "POST", "/team/roles/r1/duplicate")


MEMBER = {
    "id": "u1",
    "name": "Jane",
    "email": "jane@acme.test",
    "role": {"id": "r1", "name": "Member"},
    "project_access": {"scope": "all", "projects": []},
    "joined_at": "2026-10-01T09:00:00Z",
}


def test_remove_member(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "Member removed."})
    result: MessageResponse = client.team.members.remove("u1")
    assert result == {"message": "Member removed."}
    assert_team_request(api, "DELETE", "/team/members/u1")
    assert api.last.content == b""


def test_remove_member_checks_and_encodes_the_id(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "Member removed."})
    for invalid in ("", ".."):
        with pytest.raises(LettermintConfigError, match=r"^team\.members\.remove: userId"):
            client.team.members.remove(invalid)
    assert api.requests == []
    client.team.members.remove("a/b")
    assert api.last.url.raw_path == b"/v1/team/members/a%2Fb"


def test_remove_member_needs_the_team_token(api: MockAPI) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(LettermintConfigError, match=r"^team\.members\.remove needs team_token"):
        sending_only.team.members.remove("u1")
    assert api.requests == []


def test_removing_the_owner_is_a_conflict_error(api: MockAPI, client: Lettermint) -> None:
    body = {"error": {"code": "owner_protected", "message": "The Owner cannot be removed."}}
    api.json(409, body)
    with pytest.raises(ConflictError) as caught:
        client.team.members.remove("u1")
    assert (caught.value.status, caught.value.code, caught.value.body) == (
        409,
        "owner_protected",
        body,
    )


def test_members_can_be_filtered_by_project(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"data": [MEMBER], "next_cursor": None})
    page = client.team.members.list({"filter": {"project_id": "p1"}, "page": {"size": 5}})
    assert page["data"] == [MEMBER]
    assert api.last.url.params["filter[project_id]"] == "p1"
    assert api.last.url.params["page[size]"] == "5"
    assert list(client.team.members.iterate({"filter": {"project_id": "p1"}})) == [MEMBER]
    assert_team_request(api, "GET", "/team/members?filter%5Bproject_id%5D=p1")


def test_member_filter_follows_every_page(api: MockAPI, client: Lettermint) -> None:
    pages = {
        None: {"data": [MEMBER], "next_cursor": "c2"},
        "c2": {"data": [{**MEMBER, "id": "u2"}], "next_cursor": None},
    }
    api.respond(
        lambda request: httpx.Response(200, json=pages[request.url.params.get("page[cursor]")])
    )
    members = list(client.team.members.iterate({"filter": {"project_id": "p1"}}))
    assert [member["id"] for member in members] == ["u1", "u2"]
    assert all(r.url.params["filter[project_id]"] == "p1" for r in api.requests)


@pytest.mark.anyio
async def test_async_remove_member(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(200, {"message": "Member removed."})
    assert await aclient.team.members.remove("u1") == {"message": "Member removed."}
    assert_team_request(api, "DELETE", "/team/members/u1")
    api.json(200, {"data": [MEMBER], "next_cursor": None})
    await aclient.team.members.list({"filter": {"project_id": "p1"}})
    assert_team_request(api, "GET", "/team/members?filter%5Bproject_id%5D=p1")
