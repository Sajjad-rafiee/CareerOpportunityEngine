"""Local-only fault injection for the observability demo (OTEL_DEMO_FAULT_MODE).

Off by default; requires explicit env configuration; never touches the
public request/response contract when disabled."""

import uuid
from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api import opportunities as opportunities_module
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.main import app
from app.models.opportunity import Opportunity
from app.models.organization import Organization


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    fake_opportunity = Opportunity(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Backend Engineer",
        description=None,
        type="job",
        url="https://example.com/jobs/1",
        deadline=None,
        posted_at=None,
        created_at=datetime.now(),
        external_id="1",
        source="greenhouse",
    )
    fake_opportunity.organization = Organization(id=uuid.uuid4(), name="N26")

    monkeypatch.setattr(opportunities_module, "embed_text", lambda text: [0.0] * 384)
    monkeypatch.setattr(
        opportunities_module,
        "search_opportunities",
        lambda db, query_embedding, limit: [(fake_opportunity, 0.87)],
    )
    app.dependency_overrides[get_db] = lambda: iter([None])

    yield TestClient(app)

    app.dependency_overrides.clear()


def _settings_with_fault_mode(mode: str) -> Settings:
    return Settings(
        postgres_db="test",
        postgres_user="test",
        postgres_password="test",
        otel_demo_fault_mode=mode,
    )


def test_fault_mode_defaults_to_none():
    assert (
        Settings(postgres_db="t", postgres_user="t", postgres_password="t").otel_demo_fault_mode
        == "none"
    )


def test_disabled_by_default_search_behaves_normally(client: TestClient, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.delenv("OTEL_DEMO_FAULT_MODE", raising=False)
    # No otel_demo_fault_mode and no .env, so the real default applies.
    monkeypatch.setattr(
        opportunities_module,
        "get_settings",
        lambda: Settings(
            postgres_db="test", postgres_user="test", postgres_password="test", _env_file=None
        ),
    )

    response = client.get("/opportunities/search", params={"q": "engineer"})

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_error_mode_returns_503_without_searching(client: TestClient, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setattr(
        opportunities_module, "get_settings", lambda: _settings_with_fault_mode("error")
    )
    called = []
    monkeypatch.setattr(
        opportunities_module,
        "search_opportunities",
        lambda db, query_embedding, limit: called.append(True) or [],
    )

    response = client.get("/opportunities/search", params={"q": "engineer"})

    assert response.status_code == 503
    assert called == []


def test_delay_mode_sleeps_before_searching(client: TestClient, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setattr(
        opportunities_module, "get_settings", lambda: _settings_with_fault_mode("delay")
    )
    sleep_calls = []
    monkeypatch.setattr(
        opportunities_module.time, "sleep", lambda seconds: sleep_calls.append(seconds)
    )

    response = client.get("/opportunities/search", params={"q": "engineer"})

    assert response.status_code == 200
    assert sleep_calls == [opportunities_module._DEMO_FAULT_DELAY_SECONDS]


def test_none_mode_does_not_sleep_or_error(client: TestClient, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setattr(
        opportunities_module, "get_settings", lambda: _settings_with_fault_mode("none")
    )
    sleep_calls = []
    monkeypatch.setattr(
        opportunities_module.time, "sleep", lambda seconds: sleep_calls.append(seconds)
    )

    response = client.get("/opportunities/search", params={"q": "engineer"})

    assert response.status_code == 200
    assert sleep_calls == []
