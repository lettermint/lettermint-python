"""``projects.api_tokens`` and ``team.api_tokens``: project and team API tokens."""

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
    ListProjectApiTokensResponse,
    ListTeamApiTokensResponse,
    MessageResponse,
    ProjectApiToken,
    ProjectApiTokenCreatedResponse,
    StoreProjectApiTokenData,
    StoreTeamApiTokenData,
    TeamApiToken,
    TeamApiTokenCreatedResponse,
)

from .conftest import BASE_URL, SENDING_TOKEN, TEAM_TOKEN, MockAPI

PROJECT_TOKEN: ProjectApiToken = {
    "id": "t1",
    "project_id": "p1",
    "name": "Checkout service",
    "short_token": False,
    "created_via": "api",
    "allowed_ips": [],
    "last_used_at": None,
    "created_at": "2026-10-28T09:00:00Z",
}

PROJECT_TOKEN_CREATED: ProjectApiTokenCreatedResponse = {
    "data": {**PROJECT_TOKEN, "token": "lm_fixture_token_value"},
    "smtp": {"host": "smtp.lettermint.co", "ports": [465, 587], "username": "lettermint"},
    "message": "API token created.",
}

NEW_PROJECT_TOKEN: StoreProjectApiTokenData = {"name": "Checkout service"}


def assert_team_request(api: MockAPI, method: str, path: str) -> None:
    assert api.last.method == method
    assert str(api.last.url) == f"{BASE_URL}{path}"
    assert api.last.headers["authorization"] == f"Bearer {TEAM_TOKEN}"
    assert "x-lettermint-token" not in api.last.headers
    assert "idempotency-key" not in api.last.headers


def test_list_project_tokens(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"data": [PROJECT_TOKEN], "next_cursor": "c2"})
    page: ListProjectApiTokensResponse = client.projects.api_tokens.list(
        "p1", {"page": {"size": 10, "cursor": "c1"}, "sort": ["-created_at"]}
    )
    assert page["data"] == [PROJECT_TOKEN]
    assert page["next_cursor"] == "c2"
    assert_team_request(
        api,
        "GET",
        "/projects/p1/api-tokens?page%5Bsize%5D=10&page%5Bcursor%5D=c1&sort=-created_at",
    )
    assert api.last.content == b""


def test_iterate_project_tokens_follows_the_cursor(api: MockAPI, client: Lettermint) -> None:
    second = {**PROJECT_TOKEN, "id": "t2"}
    pages = {
        None: {"data": [PROJECT_TOKEN], "next_cursor": "c2"},
        "c2": {"data": [second], "next_cursor": None},
    }
    api.respond(
        lambda request: httpx.Response(200, json=pages[request.url.params.get("page[cursor]")])
    )
    tokens: list[ProjectApiToken] = list(
        client.projects.api_tokens.iterate("p1", {"page": {"size": 1}})
    )
    assert tokens == [PROJECT_TOKEN, second]
    assert [r.url.params.get("page[cursor]") for r in api.requests] == [None, "c2"]
    assert all(r.url.path == "/v1/projects/p1/api-tokens" for r in api.requests)


def test_create_project_token_returns_the_value_once(api: MockAPI, client: Lettermint) -> None:
    api.json(201, PROJECT_TOKEN_CREATED)
    created: ProjectApiTokenCreatedResponse = client.projects.api_tokens.create(
        "p1", NEW_PROJECT_TOKEN
    )
    assert created == PROJECT_TOKEN_CREATED
    token: str = created["data"]["token"]
    assert token == "lm_fixture_token_value"
    assert_team_request(api, "POST", "/projects/p1/api-tokens")
    assert api.last.headers["content-type"] == "application/json"
    assert api.body() == {"name": "Checkout service"}


def test_create_a_short_project_token(api: MockAPI, client: Lettermint) -> None:
    api.json(201, {**PROJECT_TOKEN_CREATED, "smtp": None})
    body: StoreProjectApiTokenData = {"name": "Printer", "short_token": True}
    created = client.projects.api_tokens.create("p1", body)
    assert created["smtp"] is None
    assert api.body() == {"name": "Printer", "short_token": True}


def test_delete_project_token(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "API token deleted."})
    result: MessageResponse = client.projects.api_tokens.delete("p1", "t1")
    assert result == {"message": "API token deleted."}
    assert_team_request(api, "DELETE", "/projects/p1/api-tokens/t1")
    assert api.last.content == b""


def test_project_tokens_need_the_team_token(api: MockAPI) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    tokens = sending_only.projects.api_tokens
    with pytest.raises(
        LettermintConfigError, match=r"^projects\.api_tokens\.list needs team_token"
    ):
        tokens.list("p1")
    with pytest.raises(
        LettermintConfigError, match=r"^projects\.api_tokens\.iterate needs team_token"
    ):
        tokens.iterate("p1")
    with pytest.raises(
        LettermintConfigError, match=r"^projects\.api_tokens\.create needs team_token"
    ):
        tokens.create("p1", NEW_PROJECT_TOKEN)
    with pytest.raises(
        LettermintConfigError, match=r"^projects\.api_tokens\.delete needs team_token"
    ):
        tokens.delete("p1", "t1")
    assert api.requests == []


