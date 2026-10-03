"""Email messages: validation, the wire format and the immutable builder base.

Shared by the synchronous and asynchronous clients. Nothing here performs I/O
or keeps state between emails.
"""

from __future__ import annotations

import base64
import copy
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, NoReturn

from typing_extensions import Buffer, NotRequired, Required, Self, TypedDict

from ._generated.types import (
    MessageTagInput,
    SandboxResult,
    SendMailRequest,
    SendMailRequestSettings,
)
from .exceptions import LettermintValidationError

__all__ = ["BaseEmailBuilder", "EmailAttachment", "EmailMessage"]

_TAG_NAME = re.compile(r"[A-Za-z0-9_-]{1,32}")
_TAG_VALUE = re.compile(r"[A-Za-z0-9_-]{1,64}")
_MAX_TAGS = 20


def as_bytes(value: object) -> bytes | None:
    """A copy of ``value`` as ``bytes`` when it is binary (bytes, bytearray, memoryview, ...)."""
    if isinstance(value, (str, int)) or value is None:
        return None
    if isinstance(value, bytes):
        return value
    try:
        return bytes(memoryview(value))  # type: ignore[arg-type]
    except TypeError:
        return None


class EmailAttachment(TypedDict):
    """An attachment of an :data:`EmailMessage`. ``content`` is base64 text or raw bytes."""

    filename: Required[str]
    #: Base64-encoded text, or raw bytes that the SDK encodes.
    content: Required[str | Buffer]
    #: MIME type, for example ``application/pdf``. Detected by the API when omitted.
    content_type: NotRequired[str]
    #: Content-ID for inline images referenced as ``cid:<content_id>`` in the HTML.
    content_id: NotRequired[str]


#: An email in the API's wire format (``reply_to``, ``scheduled_at``, ...): the
#: generated ``SendMailRequest``, except that attachment content may also be bytes.
EmailMessage = TypedDict(
    "EmailMessage",
    {
        "route": NotRequired[str],
        "from": Required[str],
        "to": Required[list[str]],
        "cc": NotRequired[list[str]],
        "bcc": NotRequired[list[str]],
        "reply_to": NotRequired[list[str]],
        "subject": Required[str],
        "scheduled_at": NotRequired[str],
        "headers": NotRequired[dict[str, str]],
        "metadata": NotRequired[dict[str, str]],
        "tag": NotRequired["str | None"],
        "tags": NotRequired[list[MessageTagInput]],
        "settings": NotRequired[SendMailRequestSettings],
        "html": NotRequired["str | None"],
        "text": NotRequired["str | None"],
        "attachments": NotRequired[list[EmailAttachment]],
        "sandbox_result": NotRequired[SandboxResult],
    },
)


def _fail(field: str, message: str) -> NoReturn:
    raise LettermintValidationError(message, field=field)


def _validate_tags(tags: object, has_legacy_tag: bool, field: str) -> None:
    if tags is None:
        return
    if not isinstance(tags, (list, tuple)):
        _fail(field, "Message tags must be a list of {name, value} mappings.")
    maximum = _MAX_TAGS - 1 if has_legacy_tag else _MAX_TAGS
    if len(tags) > maximum:
        _fail(
            field,
            f"A legacy tag and no more than {maximum} message tags are permitted."
            if has_legacy_tag
            else f"No more than {maximum} message tags are permitted.",
        )
    names: set[str] = set()
    for tag in tags:
        if (
            not isinstance(tag, Mapping)
            or not isinstance(tag.get("name"), str)
            or not isinstance(tag.get("value"), str)
        ):
            _fail(field, "Message tags must be {name, value} mappings with string values.")
        name, value = tag["name"], tag["value"]
        if not _TAG_NAME.fullmatch(name):
            _fail(field, "Message tag names must match ^[A-Za-z0-9_-]{1,32}$.")
        if name.lower().startswith("__lettermint"):
            _fail(field, "Message tag names must not start with __lettermint.")
        if not _TAG_VALUE.fullmatch(value):
            _fail(field, "Message tag values must match ^[A-Za-z0-9_-]{1,64}$.")
        if name in names:
            _fail(field, "Message tag names must be unique (case-sensitive).")
        names.add(name)


