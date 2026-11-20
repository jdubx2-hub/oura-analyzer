# oura-analyzer

A local-first Python toolkit for accessing and exploring your personal Oura data.

> **Status:** OAuth2, daily-sleep, and workout API workflows implemented. This is an independent personal project, not affiliated with Oura.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jdubx2-hub/oura-analyzer.git
cd oura-analyzer
uv sync --all-extras
uv run oura --help
```

## OAuth setup

In your Oura developer application, register this exact redirect URI:

`http://localhost:8765/callback`

Then run:

```bash
uv run oura auth login
```

The CLI prompts for your Client ID and Client Secret (the secret is hidden while typing), opens the Oura consent page, and receives the authorization callback locally. Tokens and client credentials are stored in your operating-system keychain using Python Keyring. The app requests the `daily` and `workout` scopes.

If you previously authorized the app with only the `daily` scope, run `uv run oura auth login` again and approve the additional workout permission.

Check the saved authorization without revealing credentials:

```bash
uv run oura auth status
```

## Fetch daily sleep

For example:

```bash
uv run oura sleep --start-date 2026-10-01 --end-date 2026-10-31
```

To print the full response documents to your terminal:

```bash
uv run oura sleep --start-date 2026-10-01 --end-date 2026-10-31 --show-json
```

## Fetch workouts

For example:

```bash
uv run oura workouts --start-date 2026-10-01 --end-date 2026-10-31
```

The default output shows the workout date, activity, intensity (when available), and calories (when available). Add `--show-json` to print the full workout documents.

Both API commands handle pagination and keep API response data in memory only; they do not save or cache it.

## Data handling and Oura terms

Oura's API agreement restricts retaining API data beyond the duration strictly necessary and restricts certain onward sharing and AI-platform uses. This project therefore keeps API responses in memory for the immediate command and does not write them to `data/` or other local files. Review the current [Oura API and MCP Agreement](https://cloud.ouraring.com/legal/api-agreement) before changing this behavior.

Never paste personal health records, tokens, or client secrets into public issues or commit them to Git.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
