"""Webhook verification."""

from __future__ import annotations

import email.message
import hashlib
import hmac
import json
import pickle
import time
from typing import Any

import httpx
import pytest

from lettermint import LettermintConfigError, Webhook, WebhookVerificationError

SECRET = "whsec_test0123456789abcdefABCDEF0123"
BODY = json.dumps(
    {
        "id": "d1",
        "event": "message.delivered",
        "timestamp": "2026-10-03T12:00:00Z",
        "data": {"message_id": "m1", "subject": "Grüße"},
    },
    ensure_ascii=False,
    separators=(",", ":"),
).encode("utf-8")


def sign(body: bytes, timestamp: int, secret: str = SECRET) -> str:
    return hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()


def headers(timestamp: int, *signatures: str, delivery: str | None = None) -> dict[str, str]:
    value = ",".join([f"t={timestamp}"] + [f"v1={s}" for s in signatures])
    return {
        "X-Lettermint-Signature": value,
        "X-Lettermint-Delivery": delivery if delivery is not None else str(timestamp),
    }


@pytest.fixture
def now() -> int:
    return int(time.time())


def reason_of(webhook: Webhook, body: Any, request_headers: Any) -> str:
    with pytest.raises(WebhookVerificationError) as caught:
        webhook.verify(body, request_headers)
    assert SECRET not in str(caught.value) and SECRET not in repr(caught.value)
    return caught.value.reason


def test_a_genuine_delivery_verifies(now: int) -> None:
    payload = Webhook(SECRET).verify(BODY, headers(now, sign(BODY, now)))
    assert payload["event"] == "message.delivered"
    assert payload["data"]["subject"] == "Grüße"
    assert payload["id"] == "d1"


def test_str_and_bytes_bodies(now: int) -> None:
    webhook = Webhook(SECRET)
    signature = sign(BODY, now)
    assert webhook.verify(BODY.decode("utf-8"), headers(now, signature))["id"] == "d1"
    assert webhook.verify(bytearray(BODY), headers(now, signature))["id"] == "d1"
    assert webhook.verify(memoryview(BODY), headers(now, signature))["id"] == "d1"


def test_any_v1_signature_may_match(now: int) -> None:
    webhook = Webhook(SECRET)
    good, bad = sign(BODY, now), "0" * 64
    assert webhook.verify(BODY, headers(now, bad, good))
    assert webhook.verify(BODY, headers(now, good, bad))
    assert reason_of(webhook, BODY, headers(now, bad, "1" * 64)) == "signature_mismatch"
    assert webhook.verify(
        BODY,
        {"x-lettermint-signature": f"t={now},v0=abc,v1={good}", "x-lettermint-delivery": str(now)},
    )


@pytest.mark.parametrize(
    ("make_headers", "reason"),
    [
        (lambda now, sig: {"X-Lettermint-Delivery": str(now)}, "signature_header_missing"),
        (
            lambda now, sig: {"X-Lettermint-Signature": f"t={now},v1={sig}"},
            "delivery_header_missing",
        ),
        (lambda now, sig: headers(now, sig, delivery=str(now + 1)), "delivery_timestamp_mismatch"),
        (lambda now, sig: headers(now, sig, delivery="abc"), "delivery_timestamp_mismatch"),
        (
            lambda now, sig: {
                **headers(now, sig),
                "X-Lettermint-Signature": f"t={now},t={now},v1={sig}",
            },
            "signature_header_malformed",
        ),
        (
            lambda now, sig: {**headers(now, sig), "X-Lettermint-Signature": f"v1={sig}"},
            "signature_header_malformed",
        ),
        (
            lambda now, sig: {**headers(now, sig), "X-Lettermint-Signature": f"t={now}"},
            "signature_header_malformed",
        ),
        (
            lambda now, sig: {**headers(now, sig), "X-Lettermint-Signature": f"t=abc,v1={sig}"},
            "signature_header_malformed",
        ),
        (
            lambda now, sig: {
                **headers(now, sig),
                "X-Lettermint-Signature": f"t={now},v1={sig[:-1]}é",
            },
            "signature_header_malformed",
        ),
        (
            lambda now, sig: {**headers(now, sig), "X-Lettermint-Signature": f"t=１２３,v1={sig}"},
            "signature_header_malformed",
        ),
        (
            lambda now, sig: {
                **headers(now, sig),
                "X-Lettermint-Signature": "t=" + "9" * 5000 + f",v1={sig}",
            },
            "signature_header_malformed",
        ),
        (
            lambda now, sig: {**headers(now, sig), "X-Lettermint-Signature": "   "},
            "signature_header_missing",
        ),
        (
            lambda now, sig: [
                ("X-Lettermint-Signature", f"t={now},v1={sig}"),
                ("x-lettermint-signature", f"t={now},v1={sig}"),
                ("X-Lettermint-Delivery", str(now)),
            ],
            "signature_header_malformed",
        ),
        (
            lambda now, sig: [
                ("X-Lettermint-Signature", f"t={now},v1={sig}"),
                ("X-Lettermint-Delivery", str(now)),
                ("X-Lettermint-Delivery", str(now)),
            ],
            "delivery_timestamp_mismatch",
        ),
        (
            lambda now, sig: {"X-Lettermint-Signature": 42, "X-Lettermint-Delivery": str(now)},
            "signature_header_malformed",
        ),
    ],
)
def test_invalid_headers(now: int, make_headers: Any, reason: str) -> None:
    assert reason_of(Webhook(SECRET), BODY, make_headers(now, sign(BODY, now))) == reason


