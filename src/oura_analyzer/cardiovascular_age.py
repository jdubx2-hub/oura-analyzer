"""Helpers for retrieving Oura daily cardiovascular age measurements."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

DAILY_CARDIOVASCULAR_AGE_ENDPOINT = "/usercollection/daily_cardiovascular_age"


def iter_daily_cardiovascular_age(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield cardiovascular age documents for an optional inclusive date range."""
    yield from client.iter_documents(
        DAILY_CARDIOVASCULAR_AGE_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_daily_cardiovascular_age(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return cardiovascular age documents for an optional inclusive date range."""
    return list(
        iter_daily_cardiovascular_age(client, start_date=start_date, end_date=end_date)
    )
