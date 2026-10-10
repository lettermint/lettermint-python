"""Analytics: realistic responses, ``analytics_pages`` and the errors of ``POST /analytics``."""

from __future__ import annotations

import copy
import json
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import pytest

from lettermint import (
    AsyncLettermint,
    Lettermint,
    LettermintConfigError,
    ServerError,
    ValidationError,
)
from lettermint.types import AnalyticsQuery, AnalyticsResponse

from .conftest import BASE_URL, SENDING_TOKEN, MockAPI

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> Any:
    return json.loads((FIXTURES / f"{name}.json").read_text())


PAGE_ONE = fixture("analytics-page-1")
PAGE_TWO = fixture("analytics-page-2")
SUMMARY_ONLY = fixture("analytics-summary")

QUERY: AnalyticsQuery = {
    "metrics": ["delivered", "bounced", "delivery_rate", "delivery_latency_p50_ms"],
    "include": ["summary", "time_series", "breakdown"],
    "group_by": ["recipient_domain"],
    "interval": "hour",
    "timezone": "Asia/Kolkata",
    "compare": "previous_period",
    "limit": 2,
}
WITH_CURSOR: AnalyticsQuery = {**QUERY, "cursor": "cursor-page-2"}
EXPIRED = {
    "message": "The analytics cursor is invalid or expired. Submit a new query.",
    "errors": {"cursor": ["The analytics cursor is invalid or expired. Submit a new query."]},
}


def first_then(api: MockAPI, first: httpx.Response, later: httpx.Response) -> None:
    api.respond(lambda request: first if len(api.requests) == 1 else later)


# ---------------------------------------------------------------- responses