def test_tolerance_in_both_directions(now: int) -> None:
    webhook = Webhook(SECRET, tolerance=300)
    for offset in (-300, 300, 0):
        t = now + offset
        assert webhook.verify(BODY, headers(t, sign(BODY, t)))
    for offset in (-301, 301):
        t = now + offset
        assert reason_of(webhook, BODY, headers(t, sign(BODY, t))) == "timestamp_out_of_tolerance"
    strict = Webhook(SECRET, tolerance=0)
    assert (
        reason_of(strict, BODY, headers(now - 2, sign(BODY, now - 2)))
        == "timestamp_out_of_tolerance"
    )


def test_the_body_is_signed_as_raw_bytes(now: int) -> None:
    webhook = Webhook(SECRET)
    signature = sign(BODY, now)
    reserialized = json.dumps(json.loads(BODY)).encode()
    assert reason_of(webhook, reserialized, headers(now, signature)) == "signature_mismatch"
    assert reason_of(webhook, BODY + b" ", headers(now, signature)) == "signature_mismatch"
    assert reason_of(webhook, json.loads(BODY), headers(now, signature)) == "body_invalid"
    assert reason_of(webhook, b"", headers(now, signature)) == "body_invalid"


def test_the_secret_is_used_as_given(now: int) -> None:
    stripped = SECRET.removeprefix("whsec_")
    assert reason_of(Webhook(stripped), BODY, headers(now, sign(BODY, now))) == "signature_mismatch"
    assert (
        reason_of(Webhook(SECRET + "x"), BODY, headers(now, sign(BODY, now)))
        == "signature_mismatch"
    )


def test_signed_payloads_must_be_json_objects(now: int) -> None:
    for body in (b"not json", b"[1, 2]", b"\xff\xfe"):
        assert reason_of(Webhook(SECRET), body, headers(now, sign(body, now))) == "payload_invalid"


def test_header_containers(now: int) -> None:
    webhook = Webhook(SECRET)
    signature = sign(BODY, now)
    plain = headers(now, signature)
    message = email.message.Message()
    for key, value in plain.items():
        message[key] = value
    containers: list[Any] = [
        {key.lower(): value for key, value in plain.items()},
        {key.upper(): value for key, value in plain.items()},
        {key: [value] for key, value in plain.items()},
        list(plain.items()),
        [
            (key.lower().encode(), value.encode()) for key, value in plain.items()
        ],  # raw ASGI headers
        httpx.Headers(plain),
        message,
    ]
    for container in containers:
        assert webhook.verify(BODY, container)["id"] == "d1", type(container)


def test_misused_headers_argument() -> None:
    with pytest.raises(TypeError, match="verify_signature"):
        Webhook(SECRET).verify(BODY, "t=1,v1=abc")  # type: ignore[arg-type]


def test_verify_signature(now: int) -> None:
    webhook = Webhook(SECRET)
    signature = f"t={now},v1={sign(BODY, now)}"
    assert webhook.verify_signature(BODY, signature)["id"] == "d1"
    assert webhook.verify_signature(BODY, signature, now)["id"] == "d1"
    assert webhook.verify_signature(BODY, signature, f" {now} ")["id"] == "d1"
    with pytest.raises(WebhookVerificationError) as caught:
        webhook.verify_signature(BODY, signature, now + 1)
    assert caught.value.reason == "delivery_timestamp_mismatch"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("",), "signing secret must be a non-empty string"),
        ((None,), "signing secret must be a non-empty string"),
        ((SECRET, -1), "tolerance must be a non-negative whole number"),
        ((SECRET, 1.5), "tolerance must be a non-negative whole number"),
        ((SECRET, True), "tolerance must be a non-negative whole number"),
    ],
)
def test_configuration_errors(args: tuple[Any, ...], message: str) -> None:
    with pytest.raises(LettermintConfigError, match=message):
        Webhook(*args)


def test_the_secret_never_shows(now: int) -> None:
    webhook = Webhook(SECRET, tolerance=60)
    assert repr(webhook) == "Webhook(tolerance=60)" == str(webhook)
    assert webhook.tolerance == 60
    assert SECRET not in repr(webhook._secret)
    with pytest.raises(TypeError):
        pickle.dumps(webhook)
    with pytest.raises(TypeError):
        vars(webhook)
