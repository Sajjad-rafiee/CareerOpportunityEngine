"""
تست integration: واقعاً به Greenhouse وصل می‌شه.

با `pytest -m integration` جدا اجرا می‌شه چون به شبکه وابسته‌ست و کندتره.
اجرای معمولی pytest (بدون -m) این تست رو رد می‌کنه.
"""

import pytest

from app.adapters.greenhouse import fetch_opportunities

pytestmark = pytest.mark.integration


def test_fetch_opportunities_returns_real_n26_jobs():
    opportunities = fetch_opportunities(board_token="n26", organization_name="N26")

    assert len(opportunities) > 0
    first = opportunities[0]
    assert first.source == "greenhouse"
    assert first.organization_name == "N26"
    assert first.url.startswith("https://")
