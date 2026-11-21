"""Helpers for retrieving Oura daily readiness summaries."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

DAILY_READINESS_ENDPOINT = "/usercollection/daily_readiness"


def iter_daily_readiness(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield daily readiness documents for an optional inclusive date range."""
    yield from client.iter_documents(
        DAILY_READINESS_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_daily_readiness(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return daily readiness documents for an optional inclusive date range."""
    return list(iter_daily_readiness(client, start_date=start_date, end_date=end_date))
