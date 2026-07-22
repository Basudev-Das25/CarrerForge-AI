"""ATS analysis router."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ATSAnalysisRequest(BaseModel):
    resume_id: str
    job_description: str | None = None


@router.post("/analyze")
async def analyze_resume(request: ATSAnalysisRequest):
    # TODO: Implement ATS evaluation
    # 1. Parse resume PDF/text into structured sections
    # 2. Evaluate keywords, formatting, impact, readability
    # 3. Generate scoring report with suggestions
    return {"status": "not_implemented", "message": "Phase 3 feature"}


@router.get("/{report_id}")
async def get_report(report_id: str):
    return {"id": report_id, "status": "not_implemented"}
