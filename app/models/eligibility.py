import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity


class Eligibility(Base):
    """LLM-derived, kept separate from Opportunity so it can be
    recomputed later (better prompt/model) without touching source data."""

    __tablename__ = "eligibilities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("opportunities.id"), unique=True
    )

    offers_visa_sponsorship: Mapped[bool | None] = mapped_column(Boolean, default=None)
    german_language_required: Mapped[bool | None] = mapped_column(Boolean, default=None)
    experience_level: Mapped[str] = mapped_column(String(20))
    remote_friendly: Mapped[bool | None] = mapped_column(Boolean, default=None)
    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    opportunity: Mapped["Opportunity"] = relationship(back_populates="eligibility")
