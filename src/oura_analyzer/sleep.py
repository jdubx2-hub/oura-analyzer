"""Helpers for retrieving Oura daily sleep summaries."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

DAILY_SLEEP_ENDPOINT = "/usercollection/daily_sleep"


def iter_daily_sleep(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield daily sleep documents for an optional inclusive date range.

    Results are streamed page-by-page and remain in memory; this helper does
    not write API data to disk.
    """
    yield from client.iter_documents(
        DAILY_SLEEP_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_daily_sleep(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return daily sleep documents for an optional inclusive date range."""
    return list(iter_daily_sleep(client, start_date=start_date, end_date=end_date))
