"""Check the optional, nullable inbound route domain."""

from typing import Any

import pytest
import respx
from httpx import Response

from lettermint import Lettermint
from lettermint.types import RouteData


@pytest.mark.parametrize("domain", ["incoming.example.com", None, ...])
@respx.mock
def test_inbound_route_domain(domain: Any) -> None:
    payload: RouteData = {
        "id": "route_1",
        "project_id": "project_1",
        "slug": "incoming",
        "name": "Incoming",
        "route_type": "inbound",
        "is_default": False,
        "created_at": "2026-10-01T12:00:00Z",
        "updated_at": "2026-10-01T12:00:00Z",
    }
    if domain is not ...:
        payload["inbound_route_domain"] = domain
    respx.get("https://api.lettermint.co/v1/routes/route_1").mock(
        return_value=Response(200, json=payload)
    )
    with Lettermint.api("team-token") as api:
        result = api.routes.retrieve("route_1")
    assert result == payload
    assert result.get("inbound_route_domain") == (None if domain is ... else domain)


def test_inbound_route_domain_is_declared() -> None:
    assert "inbound_route_domain" in RouteData.__annotations__
    assert "NotRequired[str | None]" in str(RouteData.__annotations__["inbound_route_domain"])
