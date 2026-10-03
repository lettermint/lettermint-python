"""Query string serialization in the API's bracket syntax.

The output is byte-for-byte what the Node.js SDK sends: nested mappings use
brackets (``page[size]=30``), lists of scalars are comma-separated, lists of
mappings are indexed (``filter[tags][0][name]=a``), booleans are ``1``/``0``
and ``None`` values are left out. Encoding follows the WHATWG
``application/x-www-form-urlencoded`` serializer (``URLSearchParams``).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any
from urllib.parse import quote_plus

_GROUP = re.compile(r"^([^\[\]]+)\[([^\[\]]+)\]$")


def _encode(text: str) -> str:
    # URLSearchParams keeps ASCII alphanumerics and *-._, turns spaces into +
    # and percent-encodes everything else (UTF-8), including ~.
    return quote_plus(text, safe="*").replace("~", "%7E")


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, bytes, int, float, bool, date, datetime))


def _scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e21:
        return str(int(value))  # JavaScript's String(30.0) is "30"
    return str(value)


def _append(pairs: list[tuple[str, str]], key: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, Mapping):
        for name, item in value.items():
            _append(pairs, f"{key}[{name}]", item)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if all(_is_scalar(item) for item in value):
            items = [_scalar(item) for item in value if item is not None]
            if items:
                pairs.append((key, ",".join(items)))
            return
        for index, item in enumerate(value):
            _append(pairs, f"{key}[{index}]", item)
        return
    pairs.append((key, _scalar(value)))


def serialize_query(query: Mapping[str, Any] | None) -> str:
    """``{"page": {"size": 10}, "sort": ["-created_at"]}`` -> ``page%5Bsize%5D=10&sort=-created_at``."""
    if not query:
        return ""
    pairs: list[tuple[str, str]] = []
    for key, value in query.items():
        _append(pairs, str(key), value)
    return "&".join(f"{_encode(key)}={_encode(value)}" for key, value in pairs)


def with_query_param(query: Mapping[str, Any] | None, name: str, value: str) -> dict[str, Any]:
    """A copy of ``query`` with the wire parameter ``name`` (``cursor`` or ``page[cursor]``) set."""
    base = dict(query or {})
    match = _GROUP.match(name)
    if not match:
        base[name] = value
        return base
    group, key = match.groups()
    base.pop(name, None)
    current = base.get(group)
    base[group] = {**(dict(current) if isinstance(current, Mapping) else {}), key: value}
    return base
