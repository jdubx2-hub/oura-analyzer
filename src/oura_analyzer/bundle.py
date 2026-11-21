"""Orchestration for collecting date-scoped Oura datasets."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from oura_analyzer.activity import get_daily_activity
from oura_analyzer.cardiovascular_age import get_daily_cardiovascular_age
from oura_analyzer.client import OuraAPIClient, OuraAPIError
from oura_analyzer.heart_rate import get_heart_rate
from oura_analyzer.readiness import get_daily_readiness
from oura_analyzer.resilience import get_daily_resilience
from oura_analyzer.sleep import get_daily_sleep, get_sleep_periods
from oura_analyzer.spo2 import get_daily_spo2
from oura_analyzer.stress import get_daily_stress
from oura_analyzer.vo2_max import get_vo2_max
from oura_analyzer.workouts import get_workouts


def _as_date(value: date | str) -> date:
    return value if isinstance(value, date) else date.fromisoformat(value)


def collect_oura_data(
    client: OuraAPIClient,
    *,
    start_date: date | str,
    end_date: date | str,
    include_heart_rate: bool = False,
    timezone_name: str = "America/Los_Angeles",
) -> dict[str, Any]:
    """Collect Oura datasets used by the JMT training workflow.

    Each dataset is fetched independently. If one endpoint is unavailable
    because of permissions, device support, or subscription status, its error
    is reported without discarding successful datasets.

    Heart-rate samples are optional because they are substantially higher
    volume. When requested, local midnight boundaries are converted to
    timezone-aware ISO timestamps for the Oura API.
    """
    start = _as_date(start_date)
    end = _as_date(end_date)
    if end < start:
        raise ValueError("end_date must be on or after start_date.")

    collectors: dict[str, Callable[..., list[dict[str, Any]]]] = {
        "workouts": get_workouts,
        "daily_sleep": get_daily_sleep,
        "sleep_periods": get_sleep_periods,
        "daily_readiness": get_daily_readiness,
        "daily_activity": get_daily_activity,
        "daily_resilience": get_daily_resilience,
        "daily_stress": get_daily_stress,
        "vo2_max": get_vo2_max,
        "daily_cardiovascular_age": get_daily_cardiovascular_age,
        "daily_spo2": get_daily_spo2,
    }

    if include_heart_rate:
        try:
            zone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {timezone_name}") from exc
        start_datetime = datetime.combine(start, time.min, tzinfo=zone)
        end_datetime = datetime.combine(end + timedelta(days=1), time.min, tzinfo=zone)

        def collect_heart_rate(
            api_client: OuraAPIClient,
            *,
            start_date: date,
            end_date: date,
        ) -> list[dict[str, Any]]:
            return get_heart_rate(
                api_client,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )

        collectors["heart_rate"] = collect_heart_rate

    datasets: dict[str, list[dict[str, Any]]] = {}
    errors: dict[str, str] = {}
    for name, collector in collectors.items():
        try:
            datasets[name] = collector(
                client,
                start_date=start,
                end_date=end,
            )
        except OuraAPIError as exc:
            errors[name] = str(exc)

    return {
        "date_range": {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "timezone": timezone_name,
        },
        "datasets": datasets,
        "errors": errors,
    }
