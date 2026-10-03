"""Sending: stateless sends, the immutable builder, tags, attachments and batches."""

from __future__ import annotations

import base64
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

import anyio
import httpx
import pytest

from lettermint import (
    AsyncEmailBuilder,
    AsyncLettermint,
    EmailBuilder,
    EmailMessage,
    Lettermint,
    LettermintValidationError,
)

from .conftest import MESSAGE, MockAPI

PENDING = {"message_id": "m1", "status": "pending"}


@pytest.fixture(autouse=True)
def accept_sends(api: MockAPI) -> None:
    api.json(202, PENDING)


def test_send_posts_the_message_as_given(api: MockAPI, client: Lettermint) -> None:
    message: EmailMessage = {
        "from": "Acme <hello@acme.test>",
        "to": ["jane@example.test"],
        "reply_to": ["support@acme.test"],
        "subject": "Your order",
        "html": "<p>Shipped</p>",
        "metadata": {"order_id": "1234"},
        "tag": "orders",
        "tags": [{"name": "campaign", "value": "orders"}],
        "settings": {"track_opens": False},
        "sandbox_result": "hard_bounced",
    }
    assert client.emails.send(message) == PENDING
    assert api.body() == message


def test_send_does_not_change_the_message(api: MockAPI, client: Lettermint) -> None:
    message: EmailMessage = {
        **MESSAGE,
        "attachments": [{"filename": "a.bin", "content": b"\x00\xff"}],
    }
    client.emails.send(message)
    assert message["attachments"][0]["content"] == b"\x00\xff"
    assert api.body()["attachments"] == [{"filename": "a.bin", "content": "AP8="}]


def test_the_builder_is_immutable(api: MockAPI, client: Lettermint) -> None:
    base = client.emails.compose().from_("Acme <hello@acme.test>").subject("Welcome")
    jane = base.to("jane@example.test").html("<p>Hi Jane</p>")
    john = base.to("john@example.test").cc("boss@example.test").html("<p>Hi John</p>")
    assert base.build() == {"from": "Acme <hello@acme.test>", "to": [], "subject": "Welcome"}
    jane.send()
    john.send(idempotency_key="welcome-john")
    jane.send()
    assert [api.body(i)["to"] for i in range(3)] == [
        ["jane@example.test"],
        ["john@example.test"],
        ["jane@example.test"],
    ]
    assert "cc" not in api.body(0) and "cc" not in api.body(2)
    assert "idempotency-key" not in api.requests[0].headers
    assert api.requests[1].headers["idempotency-key"] == "welcome-john"
    assert "idempotency-key" not in api.requests[2].headers
    with pytest.raises(AttributeError, match="immutable"):
        base._message = {}


def test_every_setter(api: MockAPI, client: Lettermint) -> None:
    when = datetime(2026, 10, 20, 9, 0, tzinfo=timezone(timedelta(hours=2)))
    builder = (
        client.emails.compose()
        .from_("hello@acme.test")
        .to("a@example.test", "b@example.test")
        .cc("c@example.test")
        .bcc("d@example.test")
        .reply_to("e@example.test")
        .subject("All fields")
        .html("<p>x</p>")
        .text("x")
        .headers({"X-Custom": "1"})
        .metadata({"k": "v"})
        .tag("legacy")
        .tags([{"name": "campaign", "value": "x"}])
        .route("broadcast")
        .scheduled_at(when)
        .settings({"track_opens": True, "track_clicks": False, "tls": "enforced"})
        .sandbox_result("delivered")
        .attach("invoice.pdf", b"%PDF-1.7", content_type="application/pdf")
        .attach("logo.png", "aGk=", content_id="logo")
    )
    builder.send()
    assert api.body() == {
        "from": "hello@acme.test",
        "to": ["a@example.test", "b@example.test"],
        "subject": "All fields",
        "cc": ["c@example.test"],
        "bcc": ["d@example.test"],
        "reply_to": ["e@example.test"],
        "html": "<p>x</p>",
        "text": "x",
        "headers": {"X-Custom": "1"},
        "metadata": {"k": "v"},
        "tag": "legacy",
        "tags": [{"name": "campaign", "value": "x"}],
        "route": "broadcast",
        "scheduled_at": "2026-10-20T09:00:00+02:00",
        "settings": {"track_opens": True, "track_clicks": False, "tls": "enforced"},
        "sandbox_result": "delivered",
        "attachments": [
            {
                "filename": "invoice.pdf",
                "content": base64.b64encode(b"%PDF-1.7").decode(),
                "content_type": "application/pdf",
            },
            {"filename": "logo.png", "content": "aGk=", "content_id": "logo"},
        ],
    }
    removed = builder.html(None).text(None).tag(None).scheduled_at(None).build()
    assert not {"html", "text", "tag", "scheduled_at"} & set(removed)
    assert builder.scheduled_at("tomorrow 9am").build()["scheduled_at"] == "tomorrow 9am"


