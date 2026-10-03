"""Query strings are serialized exactly like the Node.js SDK (``src/query.ts``)."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from lettermint import Lettermint
from lettermint._query import serialize_query, with_query_param

from .conftest import MockAPI

# The expected strings were produced by Node's serializeQuery (URLSearchParams).
CASES: list[tuple[dict[str, Any], str]] = [
    (
        {
            "page": {"size": 30, "cursor": "abc"},
            "filter": {"status": "verified"},
            "sort": ["-created_at", "domain"],
        },
        "page%5Bsize%5D=30&page%5Bcursor%5D=abc&filter%5Bstatus%5D=verified&sort=-created_at%2Cdomain",
    ),
    (
        {
            "filter": {
                "tags": [
                    {"name": "campaign", "value": "welcome"},
                    {"name": "plan", "value": "pro"},
                ],
                "search": "a b+c&d=e",
            }
        },
        "filter%5Btags%5D%5B0%5D%5Bname%5D=campaign&filter%5Btags%5D%5B0%5D%5Bvalue%5D=welcome"
        "&filter%5Btags%5D%5B1%5D%5Bname%5D=plan&filter%5Btags%5D%5B1%5D%5Bvalue%5D=pro&filter%5Bsearch%5D=a+b%2Bc%26d%3De",
    ),
    (
        {"filter": {"enabled": True, "is_default": False}, "include": ["dnsRecords"]},
        "filter%5Benabled%5D=1&filter%5Bis_default%5D=0&include=dnsRecords",
    ),
    ({"cursor": "x/y~z*", "page[size]": 10}, "cursor=x%2Fy%7Ez*&page%5Bsize%5D=10"),
    (
        {"from": "2026-10-01", "to": "2026-10-31", "project_id": None, "include_machine": True},
        "from=2026-10-01&to=2026-10-31&include_machine=1",
    ),
    (
        {"filter": {"search": "Grüße ✓ 😀", "empty": [], "nulls": [None, "a", None]}},
        "filter%5Bsearch%5D=Gr%C3%BC%C3%9Fe+%E2%9C%93+%F0%9F%98%80&filter%5Bnulls%5D=a",
    ),
    ({"sort": [], "page": {}}, ""),
    ({"weird": "!'()~*-._ :/?#[]@$,;"}, "weird=%21%27%28%29%7E*-._+%3A%2F%3F%23%5B%5D%40%24%2C%3B"),
    ({"page": {"size": 30.0}}, "page%5Bsize%5D=30"),
]


@pytest.mark.parametrize(("query", "expected"), CASES)
def test_serialization_matches_node(query: dict[str, Any], expected: str) -> None:
    assert serialize_query(query) == expected


def test_empty_queries() -> None:
    assert serialize_query(None) == ""
    assert serialize_query({}) == ""


def test_with_query_param() -> None:
    query = {"page": {"size": 10}, "filter": {"status": "verified"}}
    assert with_query_param(query, "page[cursor]", "c2") == {
        "page": {"size": 10, "cursor": "c2"},
        "filter": {"status": "verified"},
    }
    assert query == {"page": {"size": 10}, "filter": {"status": "verified"}}  # unchanged
    assert with_query_param(None, "cursor", "c2") == {"cursor": "c2"}
    assert with_query_param({"page[cursor]": "old"}, "page[cursor]", "new") == {
        "page": {"cursor": "new"}
    }


def test_queries_reach_the_wire(api: MockAPI, client: Lettermint) -> None:
    api.json(200, {"data": [], "next_cursor": None})
    client.domains.list(
        {"page": {"size": 30}, "filter": {"status": "verified"}, "sort": ["-created_at"]}
    )
    assert api.last.url.query == b"page%5Bsize%5D=30&filter%5Bstatus%5D=verified&sort=-created_at"
    client.messages.list({"filter": {"tags": [{"name": "campaign", "value": "welcome"}]}})
    assert (
        api.last.url.query
        == b"filter%5Btags%5D%5B0%5D%5Bname%5D=campaign&filter%5Btags%5D%5B0%5D%5Bvalue%5D=welcome"
    )
    api.respond(lambda request: httpx.Response(200, json={"data": []}))
    client.stats.retrieve({"from": "2026-10-01", "to": "2026-10-31", "include_machine": False})
    assert api.last.url.query == b"from=2026-10-01&to=2026-10-31&include_machine=0"
    client.domains.retrieve("d1", {"include": ["dnsRecords"]})
    assert api.last.url.query == b"include=dnsRecords"
