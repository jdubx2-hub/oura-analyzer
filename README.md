# oura-analyzer

A local-first Python toolkit for accessing, exporting, and exploring your personal Oura data.

> **Status:** Early scaffold. OAuth/API integration is not yet implemented. This project deliberately separates live API access from importing official account exports while Oura's current developer terms and data-retention rules are reviewed.

## Goals

- Keep personal data and credentials on your own machine.
- Provide a small, understandable Python package and CLI.
- Separate authentication, API transport, export ingestion, and local storage.
- Make data workflows reproducible and testable.
- Avoid committing credentials or personal health data.

## Planned workflows

1. **Official export import** — ingest files downloaded through Oura's account-data export process.
2. **OAuth/API access** — add an official OAuth 2.0 client after verifying current Oura requirements, scopes, and permitted data handling.
3. **Local analysis** — normalize data and write analysis-friendly files locally (Parquet is the intended default where appropriate).

The API and export workflows are intentionally separate. Do not assume API responses may be retained indefinitely; confirm the applicable Oura terms before enabling persistent API storage.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jdubx2-hub/oura-analyzer.git
cd oura-analyzer
uv sync --all-extras
uv run oura --help
```

The CLI is scaffolded and will gain commands as the workflows are implemented.

## Configuration and privacy

- Never commit OAuth client secrets, access/refresh tokens, or downloaded Oura data.
- Local configuration belongs outside version control (for example, in your OS keychain or an ignored local `.env` file).
- See [docs/privacy.md](docs/privacy.md) for the project's local-data approach.
- See [docs/architecture.md](docs/architecture.md) for the planned component boundaries.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Disclaimer

This is an independent personal project and is not affiliated with or endorsed by Oura. Use of Oura APIs and data remains subject to Oura's applicable terms and developer policies.
