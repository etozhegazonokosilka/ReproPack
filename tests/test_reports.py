"""Tests for JSON and HTML diagnostic reports."""

import json
from datetime import UTC, datetime
from pathlib import Path

from repropack.models import DiagnosticReport, GitInfo, ProjectInfo, PythonInfo, SystemInfo
from repropack.reports.html_report import write_html_report
from repropack.reports.json_report import write_json_report
from repropack.security import REDACTED

SECRET = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"


def test_write_json_report_serializes_redacted_diagnostic_data(tmp_path: Path) -> None:
    """The JSON report keeps diagnostic metadata while removing secrets."""
    output_path = tmp_path / "report.json"

    write_json_report(_build_report(), output_path)

    content = output_path.read_text(encoding="utf-8")
    payload = json.loads(content)
    assert payload["git"]["branch"] == f"feature/{REDACTED}"
    assert payload["python"]["packages"] == {"demo-package": "1.0.0"}
    assert SECRET not in content


def test_write_html_report_contains_required_sections_without_external_assets(
    tmp_path: Path,
) -> None:
    """The HTML report is self-contained, readable, and redacts its content."""
    output_path = tmp_path / "report.html"

    write_html_report(_build_report(), output_path)

    content = output_path.read_text(encoding="utf-8")
    for section in (
        "Overview",
        "System",
        "Python",
        "Dependencies",
        "Git",
        "Project Structure",
        "Security",
    ):
        assert section in content
    assert SECRET not in content
    assert REDACTED in content
    assert "http://" not in content
    assert "https://" not in content
    assert "<script" not in content


def _build_report() -> DiagnosticReport:
    """Build a representative report with a secret in Git metadata."""
    return DiagnosticReport(
        generated_at=datetime(2026, 9, 15, 12, 0, tzinfo=UTC),
        repropack_version="0.1.0",
        system=SystemInfo(os_name="TestOS", os_version="1.0", architecture="test-arch"),
        python=PythonInfo(
            version="3.12.3",
            implementation="CPython",
            in_virtual_environment=True,
            packages={"demo-package": "1.0.0"},
        ),
        git=GitInfo(
            is_available=True,
            is_repository=True,
            branch=f"feature/{SECRET}",
            commit="abc123",
            is_dirty=True,
            modified_files=["src/main.py"],
        ),
        project=ProjectInfo(name="sample-project", file_tree=["src/", "src/main.py"]),
    )
