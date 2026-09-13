"""Git repository information collection."""

import subprocess
from pathlib import Path

from repropack.models import GitInfo


def collect_git_info(project_path: Path) -> GitInfo:
    """Collect safe Git metadata without remotes or file contents."""
    try:
        is_repository = (
            _run_git(project_path, "rev-parse", "--is-inside-work-tree").strip() == "true"
        )
    except FileNotFoundError:
        return GitInfo(
            is_available=False,
            is_repository=False,
            unavailable_reason="Git executable is not available.",
        )
    except subprocess.CalledProcessError:
        return GitInfo(
            is_available=True,
            is_repository=False,
            unavailable_reason="Target is not a Git repository.",
        )

    if not is_repository:
        return GitInfo(
            is_available=True,
            is_repository=False,
            unavailable_reason="Target is not a Git repository.",
        )

    try:
        branch = _run_git(project_path, "branch", "--show-current").strip() or None
        commit = _run_git(project_path, "rev-parse", "HEAD").strip() or None
        status = _run_git(project_path, "status", "--porcelain", "--untracked-files=all")
    except subprocess.CalledProcessError:
        return GitInfo(
            is_available=True,
            is_repository=True,
            unavailable_reason="Git metadata could not be collected.",
        )

    modified_files, untracked_files = _parse_status(status)
    return GitInfo(
        is_available=True,
        is_repository=True,
        branch=branch,
        commit=commit,
        is_dirty=bool(status.strip()),
        modified_files=modified_files,
        untracked_files=untracked_files,
    )


def _run_git(project_path: Path, *arguments: str) -> str:
    """Run a Git command against a project and return its standard output."""
    result = subprocess.run(
        ["git", "-C", str(project_path), *arguments],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _parse_status(status: str) -> tuple[list[str], list[str]]:
    """Split porcelain status paths into modified and untracked groups."""
    modified_files: list[str] = []
    untracked_files: list[str] = []

    for line in status.splitlines():
        if len(line) < 4:
            continue

        path = line[3:]
        if line.startswith("??"):
            untracked_files.append(path)
        else:
            modified_files.append(path)

    return modified_files, untracked_files
