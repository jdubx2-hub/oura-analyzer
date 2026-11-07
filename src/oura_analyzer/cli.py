"""Command-line interface."""

import json
from datetime import date
from pathlib import Path

import keyring
import typer

from oura_analyzer.auth import OAuthError, auth_status, get_access_token, login
from oura_analyzer.client import OuraAPIError, OuraAPIClient
from oura_analyzer.exports import inspect_export
from oura_analyzer.sleep import get_daily_sleep
from oura_analyzer.storage import ensure_data_dir

app = typer.Typer(help="Import and explore your personal Oura data.")
auth_app = typer.Typer(help="Manage Oura OAuth authorization.")
app.add_typer(auth_app, name="auth")


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


@auth_app.command("login")
def auth_login() -> None:
    """Authorize this app with Oura and save tokens in the OS keychain."""
    client_id = keyring.get_password("oura-analyzer", "client_id")
    client_secret = keyring.get_password("oura-analyzer", "client_secret")
    if not client_id:
        client_id = typer.prompt("Oura Client ID")
    if not client_secret:
        client_secret = typer.prompt("Oura Client Secret", hide_input=True)
    try:
        login(client_id, client_secret)
    except (OAuthError, keyring.errors.KeyringError) as exc:
        typer.echo(f"Authentication failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@auth_app.command("status")
def auth_status_command() -> None:
    """Show whether an Oura authorization is saved (never prints tokens)."""
    try:
        status = auth_status()
    except Exception as exc:
        typer.echo(f"Could not read OS keychain: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(status, indent=2))


@app.command("sleep")
def sleep_command(
    start_date: date = typer.Option(..., "--start-date", help="First day, YYYY-MM-DD."),
    end_date: date = typer.Option(..., "--end-date", help="Last day, YYYY-MM-DD."),
    show_json: bool = typer.Option(False, "--show-json", help="Print full response documents to stdout."),
) -> None:
    """Fetch daily sleep summaries for a date range (does not save API data)."""
    if end_date < start_date:
        typer.echo("--end-date must be on or after --start-date", err=True)
        raise typer.Exit(code=2)
    try:
        token = get_access_token()
        with OuraAPIClient(token) as client:
            records = get_daily_sleep(client, start_date=start_date, end_date=end_date)
    except (OAuthError, OuraAPIError) as exc:
        typer.echo(f"Request failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Retrieved {len(records)} daily sleep records. Nothing was written to disk.")
    if show_json:
        typer.echo(json.dumps(records, indent=2, default=str))
    else:
        for record in records:
            day = record.get("day", "unknown day")
            score = record.get("score", "score unavailable")
            typer.echo(f"{day}: score={score}")


if __name__ == "__main__":
    app()
