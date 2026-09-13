"""Project structure information collection."""

from pathlib import Path

from repropack.models import ProjectInfo

IGNORED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".idea",
        ".venv",
        ".vscode",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)


def collect_project_info(project_path: Path, max_depth: int = 4) -> ProjectInfo:
    """Collect a bounded, relative project file tree without reading files."""
    return ProjectInfo(
        name=project_path.name,
        file_tree=_collect_file_tree(project_path, project_path, max_depth),
    )


def _collect_file_tree(root: Path, current_path: Path, max_depth: int) -> list[str]:
    """Build a sorted file tree for one directory level."""
    entries: list[str] = []

    for path in sorted(current_path.iterdir(), key=lambda item: item.name.casefold()):
        relative_path = path.relative_to(root)
        depth = len(relative_path.parts)
        if depth > max_depth or (path.is_dir() and path.name in IGNORED_DIRECTORY_NAMES):
            continue

        display_path = relative_path.as_posix()
        is_directory = path.is_dir() and not path.is_symlink()
        if not is_directory:
            entries.append(display_path)
            continue

        entries.append(f"{display_path}/")
        if depth < max_depth:
            entries.extend(_collect_file_tree(root, path, max_depth))

    return entries
