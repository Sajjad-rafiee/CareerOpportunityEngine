"""
تست integration: واقعاً به Gemini وصل می‌شه و چک می‌کنه استخراج
منطقی جواب می‌ده. نیاز به GEMINI_API_KEY واقعی در .env داره.
"""

import pytest

from app.services.eligibility import extract_eligibility

pytestmark = pytest.mark.integration


def test_extracts_visa_sponsorship_and_german_requirement_correctly():
    text = (
        "Senior Backend Engineer at a Berlin fintech. We offer visa sponsorship "
        "and relocation support for international candidates. Fluent German is "
        "NOT required; the team works in English. 5+ years of experience needed. "
        "This role is fully remote-friendly."
    )

    result = extract_eligibility(text)

    assert result.offers_visa_sponsorship is True
    assert result.german_language_required is False
    assert result.remote_friendly is True
    assert result.experience_level in {"mid", "senior"}
