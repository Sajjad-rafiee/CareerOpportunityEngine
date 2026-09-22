"""Structured eligibility extraction from raw posting text via an LLM.

Model: Gemini. Output is constrained to a Pydantic schema
(response_schema), so we never parse/validate free-form JSON.
"""

import logging
from functools import lru_cache

from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError
from pydantic import BaseModel, Field
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# flash-lite: enough for this extraction, and its free-tier rate limit
# is far more workable than the full flash model.
MODEL_NAME = "gemini-3.5-flash-lite"


class EligibilityExtraction(BaseModel):
    offers_visa_sponsorship: bool | None = Field(
        None,
        description="Does the posting explicitly mention visa sponsorship or relocation support?",
    )
    german_language_required: bool | None = Field(
        None, description="Does the posting require German language proficiency?"
    )
    experience_level: str = Field(
        ..., description="One of: intern, entry, mid, senior, unspecified"
    )
    remote_friendly: bool | None = Field(
        None, description="Does the posting mention remote or hybrid work is allowed?"
    )


class GeminiConfigError(Exception):
    pass


@lru_cache
def _get_client() -> genai.Client:
    api_key = get_settings().gemini_api_key
    if not api_key:
        raise GeminiConfigError(
            "GEMINI_API_KEY is not set. Get a free key from https://aistudio.google.com/apikey "
            "and add it to .env"
        )
    return genai.Client(api_key=api_key)


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, ServerError):
        return True
    # 429 (rate limit) is exactly what backoff-retry is for, unlike
    # other 4xx (bad key, rejected prompt) which won't fix themselves.
    if isinstance(exc, ClientError) and exc.code == 429:
        return True
    return False


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception(_is_retryable),
    reraise=True,
)
def extract_eligibility(text: str) -> EligibilityExtraction:
    response = _get_client().models.generate_content(
        model=MODEL_NAME,
        contents=f"Extract eligibility information from this job posting:\n\n{text}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EligibilityExtraction,
        ),
    )

    result = response.parsed
    if not isinstance(result, EligibilityExtraction):
        raise ValueError(f"Gemini did not return a parsable EligibilityExtraction: {response.text}")

    return result
