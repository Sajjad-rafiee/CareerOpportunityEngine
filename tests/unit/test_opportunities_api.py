"""
تست endpoint لیست Opportunity ها.

از یک دیتابیس SQLite در حافظه استفاده می‌کنیم و dependency واقعی
get_db رو با نسخه‌ی تستی جایگزین می‌کنیم (app.dependency_overrides) —
الگوی رسمی خود FastAPI برای تست کردن endpoint هایی که به دیتابیس
وابسته‌ن، بدون نیاز به Postgres واقعی.
"""

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
    # StaticPool چون :memory: SQLite برای هر connection جدید یک دیتابیس
    # جدا و خالی می‌سازه؛ بدون این، درخواست HTTP یک دیتابیس متفاوت از
    # همونی که باهاش داده seed کردیم می‌بینه.
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