def test_naive_datetimes_are_rejected(client: Lettermint) -> None:
    with pytest.raises(LettermintValidationError, match="timezone-aware") as caught:
        client.emails.compose().scheduled_at(datetime(2026, 10, 20, 9, 0))
    assert caught.value.field == "scheduled_at"


def test_compose_from_a_message_copies_it(client: Lettermint) -> None:
    message: EmailMessage = {**MESSAGE, "to": ["jane@example.test"]}
    builder = client.emails.compose(message)
    message["to"].append("mallory@example.test")
    assert builder.build()["to"] == ["jane@example.test"]


def test_build_returns_a_copy(client: Lettermint) -> None:
    builder = client.emails.compose().to("jane@example.test")
    built = builder.build()
    built["to"].append("mallory@example.test")
    assert builder.build()["to"] == ["jane@example.test"]


def test_repr_summarizes_attachments(client: Lettermint) -> None:
    builder = client.emails.compose().attach("a.bin", b"\x00" * 1000).attach("b.txt", "aGk=")
    text = repr(builder)
    assert text.startswith("EmailBuilder({")
    assert "<1000 bytes>" in text and "<4 base64 characters>" in text


@pytest.mark.parametrize(
    ("tags", "legacy", "message"),
    [
        ([{"name": "not valid!", "value": "x"}], None, r"names must match"),
        ([{"name": "a" * 33, "value": "x"}], None, r"names must match"),
        ([{"name": "ok", "value": "v" * 65}], None, r"values must match"),
        ([{"name": "ok", "value": ""}], None, r"values must match"),
        ([{"name": "__lettermint_x", "value": "x"}], None, r"must not start with __lettermint"),
        ([{"name": "__LETTERMINT", "value": "x"}], None, r"must not start with __lettermint"),
        ([{"name": "a", "value": "1"}, {"name": "a", "value": "2"}], None, r"must be unique"),
        (
            [{"name": f"t{i}", "value": "x"} for i in range(21)],
            None,
            r"No more than 20 message tags",
        ),
        (
            [{"name": f"t{i}", "value": "x"} for i in range(20)],
            "legacy",
            r"A legacy tag and no more than 19",
        ),
        ([{"name": "a"}], None, r"mappings with string values"),
        ("campaign", None, r"must be a list"),
    ],
)
def test_tag_validation(
    api: MockAPI, client: Lettermint, tags: Any, legacy: str | None, message: str
) -> None:
    base = client.emails.compose().from_("a@acme.test").to("b@example.test").subject("s")
    if legacy:
        base = base.tag(legacy)
    snapshot = base.build()
    with pytest.raises(LettermintValidationError, match=message) as caught:
        base.tags(tags)
    assert caught.value.field == "tags"
    assert base.build() == snapshot  # a rejected setter leaves the builder unchanged
    with pytest.raises(LettermintValidationError, match=message):
        client.emails.send({**MESSAGE, "tags": tags, **({"tag": legacy} if legacy else {})})  # type: ignore[typeddict-item]
    assert api.requests == []


def test_twenty_tags_and_case_sensitive_names_are_fine(client: Lettermint) -> None:
    tags = [{"name": f"t{i}", "value": "x"} for i in range(19)] + [{"name": "T0", "value": "y"}]
    client.emails.compose().tags(tags)  # type: ignore[arg-type]


def test_attachment_validation(api: MockAPI, client: Lettermint) -> None:
    with pytest.raises(LettermintValidationError, match="needs a filename") as caught:
        client.emails.send({**MESSAGE, "attachments": [{"filename": "", "content": "aGk="}]})
    assert caught.value.field == "attachments[0]"
    with pytest.raises(LettermintValidationError, match="base64 string or bytes"):
        client.emails.compose().attach("a.txt", 42)  # type: ignore[arg-type]
    with pytest.raises(LettermintValidationError, match="must be a mapping"):
        client.emails.send(["not", "a", "message"])  # type: ignore[arg-type]
    assert api.requests == []


