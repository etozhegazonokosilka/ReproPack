"""Command-line interface for ReproPack."""

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated
from zipfile import ZIP_DEFLATED, ZipFile

import typer

from repropack import __version__
from repropack.collectors.git import collect_git_info
from repropack.collectors.project import collect_project_info
from repropack.collectors.python import collect_python_info
from repropack.collectors.system import collect_system_info
from repropack.models import DiagnosticReport
from repropack.reports.html_report import write_html_report
from repropack.reports.json_report import write_json_report

HTML_REPORT_NAME = "report.html"
JSON_REPORT_NAME = "report.json"

app = typer.Typer(
    add_completion=False,
    help="ReproPack creates safe diagnostic archives for reproducible bug reports.",
    no_args_is_help=False,
)


@app.command(help="ReproPack creates safe diagnostic archives for reproducible bug reports.")
def main(
    project_path: Annotated[
        Path,
        typer.Argument(help="Directory to inspect."),
    ] = Path("."),
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Path for the generated ZIP archive."),
    ] = Path("repropack-report.zip"),
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Replace an existing output archive."),
    ] = False,
) -> None:
    """Create a safe diagnostic archive for a project directory."""
    resolved_project_path = project_path.expanduser().resolve()
    output_path = output.expanduser().resolve()

    if not resolved_project_path.is_dir():
        _fail(f"Project path is not an existing directory: {project_path}")
    if output_path.exists() and output_path.is_dir():
        _fail(f"Output path is a directory: {output}")
    if not output_path.parent.is_dir():
        _fail(f"Output directory does not exist: {output_path.parent}")
    if output_path.exists() and not overwrite:
        _fail(f"Output archive already exists: {output}. Use --overwrite to replace it.")

    try:
        report = _collect_report(resolved_project_path)
        _write_archive(report, output_path)
    except OSError as error:
        _fail(f"Could not create diagnostic archive: {error}")

    typer.echo(f"Created safe diagnostic archive: {output_path}")
    typer.echo(f"Included: {JSON_REPORT_NAME}, {HTML_REPORT_NAME}")


def _collect_report(project_path: Path) -> DiagnosticReport:
    """Collect validated diagnostic metadata for a project directory."""
    return DiagnosticReport(
        generated_at=datetime.now(UTC),
        repropack_version=__version__,
        system=collect_system_info(),
        python=collect_python_info(),
        git=collect_git_info(project_path),
        project=collect_project_info(project_path),
    )


def _write_archive(report: DiagnosticReport, output_path: Path) -> None:
    """Render reports and atomically place them in a ZIP archive."""
    with TemporaryDirectory(prefix=".repropack-", dir=output_path.parent) as temporary_directory:
        temporary_path = Path(temporary_directory)
        json_path = temporary_path / JSON_REPORT_NAME
        html_path = temporary_path / HTML_REPORT_NAME
        archive_path = temporary_path / "archive.zip"

        write_json_report(report, json_path)
        write_html_report(report, html_path)

        with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as archive:
            archive.write(json_path, arcname=JSON_REPORT_NAME)
            archive.write(html_path, arcname=HTML_REPORT_NAME)

        archive_path.replace(output_path)


def _fail(message: str) -> None:
    """Display a command error and stop with a non-zero status."""
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(code=1)
