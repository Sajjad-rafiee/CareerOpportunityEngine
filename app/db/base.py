"""Base class for all SQLAlchemy models.

Kept separate from session.py so Alembic can import Base.metadata
for autogenerate without needing a live engine.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
