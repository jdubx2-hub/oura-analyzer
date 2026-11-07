# Privacy and local data handling

This project is designed for one person's local use.

- Do not commit personal Oura exports, health data, tokens, client secrets, or
  machine-specific configuration.
- The repository's `.gitignore` excludes common local data and secret files.
- Keep credentials in the operating-system keychain where practical.
- Prefer importing data downloaded directly by the account holder from Oura.
- Do not upload personal data to third-party services as part of the default
  workflow.

## OAuth and API data

The OAuth/API path is not implemented yet. Before enabling it, verify Oura's
current developer terms, API documentation, permitted use, and retention
requirements. A local personal project should not assume that API responses
may be archived indefinitely.

## Website and policy note

This document describes the intended behavior of this software; it is not
legal advice and is not a substitute for any privacy policy Oura may require
for an OAuth application registration.