@pytest.mark.parametrize(
    ("call", "label"),
    [
        (lambda c, i: c.projects.api_tokens.list(i), "list"),
        (lambda c, i: c.projects.api_tokens.iterate(i), "iterate"),
        (lambda c, i: c.projects.api_tokens.create(i, NEW_PROJECT_TOKEN), "create"),
        (lambda c, i: c.projects.api_tokens.delete(i, "t1"), "delete"),
    ],
)
def test_project_ids_are_checked(api: MockAPI, client: Lettermint, call: Any, label: str) -> None:
    for invalid in ("", ".."):
        with pytest.raises(
            LettermintConfigError, match=rf"^projects\.api_tokens\.{label}: projectId"
        ):
            call(client, invalid)
    assert api.requests == []


def test_token_ids_are_checked_and_encoded(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "API token deleted."})
    for invalid in ("", ".."):
        with pytest.raises(LettermintConfigError, match=r"^projects\.api_tokens\.delete: tokenId"):
            client.projects.api_tokens.delete("p1", invalid)
    assert api.requests == []
    client.projects.api_tokens.delete("p/1", "t/1")
    assert api.last.url.raw_path == b"/v1/projects/p%2F1/api-tokens/t%2F1"


def test_an_invalid_project_token_is_a_validation_error(api: MockAPI, client: Lettermint) -> None:
    body = {
        "message": "The name field is required.",
        "errors": {"name": ["The name field is required."]},
    }
    api.json(422, body)
    with pytest.raises(ValidationError) as caught:
        client.projects.api_tokens.create("p1", {"name": ""})
    assert caught.value.status == 422
    assert caught.value.errors == {"name": ["The name field is required."]}


def test_deleting_an_unknown_project_token_is_not_found(api: MockAPI, client: Lettermint) -> None:
    api.json(404, {"message": "Not found."})
    with pytest.raises(NotFoundError) as caught:
        client.projects.api_tokens.delete("p1", "missing")
    assert caught.value.status == 404


@pytest.mark.anyio
async def test_async_project_tokens(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(201, PROJECT_TOKEN_CREATED)
    created = await aclient.projects.api_tokens.create("p1", NEW_PROJECT_TOKEN)
    assert created == PROJECT_TOKEN_CREATED
    assert_team_request(api, "POST", "/projects/p1/api-tokens")
    assert api.body() == NEW_PROJECT_TOKEN
    api.json(200, {"data": [PROJECT_TOKEN], "next_cursor": None})
    assert [item async for item in aclient.projects.api_tokens.iterate("p1")] == [PROJECT_TOKEN]
    assert_team_request(api, "GET", "/projects/p1/api-tokens")
    api.json(200, {"message": "API token deleted."})
    assert await aclient.projects.api_tokens.delete("p1", "t1") == {"message": "API token deleted."}
    assert_team_request(api, "DELETE", "/projects/p1/api-tokens/t1")


TEAM_API_TOKEN: TeamApiToken = {
    "id": "t1",
    "name": "Deploys",
    "abilities": ["read:domains", "write:domains"],
    "allowed_ips": ["203.0.113.0/24"],
    "created_via": "api",
    "expires_at": "2027-01-01T00:00:00Z",
    "last_used_at": None,
    "created_at": "2026-10-28T09:00:00Z",
}

TEAM_API_TOKEN_CREATED: TeamApiTokenCreatedResponse = {
    "data": {**TEAM_API_TOKEN, "token": "lm_team_fixture_token_value"},
    "message": "API token created.",
}

NEW_TEAM_API_TOKEN: StoreTeamApiTokenData = {
    "name": "Deploys",
    "abilities": ["read:domains", "write:domains"],
}


def test_list_team_tokens(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"data": [TEAM_API_TOKEN], "next_cursor": "c2"})
    page: ListTeamApiTokensResponse = client.team.api_tokens.list(
        {"page": {"size": 10, "cursor": "c1"}, "sort": ["name"]}
    )
    assert page["data"] == [TEAM_API_TOKEN]
    assert page["next_cursor"] == "c2"
    assert_team_request(
        api, "GET", "/team/api-tokens?page%5Bsize%5D=10&page%5Bcursor%5D=c1&sort=name"
    )
    assert api.last.content == b""


