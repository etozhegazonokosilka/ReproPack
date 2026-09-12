"""Validated data models for diagnostic reports."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportModel(BaseModel):
    """Base model that rejects unexpected report fields."""

    model_config = ConfigDict(extra="forbid")


class SystemInfo(ReportModel):
    """Safe operating-system metadata."""

    os_name: str
    os_version: str
    architecture: str


class PythonInfo(ReportModel):
    """Python runtime and installed-package metadata."""

    version: str
    implementation: str
    in_virtual_environment: bool
    packages: dict[str, str] = Field(default_factory=dict)


class GitInfo(ReportModel):
    """Safe Git repository metadata."""

    is_available: bool
    is_repository: bool
    branch: str | None = None
    commit: str | None = None
    is_dirty: bool | None = None
    modified_files: list[str] = Field(default_factory=list)
    untracked_files: list[str] = Field(default_factory=list)
    unavailable_reason: str | None = None


class ProjectInfo(ReportModel):
    """Project name and relative file-tree representation."""

    name: str
    file_tree: list[str]


class DiagnosticReport(ReportModel):
    """Complete validated diagnostic report."""

    generated_at: datetime
    repropack_version: str
    system: SystemInfo
    python: PythonInfo
    git: GitInfo
    project: ProjectInfo
    schema_version: str = "1.0"
    redaction_count: int = Field(default=0, ge=0)
