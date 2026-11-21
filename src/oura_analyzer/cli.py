"""Command-line interface."""

import json
from datetime import date
from pathlib import Path

import keyring
import typer

from oura_analyzer.auth import OAuthError, auth_status, get_access_token, login
from oura_analyzer.bundle import collect_oura_data
from oura_analyzer.client import OuraAPIError, OuraAPIClient
from oura_analyzer.exports import inspect_export
from oura_analyzer.sleep import get_daily_sleep
from oura_analyzer.storage import ensure_data_dir
from oura_analyzer.workouts import get_workouts

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


def _parse_date_range(start_date: str, end_date: str) -> tuple[date, date]:
    """Parse and validate the inclusive date range shared by data commands."""
    try:
        parsed_start = date.fromisoformat(start_date)
        parsed_end = date.fromisoformat(end_date)
    except ValueError as exc:
        typer.echo("Dates must use YYYY-MM-DD format.", err=True)
        raise typer.Exit(code=2) from exc
    if parsed_end < parsed_start:
        typer.echo("--end-date must be on or after --start-date", err=True)
        raise typer.Exit(code=2)
    return parsed_start, parsed_end


@app.command("sleep")
def sleep_command(
    start_date: str = typer.Option(..., "--start-date", help="First day, YYYY-MM-DD."),
    end_date: str = typer.Option(..., "--end-date", help="Last day, YYYY-MM-DD."),
    show_json: bool = typer.Option(False, "--show-json", help="Print full response documents to stdout."),
) -> None:
    """Fetch daily sleep summaries for a date range (does not save API data)."""
    parsed_start, parsed_end = _parse_date_range(start_date, end_date)
    try:
        token = get_access_token()
        with OuraAPIClient(token) as client:
            records = get_daily_sleep(client, start_date=parsed_start, end_date=parsed_end)
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


@app.command("workouts")
def workouts_command(
    start_date: str = typer.Option(..., "--start-date", help="First day, YYYY-MM-DD."),
    end_date: str = typer.Option(..., "--end-date", help="Last day, YYYY-MM-DD."),
    show_json: bool = typer.Option(False, "--show-json", help="Print full response documents to stdout."),
) -> None:
    """Fetch workout records for a date range (does not save API data)."""
    parsed_start, parsed_end = _parse_date_range(start_date, end_date)
    try:
        token = get_access_token()
        with OuraAPIClient(token) as client:
            records = get_workouts(client, start_date=parsed_start, end_date=parsed_end)
    except (OAuthError, OuraAPIError) as exc:
        typer.echo(f"Request failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Retrieved {len(records)} workout records. Nothing was written to disk.")
    if show_json:
        typer.echo(json.dumps(records, indent=2, default=str))
    else:
        for record in records:
            day = record.get("day", "unknown day")
            activity = record.get("activity") or record.get("label") or "workout"
            details = []
            if record.get("intensity"):
                details.append(f"intensity={record['intensity']}")
            if record.get("calories") is not None:
                details.append(f"calories={record['calories']}")
            if record.get("distance") is not None:
                distance_miles = record["distance"] / 1609.344
                details.append(f"distance={distance_miles:.2f} mi")
            detail_text = f" ({', '.join(details)})" if details else ""
            typer.echo(f"{day}: {activity}{detail_text}")


@app.command("collect")
def collect_command(
    start_date: str = typer.Option(..., "--start-date", help="First day, YYYY-MM-DD."),
    end_date: str = typer.Option(..., "--end-date", help="Last day, YYYY-MM-DD."),
    show_json: bool = typer.Option(False, "--show-json", help="Print the collected datasets as JSON."),
) -> None:
    """Collect the date-scoped Oura datasets used by the JMT training workflow."""
    parsed_start, parsed_end = _parse_date_range(start_date, end_date)
    try:
        token = get_access_token()
        with OuraAPIClient(token) as client:
            result = collect_oura_data(
                client,
                start_date=parsed_start,
                end_date=parsed_end,
            )
    except (OAuthError, OuraAPIError) as exc:
        typer.echo(f"Collection failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    datasets = result["datasets"]
    total_records = sum(len(records) for records in datasets.values())
    typer.echo(
        f"Collected {total_records} records across {len(datasets)} datasets "
        f"for {parsed_start} through {parsed_end}."
    )
    for name, records in datasets.items():
        typer.echo(f"  {name}: {len(records)} records")
    for name, error in result["errors"].items():
        typer.echo(f"  {name}: unavailable ({error})", err=True)

    if show_json:
        typer.echo(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    app()
