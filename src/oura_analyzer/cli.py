"""Command-line interface."""

from pathlib import Path

import typer

from oura_analyzer.exports import inspect_export
from oura_analyzer.storage import ensure_data_dir

app = typer.Typer(help="Import and explore your personal Oura data.")


@app.command()
def init(
    data_path: Path = typer.Option(Path("data"), "--data-dir", help="Local data directory."),
) -> None:
    """Create the local data directory."""
    location = ensure_data_dir(data_path)
    typer.echo(f"Created/verified data directory: {location.resolve()}")


@app.command("inspect-export")
def inspect_export_command(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
) -> None:
    """List files in an extracted official Oura account export."""
    files = inspect_export(path)
    if not files:
        typer.echo("No files found.")
        raise typer.Exit()
    for file in files:
        typer.echo(str(file))


if __name__ == "__main__":
    app()
