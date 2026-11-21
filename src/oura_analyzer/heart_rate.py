"""Helpers for retrieving Oura's timestamped heart-rate measurements."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Any

from oura_analyzer.client import OuraAPIClient

HEART_RATE_ENDPOINT = "/usercollection/heartrate"


def _parse_datetime(value: datetime | str) -> datetime:
    """Parse a datetime while requiring an explicit timezone offset."""
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Heart-rate datetimes must include a timezone offset.")
    return parsed


def iter_heart_rate(
    client: OuraAPIClient,
    *,
    start_datetime: datetime | str,
    end_datetime: datetime | str,
) -> Iterator[dict[str, Any]]:
    """Yield heart-rate samples for a timezone-aware datetime interval.

    Oura returns samples at approximately five-minute intervals.
    """
    start = _parse_datetime(start_datetime)
    end = _parse_datetime(end_datetime)
    if end <= start:
        raise ValueError("end_datetime must be after start_datetime.")

    yield from client.iter_pages(
        HEART_RATE_ENDPOINT,
        params={
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
        },
    )


def get_heart_rate(
    client: OuraAPIClient,
    *,
    start_datetime: datetime | str,
    end_datetime: datetime | str,
) -> list[dict[str, Any]]:
    """Return heart-rate samples for a timezone-aware datetime interval."""
    return list(
        iter_heart_rate(
            client,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
    )
