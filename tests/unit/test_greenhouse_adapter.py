"""normalize_job logic, no network. fetch_raw_jobs has its own
integration test (tests/integration/test_greenhouse_live.py)."""

from app.adapters.greenhouse import normalize_job
from app.schemas.opportunity import OpportunityIngest


def make_raw_job(**overrides) -> dict:
    raw_job = {
        "id": 8556658002,
        "title": "AI Engineer",
        "absolute_url": "https://job-boards.greenhouse.io/n26/jobs/8556658002",
        "content": "<p>Some job description</p>",
        "first_published": "2026-05-22T09:16:29-04:00",
    }
    raw_job.update(overrides)
    return raw_job


def test_normalize_job_maps_fields_correctly():
    raw_job = make_raw_job()

    result = normalize_job(raw_job, organization_name="N26")

    assert isinstance(result, OpportunityIngest)
    assert result.title == "AI Engineer"
    assert result.url == "https://job-boards.greenhouse.io/n26/jobs/8556658002"
    assert result.organization_name == "N26"
    assert result.external_id == "8556658002"
    assert result.source == "greenhouse"
    assert result.type == "job"


def test_normalize_job_handles_missing_content():
    raw_job = make_raw_job()
    del raw_job["content"]

    result = normalize_job(raw_job, organization_name="N26")

    assert result.description is None


def test_normalize_job_converts_id_to_string():
    raw_job = make_raw_job(id=123)

    result = normalize_job(raw_job, organization_name="N26")

    assert result.external_id == "123"
    assert isinstance(result.external_id, str)
