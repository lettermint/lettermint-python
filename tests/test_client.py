"""Client construction, tokens, options, redaction and lifecycle."""

from __future__ import annotations

import copy
import pickle
import pprint
from typing import Any

import httpx
import pytest

import lettermint
from lettermint import AsyncLettermint, Lettermint, LettermintConfigError

from .conftest import BASE_URL, SENDING_TOKEN, TEAM_TOKEN, MockAPI

CLIENTS = [Lettermint, AsyncLettermint]


@pytest.mark.parametrize("cls", CLIENTS)
@pytest.mark.parametrize(
    ("token", "kind"),
    [
        ("lm_team_Conformance0Token1Fake2Value3Only4Test5D", "team"),
        ("lm_Proj32Conformance0Token1Fake2Val", "sending"),
        ("lm_Proj22Conformance0Toke", "sending"),
    ],
)
def test_token_string_is_classified_by_prefix(cls: Any, token: str, kind: str) -> None:
    client = cls(token)
    config = client._transport.config
    assert (config.team_token is not None) == (kind == "team")
    assert (config.sending_token is not None) == (kind == "sending")


@pytest.mark.parametrize("cls", CLIENTS)
@pytest.mark.parametrize(
    "token",
    [
        "lm_sso_SsoConformance0Token1Fake2Value3",
        "",
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjb25mb3JtYW5jZSJ9.Y29uZm9ybWFuY2Utc2lnbmF0dXJl",
        "sk_conformance_0123456789abcdef",
        "lm_team_",
        "lm_",
        "lm_with space",
        " lm_leadingspace",
    ],
)
def test_other_token_formats_are_config_errors_without_the_token(cls: Any, token: str) -> None:
    with pytest.raises(LettermintConfigError) as caught:
        cls(token)
    assert (
        str(caught.value)
        == "Unrecognised token format; pass sending_token=... or team_token=... instead."
    )
    if token:
        assert token not in str(caught.value)


@pytest.mark.parametrize("cls", CLIENTS)
def test_a_token_is_required(cls: Any) -> None:
    with pytest.raises(LettermintConfigError, match="Pass sending_token, team_token or both"):
        cls()


@pytest.mark.parametrize("cls", CLIENTS)
def test_shorthand_and_explicit_tokens_are_exclusive(cls: Any) -> None:
    with pytest.raises(LettermintConfigError, match="not both"):
        cls(SENDING_TOKEN, team_token=TEAM_TOKEN)


@pytest.mark.parametrize("cls", CLIENTS)
@pytest.mark.parametrize(
    ("options", "message"),
    [
        ({"sending_token": ""}, "sending_token must be a non-empty string"),
        ({"team_token": 42}, "team_token must be a non-empty string"),
        ({"sending_token": "lm_abc\n"}, "not allowed in an HTTP header"),
        ({"sending_token": SENDING_TOKEN, "timeout": 0}, "timeout must be a positive number"),
        (
            {"sending_token": SENDING_TOKEN, "timeout": float("inf")},
            "timeout must be a positive number",
        ),
        ({"sending_token": SENDING_TOKEN, "timeout": True}, "timeout must be a positive number"),
        ({"sending_token": SENDING_TOKEN, "base_url": "ftp://x"}, "absolute http"),
        ({"sending_token": SENDING_TOKEN, "base_url": "/v1"}, "absolute http"),
        ({"sending_token": SENDING_TOKEN, "base_url": "https://u:p@api.test"}, "credentials"),
        ({"sending_token": SENDING_TOKEN, "base_url": "https://api.test/v1?x=1"}, "query"),
        ({"sending_token": SENDING_TOKEN, "http_client": object()}, "http_client must be"),
    ],
)
def test_invalid_options(cls: Any, options: dict[str, Any], message: str) -> None:
    with pytest.raises(LettermintConfigError, match=message) as caught:
        cls(**options)
    assert "lm_abc" not in str(caught.value)


def test_the_http_client_type_must_match() -> None:
    with pytest.raises(LettermintConfigError, match="httpx.Client"):
        Lettermint(sending_token=SENDING_TOKEN, http_client=httpx.AsyncClient())  # type: ignore[arg-type]
    with pytest.raises(LettermintConfigError, match="httpx.AsyncClient"):
        AsyncLettermint(sending_token=SENDING_TOKEN, http_client=httpx.Client())  # type: ignore[arg-type]