def validate_email_message(message: object, prefix: str = "") -> None:
    """Checks what the SDK can check before a request: the shape, tags and attachments."""

    def at(field: str) -> str:
        return f"{prefix}.{field}" if prefix else field

    if not isinstance(message, Mapping):
        _fail(prefix or "message", "An email message must be a mapping.")
    legacy_tag = message.get("tag")
    if legacy_tag is not None and not isinstance(legacy_tag, str):
        _fail(at("tag"), "The legacy tag must be a string.")
    _validate_tags(
        message.get("tags"), isinstance(legacy_tag, str) and legacy_tag != "", at("tags")
    )
    attachments = message.get("attachments")
    if attachments is not None:
        if not isinstance(attachments, (list, tuple)):
            _fail(at("attachments"), "Attachments must be a list.")
        for index, attachment in enumerate(attachments):
            field = f"{at('attachments')}[{index}]"
            if (
                not isinstance(attachment, Mapping)
                or not isinstance(attachment.get("filename"), str)
                or not attachment["filename"]
            ):
                _fail(field, "An attachment needs a filename.")
            content = attachment.get("content")
            if not isinstance(content, str) and as_bytes(content) is None:
                _fail(field, "Attachment content must be a base64 string or bytes.")


def _copy(value: Any) -> Any:
    """Copies plain data (mappings, lists, scalars and bytes)."""
    if isinstance(value, Mapping):
        return {key: _copy(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_copy(item) for item in value]
    binary = as_bytes(value)
    return binary if binary is not None else copy.copy(value)


def to_wire(message: Mapping[str, Any]) -> SendMailRequest:
    """A deep copy of the message in wire format, with bytes attachment content base64-encoded."""
    wire: dict[str, Any] = _copy(message)
    if wire.get("attachments"):
        wire["attachments"] = [
            {
                **attachment,
                "content": base64.b64encode(attachment["content"]).decode("ascii")
                if isinstance(attachment["content"], bytes)
                else attachment["content"],
            }
            for attachment in wire["attachments"]
        ]
    return wire  # type: ignore[return-value]


def _summary(message: Mapping[str, Any]) -> dict[str, Any]:
    """The message for ``repr()``: attachment content is summarized, not printed."""
    view = dict(message)
    if view.get("attachments"):
        view["attachments"] = [
            {
                **attachment,
                "content": f"<{len(attachment['content'])} {'bytes' if isinstance(attachment['content'], bytes) else 'base64 characters'}>",
            }
            for attachment in view["attachments"]
        ]
    return view


class BaseEmailBuilder:
    """The immutable state and setters of :class:`EmailBuilder` and :class:`AsyncEmailBuilder`.

    Every setter returns a new builder and leaves this one unchanged, so a base
    builder can be shared and reused safely, also across threads and tasks.
    ``to``, ``cc``, ``bcc`` and ``reply_to`` replace their list; ``attach``
    appends. A setter that raises leaves the builder unchanged.
    """

    __slots__ = ("_emails", "_message")

    _emails: Any
    _message: dict[str, Any]

    def __init__(self, emails: Any, message: Mapping[str, Any] | None = None) -> None:
        object.__setattr__(self, "_emails", emails)
        object.__setattr__(
            self,
            "_message",
            dict(message) if message is not None else {"from": "", "to": [], "subject": ""},
        )

    def __setattr__(self, name: str, value: Any) -> NoReturn:
        raise AttributeError(f"{type(self).__name__} is immutable; setters return a new builder")

    def __delattr__(self, name: str) -> NoReturn:
        raise AttributeError(f"{type(self).__name__} is immutable; setters return a new builder")

    def __reduce__(self) -> NoReturn:
        raise TypeError(f"{type(self).__name__} cannot be pickled; pickle build() instead")

    def _with(self, **changes: Any) -> Self:
        message = dict(self._message)
        for key, value in changes.items():
            key = key.rstrip("_")
            if value is None:
                message.pop(key, None)
            else:
                message[key] = value
        validate_email_message(message)
        return type(self)(self._emails, message)

    def from_(self, address: str) -> Self:
        """Sender, for example ``Acme <hello@acme.com>``. (``from`` is a Python keyword.)"""
        return self._with(from_=address)

    def to(self, *addresses: str) -> Self:
        """Replaces the recipients."""
        return self._with(to=list(addresses))

    def cc(self, *addresses: str) -> Self:
        """Replaces the CC recipients."""
        return self._with(cc=list(addresses))

    def bcc(self, *addresses: str) -> Self:
        """Replaces the BCC recipients."""
        return self._with(bcc=list(addresses))

    def reply_to(self, *addresses: str) -> Self:
        """Replaces the Reply-To addresses."""
        return self._with(reply_to=list(addresses))

    def subject(self, subject: str) -> Self:
        return self._with(subject=subject)

    def html(self, html: str | None) -> Self:
        """HTML body. ``None`` removes it."""
        return self._with(html=html)

    def text(self, text: str | None) -> Self:
        """Plain-text body. ``None`` removes it."""
        return self._with(text=text)

    def headers(self, headers: Mapping[str, str]) -> Self:
        """Replaces the custom email headers."""
        return self._with(headers=dict(headers))

    def metadata(self, metadata: Mapping[str, str]) -> Self:
        """Replaces the metadata (stored with the email, not added as headers)."""
        return self._with(metadata=dict(metadata))

    def tag(self, tag: str | None) -> Self:
        """The legacy single tag. ``None`` removes it."""
        return self._with(tag=tag)

    def tags(self, tags: Sequence[MessageTagInput]) -> Self:
        """Replaces the name/value tags (up to 20, or 19 with a legacy ``tag``)."""
        if not isinstance(tags, (list, tuple)):
            _fail("tags", "Message tags must be a list of {name, value} mappings.")
        return self._with(tags=[dict(tag) if isinstance(tag, Mapping) else tag for tag in tags])

    def route(self, route: str) -> Self:
        """The route slug to send through."""
        return self._with(route=route)

    def scheduled_at(self, when: str | datetime | None) -> Self:
        """Schedules delivery: ISO 8601 or English text (``tomorrow 9am``), or an aware datetime.

        ``None`` removes it. A naive datetime raises
        :class:`~lettermint.LettermintValidationError`, because its time zone is unknown.
        """
        if isinstance(when, datetime):
            if when.tzinfo is None or when.utcoffset() is None:
                _fail("scheduled_at", "scheduled_at needs a timezone-aware datetime.")
            when = when.isoformat()
        return self._with(scheduled_at=when)

    def settings(self, settings: SendMailRequestSettings) -> Self:
        """Per-email settings that override the route settings."""
        return self._with(settings=dict(settings))

    def sandbox_result(self, result: SandboxResult) -> Self:
        """The result a Sandbox project simulates for every recipient."""
        return self._with(sandbox_result=result)

    def attach(
        self,
        filename: str,
        content: str | Buffer,
        *,
        content_type: str | None = None,
        content_id: str | None = None,
    ) -> Self:
        """Adds an attachment. ``content`` is base64 text or raw bytes (encoded by the SDK)."""
        attachment: dict[str, Any] = {
            "filename": filename,
            "content": content if isinstance(content, str) else (as_bytes(content) or content),
        }
        if content_type is not None:
            attachment["content_type"] = content_type
        if content_id is not None:
            attachment["content_id"] = content_id
        return self._with(attachments=[*self._message.get("attachments", []), attachment])

    def build(self) -> SendMailRequest:
        """A copy of the message in the API's wire format, with attachments base64-encoded."""
        return to_wire(self._message)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({_summary(self._message)!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEmailBuilder):
            return NotImplemented
        return type(self) is type(other) and self._message == other._message

    __hash__ = None  # type: ignore[assignment]


def check_message(message: object, prefix: str = "") -> SendMailRequest:
    """Validates a message (or a builder) and returns its wire format."""
    if isinstance(message, BaseEmailBuilder):
        return message.build()
    validate_email_message(message, prefix)
    return to_wire(message)  # type: ignore[arg-type]


def initial_message(message: object) -> dict[str, Any]:
    validate_email_message(message)
    return _copy(message)  # type: ignore[no-any-return]
