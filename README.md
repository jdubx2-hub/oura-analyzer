# oura-analyzer

A local-first Python toolkit for accessing and exploring your personal Oura data.

> **Status:** OAuth2 and ingestion modules for workouts, sleep, readiness, activity, resilience, stress, VO₂ max, cardiovascular age, SpO₂, and heart rate are implemented. This is an independent personal project, not affiliated with Oura.

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

The CLI prompts for your Client ID and Client Secret (the secret is hidden while typing), opens the Oura consent page, and receives the authorization callback locally. Tokens and client credentials are stored in your operating-system keychain using Python Keyring. The app requests the `daily`, `workout`, `heartrate`, `spo2`, and `heart_health` scopes.

If you previously authorized the app with fewer scopes, run `uv run oura auth login` again and approve the additional permissions.

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

## Collect JMT-relevant Oura data

Fetch the date-scoped datasets used by the JMT training workflow:

```bash
uv run oura collect --start-date 2026-10-01 --end-date 2026-10-31
```

This retrieves workouts, daily sleep summaries, individual sleep periods, readiness, activity, resilience, stress, VO₂ max, cardiovascular age, and SpO₂. Each dataset is fetched independently; if an endpoint is unavailable because of permissions or device support, the command reports that dataset's error while retaining the other successful results in memory.

Add `--show-json` to print the combined response:

```bash
uv run oura collect --start-date 2026-10-01 --end-date 2026-10-31 --show-json
```

## Fetch detailed heart-rate samples

Heart rate is a timestamped time series, so it uses timezone-aware datetime bounds rather than calendar dates:

```bash
uv run oura heart-rate \
  --start-datetime "2026-10-01T00:00:00-07:00" \
  --end-datetime "2026-10-02T00:00:00-07:00"
```

Use `--show-json` to print the individual samples. The API returns heart-rate samples at approximately five-minute intervals.

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
