"""Small HTTP client for Oura API v2.

Responses are returned in memory only. This module intentionally has no
implicit file-writing or caching behavior.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

import httpx

API_BASE_URL = "https://api.ouraring.com/v2"
USER_AGENT = "oura-analyzer/0.2.0"


class OuraAPIError(RuntimeError):
    """Raised for an unsuccessful Oura API response."""


class OuraAPIClient:
    """Authenticated Oura API v2 client."""

    def __init__(self, access_token: str, *, transport: httpx.BaseTransport | None = None):
        self._client = httpx.Client(
            base_url=API_BASE_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=30.0,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> OuraAPIClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._client.get(endpoint, params=params)
        if response.is_error:
            try:
                payload = response.json()
                detail = payload.get("detail") or payload.get("title") or payload
            except ValueError:
                detail = response.text[:500]
            raise OuraAPIError(f"Oura API request failed ({response.status_code}): {detail}")
        return response.json()

    def iter_documents(
        self,
        endpoint: str,
        *,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield all documents from a paginated Oura collection endpoint."""
        params: dict[str, str] = {}
        if start_date is not None:
            params["start_date"] = start_date.isoformat() if isinstance(start_date, date) else start_date
        if end_date is not None:
            params["end_date"] = end_date.isoformat() if isinstance(end_date, date) else end_date

        while True:
            payload = self.get(endpoint, params=params)
            yield from payload.get("data", [])
            next_token = payload.get("next_token")
            if not next_token:
                break
            params["next_token"] = next_token
