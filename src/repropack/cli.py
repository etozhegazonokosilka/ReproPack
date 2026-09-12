"""Command-line interface for ReproPack."""

import typer

app = typer.Typer(
    add_completion=False,
    help="ReproPack creates safe diagnostic archives for reproducible bug reports.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Create safe diagnostic archives for reproducible bug reports."""
