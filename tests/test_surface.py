"""The public surface: every generated operation is reachable, the layout matches the
other SDKs, and the synchronous and asynchronous clients are the same API."""

from __future__ import annotations

import inspect
import re
import typing
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx
import pytest

import lettermint
from lettermint import AsyncLettermint, Lettermint, UnexpectedResponseError
from lettermint import types as lm_types
from lettermint._generated.operations import OPERATIONS

from .conftest import BASE_URL, MESSAGE, MockAPI

# (method path, positional arguments, operation key)
CALLS: list[tuple[str, tuple[Any, ...], str]] = [
    ("ping", (), "GET /ping"),
    ("analytics", ({"from": "2026-10-01", "to": "2026-10-31"},), "POST /analytics"),
    ("blocked_file_types", (), "GET /blocked-file-types"),
    ("emails.send", (MESSAGE,), "POST /send"),
    ("emails.send_batch", ([MESSAGE],), "POST /send/batch"),
    ("emails.ping", (), "GET /ping"),
    ("domains.list", (), "GET /domains"),
    ("domains.iterate", (), "GET /domains"),
    ("domains.create", ({"domain": "acme.test"},), "POST /domains"),
    ("domains.retrieve", ("d1",), "GET /domains/{domainId}"),
    ("domains.delete", ("d1",), "DELETE /domains/{domainId}"),
    ("domains.verify_dns_records", ("d1",), "POST /domains/{domainId}/dns-records/verify"),
    (
        "domains.verify_dns_record",
        ("d1", "r1"),
        "POST /domains/{domainId}/dns-records/{recordId}/verify",
    ),
    ("domains.update_projects", ("d1", {"project_ids": []}), "PUT /domains/{domainId}/projects"),
    ("messages.list", (), "GET /messages"),
    ("messages.iterate", (), "GET /messages"),
    ("messages.retrieve", ("m1",), "GET /messages/{messageId}"),
    ("messages.events", ("m1",), "GET /messages/{messageId}/events"),
    ("messages.iterate_events", ("m1",), "GET /messages/{messageId}/events"),
    ("messages.source", ("m1",), "GET /messages/{messageId}/source"),
    ("messages.html", ("m1",), "GET /messages/{messageId}/html"),
    ("messages.text", ("m1",), "GET /messages/{messageId}/text"),
    (
        "messages.reschedule",
        ("m1", {"scheduled_at": "2026-10-20T09:00:00Z"}),
        "PATCH /messages/{messageId}",
    ),
    ("messages.cancel", ("m1",), "POST /messages/{messageId}/cancel"),
    ("messages.process", ("m1",), "POST /messages/{messageId}/process"),
    ("projects.list", (), "GET /projects"),
    ("projects.iterate", (), "GET /projects"),
    ("projects.create", ({"name": "Production"},), "POST /projects"),
    ("projects.retrieve", ("p1",), "GET /projects/{projectId}"),
    ("projects.update", ("p1", {"name": "Renamed"}), "PUT /projects/{projectId}"),
    ("projects.delete", ("p1",), "DELETE /projects/{projectId}"),
    ("projects.rotate_token", ("p1",), "POST /projects/{projectId}/rotate-token"),
    ("projects.report_forwarding.retrieve", ("p1",), "GET /projects/{projectId}/report-forwarding"),
    (
        "projects.report_forwarding.update",
        ("p1", {"email": "dmarc@acme.test"}),
        "PUT /projects/{projectId}/report-forwarding",
    ),
    (
        "projects.report_forwarding.delete",
        ("p1",),
        "DELETE /projects/{projectId}/report-forwarding",
    ),
    (
        "projects.report_forwarding.verify",
        ("p1", {"code": "123456"}),
        "POST /projects/{projectId}/report-forwarding/verify",
    ),
    (
        "projects.report_forwarding.resend_code",
        ("p1",),
        "POST /projects/{projectId}/report-forwarding/resend-code",
    ),
    ("routes.list", ("p1",), "GET /projects/{projectId}/routes"),
    ("routes.iterate", ("p1",), "GET /projects/{projectId}/routes"),
    (
        "routes.create",
        ("p1", {"name": "Broadcast", "route_type": "broadcast"}),
        "POST /projects/{projectId}/routes",
    ),
    ("routes.retrieve", ("r1",), "GET /routes/{routeId}"),
    ("routes.update", ("r1", {"name": "Renamed"}), "PUT /routes/{routeId}"),
    ("routes.delete", ("r1",), "DELETE /routes/{routeId}"),
    ("routes.verify_inbound_domain", ("r1",), "POST /routes/{routeId}/verify-inbound-domain"),
    ("stats.retrieve", ({"from": "2026-10-01", "to": "2026-10-31"},), "GET /stats"),
    ("suppressions.list", (), "GET /suppressions"),
    ("suppressions.iterate", (), "GET /suppressions"),
    (
        "suppressions.create",
        ({"value": "x@example.test", "reason": "manual"},),
        "POST /suppressions",
    ),
    ("suppressions.delete", ("s1",), "DELETE /suppressions/{suppressionId}"),
    ("team.retrieve", (), "GET /team"),
    ("team.update", ({"name": "Acme"},), "PUT /team"),
    ("team.usage", (), "GET /team/usage"),
    ("team.roles", (), "GET /team/roles"),
    ("team.members.list", (), "GET /team/members"),
    ("team.members.iterate", (), "GET /team/members"),
    ("team.members.retrieve", ("u1",), "GET /team/members/{userId}"),
    (
        "team.members.update_assignment",
        ("u1", {"role": "admin"}),
        "PUT /team/members/{userId}/assignment",
    ),
    ("webhooks.list", (), "GET /webhooks"),
    ("webhooks.iterate", (), "GET /webhooks"),
    (
        "webhooks.create",
        ({"url": "https://acme.test/hook", "events": ["message.delivered"]},),
        "POST /webhooks",
    ),
    ("webhooks.retrieve", ("w1",), "GET /webhooks/{webhookId}"),
    ("webhooks.update", ("w1", {"enabled": False}), "PUT /webhooks/{webhookId}"),
    ("webhooks.delete", ("w1",), "DELETE /webhooks/{webhookId}"),
    ("webhooks.test", ("w1",), "POST /webhooks/{webhookId}/test"),
    ("webhooks.regenerate_secret", ("w1",), "POST /webhooks/{webhookId}/regenerate-secret"),
    ("webhooks.deliveries.list", ("w1",), "GET /webhooks/{webhookId}/deliveries"),
    ("webhooks.deliveries.iterate", ("w1",), "GET /webhooks/{webhookId}/deliveries"),
    (
        "webhooks.deliveries.retrieve",
        ("w1", "dl1"),
        "GET /webhooks/{webhookId}/deliveries/{deliveryId}",
    ),
]

