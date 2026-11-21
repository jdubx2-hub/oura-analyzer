from datetime import datetime

import httpx
import pytest

from oura_analyzer.client import OuraAPIClient
from oura_analyzer.heart_rate import get_heart_rate


def test_heart_rate_uses_datetime_filters_and_pagination() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.params.get("next_token") == "page-2":
            return httpx.Response(200, json={"data": [{"bpm": 72}]})
        return httpx.Response(
            200,
            json={"data": [{"bpm": 68}], "next_token": "page-2"},
        )

    with OuraAPIClient("test-token", transport=httpx.MockTransport(handler)) as client:
        rows = get_heart_rate(
            client,
            start_datetime=datetime.fromisoformat("2026-10-01T00:00:00-07:00"),
            end_datetime="2026-10-02T00:00:00-07:00",
        )

    assert [row["bpm"] for row in rows] == [68, 72]
    assert requests[0].url.path == "/v2/usercollection/heartrate"
    assert requests[0].url.params["start_datetime"] == "2026-10-01T00:00:00-07:00"
    assert requests[0].url.params["end_datetime"] == "2026-10-02T00:00:00-07:00"
    assert requests[1].url.params["next_token"] == "page-2"


def test_heart_rate_rejects_naive_datetime() -> None:
    with OuraAPIClient("test-token", transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"data": []}))) as client:
        with pytest.raises(ValueError, match="timezone offset"):
            get_heart_rate(
                client,
                start_datetime=datetime(2026, 10, 1),
                end_datetime=datetime.fromisoformat("2026-10-02T00:00:00-07:00"),
            )


def test_heart_rate_rejects_reversed_range() -> None:
    with OuraAPIClient("test-token", transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"data": []}))) as client:
        with pytest.raises(ValueError, match="after"):
            get_heart_rate(
                client,
                start_datetime="2026-10-02T00:00:00-07:00",
                end_datetime="2026-10-01T00:00:00-07:00",
            )
