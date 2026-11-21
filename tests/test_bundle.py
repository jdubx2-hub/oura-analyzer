from datetime import date

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
    }
    assert result["datasets"]["workouts"] == [{"id": "workout-1"}]
    assert "sleep_periods" not in result["datasets"]
    assert result["errors"] == {"sleep_periods": "Oura API request failed (403): missing scope"}
