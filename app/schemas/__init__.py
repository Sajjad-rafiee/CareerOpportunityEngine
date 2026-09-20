"""
Pydantic schemas for data validation and serialization.

این پوشه شامل schema های مختلف است:
- greenhouse.py: Schema برای داده‌های Greenhouse API
- opportunity.py: Schema داخلی برای Opportunity (مستقل از منبع)
"""

from app.schemas.opportunity import OpportunityCreate, OpportunityResponse

__all__ = ["OpportunityCreate", "OpportunityResponse"]
