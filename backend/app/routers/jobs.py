"""Job Intelligence API — parse, store, search, and manage job descriptions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.job.intelligence import JobIntelligence
from app.services.job.repository import JobRepository

router = APIRouter()

DEFAULT_USER_ID = "default"


class ParseJDRequest(BaseModel):
    raw_text: str = Field(..., min_length=20)


class SaveJDRequest(BaseModel):
    raw_text: str
    parsed_data: dict = {}
    title: str | None = None
    company: str | None = None
    tags: list[str] | None = None


class MatchRequest(BaseModel):
    candidate_profile: dict


# ── Parse ───────────────────────────────────────────────────

@router.post("/parse")
async def parse_job_description(request: ParseJDRequest):
    """Parse a raw job description into a structured profile using AI."""
    ji = JobIntelligence()
    profile = await ji.parse_job_description(request.raw_text)
    return {
        "status": "parsed",
        "profile": profile.to_dict(),
        "all_skills": list(profile.all_skills()),
    }


@router.post("/extract-requirements")
async def extract_requirements(request: ParseJDRequest):
    """Extract key requirements from a job description."""
    ji = JobIntelligence()
    requirements = await ji.extract_requirements(request.raw_text)
    return requirements


@router.post("/classify")
async def classify_job(request: ParseJDRequest):
    """Classify a job description."""
    ji = JobIntelligence()
    classification = await ji.classify_job(request.raw_text)
    return classification


@router.post("/match")
async def match_candidate(request: MatchRequest):
    """Match a candidate profile against a job profile."""
    ji = JobIntelligence()
    # This would need a job profile as input too
    return {"status": "not_implemented", "message": "Requires job_profile input"}


# ── CRUD ────────────────────────────────────────────────────

@router.post("/save")
async def save_job_description(request: SaveJDRequest, db: AsyncSession = Depends(get_db)):
    """Save a job description to the database."""
    repo = JobRepository(db, DEFAULT_USER_ID)
    ji = JobIntelligence()

    if not request.parsed_data:
        profile = await ji.parse_job_description(request.raw_text)
        parsed_data = profile.to_dict()
    else:
        parsed_data = request.parsed_data

    jd = await repo.save(
        raw_text=request.raw_text,
        parsed_data=parsed_data,
        title=request.title,
        company=request.company,
        tags=request.tags,
    )
    return {"id": jd.id, "title": jd.title, "company": jd.company}


@router.get("/")
async def list_jobs(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    company: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all job descriptions."""
    repo = JobRepository(db, DEFAULT_USER_ID)
    jds = await repo.list_all(limit=limit, offset=offset, company=company)
    return {
        "total": await repo.count(),
        "items": [
            {
                "id": jd.id,
                "title": jd.title,
                "company": jd.company,
                "created_at": str(jd.created_at) if jd.created_at else None,
                "keywords": jd.keywords or [],
            }
            for jd in jds
        ],
    }


@router.get("/stats")
async def job_stats(db: AsyncSession = Depends(get_db)):
    """Get job repository statistics."""
    repo = JobRepository(db, DEFAULT_USER_ID)
    return await repo.get_stats()


@router.get("/search")
async def search_jobs(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=20, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Search job descriptions."""
    repo = JobRepository(db, DEFAULT_USER_ID)
    results = await repo.search(q, limit=limit)
    return {
        "query": q,
        "total": len(results),
        "items": [
            {"id": jd.id, "title": jd.title, "company": jd.company}
            for jd in results
        ],
    }


@router.get("/{jd_id}")
async def get_job(jd_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific job description."""
    repo = JobRepository(db, DEFAULT_USER_ID)
    jd = await repo.get(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return {
        "id": jd.id,
        "title": jd.title,
        "company": jd.company,
        "raw_text": jd.raw_text,
        "parsed_json": jd.parsed_json,
        "keywords": jd.keywords,
        "requirements": jd.requirements,
        "created_at": str(jd.created_at) if jd.created_at else None,
    }


@router.delete("/{jd_id}")
async def delete_job(jd_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a job description."""
    repo = JobRepository(db, DEFAULT_USER_ID)
    if not await repo.delete(jd_id):
        raise HTTPException(status_code=404, detail="Job description not found")
    return {"status": "deleted"}


@router.post("/compare")
async def compare_jobs(jd_id_1: str, jd_id_2: str, db: AsyncSession = Depends(get_db)):
    """Compare two job descriptions."""
    repo = JobRepository(db, DEFAULT_USER_ID)
    return await repo.compare(jd_id_1, jd_id_2)
