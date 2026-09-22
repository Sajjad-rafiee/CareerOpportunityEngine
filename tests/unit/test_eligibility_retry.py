"""
تست رفتار retry برای extract_eligibility، بدون تماس واقعی با Gemini.

این تست‌ها دقیقاً همون باگی رو پوشش می‌دن که در استفاده‌ی واقعی پیدا شد:
خطای ۴۲۹ (rate limit) باید retry بشه، نه این‌که مثل بقیه‌ی خطاهای ۴xx
بلافاصله fail بشه.
"""

from typing import Any

import pytest
from google.genai.errors import ClientError, ServerError
from tenacity import wait_none

from app.services import eligibility as eligibility_module
from app.services.eligibility import EligibilityExtraction, extract_eligibility


class FakeResponse:
    def __init__(self, parsed: EligibilityExtraction):
        self.parsed = parsed
        self.text = "n/a"


class FakeModels:
    def __init__(self, effects: list[Any]):
        self._effects = list(effects)
        self.call_count = 0

    def generate_content(self, **kwargs: Any) -> FakeResponse:
        self.call_count += 1
        effect = self._effects.pop(0)
        if isinstance(effect, Exception):
            raise effect
        return FakeResponse(effect)


class FakeClient:
    def __init__(self, effects: list[Any]):
        self.models = FakeModels(effects)


@pytest.fixture(autouse=True)
def _no_retry_wait():
    original_wait = extract_eligibility.retry.wait
    extract_eligibility.retry.wait = wait_none()
    yield
    extract_eligibility.retry.wait = original_wait


def make_client_error(code: int) -> ClientError:
    return ClientError(code, {"error": {"code": code, "message": "boom", "status": "TEST"}})


def make_server_error() -> ServerError:
    return ServerError(500, {"error": {"code": 500, "message": "boom", "status": "INTERNAL"}})


def test_retries_on_rate_limit_then_succeeds(monkeypatch: pytest.MonkeyPatch):
    expected = EligibilityExtraction(experience_level="mid")
    fake_client = FakeClient([make_client_error(429), expected])
    monkeypatch.setattr(eligibility_module, "_get_client", lambda: fake_client)

    result = extract_eligibility("some job posting text")

    assert result == expected
    assert fake_client.models.call_count == 2


def test_does_not_retry_on_non_rate_limit_client_errors(monkeypatch: pytest.MonkeyPatch):
    fake_client = FakeClient([make_client_error(400)])
    monkeypatch.setattr(eligibility_module, "_get_client", lambda: fake_client)

    with pytest.raises(ClientError):
        extract_eligibility("some job posting text")

    assert fake_client.models.call_count == 1


def test_retries_on_server_error(monkeypatch: pytest.MonkeyPatch):
    expected = EligibilityExtraction(experience_level="senior")
    fake_client = FakeClient([make_server_error(), expected])
    monkeypatch.setattr(eligibility_module, "_get_client", lambda: fake_client)

    result = extract_eligibility("some job posting text")

    assert result == expected
    assert fake_client.models.call_count == 2
