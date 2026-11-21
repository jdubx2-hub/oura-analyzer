import httpx
import pytest

from oura_analyzer.activity import get_daily_activity
from oura_analyzer.cardiovascular_age import get_daily_cardiovascular_age
from oura_analyzer.client import OuraAPIClient
from oura_analyzer.readiness import get_daily_readiness
from oura_analyzer.resilience import get_daily_resilience
from oura_analyzer.sleep import get_sleep_periods
from oura_analyzer.spo2 import get_daily_spo2
from oura_analyzer.stress import get_daily_stress
from oura_analyzer.vo2_max import get_vo2_max


@pytest.mark.parametrize(
    ("fetch", "endpoint"),
    [
        (get_daily_activity, "/v2/usercollection/daily_activity"),
        (get_daily_readiness, "/v2/usercollection/daily_readiness"),
        (get_daily_resilience, "/v2/usercollection/daily_resilience"),
        (get_daily_stress, "/v2/usercollection/daily_stress"),
        (get_vo2_max, "/v2/usercollection/vO2_max"),
        (get_daily_cardiovascular_age, "/v2/usercollection/daily_cardiovascular_age"),
        (get_daily_spo2, "/v2/usercollection/daily_spo2"),
        (get_sleep_periods, "/v2/usercollection/sleep"),
    ],
)
def test_daily_collection_fetches_all_pages_and_date_filters(fetch, endpoint: str) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.params.get("next_token") == "page-2":
            return httpx.Response(200, json={"data": [{"id": "second"}]})
        return httpx.Response(
            200,
            json={"data": [{"id": "first"}], "next_token": "page-2"},
        )

    with OuraAPIClient("test-token", transport=httpx.MockTransport(handler)) as client:
        rows = fetch(client, start_date="2026-10-01", end_date="2026-10-31")

    assert [row["id"] for row in rows] == ["first", "second"]
    assert requests[0].url.path == endpoint
    assert requests[0].url.params["start_date"] == "2026-10-01"
    assert requests[0].url.params["end_date"] == "2026-10-31"
    assert requests[1].url.params["next_token"] == "page-2"
