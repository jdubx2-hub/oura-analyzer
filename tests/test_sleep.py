import httpx

from oura_analyzer.client import OuraAPIClient
from oura_analyzer.sleep import get_daily_sleep


def test_daily_sleep_fetches_all_pages_and_date_filters() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.params.get("next_token") == "page-2":
            return httpx.Response(200, json={"data": [{"day": "2026-10-02", "score": 81}]})
        return httpx.Response(
            200,
            json={
                "data": [{"day": "2026-10-01", "score": 78}],
                "next_token": "page-2",
            },
        )

    transport = httpx.MockTransport(handler)
    with OuraAPIClient("test-token", transport=transport) as client:
        rows = get_daily_sleep(
            client,
            start_date="2026-10-01",
            end_date="2026-10-31",
        )

    assert [row["day"] for row in rows] == ["2026-10-01", "2026-10-02"]
    assert requests[0].url.params["start_date"] == "2026-10-01"
    assert requests[0].url.params["end_date"] == "2026-10-31"
    assert requests[1].url.params["next_token"] == "page-2"
