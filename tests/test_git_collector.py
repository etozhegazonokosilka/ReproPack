"""Tests for the Git repository collector."""

import subprocess
from pathlib import Path

from pytest import MonkeyPatch

from repropack.collectors.git import collect_git_info


def test_collect_git_info_returns_safe_repository_metadata(monkeypatch: MonkeyPatch) -> None:
    """The collector returns branch, commit, status, and file paths without Git remotes."""
    outputs = {
        ("rev-parse", "--is-inside-work-tree"): "true\n",
        ("branch", "--show-current"): "main\n",
        ("rev-parse", "HEAD"): "abc123\n",
        ("status", "--porcelain", "--untracked-files=all"): " M src/app.py\n?? notes.txt\n",
    }
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, outputs[tuple(command[3:])], "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    info = collect_git_info(Path("/project"))

    assert info.is_available is True
    assert info.is_repository is True
    assert info.branch == "main"
    assert info.commit == "abc123"
    assert info.is_dirty is True
    assert info.modified_files == ["src/app.py"]
    assert info.untracked_files == ["notes.txt"]
    assert all("remote" not in command and "diff" not in command for command in commands)


def test_collect_git_info_handles_missing_git(monkeypatch: MonkeyPatch) -> None:
    """The collector returns an unavailable state when Git is not installed."""

    def raise_file_not_found(*_args: object, **_kwargs: object) -> None:
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)

    info = collect_git_info(Path("/project"))

    assert info.is_available is False
    assert info.is_repository is False
    assert info.unavailable_reason == "Git executable is not available."


def test_collect_git_info_handles_non_repository(monkeypatch: MonkeyPatch) -> None:
    """The collector returns a safe state when the target is not a Git repository."""
    error = subprocess.CalledProcessError(128, ["git", "rev-parse", "--is-inside-work-tree"])
    monkeypatch.setattr(subprocess, "run", lambda *_args, **_kwargs: (_ for _ in ()).throw(error))

    info = collect_git_info(Path("/project"))

    assert info.is_available is True
    assert info.is_repository is False
    assert info.unavailable_reason == "Target is not a Git repository."
