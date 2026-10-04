"""The I/O-free core shared by the synchronous and asynchronous clients.

Token handling, option checks, request preparation, response decoding and
error mapping live here, once. The transports in ``_transport.py`` only move
bytes.
"""

from __future__ import annotations

import codecs
import contextlib
import json
import math
import platform
import re
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from typing import Any, Literal, NoReturn, TypeAlias
from urllib.parse import quote, urlsplit

from ._generated.operations import OPERATIONS, Operation
from ._query import serialize_query
from ._version import __version__
from .exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    LettermintConfigError,
    LettermintValidationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    UnexpectedResponseError,
    ValidationError,
)

DEFAULT_BASE_URL = "https://api.lettermint.co/v1"
DEFAULT_TIMEOUT = 30.0
REDACTED = "[redacted]"
USER_AGENT = f"lettermint-python/{__version__} python/{platform.python_version()}"

#: Team API tokens: ``ApiToken::TEAM_PREFIX`` in the Lettermint backend.
_TEAM_TOKEN = re.compile(r"lm_team_[0-9A-Za-z]+")
#: Project sending tokens (32 or 22 random characters): ``ApiToken::PROJECT_PREFIX``.
_SENDING_TOKEN = re.compile(r"lm_[0-9A-Za-z]+")
#: Characters allowed in a token, so that it is a valid HTTP header value.
_HEADER_SAFE = re.compile(r"[\x21-\x7e]+")
_HEADER_VALUE = re.compile(r"[^\r\n\0]+")
_PATH_PARAM = re.compile(r"\{(\w+)\}")
_CHARSET = re.compile(r"charset\s*=\s*\"?([\w.:-]+)", re.IGNORECASE)

TokenKind: TypeAlias = Literal["sending", "team"]
AuthChoice: TypeAlias = Literal["sending", "team", "either"]


class Secret:
    """A credential that never shows up in ``repr()``, ``str()``, ``vars()`` or pickles."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    def reveal(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return REDACTED

    __str__ = __repr__

    def __format__(self, spec: str) -> str:
        return REDACTED

    def __reduce__(self) -> NoReturn:
        raise TypeError("Lettermint credentials cannot be pickled")


def detect_token_kind(token: object) -> TokenKind:
    """Classifies a token passed as ``Lettermint(token)``.

    The team pattern is checked first, because every team token also starts
    with ``lm_``. The error message never contains the token.
    """
    if isinstance(token, str):
        if _TEAM_TOKEN.fullmatch(token):
            return "team"
        if _SENDING_TOKEN.fullmatch(token):
            return "sending"
    raise LettermintConfigError(
        "Unrecognised token format; pass sending_token=... or team_token=... instead."
    )


def check_token(option: str, token: object) -> Secret | None:
    if token is None:
        return None
    if not isinstance(token, str) or not token:
        raise LettermintConfigError(f"{option} must be a non-empty string.")
    if not _HEADER_SAFE.fullmatch(token):
        raise LettermintConfigError(
            f"{option} contains whitespace or characters that are not allowed in an HTTP header."
        )
    return Secret(token)


def check_timeout(value: object, option: str = "timeout") -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise LettermintConfigError(f"{option} must be a positive number of seconds.")
    return float(value)


def check_base_url(value: object) -> str:
    if not isinstance(value, str):
        raise LettermintConfigError("base_url must be a string.")
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError:
        raise LettermintConfigError("base_url must be an absolute http(s) URL.") from None
    if url.scheme not in ("http", "https") or not url.hostname:
        raise LettermintConfigError("base_url must be an absolute http(s) URL.")
    if url.username is not None or url.password is not None or url.query or url.fragment:
        raise LettermintConfigError(
            "base_url must not contain credentials, a query string or a fragment."
        )
    del port
    return value.rstrip("/")


@dataclass(frozen=True)
class Config:
    """A client's settings. The tokens are :class:`Secret`\\ s, so ``repr()`` is safe."""

    sending_token: Secret | None
    team_token: Secret | None
    base_url: str
    timeout: float


