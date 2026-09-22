"""Greenhouse Job Board adapter.

Fetches raw postings and normalizes them into OpportunityIngest.
No business logic (eligibility, matching, persistence) belongs here.
"""

import logging

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.schemas.opportunity import OpportunityIngest

logger = logging.getLogger(__name__)

GREENHOUSE_JOBS_URL = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"


class GreenhouseAPIError(Exception):
    pass


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        # 5xx is transient; 4xx (bad board token, etc.) won't fix itself.
        return exc.response.status_code >= 500
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception(_is_retryable),
    reraise=True,
)
def _get_jobs_page(board_token: str) -> httpx.Response:
    url = GREENHOUSE_JOBS_URL.format(board_token=board_token)
    response = httpx.get(url, params={"content": "true"}, timeout=10)
    response.raise_for_status()
    return response


def fetch_raw_jobs(board_token: str) -> list[dict]:
    try:
        response = _get_jobs_page(board_token)
    except httpx.HTTPStatusError as exc:
        raise GreenhouseAPIError(
            f"Greenhouse returned {exc.response.status_code} for board '{board_token}'"
        ) from exc
    except httpx.TransportError as exc:
        raise GreenhouseAPIError(
            f"Network error calling Greenhouse for board '{board_token}': {exc}"
        ) from exc

    data = response.json()
    jobs = data.get("jobs")
    if jobs is None:
        raise GreenhouseAPIError(f"Unexpected Greenhouse response shape: {data}")

    logger.info("Fetched %d raw jobs from Greenhouse board '%s'", len(jobs), board_token)
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
