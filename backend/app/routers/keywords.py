"""Keywords API — extract meaningful keywords from job descriptions."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.keywords.extractor import KeywordExtractor

router = APIRouter()


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=10000)


@router.post("/extract")
async def extract_keywords(request: ExtractRequest):
    """Extract grounded keywords from a job description.

    Uses LLM extraction when an AI provider is configured, otherwise
    falls back to KeyBERT semantic scoring. Every returned keyword is
    verified to appear verbatim in the job description.
    """
    extractor = KeywordExtractor()
    result = await extractor.extract_async(request.text)
    return result.to_dict()
