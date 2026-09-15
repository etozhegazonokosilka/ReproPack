"""Shared diagnostic report rendering data."""

from repropack.models import DiagnosticReport
from repropack.security import redact_data


def build_report_payload(report: DiagnosticReport) -> dict[str, object]:
    """Convert a diagnostic report into a redacted serializable payload."""
    redacted_data = redact_data(report.model_dump(mode="json"))
    if not isinstance(redacted_data, dict):
        raise TypeError("Diagnostic report data must be a dictionary.")
    return {str(key): value for key, value in redacted_data.items()}