LAYOUT = {
    "domains": [
        "create",
        "delete",
        "iterate",
        "list",
        "retrieve",
        "update_projects",
        "verify_dns_record",
        "verify_dns_records",
    ],
    "messages": [
        "cancel",
        "events",
        "html",
        "iterate",
        "iterate_events",
        "list",
        "process",
        "reschedule",
        "retrieve",
        "source",
        "text",
    ],
    "projects": ["create", "delete", "iterate", "list", "retrieve", "rotate_token", "update"],
    "projects.report_forwarding": ["delete", "resend_code", "retrieve", "update", "verify"],
    "routes": [
        "create",
        "delete",
        "iterate",
        "list",
        "retrieve",
        "update",
        "verify_inbound_domain",
    ],
    "stats": ["retrieve"],
    "suppressions": ["create", "delete", "iterate", "list"],
    "team": ["retrieve", "roles", "update", "usage"],
    "team.members": ["iterate", "list", "retrieve", "update_assignment"],
    "webhooks": [
        "create",
        "delete",
        "iterate",
        "list",
        "regenerate_secret",
        "retrieve",
        "test",
        "update",
    ],
    "webhooks.deliveries": ["iterate", "list", "retrieve"],
    "emails": ["compose", "ping", "send", "send_batch"],
    "": ["analytics", "blocked_file_types", "close", "ping"],
}


