"""Opportunity list endpoint, backed by SQLite via FastAPI's
dependency_overrides instead of real Postgres."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Opportunity, Organization


@pytest.fixture
def client() -> Iterator[TestClient]:
    # StaticPool: :memory: SQLite gives each new connection a separate
    # empty database, so without this the HTTP request would see a
    # different database than the one we seeded.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db() -> Iterator[object]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestingSessionLocal() as db:
        organization = Organization(name="N26")
        db.add(organization)
        db.flush()
        for i in range(3):
            db.add(
                Opportunity(
                    organization_id=organization.id,
                    title=f"Job {i}",
                    type="job",
                    url=f"https://example.com/jobs/{i}",
                    external_id=str(i),
                    source="greenhouse",
                )
            )
        db.commit()

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_lists_opportunities_with_organization_name(client: TestClient) -> None:
    response = client.get("/opportunities", params={"limit": 2, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["items"][0]["organization_name"] == "N26"


def test_respects_offset_for_the_next_page(client: TestClient) -> None:
    response = client.get("/opportunities", params={"limit": 2, "offset": 2})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_rejects_limit_above_the_allowed_maximum(client: TestClient) -> None:
    response = client.get("/opportunities", params={"limit": 1000})

    assert response.status_code == 422
