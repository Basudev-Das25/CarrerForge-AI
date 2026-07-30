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
    """Extract keywords from a job description using statistical + semantic analysis."""
    extractor = KeywordExtractor()
    result = extractor.extract(request.text)
    return result.to_dict()
