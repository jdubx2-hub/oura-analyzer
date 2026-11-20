"""Helpers for retrieving Oura workout documents."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Any

from oura_analyzer.client import OuraAPIClient

WORKOUT_ENDPOINT = "/usercollection/workout"


def iter_workouts(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield workout documents for an optional inclusive date range.

    Results are streamed page-by-page and remain in memory; this helper does
    not write API data to disk.
    """
    yield from client.iter_documents(
        WORKOUT_ENDPOINT,
        start_date=start_date,
        end_date=end_date,
    )


def get_workouts(
    client: OuraAPIClient,
    *,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> list[dict[str, Any]]:
    """Return workout documents for an optional inclusive date range."""
    return list(iter_workouts(client, start_date=start_date, end_date=end_date))
