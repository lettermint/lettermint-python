"""The two I/O shells: :class:`Transport` (threads) and :class:`AsyncTransport` (AnyIO).

Both send a prepared :class:`~lettermint._core.Call` and decode the answer
with the shared core. They never follow redirects and never retry. The
timeout covers the whole exchange, including the body.

Exceptions of the HTTP library are translated into SDK exceptions *outside*
the ``except`` block, so the SDK exception has no ``__context__`` or
``__cause__`` that holds the request and its headers.
"""

from __future__ import annotations

import contextvars
import threading
from typing import Any

import anyio
import httpx

from ._core import Call, Config, decode, prepare, scrub
from .exceptions import (
    APIConnectionError,
    APITimeoutError,
    LettermintConfigError,
    LettermintError,
    RedirectError,
)

__all__ = ["AsyncTransport", "Transport"]

_Outcome = tuple[int, str, dict[str, str], bytes]


def _translate(error: BaseException, call: Call, config: Config) -> LettermintError | None:
    """The SDK exception for an HTTP library exception, or ``None`` for anything else."""
    if isinstance(error, httpx.TimeoutException):
        return APITimeoutError(call.timeout)
    if isinstance(error, (httpx.HTTPError, httpx.InvalidURL)):
        detail = scrub(str(error), config)
        return APIConnectionError(
            f"{call.label}: could not reach the Lettermint API ({type(error).__name__}"
            + (f": {detail})" if detail else ")")
        )
    if isinstance(error, RuntimeError) and "closed" in str(error):
        return LettermintConfigError(f"{call.label}: the HTTP client is closed.")
    return None


def _headers(response: httpx.Response) -> dict[str, str]:
    return {key.lower(): value for key, value in response.headers.items()}


class _Base:
    def __init__(self, config: Config, owns_client: bool) -> None:
        self.config = config
        self._owns_client = owns_client
        self._closed = False

    def prepare(self, key: str, **arguments: Any) -> Call:
        call = prepare(self.config, key, **arguments)
        if self._closed:
            raise LettermintConfigError(f"{call.label}: the client is closed.")
        return call

    def _request(self, client: httpx.Client | httpx.AsyncClient, call: Call) -> httpx.Request:
        # The only place where the credential leaves its Secret; the header dict
        # does not outlive this frame.
        return client.build_request(
            call.method,
            call.url,
            headers=call.request_headers(),
            content=call.content,
            timeout=httpx.Timeout(call.timeout),
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __reduce__(self) -> Any:
        raise TypeError("Lettermint transports cannot be pickled")


class Transport(_Base):
    """Sends requests with an ``httpx.Client``.

    The exchange runs on a worker thread so that the timeout covers the whole
    request, including a body that arrives slowly: the caller stops waiting
    at the deadline and the worker stops reading. ``httpx``'s own per-phase
    timeouts, set to the same value, bound the abandoned worker.
    """

    def __init__(self, config: Config, client: httpx.Client, owns_client: bool) -> None:
        super().__init__(config, owns_client)
        self._client = client

    def request(self, key: str, **arguments: Any) -> Any:
        call = self.prepare(key, **arguments)
        status, reason, headers, body = self._exchange(call)
        return decode(call, status, reason, headers, body)

    def _exchange(self, call: Call) -> _Outcome:
        request = self._request(self._client, call)
        client = self._client
        box: list[_Outcome | BaseException] = []
        done = threading.Event()
        abandoned = threading.Event()

        def work() -> None:
            try:
                response = client.send(request, stream=True, follow_redirects=False)
                try:
                    chunks: list[bytes] = []
                    if not 300 <= response.status_code < 400:
                        for chunk in response.iter_bytes():
                            if abandoned.is_set():
                                return
                            chunks.append(chunk)
                    box.append(
                        (
                            response.status_code,
                            response.reason_phrase,
                            _headers(response),
                            b"".join(chunks),
                        )
                    )
                finally:
                    response.close()
            except BaseException as error:  # handed to the caller's thread
                box.append(error)
            finally:
                done.set()

        worker = threading.Thread(
            target=contextvars.copy_context().run,
            args=(work,),
            name="lettermint-request",
            daemon=True,
        )
        worker.start()
        if not done.wait(call.timeout) or not box:
            abandoned.set()
            raise APITimeoutError(call.timeout)
        outcome = box[0]
        if isinstance(outcome, BaseException):
            translated = _translate(outcome, call, self.config)
            if translated is None:
                raise outcome
            raise translated
        return _check_redirect(outcome)

    def close(self) -> None:
        self._closed = True
        if self._owns_client:
            self._client.close()


class AsyncTransport(_Base):
    """Sends requests with an ``httpx.AsyncClient``, under an AnyIO deadline.

    Works with asyncio and trio. Cancelling the calling task cancels the
    request; the SDK does not catch the cancellation.
    """

    def __init__(self, config: Config, client: httpx.AsyncClient, owns_client: bool) -> None:
        super().__init__(config, owns_client)
        self._client = client

    async def request(self, key: str, **arguments: Any) -> Any:
        call = self.prepare(key, **arguments)
        status, reason, headers, body = await self._exchange(call)
        return decode(call, status, reason, headers, body)

    async def _exchange(self, call: Call) -> _Outcome:
        request = self._request(self._client, call)
        failure: LettermintError | None = None
        outcome: _Outcome | None = None
        try:
            with anyio.fail_after(call.timeout):
                response = await self._client.send(request, stream=True, follow_redirects=False)
                try:
                    body = b""
                    if not 300 <= response.status_code < 400:
                        body = await response.aread()
                    outcome = (
                        response.status_code,
                        response.reason_phrase,
                        _headers(response),
                        body,
                    )
                finally:
                    await response.aclose()
        except TimeoutError:
            failure = APITimeoutError(call.timeout)
        except Exception as error:
            failure = _translate(error, call, self.config)
            if failure is None:
                raise
        if failure is not None:
            raise failure
        assert outcome is not None
        return _check_redirect(outcome)

    async def close(self) -> None:
        self._closed = True
        if self._owns_client:
            await self._client.aclose()


def _check_redirect(outcome: _Outcome) -> _Outcome:
    if 300 <= outcome[0] < 400:
        raise RedirectError(outcome[0])
    return outcome
