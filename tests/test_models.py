"""Tests for diagnostic report data models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from repropack.models import DiagnosticReport, GitInfo, ProjectInfo, PythonInfo, SystemInfo


def test_system_info_stores_safe_platform_metadata() -> None:
    """System information contains only requested platform metadata."""
    info = SystemInfo(os_name="Linux", os_version="6.8", architecture="x86_64")

    assert info.model_dump() == {
        "os_name": "Linux",
        "os_version": "6.8",
        "architecture": "x86_64",
    }


def test_python_info_keeps_package_versions() -> None:
    """Python information preserves an installed-package mapping."""
    info = PythonInfo(
        version="3.12.3",
        implementation="CPython",
        in_virtual_environment=True,
        packages={"pydantic": "2.13.5"},
    )

    assert info.packages == {"pydantic": "2.13.5"}
    assert info.in_virtual_environment is True


def test_git_info_defaults_file_lists_to_empty() -> None:
    """Unavailable Git data has no file paths by default."""
    info = GitInfo(is_available=False, is_repository=False, unavailable_reason="Git is unavailable")

    assert info.modified_files == []
    assert info.untracked_files == []
    assert info.branch is None
    assert info.commit is None
    assert info.is_dirty is None


def test_project_info_stores_only_relative_file_tree() -> None:
    """Project information represents the project with relative paths."""
    info = ProjectInfo(name="sample-project", file_tree=["src/", "src/main.py"])

    assert info.file_tree == ["src/", "src/main.py"]


def test_diagnostic_report_serializes_nested_models() -> None:
    """A complete diagnostic report serializes its nested sections."""
    report = DiagnosticReport(
        generated_at=datetime(2026, 9, 12, 12, 0, tzinfo=UTC),
        repropack_version="0.1.0",
        system=SystemInfo(os_name="Linux", os_version="6.8", architecture="x86_64"),
        python=PythonInfo(
            version="3.12.3",
            implementation="CPython",
            in_virtual_environment=True,
        ),
        git=GitInfo(is_available=True, is_repository=True, branch="main", commit="abc123"),
        project=ProjectInfo(name="sample-project", file_tree=["README.md"]),
    )

    payload = report.model_dump(mode="json")

    assert payload["schema_version"] == "1.0"
    assert payload["generated_at"] == "2026-09-12T12:00:00Z"
    assert payload["git"]["branch"] == "main"
    assert payload["redaction_count"] == 0


def test_diagnostic_report_rejects_negative_redaction_count() -> None:
    """The redaction count cannot be negative."""
    with pytest.raises(ValidationError):
        DiagnosticReport(
            generated_at=datetime.now(UTC),
            repropack_version="0.1.0",
            system=SystemInfo(os_name="Linux", os_version="6.8", architecture="x86_64"),
            python=PythonInfo(
                version="3.12.3",
                implementation="CPython",
                in_virtual_environment=True,
            ),
            git=GitInfo(is_available=True, is_repository=True),
            project=ProjectInfo(name="sample-project", file_tree=[]),
            redaction_count=-1,
        )
