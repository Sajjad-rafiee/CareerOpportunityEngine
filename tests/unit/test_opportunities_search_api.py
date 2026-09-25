"""Search endpoint routing/validation/response shape, with embed_text
and search_opportunities mocked - the real search logic has its own
integration test."""

import uuid
from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api import opportunities as opportunities_module
from app.core.config import Settings
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

    # The endpoint reads fault-mode settings; keep them independent of .env.
    monkeypatch.setattr(
        opportunities_module,
        "get_settings",
        lambda: Settings(
            postgres_db="test",
            postgres_user="test",
            postgres_password="test",
            otel_demo_fault_mode="none",
        ),
    )

    # search_opportunities is mocked so no real query runs, but the
    # real get_db would still try to build a Postgres engine without this.
    app.dependency_overrides[get_db] = lambda: iter([None])

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_search_returns_matches_with_similarity_score(client: TestClient) -> None:
    response = client.get("/opportunities/search", params={"q": "python developer"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Backend Engineer"
    assert body[0]["organization_name"] == "N26"
    assert body[0]["score"] == pytest.approx(0.87)


def test_search_requires_a_query(client: TestClient) -> None:
    response = client.get("/opportunities/search")

    assert response.status_code == 422
