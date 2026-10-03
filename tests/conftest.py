"""Shared fixtures: fake tokens and a recording mock API on ``httpx.MockTransport``.

No test talks to the real Lettermint API.
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

import lettermint

SENDING_TOKEN = "lm_TestSendingToken0123456789abcdef"
TEAM_TOKEN = "lm_team_TestTeamToken0123456789abcdef"
BASE_URL = "https://api.lettermint.test/v1"

Handler = Callable[[httpx.Request], Any]


class MockAPI:
    """Records every request and answers with ``handler`` (default: a JSON ``{}``)."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.handler: Handler = lambda request: httpx.Response(200, json={})

    def respond(self, handler: Handler) -> None:
        self.handler = handler

    def json(self, status: int, body: Any, **headers: str) -> None:
        self.handler = lambda request: httpx.Response(status, json=body, headers=headers)

    def _record(self, request: httpx.Request) -> Any:
        request.read()
        self.requests.append(request)
        return self.handler(request)

    def sync_client(self, **options: Any) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self._record), **options)

    def async_client(self, **options: Any) -> httpx.AsyncClient:
        async def handle(request: httpx.Request) -> httpx.Response:
            result = self._record(request)
            if inspect.isawaitable(result):
                result = await result
            return result  # type: ignore[no-any-return]

        return httpx.AsyncClient(transport=httpx.MockTransport(handle), **options)

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    def body(self, index: int = -1) -> Any:
        return json.loads(self.requests[index].content)


@pytest.fixture
def api() -> MockAPI:
    return MockAPI()


@pytest.fixture
def client(api: MockAPI) -> lettermint.Lettermint:
    return lettermint.Lettermint(
        sending_token=SENDING_TOKEN,
        team_token=TEAM_TOKEN,
        base_url=BASE_URL,
        http_client=api.sync_client(),
    )


@pytest.fixture
def aclient(api: MockAPI) -> lettermint.AsyncLettermint:
    return lettermint.AsyncLettermint(
        sending_token=SENDING_TOKEN,
        team_token=TEAM_TOKEN,
        base_url=BASE_URL,
        http_client=api.async_client(),
    )


@pytest.fixture(params=["asyncio", "trio"])
def anyio_backend(request: pytest.FixtureRequest) -> str:
    return str(request.param)


MESSAGE: lettermint.EmailMessage = {
    "from": "Acme <hello@acme.test>",
    "to": ["jane@example.test"],
    "subject": "Welcome",
    "html": "<p>Hi</p>",
}