def respond_for(request: httpx.Request) -> httpx.Response:
    """A minimal valid answer for any operation."""
    path = request.url.path.removeprefix("/v1")
    for key, operation in OPERATIONS.items():
        method, template = key.split(" ", 1)
        if method == request.method and re.fullmatch(re.sub(r"\{\w+\}", "[^/]+", template), path):
            if operation.response.type == "empty":
                return httpx.Response(204)
            if operation.response.type == "text":
                return httpx.Response(200, text="pong")
            if operation.pagination:
                return httpx.Response(200, json={"data": [{"id": "x"}], "next_cursor": None})
            return httpx.Response(200, json={})
    return httpx.Response(404, json={"message": "no such route"})


def operation_of(request: httpx.Request) -> str:
    path = request.url.path.removeprefix("/v1")
    for key in OPERATIONS:
        method, template = key.split(" ", 1)
        if method == request.method and re.fullmatch(re.sub(r"\{\w+\}", "[^/]+", template), path):
            return key
    raise AssertionError(f"no operation for {request.method} {path}")


def resolve(root: Any, dotted: str) -> Any:
    target = root
    for part in dotted.split("."):
        target = getattr(target, part)
    return target


def test_every_operation_is_reachable_from_the_sync_client(
    api: MockAPI, client: Lettermint
) -> None:
    api.respond(respond_for)
    reached: set[str] = set()
    for dotted, args, key in CALLS:
        before = len(api.requests)
        result = resolve(client, dotted)(*args)
        if isinstance(result, Iterator):
            assert list(result) == [{"id": "x"}]
        assert [operation_of(r) for r in api.requests[before:]] == [key], dotted
        reached.add(key)
    assert reached == set(OPERATIONS)


@pytest.mark.anyio
async def test_every_operation_is_reachable_from_the_async_client(
    api: MockAPI, aclient: AsyncLettermint
) -> None:
    api.respond(respond_for)
    reached: set[str] = set()
    for dotted, args, key in CALLS:
        before = len(api.requests)
        result = resolve(aclient, dotted)(*args)
        if isinstance(result, AsyncIterator):
            assert [item async for item in result] == [{"id": "x"}]
        else:
            await result
        assert [operation_of(r) for r in api.requests[before:]] == [key], dotted
        reached.add(key)
    assert reached == set(OPERATIONS)


def _public_methods(obj: Any) -> list[str]:
    return sorted(
        name
        for name, value in inspect.getmembers(type(obj))
        if not name.startswith("_") and callable(value)
    )


@pytest.mark.parametrize("cls", [Lettermint, AsyncLettermint])
def test_layout_matches_the_other_sdks(cls: Any) -> None:
    client = cls(sending_token="lm_abc", team_token="lm_team_abc")
    for group, methods in LAYOUT.items():
        target = resolve(client, group) if group else client
        assert _public_methods(target) == methods, group


def test_sync_and_async_clients_have_the_same_signatures() -> None:
    sync = Lettermint(sending_token="lm_abc", team_token="lm_team_abc")
    asynchronous = AsyncLettermint(sending_token="lm_abc", team_token="lm_team_abc")
    for group in LAYOUT:
        for name in LAYOUT[group]:
            left = resolve(sync, f"{group}.{name}" if group else name)
            right = resolve(asynchronous, f"{group}.{name}" if group else name)
            assert str(inspect.signature(left)).replace("Async", "") == str(
                inspect.signature(right)
            ).replace("Async", ""), (group, name)
            assert inspect.iscoroutinefunction(right) != (
                name in ("compose", "iterate", "iterate_events")
            ), (group, name)
    builder_methods = _public_methods(sync.emails.compose())
    assert builder_methods == _public_methods(asynchronous.emails.compose())
    assert "send" in builder_methods and "build" in builder_methods and "from_" in builder_methods


