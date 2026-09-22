"""Retry behavior for fetch_raw_jobs, no real network. httpx.get is
faked to control failures precisely; retry wait is zeroed so these
run instantly."""

import httpx
import pytest
from tenacity import wait_none

from app.adapters import greenhouse
from app.adapters.greenhouse import GreenhouseAPIError, fetch_raw_jobs


@pytest.fixture(autouse=True)
def _no_retry_wait():
    original_wait = greenhouse._get_jobs_page.retry.wait
    greenhouse._get_jobs_page.retry.wait = wait_none()
    yield
    greenhouse._get_jobs_page.retry.wait = original_wait


def make_response(status_code: int, json_body: dict | None = None) -> httpx.Response:
    request = httpx.Request("GET", "https://boards-api.greenhouse.io/v1/boards/test/jobs")
    return httpx.Response(status_code=status_code, json=json_body, request=request)


def test_retries_on_connection_error_then_succeeds(monkeypatch):
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ConnectError("boom", request=httpx.Request("GET", url))
        return make_response(200, {"jobs": [{"id": 1}]})

    monkeypatch.setattr(greenhouse.httpx, "get", fake_get)

    jobs = fetch_raw_jobs("test")

    assert jobs == [{"id": 1}]
    assert calls["count"] == 2


def test_gives_up_after_three_attempts_on_persistent_connection_error(monkeypatch):
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        calls["count"] += 1
        raise httpx.ConnectError("boom", request=httpx.Request("GET", url))

    monkeypatch.setattr(greenhouse.httpx, "get", fake_get)

    with pytest.raises(GreenhouseAPIError):
        fetch_raw_jobs("test")

    assert calls["count"] == 3


def test_retries_on_server_error(monkeypatch):
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        calls["count"] += 1
        if calls["count"] == 1:
            return make_response(503)
        return make_response(200, {"jobs": []})

    monkeypatch.setattr(greenhouse.httpx, "get", fake_get)

    jobs = fetch_raw_jobs("test")

    assert jobs == []
    assert calls["count"] == 2


def test_does_not_retry_on_client_error(monkeypatch):
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        calls["count"] += 1
        return make_response(404)

    monkeypatch.setattr(greenhouse.httpx, "get", fake_get)

    with pytest.raises(GreenhouseAPIError):
        fetch_raw_jobs("test")

    assert calls["count"] == 1
