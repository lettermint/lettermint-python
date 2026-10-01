import json

import pytest
import respx
from httpx import Response

from lettermint import AsyncLettermint, Lettermint, types

PAYLOAD = {
    "metrics": ["accepted", "delivered"],
    "include": ["summary"],
    "interval": "day",
    "filters": [{"dimension": "project", "operator": "eq", "values": ["project/id"]}],
    "sort": {"metric": "accepted", "direction": "desc"},
    "limit": 10,
}
RESOURCE = {"destination": None, "verified": False, "verified_at": None}


def routes():
    base = "https://api.lettermint.co/v1"
    path = base + "/projects/project%2Fid/report-forwarding"
    return [
        respx.post(base + "/analytics").mock(
            return_value=Response(200, json={"data": {}, "meta": {}, "pagination": ["cursor"]})
        ),
        respx.get(path).mock(return_value=Response(200, json={"data": RESOURCE})),
        respx.put(path).mock(return_value=Response(200, json={"data": RESOURCE})),
        respx.post(path + "/verify").mock(return_value=Response(200, json={"data": RESOURCE})),
        respx.post(path + "/resend-code").mock(return_value=Response(200, json={"data": RESOURCE})),
        respx.delete(path).mock(return_value=Response(204)),
    ]


def assert_requests(registered):
    for route in registered:
        assert route.call_count == 1
        request = route.calls.last.request
        assert request.headers["authorization"] == "Bearer team-token"
        assert "x-lettermint-token" not in request.headers
    assert json.loads(registered[0].calls.last.request.content) == PAYLOAD
    assert json.loads(registered[2].calls.last.request.content) == {
        "destination": "reports@example.com"
    }
    assert json.loads(registered[3].calls.last.request.content) == {"code": "123456"}


@respx.mock
def test_sync_analytics_and_forwarding():
    registered = routes()
    with Lettermint.api("team-token") as api:
        api.analytics(PAYLOAD)
        assert api.projects.retrieve_report_forwarding("project/id")["data"] == RESOURCE
        api.projects.update_report_forwarding("project/id", {"destination": "reports@example.com"})
        api.projects.verify_report_forwarding("project/id", {"code": "123456"})
        api.projects.resend_report_forwarding_code("project/id")
        assert api.projects.delete_report_forwarding("project/id") is None
    assert_requests(registered)


@pytest.mark.asyncio
@respx.mock
async def test_async_analytics_and_forwarding():
    registered = routes()
    async with AsyncLettermint.api("team-token") as api:
        await api.analytics(PAYLOAD)
        assert (await api.projects.retrieve_report_forwarding("project/id"))["data"] == RESOURCE
        await api.projects.update_report_forwarding(
            "project/id", {"destination": "reports@example.com"}
        )
        await api.projects.verify_report_forwarding("project/id", {"code": "123456"})
        await api.projects.resend_report_forwarding_code("project/id")
        assert await api.projects.delete_report_forwarding("project/id") is None
    assert_requests(registered)


def test_public_types_and_new_fields():
    for name in ("RescheduleMessageResponse", "CancelScheduledMessageResponse", "CursorPaginator"):
        assert hasattr(types, name)
    assert "api_token" in types.ProjectStoreResponse.__annotations__
    assert "delivery_mode" in types.ProjectListData.__annotations__
    assert "delivery_mode_filter" in types.WebhookListData.__annotations__
    assert "sandbox" in types.WebhookDeliveryListData.__annotations__
    assert "ticket_identifier" in types.SuppressionDestroyResponse.__annotations__
    assert set(types.AnalyticsRequest.__annotations__) == {
        "metrics",
        "from",
        "to",
        "timezone",
        "include",
        "group_by",
        "filters",
        "interval",
        "compare",
        "include_trend",
        "sort",
        "limit",
        "cursor",
    }
