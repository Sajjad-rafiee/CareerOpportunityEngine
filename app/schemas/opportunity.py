"""Internal Opportunity schema, independent of any single source."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OpportunityBase(BaseModel):
    title: str
    description: str | None = None
    type: str = Field(..., description="job, phd, postdoc, etc")
    url: str
    deadline: date | None = None
    posted_at: datetime | None = None


class OpportunityIngest(OpportunityBase):
    """Adapter output before the record has a database organization_id."""

    organization_name: str
    external_id: str
    source: str


class OpportunityResponse(OpportunityBase):
    id: UUID
    organization_id: UUID
    organization_name: str
    external_id: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedOpportunities(BaseModel):
    items: list[OpportunityResponse]
    total: int
    limit: int
    offset: int


class OpportunitySearchResult(OpportunityResponse):
    score: float = Field(..., description="Cosine similarity to the query, 0-1, higher is closer")
