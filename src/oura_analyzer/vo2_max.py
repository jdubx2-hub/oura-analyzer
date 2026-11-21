"""Helpers for retrieving Oura VO2 max measurements."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

VO2_MAX_ENDPOINT = "/usercollection/vO2_max"


def iter_vo2_max(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield VO2 max documents for an optional inclusive date range."""
    yield from client.iter_documents(
        VO2_MAX_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_vo2_max(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return VO2 max documents for an optional inclusive date range."""
    return list(iter_vo2_max(client, start_date=start_date, end_date=end_date))