def build_config(
    token: object,
    sending_token: object,
    team_token: object,
    base_url: object,
    timeout: object,
) -> Config:
    if token is not None:
        if sending_token is not None or team_token is not None:
            raise LettermintConfigError(
                "Pass a token string or sending_token/team_token, not both."
            )
        if detect_token_kind(token) == "team":
            team_token = token
        else:
            sending_token = token
    sending = check_token("sending_token", sending_token)
    team = check_token("team_token", team_token)
    if sending is None and team is None:
        raise LettermintConfigError("Pass sending_token, team_token or both.")
    return Config(sending, team, check_base_url(base_url), check_timeout(timeout))


def describe_client(name: str, config: Config) -> str:
    return (
        f"{name}(base_url={config.base_url!r}, timeout={config.timeout!r}, "
        f"sending_token={REDACTED if config.sending_token else None}, "
        f"team_token={REDACTED if config.team_token else None})"
    )


def auth_header(config: Config, label: str, auth: AuthChoice) -> tuple[str, Secret]:
    """The header that carries the token for ``auth``. Never falls back to the other token."""
    if auth == "team" or (auth == "either" and config.team_token is not None):
        if config.team_token is None:
            raise LettermintConfigError(
                f"{label} needs team_token; pass Lettermint(team_token=...)."
            )
        return "Authorization", config.team_token
    if config.sending_token is None:
        raise LettermintConfigError(
            f"{label} needs sending_token; pass Lettermint(sending_token=...)."
        )
    return "x-lettermint-token", config.sending_token


def encode_path_param(label: str, name: str, value: object) -> str:
    if not isinstance(value, str) or value in ("", ".", ".."):
        raise LettermintConfigError(
            f'{label}: {name} must be a non-empty string other than "." and "..".'
        )
    return quote(value, safe="")


def check_idempotency_key(value: object) -> str:
    if not isinstance(value, str) or not _HEADER_VALUE.fullmatch(value):
        raise LettermintValidationError(
            "idempotency_key must be a non-empty string without line breaks.",
            field="idempotency_key",
        )
    return value


@dataclass(frozen=True)
class Call:
    """One prepared request. Holds the token as a :class:`Secret`, so ``repr()`` is safe."""

    label: str
    method: str
    url: str
    headers: tuple[tuple[str, str], ...]
    content: bytes | None
    auth: tuple[str, Secret] = field(repr=False)
    timeout: float
    response_type: str

    def request_headers(self) -> dict[str, str]:
        """The headers including the credential. Use them only to send the request."""
        name, secret = self.auth
        value = secret.reveal()
        return {**dict(self.headers), name: f"Bearer {value}" if name == "Authorization" else value}


_NO_BODY: Any = object()


def _encode_json(body: Any) -> tuple[bytes | None, str]:
    try:
        text = json.dumps(body, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError) as error:
        return None, str(error)
    return text.encode("utf-8"), ""


def prepare(
    config: Config,
    key: str,
    *,
    label: str,
    path: Mapping[str, str] | None = None,
    query: Mapping[str, Any] | None = None,
    body: Any = _NO_BODY,
    idempotency_key: str | None = None,
    auth: AuthChoice | None = None,
    timeout: float | None = None,
) -> Call:
    """Checks a call and turns it into a :class:`Call`. Raises before any request."""
    operation: Operation = OPERATIONS[key]
    credential = auth_header(config, label, auth or operation.auth)
    params = path or {}
    url_path = _PATH_PARAM.sub(
        lambda match: encode_path_param(label, match.group(1), params.get(match.group(1))),
        operation.path,
    )
    seconds = config.timeout if timeout is None else check_timeout(timeout)
    headers: list[tuple[str, str]] = [("Accept", "application/json"), ("User-Agent", USER_AGENT)]
    if idempotency_key is not None:
        headers.append(("Idempotency-Key", check_idempotency_key(idempotency_key)))
    content: bytes | None = None
    if body is not _NO_BODY:
        content, problem = _encode_json(body)
        if content is None:
            raise LettermintValidationError(
                f"{label}: the request body cannot be encoded as JSON ({problem}).", field="body"
            )
        headers.append(("Content-Type", "application/json"))
    if query is not None and not isinstance(query, Mapping):
        raise LettermintConfigError(f"{label}: the query must be a mapping.")
    query_string = serialize_query(query)
    url = config.base_url + url_path + (f"?{query_string}" if query_string else "")
    return Call(
        label=label,
        method=operation.method,
        url=url,
        headers=tuple(headers),
        content=content,
        auth=credential,
        timeout=seconds,
        response_type=operation.response.type,
    )


