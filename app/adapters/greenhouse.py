"""
Adapter برای Greenhouse Job Board API.

مسئولیت این فایل فقط یک چیزه: گرفتن داده خام از Greenhouse و تبدیلش به
فرمت داخلی ما (OpportunityIngest). هیچ منطق تجاری (eligibility, matching,
ذخیره در دیتابیس) نباید اینجا باشه.
"""

import httpx

from app.schemas.opportunity import OpportunityIngest

GREENHOUSE_JOBS_URL = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"


class GreenhouseAPIError(Exception):
    """وقتی Greenhouse خطا برگردونه یا جواب به شکلی که انتظار داریم نباشه."""


def fetch_raw_jobs(board_token: str) -> list[dict]:
    url = GREENHOUSE_JOBS_URL.format(board_token=board_token)
    response = httpx.get(url, params={"content": "true"}, timeout=10)

    if response.status_code != 200:
        raise GreenhouseAPIError(
            f"Greenhouse returned {response.status_code} for board '{board_token}'"
        )

    data = response.json()
    jobs = data.get("jobs")
    if jobs is None:
        raise GreenhouseAPIError(f"Unexpected Greenhouse response shape: {data}")

    return jobs


def normalize_job(raw_job: dict, organization_name: str) -> OpportunityIngest:
    return OpportunityIngest(
        title=raw_job["title"],
        description=raw_job.get("content"),
        type="job",
        url=raw_job["absolute_url"],
        deadline=None,
        posted_at=raw_job.get("first_published"),
        organization_name=organization_name,
        external_id=str(raw_job["id"]),
        source="greenhouse",
    )


def fetch_opportunities(board_token: str, organization_name: str) -> list[OpportunityIngest]:
    raw_jobs = fetch_raw_jobs(board_token)
    return [normalize_job(job, organization_name) for job in raw_jobs]
