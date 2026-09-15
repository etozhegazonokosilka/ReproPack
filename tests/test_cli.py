"""Tests for the command-line interface."""

import json
from pathlib import Path
from zipfile import ZipFile

from pytest import MonkeyPatch
from typer.testing import CliRunner

from repropack.cli import app
from repropack.models import GitInfo, ProjectInfo, PythonInfo, SystemInfo

runner = CliRunner()

SECRET = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"


def test_help_displays_project_name_and_description() -> None:
    """The command exposes a useful help screen."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "ReproPack" in result.output
    assert "safe diagnostic archives" in result.output


def test_command_creates_redacted_zip_archive(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """The root command packages both safe report formats."""
    project_path = tmp_path / "demo-project"
    project_path.mkdir()
    output_path = tmp_path / "diagnostic.zip"
    _stub_collectors(monkeypatch)

    result = runner.invoke(app, [str(project_path), "--output", str(output_path)])

    assert result.exit_code == 0
    assert "Created safe diagnostic archive" in result.output
    assert output_path.is_file()
    with ZipFile(output_path) as archive:
        assert set(archive.namelist()) == {"report.json", "report.html"}
        report_json = archive.read("report.json").decode("utf-8")
        report_html = archive.read("report.html").decode("utf-8")
    assert json.loads(report_json)["git"]["branch"] == "feature/[REDACTED]"
    assert SECRET not in report_json
    assert SECRET not in report_html


def test_command_refuses_to_overwrite_an_archive(tmp_path: Path) -> None:
    """Existing archives require an explicit overwrite option."""
    project_path = tmp_path / "demo-project"
    project_path.mkdir()
    output_path = tmp_path / "diagnostic.zip"
    output_path.write_text("keep this file", encoding="utf-8")

    result = runner.invoke(app, [str(project_path), "--output", str(output_path)])

    assert result.exit_code == 1
    assert "already exists" in result.output
    assert output_path.read_text(encoding="utf-8") == "keep this file"


def _stub_collectors(monkeypatch: MonkeyPatch) -> None:
    """Replace host-specific collectors with deterministic report data."""
    monkeypatch.setattr(
        "repropack.cli.collect_system_info",
        lambda: SystemInfo(os_name="TestOS", os_version="1.0", architecture="test-arch"),
    )
    monkeypatch.setattr(
        "repropack.cli.collect_python_info",
        lambda: PythonInfo(
            version="3.12.3",
            implementation="CPython",
            in_virtual_environment=True,
            packages={"demo-package": "1.0.0"},
        ),
    )
    monkeypatch.setattr(
        "repropack.cli.collect_git_info",
        lambda _: GitInfo(
            is_available=True,
            is_repository=True,
            branch=f"feature/{SECRET}",
            commit="abc123",
            is_dirty=False,
        ),
    )
    monkeypatch.setattr(
        "repropack.cli.collect_project_info",
        lambda _: ProjectInfo(name="demo-project", file_tree=["src/", "src/main.py"]),
    )