def scrub(text: str, config: Config) -> str:
    """Removes both tokens from a message, in case a library echoes a header."""
    for secret in (config.sending_token, config.team_token):
        if secret is not None:
            text = text.replace(secret.reveal(), REDACTED)
    return text


def _text(headers: Mapping[str, str], body: bytes) -> str:
    match = _CHARSET.search(headers.get("content-type", ""))
    encoding = "utf-8"
    if match:
        with contextlib.suppress(LookupError):
            encoding = codecs.lookup(match.group(1)).name
    return body.decode(encoding, errors="replace")


def parse_retry_after(value: str | None) -> int | None:
    if not value:
        return None
    value = value.strip()
    if value.isascii() and value.isdigit():
        return int(value)
    try:
        moment = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    if moment.tzinfo is None:
        return None
    return max(0, math.ceil(moment.timestamp() - time.time()))


def _api_error(status: int, reason: str, headers: Mapping[str, str], body: Any) -> APIError:
    message = ""
    code: str | None = None
    details: Any = None
    errors: dict[str, list[str]] | None = None
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            if isinstance(error.get("code"), str):
                code = error["code"]
            if isinstance(error.get("message"), str):
                message = error["message"]
            details = error.get("details")
        elif isinstance(error, str):
            code = error
        if not message and isinstance(body.get("message"), str):
            message = body["message"]
        if isinstance(body.get("errors"), dict):
            errors = body["errors"]
    message = message or reason or f"HTTP {status}"
    common: dict[str, Any] = {"status": status, "code": code, "details": details, "body": body}
    if status == 401:
        return AuthenticationError(message, **common)
    if status == 403:
        return PermissionDeniedError(message, **common)
    if status == 404:
        return NotFoundError(message, **common)
    if status == 409:
        return ConflictError(message, **common)
    if status == 422:
        return ValidationError(message, errors=errors, **common)
    if status == 429:
        return RateLimitError(
            message, retry_after=parse_retry_after(headers.get("retry-after")), **common
        )
    if status >= 500:
        return ServerError(message, **common)
    return APIError(message, **common)


_INVALID: Any = object()


def _parse_json(text: str) -> Any:
    """The decoded JSON, or ``_INVALID``. Lets callers raise outside an ``except`` block."""
    try:
        return json.loads(text)
    except ValueError:
        return _INVALID


def decode(call: Call, status: int, reason: str, headers: Mapping[str, str], body: bytes) -> Any:
    """The decoded success body, or the matching exception. ``headers`` keys are lower case."""
    if 200 <= status < 300:
        if call.response_type == "empty" or status in (204, 205):
            return None
        text = _text(headers, body)
        if call.response_type == "text":
            return text
        if not text.strip():
            raise UnexpectedResponseError(
                f"The Lettermint API answered with HTTP {status} and an empty body where JSON was expected.",
                status=status,
                body=text,
            )
        value = _parse_json(text)
        if value is _INVALID:
            raise UnexpectedResponseError(
                f"The Lettermint API answered with HTTP {status} and a body that is not valid JSON.",
                status=status,
                body=text,
            )
        return value
    text = _text(headers, body)
    if status < 400:
        raise UnexpectedResponseError(
            f"The Lettermint API answered with an unexpected HTTP status {status}.",
            status=status,
            body=text,
        )
    parsed: Any = None
    if text.strip():
        parsed = _parse_json(text)
        if parsed is _INVALID:
            content_type = headers.get("content-type", "").split(";")[0].strip()
            raise UnexpectedResponseError(
                f"The Lettermint API answered with HTTP {status} and a body that is not JSON"
                + (f" ({content_type})." if content_type else "."),
                status=status,
                body=text,
            )
    raise _api_error(status, reason, headers, parsed)
