# Architecture

```text
CLI
 ├── auth.py ──> Oura OAuth2 authorization code + PKCE
 │                └── OS keychain (client credentials + rotating tokens)
 ├── bundle.py ─> orchestrates date-scoped datasets for JMT export
 ├── client.py ─> authenticated HTTP transport + generic pagination
 ├── workouts.py ─> /usercollection/workout
 ├── sleep.py ───> /usercollection/daily_sleep and /usercollection/sleep
 ├── readiness.py ─> /usercollection/daily_readiness
 ├── activity.py ──> /usercollection/daily_activity
 ├── resilience.py > /usercollection/daily_resilience
 ├── stress.py ────> /usercollection/daily_stress
 ├── vo2_max.py ───> /usercollection/vO2_max
 ├── cardiovascular_age.py > /usercollection/daily_cardiovascular_age
 ├── spo2.py ──────> /usercollection/daily_spo2
 └── heart_rate.py > /usercollection/heartrate (timestamp-bounded)
                         └── response objects in memory only
```

## Boundaries

- `auth.py`: OAuth authorization, callback validation, PKCE, token refresh, and keychain storage. Requests the `daily`, `workout`, `heartrate`, `spo2`, and `heart_health` scopes.
- `client.py`: authenticated HTTP transport, API error handling, and pagination for both date-filtered collections and arbitrary query parameters.
- Endpoint modules: small typed-by-convention wrappers around individual Oura API v2 collections. They return raw response dictionaries and do not write files.
- `bundle.py`: orchestrates the date-scoped collections needed by the JMT workflow. It reports endpoint-level API errors without discarding successful datasets.
- `exports.py`: separate importer for files obtained from Oura's official account export.
- `storage.py`: local directory helpers; not used to persist API responses.

## Dataset organization

- Workout summaries are event-level records.
- Daily sleep, readiness, activity, resilience, stress, cardiovascular age, VO₂ max, and SpO₂ are date-scoped collections.
- Individual sleep periods provide richer sleep-stage and biometric details than daily sleep summaries.
- Heart-rate samples are a higher-volume time series queried by timezone-aware datetime bounds. They are fetched separately from the date-scoped bundle.

## API data handling

API responses are returned to the calling process and are not implicitly cached or written to disk. The export/storage policy remains separate from ingestion so that downstream packaging can be developed without coupling it to a particular persistence mechanism.