def test_return_annotations_match_the_operation_table() -> None:
    client = Lettermint(sending_token="lm_abc", team_token="lm_team_abc")
    for dotted, _, key in CALLS:
        if dotted in ("ping", "emails.ping"):
            continue
        hints = typing.get_type_hints(resolve(client, dotted))
        operation = OPERATIONS[key]
        returned = hints["return"]
        if dotted.endswith(("iterate", "iterate_events")):
            assert operation.pagination is not None
            assert typing.get_args(returned) == (getattr(lm_types, operation.pagination.items),), (
                dotted
            )
        elif operation.response.type == "text":
            assert returned is str, dotted
        elif operation.response.type == "empty":
            assert returned is type(None), dotted
        else:
            assert returned == getattr(lm_types, operation.response.type), dotted


def test_pagination_follows_cursors_and_stops_on_a_repeat(api: MockAPI, client: Lettermint) -> None:
    pages = {
        None: {"data": [1, 2], "next_cursor": "c2"},
        "c2": {"data": [3], "next_cursor": "c3"},
        "c3": {"data": [4], "next_cursor": "c2"},
    }
    api.respond(
        lambda request: httpx.Response(200, json=pages[request.url.params.get("page[cursor]")])
    )
    items: list[Any] = list(
        client.domains.iterate({"page": {"size": 2}, "filter": {"status": "verified"}})
    )
    assert items == [1, 2, 3, 4]
    assert [r.url.params.get("page[cursor]") for r in api.requests] == [None, "c2", "c3"]
    assert all(
        r.url.params["page[size]"] == "2" and r.url.params["filter[status]"] == "verified"
        for r in api.requests
    )


def test_pagination_is_lazy_and_uses_the_cursor_parameter_of_the_operation(
    api: MockAPI, client: Lettermint
) -> None:
    api.respond(
        lambda request: httpx.Response(
            200, json={"data": ["a"], "next_cursor": "n" + (request.url.params.get("cursor") or "")}
        )
    )
    iterator: Iterator[Any] = client.webhooks.iterate()
    assert api.requests == []
    assert [next(iterator), next(iterator)] == ["a", "a"]
    assert [r.url.params.get("cursor") for r in api.requests] == [None, "n"]


def test_pagination_rejects_pages_without_data(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"items": []})
    with pytest.raises(
        UnexpectedResponseError,
        match="domains.iterate: the API returned a page without a data array",
    ):
        list(client.domains.iterate())


def test_top_level_exports_do_not_collide_with_generated_types() -> None:
    assert not set(lettermint.__all__) & (set(lm_types.__all__) - {"CursorPage"})
    assert set(lettermint.__all__) == {
        name for name in dir(lettermint) if not name.startswith("_")
    } - {
        "exceptions",
        "webhook",
    } | {"__version__"}


def test_email_message_mirrors_the_generated_request() -> None:
    assert lettermint.EmailMessage.__required_keys__ == lm_types.SendMailRequest.__required_keys__
    assert lettermint.EmailMessage.__optional_keys__ == lm_types.SendMailRequest.__optional_keys__


def test_generated_header() -> None:
    from pathlib import Path

    folder = Path(lettermint.__file__).parent / "_generated"
    for name in ("__init__.py", "types.py", "operations.py"):
        lines = (folder / name).read_text().splitlines()
        assert lines[0] == "# Generated by lettermint/sdk-generator — do not edit."
        assert lines[4] == "# Naming profile: next"
    assert BASE_URL  # the mock origin is never the real API