def test_analytics_keeps_null_values_empty_rate_bases_and_both_timestamp_formats(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(200, PAGE_ONE)
    result = client.analytics(QUERY)

    assert (api.last.method, api.last.url.path) == ("POST", "/v1/analytics")
    assert api.body() == QUERY
    summary = result["data"]["summary"]
    assert summary["metrics"] == {
        "delivered": 1200,
        "bounced": 0,
        "delivery_rate": 0.9836,
        "delivery_latency_p50_ms": None,
    }
    assert summary["rate_bases"]["delivery_rate"] == {"numerator": 1200, "denominator": 1220}
    assert summary["previous"]["rate_bases"]["delivery_rate"] == {
        "numerator": None,
        "denominator": None,
    }
    assert summary["change"]["delivery_rate"] == {
        "absolute": None,
        "relative": None,
        "percentage_points": None,
    }
    assert "percentage_points" not in summary["change"]["delivered"]

    complete, unavailable = result["data"]["time_series"]
    assert complete["from"] == "2026-09-15T08:30:00+05:30"
    assert datetime.fromisoformat(complete["from"]) == datetime(
        2026, 9, 15, 3, 0, tzinfo=timezone.utc
    )
    assert (unavailable["available"], unavailable["partial"]) == (False, True)
    assert unavailable["rate_bases"] == {}
    assert unavailable["metrics"]["delivered"] is None

    meta = result["meta"]
    assert meta["generated_at"] == "2026-09-15T04:12:30.482915Z"
    assert meta["from"] == "2026-09-15T03:00:00.000000Z"
    assert meta["last_ingested_at"] is None
    assert meta["comparison"] == {
        "from": "2026-09-15T01:00:00.000000Z",
        "to": "2026-09-15T03:00:00.000000Z",
        "partial": False,
    }
    assert result["pagination"] == {
        "total_groups": 3,
        "returned_groups": 2,
        "next_cursor": "cursor-page-2",
        "truncated": False,
    }


def test_analytics_leaves_out_the_sections_and_comparison_a_query_did_not_ask_for(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(200, SUMMARY_ONLY)
    result = client.analytics({"metrics": ["delivered"]})
    assert result["data"]["summary"]["rate_bases"] == {}
    assert "time_series" not in result["data"]
    assert "breakdown" not in result["data"]
    assert "previous" not in result["data"]["summary"]
    assert "comparison" not in result["meta"]
    assert result["pagination"]["next_cursor"] is None


def test_analytics_keeps_a_null_dimension_value_in_a_breakdown_row(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(200, PAGE_TWO)
    result = client.analytics(WITH_CURSOR)
    breakdown = result["data"]["breakdown"]
    assert len(breakdown) == 1
    assert breakdown[0]["dimensions"] == {"recipient_domain": None}
    assert breakdown[0]["metrics"]["bounced"] is None


# ---------------------------------------------------------------- analytics_pages


def test_analytics_pages_follows_next_cursor_and_yields_every_response(
    api: MockAPI, client: Lettermint
) -> None:
    sent = copy.deepcopy(QUERY)
    first_then(api, httpx.Response(200, json=PAGE_ONE), httpx.Response(200, json=PAGE_TWO))
    pages = list(client.analytics_pages(sent))

    assert pages == [PAGE_ONE, PAGE_TWO]
    assert [(r.method, r.url.path) for r in api.requests] == [("POST", "/v1/analytics")] * 2
    assert api.body(0) == QUERY
    assert api.body(1) == WITH_CURSOR
    assert sent == QUERY

    rows = [row for page in pages for row in page["data"].get("breakdown", [])]
    assert [row["dimensions"]["recipient_domain"] for row in rows] == [
        "gmail.com",
        "outlook.com",
        None,
    ]
    assert (pages[1]["pagination"]["returned_groups"], pages[1]["pagination"]["next_cursor"]) == (
        1,
        None,
    )


def test_analytics_pages_makes_one_request_for_a_query_without_more_pages(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(200, SUMMARY_ONLY)
    assert list(client.analytics_pages({"metrics": ["delivered"]})) == [SUMMARY_ONLY]
    assert len(api.requests) == 1


def test_analytics_pages_requests_the_next_page_only_when_it_is_asked_for(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(200, PAGE_ONE)
    pages: Iterator[AnalyticsResponse] = client.analytics_pages(QUERY)
    assert api.requests == []
    for page in pages:
        assert page["pagination"]["next_cursor"] == "cursor-page-2"
        break
    assert len(api.requests) == 1


def test_analytics_pages_stops_when_the_api_repeats_a_cursor(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(200, PAGE_ONE)
    assert len(list(client.analytics_pages(QUERY))) == 2
    assert len(api.requests) == 2


def test_analytics_pages_stops_when_the_api_returns_the_cursor_the_query_started_from(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(200, PAGE_ONE)
    assert len(list(client.analytics_pages(WITH_CURSOR))) == 1
    assert [api.body(index) for index in range(len(api.requests))] == [WITH_CURSOR]


def test_analytics_pages_passes_the_timeout_to_every_page_and_surfaces_an_expired_cursor(
    api: MockAPI, client: Lettermint
) -> None:
    first_then(api, httpx.Response(200, json=PAGE_ONE), httpx.Response(422, json=EXPIRED))
    pages = client.analytics_pages(QUERY, timeout=7)
    assert next(pages) == PAGE_ONE
    with pytest.raises(ValidationError) as caught:
        next(pages)
    assert caught.value.errors == EXPIRED["errors"]
    assert len(api.requests) == 2
    assert all(r.extensions["timeout"]["read"] == 7 for r in api.requests)


def test_analytics_pages_checks_the_token_and_the_timeout_before_the_first_page(
    api: MockAPI, client: Lettermint
) -> None:
    with pytest.raises(LettermintConfigError, match="timeout must be a positive number"):
        client.analytics_pages(QUERY, timeout=-1)
    sending_only = Lettermint(SENDING_TOKEN, base_url=BASE_URL, http_client=api.sync_client())
    with pytest.raises(LettermintConfigError, match="analytics_pages needs team_token"):
        sending_only.analytics_pages(QUERY)
    assert api.requests == []


@pytest.mark.anyio
async def test_async_analytics_pages_follows_next_cursor_and_yields_every_response(
    api: MockAPI, aclient: AsyncLettermint
) -> None:
    sent = copy.deepcopy(QUERY)
    first_then(api, httpx.Response(200, json=PAGE_ONE), httpx.Response(200, json=PAGE_TWO))
    pages = [page async for page in aclient.analytics_pages(sent)]
    assert pages == [PAGE_ONE, PAGE_TWO]
    assert [api.body(0), api.body(1)] == [QUERY, WITH_CURSOR]
    assert sent == QUERY


@pytest.mark.anyio
async def test_async_analytics_pages_is_lazy_and_stops_on_a_repeated_cursor(
    api: MockAPI, aclient: AsyncLettermint
) -> None:
    api.json(200, PAGE_ONE)
    pages: AsyncIterator[AnalyticsResponse] = aclient.analytics_pages(QUERY)
    assert api.requests == []
    assert (await anext(pages))["pagination"]["next_cursor"] == "cursor-page-2"
    assert len(api.requests) == 1
    assert [page async for page in pages] == [PAGE_ONE]
    assert len(api.requests) == 2
    assert [page async for page in aclient.analytics_pages(WITH_CURSOR)] == [PAGE_ONE]
    assert len(api.requests) == 3


@pytest.mark.anyio
async def test_async_analytics_pages_passes_the_timeout_and_surfaces_an_expired_cursor(
    api: MockAPI, aclient: AsyncLettermint
) -> None:
    first_then(api, httpx.Response(200, json=PAGE_ONE), httpx.Response(422, json=EXPIRED))
    pages = aclient.analytics_pages(QUERY, timeout=7)
    assert await anext(pages) == PAGE_ONE
    with pytest.raises(ValidationError) as caught:
        await anext(pages)
    assert caught.value.errors == EXPIRED["errors"]
    assert all(r.extensions["timeout"]["read"] == 7 for r in api.requests)
    with pytest.raises(LettermintConfigError, match="timeout must be a positive number"):
        aclient.analytics_pages(QUERY, timeout=-1)
    assert len(api.requests) == 2


# ---------------------------------------------------------------- errors


def test_analytics_reads_field_errors_from_a_422(api: MockAPI, client: Lettermint) -> None:
    body = {
        "message": "smtp_response_group can only be used in group_by.",
        "errors": {"filters": ["smtp_response_group can only be used in group_by."]},
    }
    api.json(422, body)
    with pytest.raises(ValidationError) as caught:
        client.analytics(QUERY)
    assert (caught.value.status, caught.value.message, caught.value.errors) == (
        422,
        body["message"],
        body["errors"],
    )


def test_analytics_reads_retry_after_from_a_503(api: MockAPI, client: Lettermint) -> None:
    body = {"error": {"code": "SERVICE_UNAVAILABLE", "message": "Try again shortly."}}
    api.json(503, body, **{"Retry-After": "2"})
    with pytest.raises(ServerError) as caught:
        client.analytics(QUERY)
    assert (caught.value.status, caught.value.code, caught.value.retry_after) == (
        503,
        "SERVICE_UNAVAILABLE",
        2,
    )


def test_analytics_has_no_retry_after_for_a_503_or_504_without_the_header(
    api: MockAPI, client: Lettermint
) -> None:
    api.json(503, {"message": "Analytics is unavailable."})
    with pytest.raises(ServerError) as unavailable:
        client.analytics(QUERY)
    assert unavailable.value.retry_after is None

    message = (
        "Analytics exceeded the query time limit. Retry with a shorter period or fewer dimensions."
    )
    api.json(504, {"message": message})
    with pytest.raises(ServerError) as timed_out:
        client.analytics(QUERY)
    assert (timed_out.value.status, timed_out.value.message) == (504, message)
    assert timed_out.value.retry_after is None
