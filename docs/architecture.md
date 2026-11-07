# Architecture

The project is split into boundaries so that authentication, remote access,
ingestion, and persistence can evolve independently.

```text
CLI
 ├── official export importer ──> validation / normalization ──> local storage
 └── OAuth auth ──> API client ──> transient analysis
                                      (persistence only if terms allow)
```

## Planned modules

- `auth.py`: OAuth 2.0 authorization and secure credential handling.
- `client.py`: thin HTTP client for documented Oura API endpoints.
- `exports.py`: ingest files obtained through Oura's official account export.
- `storage.py`: explicit local filesystem and Parquet operations.
- `config.py`: paths and non-secret settings.
- `cli.py`: user-facing commands.

## Design principles

1. Local-first: personal files and credentials stay on the user's machine.
2. Explicit persistence: network responses are not silently written to disk.
3. Traceable transformations: preserve raw official exports and write derived
   datasets separately.
4. Small interfaces: keep the API client independent from analysis/storage.
5. Terms-aware: confirm Oura's current developer agreement before enabling
   API data retention, sharing, or downstream integrations.
