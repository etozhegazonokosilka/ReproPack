"""Tests for the system information collector."""

import platform

from pytest import MonkeyPatch

from repropack.collectors.system import collect_system_info


def test_collect_system_info_returns_requested_platform_metadata(monkeypatch: MonkeyPatch) -> None:
    """The collector maps platform values to safe system metadata."""
    monkeypatch.setattr(platform, "system", lambda: "TestOS")
    monkeypatch.setattr(platform, "version", lambda: "2026.9")
    monkeypatch.setattr(platform, "machine", lambda: "test-arch")

    info = collect_system_info()

    assert info.os_name == "TestOS"
    assert info.os_version == "2026.9"
    assert info.architecture == "test-arch"
