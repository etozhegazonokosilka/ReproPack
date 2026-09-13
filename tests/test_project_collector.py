"""Tests for the project structure collector."""

from pathlib import Path

from repropack.collectors.project import collect_project_info


def test_collect_project_info_limits_tree_depth(tmp_path: Path) -> None:
    """The collector includes entries only through the requested depth."""
    for relative_path in (
        "README.md",
        "src/app.py",
        "src/package/__init__.py",
        "src/package/deep/module.py",
        "src/package/deep/too/deep.py",
    ):
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    info = collect_project_info(tmp_path, max_depth=4)

    assert info.name == tmp_path.name
    assert info.file_tree == [
        "README.md",
        "src/",
        "src/app.py",
        "src/package/",
        "src/package/__init__.py",
        "src/package/deep/",
        "src/package/deep/module.py",
        "src/package/deep/too/",
    ]


def test_collect_project_info_ignores_generated_directories(tmp_path: Path) -> None:
    """The collector skips directories that do not describe the source project."""
    ignored_directories = (
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".idea",
        ".vscode",
    )
    for directory in ignored_directories:
        path = tmp_path / directory / "generated-file.txt"
        path.parent.mkdir(parents=True)
        path.touch()

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").touch()

    info = collect_project_info(tmp_path)

    assert info.file_tree == ["src/", "src/main.py"]
