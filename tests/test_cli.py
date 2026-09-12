"""Tests for the command-line interface."""

from typer.testing import CliRunner

from repropack.cli import app

runner = CliRunner()


def test_help_displays_project_name_and_description() -> None:
    """The command exposes a useful help screen."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "ReproPack" in result.output
    assert "safe diagnostic archives" in result.output
