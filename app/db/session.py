"""Engine and session factory for Postgres.

get_engine() is lazy so importing this module never requires .env
to be present (e.g. in CI, where unit tests use SQLite instead).
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url)


def SessionLocal() -> Session:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
