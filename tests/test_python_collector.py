"""Tests for the Python environment collector."""

import platform
import sys
from importlib import metadata
from types import SimpleNamespace

from pytest import MonkeyPatch

from repropack.collectors.python import collect_python_info


def test_collect_python_info_returns_runtime_and_sorted_packages(monkeypatch: MonkeyPatch) -> None:
    """The collector returns safe runtime metadata and package versions."""
    distributions = [
        SimpleNamespace(metadata={"Name": "Zeta"}, version="2.0.0"),
        SimpleNamespace(metadata={"Name": "alpha"}, version="1.0.0"),
    ]
    monkeypatch.setattr(platform, "python_version", lambda: "3.12.3")
    monkeypatch.setattr(platform, "python_implementation", lambda: "CPython")
    monkeypatch.setattr(sys, "prefix", "/project/.venv")
    monkeypatch.setattr(sys, "base_prefix", "/usr")
    monkeypatch.setattr(metadata, "distributions", lambda: distributions)

    info = collect_python_info()

    assert info.version == "3.12.3"
    assert info.implementation == "CPython"
    assert info.in_virtual_environment is True
    assert info.packages == {"alpha": "1.0.0", "Zeta": "2.0.0"}