def test_iterate_team_tokens_follows_the_cursor(api: MockAPI, client: Lettermint) -> None:
    second = {**TEAM_API_TOKEN, "id": "t2"}
    pages = {
        None: {"data": [TEAM_API_TOKEN], "next_cursor": "c2"},
        "c2": {"data": [second], "next_cursor": None},
    }
    api.respond(
        lambda request: httpx.Response(200, json=pages[request.url.params.get("page[cursor]")])
    )
    tokens: list[TeamApiToken] = list(client.team.api_tokens.iterate({"page": {"size": 1}}))
    assert tokens == [TEAM_API_TOKEN, second]
    assert [r.url.params.get("page[cursor]") for r in api.requests] == [None, "c2"]
    assert all(r.url.params["page[size]"] == "1" for r in api.requests)


def test_create_team_token_returns_the_value_once(api: MockAPI, client: Lettermint) -> None:
    api.json(201, TEAM_API_TOKEN_CREATED)
    created: TeamApiTokenCreatedResponse = client.team.api_tokens.create(NEW_TEAM_API_TOKEN)
    assert created == TEAM_API_TOKEN_CREATED
    token: str = created["data"]["token"]
    assert token == "lm_team_fixture_token_value"
    assert_team_request(api, "POST", "/team/api-tokens")
    assert api.last.headers["content-type"] == "application/json"
    assert api.body() == {"name": "Deploys", "abilities": ["read:domains", "write:domains"]}


@pytest.mark.parametrize("expires_at", ["2026-12-01T00:00:00Z", None])
def test_create_team_token_with_an_expiry(
    api: MockAPI, client: Lettermint, expires_at: str | None
) -> None:
    api.json(201, TEAM_API_TOKEN_CREATED)
    body: StoreTeamApiTokenData = {
        "name": "Nightly",
        "abilities": ["read:messages"],
        "expires_at": expires_at,
    }
    client.team.api_tokens.create(body)
    assert api.body() == {
        "name": "Nightly",
        "abilities": ["read:messages"],
        "expires_at": expires_at,
    }


def test_delete_team_token(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "API token deleted."})
    result: MessageResponse = client.team.api_tokens.delete("t1")
    assert result == {"message": "API token deleted."}
    assert_team_request(api, "DELETE", "/team/api-tokens/t1")
    assert api.last.content == b""


def test_team_tokens_need_the_team_token(api: MockAPI) -> None:
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    tokens = sending_only.team.api_tokens
    with pytest.raises(LettermintConfigError, match=r"^team\.api_tokens\.list needs team_token"):
        tokens.list()
    with pytest.raises(LettermintConfigError, match=r"^team\.api_tokens\.iterate needs team_token"):
        tokens.iterate()
    with pytest.raises(LettermintConfigError, match=r"^team\.api_tokens\.create needs team_token"):
        tokens.create(NEW_TEAM_API_TOKEN)
    with pytest.raises(LettermintConfigError, match=r"^team\.api_tokens\.delete needs team_token"):
        tokens.delete("t1")
    assert api.requests == []


def test_team_token_ids_are_checked_and_encoded(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"message": "API token deleted."})
    for invalid in ("", ".."):
        with pytest.raises(LettermintConfigError, match=r"^team\.api_tokens\.delete: tokenId"):
            client.team.api_tokens.delete(invalid)
    assert api.requests == []
    client.team.api_tokens.delete("t/1")
    assert api.last.url.raw_path == b"/v1/team/api-tokens/t%2F1"


def test_an_ability_the_token_lacks_is_a_validation_error(api: MockAPI, client: Lettermint) -> None:
    body = {
        "message": "The token does not have the write:team ability.",
        "errors": {"abilities.0": ["The token does not have the write:team ability."]},
    }
    api.json(422, body)
    with pytest.raises(ValidationError) as caught:
        client.team.api_tokens.create({"name": "Admin", "abilities": ["write:team"]})
    assert caught.value.status == 422
    assert caught.value.errors == body["errors"]


def test_deleting_a_token_with_more_abilities_is_forbidden(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(403, {"message": "This action is unauthorized."})
    with pytest.raises(PermissionDeniedError) as caught:
        client.team.api_tokens.delete("t1")
    assert caught.value.status == 403


@pytest.mark.anyio
async def test_async_team_tokens(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(201, TEAM_API_TOKEN_CREATED)
    created = await aclient.team.api_tokens.create(NEW_TEAM_API_TOKEN)
    assert created == TEAM_API_TOKEN_CREATED
    assert_team_request(api, "POST", "/team/api-tokens")
    assert api.body() == NEW_TEAM_API_TOKEN
    api.json(200, {"data": [TEAM_API_TOKEN], "next_cursor": None})
    assert [item async for item in aclient.team.api_tokens.iterate()] == [TEAM_API_TOKEN]
    assert_team_request(api, "GET", "/team/api-tokens")
    api.json(200, {"message": "API token deleted."})
    assert await aclient.team.api_tokens.delete("t1") == {"message": "API token deleted."}
    assert_team_request(api, "DELETE", "/team/api-tokens/t1")
