"""The generated synchronous layer is current, and packaging declares what the code imports."""

from __future__ import annotations

import re
import subprocess
import sys
from importlib.metadata import requires
from pathlib import Path

import lettermint

ROOT = Path(__file__).resolve().parents[1]


def test_the_sync_layer_is_generated_from_the_async_layer() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "unasync.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_generated_headers() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"],
        capture_output=True,
        text=True,
        env={"LETTERMINT_SDK_GENERATOR": str(ROOT / "no-generator-here"), "PATH": ""},
    )
    assert result.returncode == 0, result.stderr
    assert "Naming profile: next" in result.stdout


def test_runtime_dependencies_are_declared_for_every_python_version() -> None:
    package_dir = Path(lettermint.__file__).parent
    imported = set()
    for path in package_dir.rglob("*.py"):
        imported |= set(
            re.findall(
                r"^\s*(?:from|import) (typing_extensions|httpx|anyio)\b",
                path.read_text(),
                re.MULTILINE,
            )
        )
    assert imported == {"typing_extensions", "httpx", "anyio"}
    declared = [r for r in requires("lettermint") or [] if "extra ==" not in r]
    for name in imported:
        matching = [
            r for r in declared if re.match(rf"{name.replace('_', '[-_]')}\b", r, re.IGNORECASE)
        ]
        assert matching and ";" not in matching[0], (
            f"{name} must be an unconditional dependency, got {declared}"
        )


def test_the_version_comes_from_one_place() -> None:
    text = (ROOT / "src" / "lettermint" / "_version.py").read_text()
    assert re.search(r'^__version__ = "\d+\.\d+\.\d+.*"$', text, re.MULTILINE)
    assert 'dynamic = ["version"]' in (ROOT / "pyproject.toml").read_text()