def test_send_batch_mixes_messages_and_builders(api: MockAPI, client: Lettermint) -> None:
    api.json(202, [PENDING, PENDING])
    builder = (
        client.emails.compose()
        .from_("a@acme.test")
        .to("b@example.test")
        .subject("B")
        .attach("x.bin", b"\x01")
    )
    result = client.emails.send_batch([MESSAGE, builder], idempotency_key="batch-1")
    assert result == [PENDING, PENDING]
    assert str(api.last.url).endswith("/send/batch")
    assert api.last.headers["idempotency-key"] == "batch-1"
    assert api.body() == [
        MESSAGE,
        {
            "from": "a@acme.test",
            "to": ["b@example.test"],
            "subject": "B",
            "attachments": [{"filename": "x.bin", "content": "AQ=="}],
        },
    ]


def test_send_batch_names_the_bad_message(api: MockAPI, client: Lettermint) -> None:
    with pytest.raises(LettermintValidationError) as caught:
        client.emails.send_batch(
            [MESSAGE, {**MESSAGE, "tags": [{"name": "bad name", "value": "x"}]}]
        )
    assert caught.value.field == "messages[1].tags"
    with pytest.raises(LettermintValidationError, match="takes a list"):
        client.emails.send_batch(MESSAGE)  # type: ignore[arg-type]
    assert api.requests == []


def test_a_failed_send_leaves_nothing_behind(api: MockAPI, client: Lettermint) -> None:
    api.json(500, {"message": "Server Error"})
    full = (
        client.emails.compose()
        .from_("a@acme.test")
        .to("x@example.test")
        .cc("cc@example.test")
        .subject("A")
    )
    with pytest.raises(Exception, match="Server Error"):
        full.send(idempotency_key="key-a")
    api.json(202, PENDING)
    client.emails.compose().from_("c@acme.test").to("c@example.test").subject("C").send()
    assert api.body() == {"from": "c@acme.test", "to": ["c@example.test"], "subject": "C"}
    assert "idempotency-key" not in api.last.headers


def test_threads_share_a_base_builder_safely(api: MockAPI, client: Lettermint) -> None:
    base = client.emails.compose().from_("a@acme.test").subject("Hi")
    barrier = threading.Barrier(8)

    def send(index: int) -> None:
        draft = base.to(f"user{index}@example.test")
        barrier.wait()
        draft.html(f"<p>{index}</p>").send(idempotency_key=f"key-{index}")

    threads = [threading.Thread(target=send, args=(i,)) for i in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    seen = {
        (api.body(i)["to"][0], api.body(i)["html"], request.headers["idempotency-key"])
        for i, request in enumerate(api.requests)
    }
    assert seen == {(f"user{i}@example.test", f"<p>{i}</p>", f"key-{i}") for i in range(8)}


@pytest.mark.anyio
async def test_async_tasks_interleaving_setters_stay_isolated(
    api: MockAPI, aclient: AsyncLettermint
) -> None:
    async def compose_and_send(name: str) -> None:
        builder: AsyncEmailBuilder = aclient.emails.compose()
        for setter, value in (
            ("from_", f"{name}@acme.test"),
            ("to", f"{name}@example.test"),
            ("subject", name),
            ("html", f"<p>{name}</p>"),
        ):
            builder = getattr(builder, setter)(value)
            await anyio.sleep(0)
        await builder.send(idempotency_key=f"key-{name}")

    async with anyio.create_task_group() as group:
        group.start_soon(compose_and_send, "a")
        group.start_soon(compose_and_send, "b")
    bodies = sorted(
        (api.body(i)["subject"], api.body(i)["to"], r.headers["idempotency-key"])
        for i, r in enumerate(api.requests)
    )
    assert bodies == [("a", ["a@example.test"], "key-a"), ("b", ["b@example.test"], "key-b")]


@pytest.mark.anyio
async def test_async_send_batch_and_ping(api: MockAPI, aclient: AsyncLettermint) -> None:
    api.json(202, [PENDING])
    assert await aclient.emails.send_batch([aclient.emails.compose(MESSAGE)]) == [PENDING]
    api.respond(lambda request: httpx.Response(200, text="pong"))
    assert await aclient.emails.ping() == "pong"


def test_builders_compare_by_message(client: Lettermint) -> None:
    a = client.emails.compose().to("x@example.test")
    assert a == client.emails.compose().to("x@example.test")
    assert a != a.to("y@example.test")
    assert isinstance(a, EmailBuilder)
    with pytest.raises(TypeError):
        hash(a)
