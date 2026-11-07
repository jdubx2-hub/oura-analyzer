# Architecture

```text
CLI
 ├── auth.py ──> Oura OAuth2 authorization code + PKCE
 │                └── OS keychain (client credentials + rotating tokens)
 └── sleep.py ──> client.py ──> Oura API v2
                                  └── response objects in memory only
```

## Boundaries

- `auth.py`: OAuth authorization, callback validation, PKCE, token refresh, keychain storage.
- `client.py`: authenticated HTTP transport, error handling, generic pagination.
- `sleep.py`: endpoint-specific daily sleep helper.
- `exports.py`: separate importer for files obtained through Oura's official account export.
- `storage.py`: local directory helpers; not used to persist API responses.

## API data handling

The current Oura API agreement restricts API data retention to the duration strictly necessary. API responses are therefore returned to the calling process and not implicitly cached or written to disk. Revisit this only after confirming written authorization or updated applicable terms.
