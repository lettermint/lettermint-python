"""Typed reusable message tags."""

import re
from dataclasses import dataclass
from typing import Any

_NAME = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
_VALUE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@dataclass(frozen=True)
class MessageTag:
    """A reusable exact-match message tag."""

    name: str
    value: str

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.name):
            raise ValueError("Message tag names must match ^[A-Za-z0-9_-]{1,32}$")
        if self.name.lower().startswith("__lettermint"):
            raise ValueError("Message tag names must not start with __lettermint")
        if not _VALUE.fullmatch(self.value):
            raise ValueError("Message tag values must match ^[A-Za-z0-9_-]{1,64}$")

    def to_dict(self) -> dict[str, str]:
        """Return the Sending API representation."""
        return {"name": self.name, "value": self.value}


def normalize_message_tags(payload: Any) -> Any:
    """Normalize and validate typed tags in one message or a batch."""
    if isinstance(payload, list):
        return [normalize_message_tags(message) for message in payload]
    if not isinstance(payload, dict) or "tags" not in payload:
        return payload

    result = dict(payload)
    raw_tags = result["tags"]
    if not isinstance(raw_tags, list):
        raise ValueError("Message tags must be a list")
    maximum = 19 if result.get("tag") is not None else 20
    if len(raw_tags) > maximum:
        raise ValueError(f"No more than {maximum} message tags are permitted")
    tags = [tag if isinstance(tag, MessageTag) else MessageTag(**tag) for tag in raw_tags]
    names = [tag.name for tag in tags]
    if len(names) != len(set(names)):
        raise ValueError("Message tag names must be unique and case-sensitive")
    result["tags"] = [tag.to_dict() for tag in tags]
    return result
