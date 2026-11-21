"""Helpers for retrieving Oura daily stress summaries."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

DAILY_STRESS_ENDPOINT = "/usercollection/daily_stress"


def iter_daily_stress(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield daily stress documents for an optional inclusive date range."""
    yield from client.iter_documents(
        DAILY_STRESS_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_daily_stress(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return daily stress documents for an optional inclusive date range."""
    return list(iter_daily_stress(client, start_date=start_date, end_date=end_date))