def test_base_url_trailing_slashes_are_removed(api: MockAPI) -> None:
    client = Lettermint(TEAM_TOKEN, base_url=BASE_URL + "//", http_client=api.sync_client())
    api.respond(lambda request: httpx.Response(200, text="pong"))
    client.ping()
    assert str(api.last.url) == BASE_URL + "/ping"


def _renderings(value: Any) -> list[str]:
    rendered = [repr(value), str(value), f"{value}", f"{value!r}", pprint.pformat(value)]
    if hasattr(value, "__dict__"):
        rendered.append(repr(vars(value)))
        rendered += [repr(item) for item in vars(value).values()]
        rendered += [repr(vars(item)) for item in vars(value).values() if hasattr(item, "__dict__")]
    return rendered


@pytest.mark.parametrize("cls", CLIENTS)
def test_tokens_never_appear_in_debug_output(cls: Any) -> None:
    client = cls(sending_token=SENDING_TOKEN, team_token=TEAM_TOKEN)
    subjects = [
        client,
        client.emails,
        client.domains,
        client.webhooks.deliveries,
        client.projects.report_forwarding,
        client._transport,
        client._transport.config,
        client.emails.compose().from_("a@acme.test").to("b@example.test"),
    ]
    for subject in subjects:
        for text in _renderings(subject):
            assert SENDING_TOKEN not in text
            assert TEAM_TOKEN not in text
    assert repr(client) == (
        f"{cls.__name__}(base_url='https://api.lettermint.co/v1', timeout=30.0, "
        "sending_token=[redacted], team_token=[redacted])"
    )
    assert repr(cls(TEAM_TOKEN)).endswith("sending_token=None, team_token=[redacted])")


@pytest.mark.parametrize("cls", CLIENTS)
def test_clients_and_credentials_cannot_be_pickled_or_copied(cls: Any) -> None:
    client = cls(sending_token=SENDING_TOKEN)
    for subject in (
        client,
        client.emails,
        client._transport,
        client._transport.config.sending_token,
    ):
        with pytest.raises(TypeError):
            pickle.dumps(subject)
    with pytest.raises(TypeError):
        copy.deepcopy(client._transport.config)


def test_sync_context_manager_closes_the_client_it_created() -> None:
    with Lettermint(SENDING_TOKEN) as client:
        http = client._transport._client
        assert not http.is_closed
    assert http.is_closed
    with pytest.raises(LettermintConfigError, match="emails.ping: the client is closed"):
        client.emails.ping()


@pytest.mark.anyio
async def test_async_context_manager_closes_the_client_it_created() -> None:
    async with AsyncLettermint(SENDING_TOKEN) as client:
        http = client._transport._client
        assert not http.is_closed
    assert http.is_closed
    with pytest.raises(LettermintConfigError, match="the client is closed"):
        await client.emails.ping()


def test_an_injected_http_client_is_not_closed(api: MockAPI) -> None:
    http = api.sync_client()
    with Lettermint(SENDING_TOKEN, http_client=http):
        pass
    assert not http.is_closed


@pytest.mark.anyio
async def test_an_injected_async_http_client_is_not_closed(api: MockAPI) -> None:
    http = api.async_client()
    async with AsyncLettermint(SENDING_TOKEN, http_client=http):
        pass
    assert not http.is_closed
    await http.aclose()


def test_a_closed_injected_http_client_is_a_config_error(api: MockAPI) -> None:
    http = api.sync_client()
    client = Lettermint(SENDING_TOKEN, http_client=http)
    http.close()
    with pytest.raises(LettermintConfigError, match="the HTTP client is closed") as caught:
        client.emails.ping()
    assert caught.value.__context__ is None and caught.value.__cause__ is None


def test_the_default_http_client_does_not_follow_redirects() -> None:
    client = Lettermint(SENDING_TOKEN, timeout=12.5)
    http = client._transport._client
    assert isinstance(http, httpx.Client)
    assert http.follow_redirects is False
    assert http.timeout.read == 12.5
    client.close()


def test_version_and_user_agent(api: MockAPI, client: Lettermint) -> None:
    api.respond(lambda request: httpx.Response(200, text="pong"))
    client.ping()
    assert api.last.headers["user-agent"].startswith(
        f"lettermint-python/{lettermint.__version__} python/"
    )
    assert api.last.headers["accept"] == "application/json"
