"""Helpers for retrieving Oura daily blood oxygen summaries."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

DAILY_SPO2_ENDPOINT = "/usercollection/daily_spo2"


def iter_daily_spo2(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield daily SpO2 documents for an optional inclusive date range."""
    yield from client.iter_documents(
        DAILY_SPO2_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_daily_spo2(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return daily SpO2 documents for an optional inclusive date range."""
    return list(iter_daily_spo2(client, start_date=start_date, end_date=end_date))
