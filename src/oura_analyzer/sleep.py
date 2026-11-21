"""Helpers for retrieving Oura sleep summaries and detailed sleep periods."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

DAILY_SLEEP_ENDPOINT = "/usercollection/daily_sleep"
SLEEP_ENDPOINT = "/usercollection/sleep"


def iter_daily_sleep(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield daily sleep summary documents for an optional inclusive date range."""
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
    """Return daily sleep summary documents for an optional inclusive date range."""
    return list(iter_daily_sleep(client, start_date=start_date, end_date=end_date))


def iter_sleep_periods(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield individual sleep-period documents for an optional inclusive date range.

    A day can contain multiple sleep periods. These records include richer
    sleep-stage and biometric details than the daily summary endpoint.
    """
    yield from client.iter_documents(
        SLEEP_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_sleep_periods(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return individual sleep-period documents for an optional date range."""
    return list(iter_sleep_periods(client, start_date=start_date, end_date=end_date))
