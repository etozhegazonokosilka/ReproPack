"""HTML diagnostic report rendering."""

from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from repropack.models import DiagnosticReport
from repropack.reports.data import build_report_payload
from repropack.security import REDACTED

TEMPLATE_NAME = "report.html.j2"


def write_html_report(report: DiagnosticReport, output_path: Path) -> None:
    """Write a redacted, self-contained diagnostic report as HTML."""
    template_directory = files("repropack.reports").joinpath("templates")
    environment = Environment(
        loader=FileSystemLoader(str(template_directory)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    rendered_html = environment.get_template(TEMPLATE_NAME).render(
        report=build_report_payload(report),
        redacted_marker=REDACTED,
    )
    output_path.write_text(rendered_html, encoding="utf-8")
