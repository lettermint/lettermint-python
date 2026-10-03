"""Packaging checks for the declared runtime dependencies."""

import re
from importlib.metadata import requires
from pathlib import Path

import lettermint


def test_typing_extensions_declared_for_all_python_versions() -> None:
    """Modules import typing_extensions unconditionally, so it must be an unconditional dependency."""
    package_dir = Path(lettermint.__file__).parent
    imports_typing_extensions = any(
        re.search(r"^\s*(from|import) typing_extensions\b", path.read_text(), re.MULTILINE)
        for path in package_dir.rglob("*.py")
    )
    assert imports_typing_extensions

    declared = requires("lettermint") or []
    unconditional = [
        requirement
        for requirement in declared
        if re.match(r"typing[-_]extensions\b", requirement, re.IGNORECASE)
        and "extra ==" not in requirement
        and ";" not in requirement
    ]
    assert unconditional, f"typing_extensions must be an unconditional dependency, got {declared}"
