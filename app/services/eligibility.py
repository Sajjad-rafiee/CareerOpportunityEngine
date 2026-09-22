"""
استخراج ساختاریافته‌ی اطلاعات واجد شرایط بودن از متن خام آگهی، با LLM.

مدل: Gemini (رایگان برای این حجم استفاده، کلید از aistudio.google.com).
خروجی با Pydantic constrain می‌شه (response_schema) پس خود Gemini
تضمین می‌کنه فرمت جواب درسته - دیگه لازم نیست خودمون JSON رو parse
و validate کنیم.
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

# flash-lite: کافیه برای استخراج چند فیلد ساده، و rate limit رایگانش
# خیلی بازتر از مدل flash کامله (که برای این حجم استفاده به سرعت پر شد).
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
    """وقتی GEMINI_API_KEY تنظیم نشده - خطای قابل‌فهم به‌جای کرش عجیب."""


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
    # ۵xx (خطای سرور گوگل): موقتیه.
    if isinstance(exc, ServerError):
        return True
    # ۴۲۹ (rate limit): دقیقاً همون خطاییه که retry با backoff برای طراحی
    # شده - برخلاف بقیه‌ی ۴xx (کلید نامعتبر، prompt رد شده) که تلاش
    # دوباره فایده‌ای نداره.
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
