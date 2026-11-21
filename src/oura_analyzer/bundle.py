"""Orchestration for collecting date-scoped Oura datasets."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from oura_analyzer.activity import get_daily_activity
from oura_analyzer.cardiovascular_age import get_daily_cardiovascular_age
from oura_analyzer.client import OuraAPIClient, OuraAPIError
from oura_analyzer.readiness import get_daily_readiness
from oura_analyzer.resilience import get_daily_resilience
from oura_analyzer.sleep import get_daily_sleep, get_sleep_periods
from oura_analyzer.spo2 import get_daily_spo2
from oura_analyzer.stress import get_daily_stress
from oura_analyzer.vo2_max import get_vo2_max
from oura_analyzer.workouts import get_workouts


def collect_oura_data(
    client: OuraAPIClient,
    *,
    start_date: date | str,
    end_date: date | str,
) -> dict[str, Any]:
    """Collect the date-scoped Oura datasets used by the JMT training workflow.

    Each dataset is fetched independently. If one endpoint is unavailable
    because of permissions, device support, or subscription status, its error
    is reported without discarding successful datasets.
    """
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

    datasets: dict[str, list[dict[str, Any]]] = {}
    errors: dict[str, str] = {}
    for name, collector in collectors.items():
        try:
            datasets[name] = collector(
                client,
                start_date=start_date,
                end_date=end_date,
            )
        except OuraAPIError as exc:
            errors[name] = str(exc)

    return {
        "date_range": {
            "start_date": start_date.isoformat() if isinstance(start_date, date) else start_date,
            "end_date": end_date.isoformat() if isinstance(end_date, date) else end_date,
        },
        "datasets": datasets,
        "errors": errors,
    }
