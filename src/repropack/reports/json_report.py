"""JSON diagnostic report rendering."""

import json
from pathlib import Path

from repropack.models import DiagnosticReport
from repropack.reports.data import build_report_payload


def write_json_report(report: DiagnosticReport, output_path: Path) -> None:
    """Write a redacted diagnostic report as formatted JSON."""
    output_path.write_text(
        json.dumps(build_report_payload(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
