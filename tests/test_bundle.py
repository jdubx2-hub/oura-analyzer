from datetime import date

import pytest

from oura_analyzer import bundle
from oura_analyzer.client import OuraAPIError


def test_collect_oura_data_keeps_successful_datasets_when_one_endpoint_fails(
    monkeypatch,
) -> None:
    def successful_fetch(client, *, start_date, end_date):
        return [{"id": "workout-1"}]

    def failed_fetch(client, *, start_date, end_date):
        raise OuraAPIError("403: missing scope")

    monkeypatch.setattr(bundle, "get_workouts", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_sleep", successful_fetch)
    monkeypatch.setattr(bundle, "get_sleep_periods", failed_fetch)
    monkeypatch.setattr(bundle, "get_daily_readiness", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_activity", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_resilience", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_stress", successful_fetch)
    monkeypatch.setattr(bundle, "get_vo2_max", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_cardiovascular_age", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_spo2", successful_fetch)

    result = bundle.collect_oura_data(
        object(),
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 31),
    )

    assert result["date_range"] == {
        "start_date": "2026-10-01",
        "end_date": "2026-10-31",
        "timezone": "America/Los_Angeles",
    }
    assert result["datasets"]["workouts"] == [{"id": "workout-1"}]
    assert "sleep_periods" not in result["datasets"]
    assert result["errors"] == {"sleep_periods": "403: missing scope"}


def test_collect_heart_rate_uses_local_midnight_and_dst_aware_boundaries(monkeypatch) -> None:
    captured = {}

    def successful_fetch(client, *, start_date, end_date):
        return []

    def heart_rate_fetch(client, *, start_datetime, end_datetime):
        captured["start"] = start_datetime
        captured["end"] = end_datetime
        return [{"bpm": 65}]

    monkeypatch.setattr(bundle, "get_workouts", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_sleep", successful_fetch)
    monkeypatch.setattr(bundle, "get_sleep_periods", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_readiness", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_activity", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_resilience", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_stress", successful_fetch)
    monkeypatch.setattr(bundle, "get_vo2_max", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_cardiovascular_age", successful_fetch)
    monkeypatch.setattr(bundle, "get_daily_spo2", successful_fetch)
    monkeypatch.setattr(bundle, "get_heart_rate", heart_rate_fetch)

    result = bundle.collect_oura_data(
        object(),
        start_date="2026-11-01",
        end_date="2026-11-01",
        include_heart_rate=True,
        timezone_name="America/Los_Angeles",
    )

    assert result["datasets"]["heart_rate"] == [{"bpm": 65}]
    assert captured["start"] == "2026-11-01T00:00:00-07:00"
    assert captured["end"] == "2026-11-02T00:00:00-08:00"


def test_collect_rejects_unknown_timezone_when_heart_rate_requested() -> None:
    with pytest.raises(ValueError, match="Unknown timezone"):
        bundle.collect_oura_data(
            object(),
            start_date="2026-10-01",
            end_date="2026-10-02",
            include_heart_rate=True,
            timezone_name="Mars/Olympus",
        )
