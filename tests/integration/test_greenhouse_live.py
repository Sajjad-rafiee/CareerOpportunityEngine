"""Hits the real Greenhouse API. Opt-in via `pytest -m integration`."""

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
