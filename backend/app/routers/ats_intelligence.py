"""ATS Intelligence API — analyze, optimize, compare, and report."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.db.models import ATSReport as ATSReportModel, ResumeVersion as ResumeVersionModel
from app.services.ats.engine import ATSEngine
from app.services.ats.types import ATSReport

router = APIRouter()

DEFAULT_USER_ID = "default"


class AnalyzeRequest(BaseModel):
    resume: dict
    job_profile: dict


class OptimizeRequest(BaseModel):
    resume: dict
    job_profile: dict
    target_score: float = Field(default=85.0, ge=0, le=100)
    max_iterations: int = Field(default=3, ge=1, le=10)


class CompareRequest(BaseModel):
    resume_a: dict
    resume_b: dict
    job_profile: dict | None = None


# ── Analysis ─────────────────────────────────────────────

@router.post("/analyze")
async def analyze_resume(request: AnalyzeRequest):
    """Run full ATS analysis on a resume."""
    engine = ATSEngine()
    report = await engine.analyze(request.resume, request.job_profile)
    return {"report": report.to_dict()}


@router.post("/analyze-version/{version_id}")
async def analyze_version(version_id: str, job_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """Analyze a stored resume version against a job."""
    result = await db.execute(
        select(ResumeVersionModel)
        .where(ResumeVersionModel.id == version_id, ResumeVersionModel.user_id == DEFAULT_USER_ID)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    content = version.content_json or {}
    resume = content.get("resume", {})
    job_profile = content.get("job_profile", {})

    engine = ATSEngine()
    report = await engine.analyze(resume, job_profile)

    # Store the report
    report_model = ATSReportModel(
        resume_version_id=version_id,
        score=report.overall_score,
        keyword_score=report.matched_keywords.__len__() / max(len(job_profile.get("keywords", [])), 1) * 100,
        impact_score=report.impact_score,
        readability_score=report.readability_score,
        coverage_score=report.semantic_score,
        report_json=report.to_dict(),
        suggestions=[s.get("description", "") for s in report.suggestions[:10]],
    )
    db.add(report_model)
    await db.flush()

    return {"report": report.to_dict(), "report_id": report_model.id}


# ── Optimization ─────────────────────────────────────────

@router.post("/optimize")
async def optimize_resume(request: OptimizeRequest):
    """Iteratively optimize a resume for ATS scoring."""
    engine = ATSEngine()

    # Initial analysis
    initial_report = await engine.analyze(request.resume, request.job_profile)

    # Optimize (AI-dependent — may fail if no provider available)
    try:
        optimized_resume, plan = await engine.optimize(
            resume=request.resume,
            job_profile=request.job_profile,
            report=initial_report,
            target_score=request.target_score,
            max_iterations=request.max_iterations,
        )

        # Final analysis
        final_report = await engine.analyze(optimized_resume, request.job_profile)
        plan.current_score = initial_report.overall_score

        return {
            "resume": optimized_resume,
            "plan": plan.to_dict(),
            "initial_score": initial_report.overall_score,
            "final_score": final_report.overall_score,
            "improvement": final_report.overall_score - initial_report.overall_score,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail="AI optimization failed")


# ── Comparison ───────────────────────────────────────────

@router.post("/compare")
async def compare_resumes(request: CompareRequest):
    """Compare two resume versions."""
    engine = ATSEngine()
    result = await engine.compare(request.resume_a, request.resume_b, request.job_profile)
    return {"comparison": result.to_dict()}


@router.post("/compare-versions")
async def compare_versions(v1: str, v2: str, db: AsyncSession = Depends(get_db)):
    """Compare two stored resume versions."""
    r1 = await db.execute(
        select(ResumeVersionModel)
        .where(ResumeVersionModel.id == v1, ResumeVersionModel.user_id == DEFAULT_USER_ID)
    )
    r2 = await db.execute(
        select(ResumeVersionModel)
        .where(ResumeVersionModel.id == v2, ResumeVersionModel.user_id == DEFAULT_USER_ID)
    )
    v1_model = r1.scalar_one_or_none()
    v2_model = r2.scalar_one_or_none()
    if not v1_model or not v2_model:
        raise HTTPException(status_code=404, detail="Version not found")

    resume_a = (v1_model.content_json or {}).get("resume", {})
    resume_b = (v2_model.content_json or {}).get("resume", {})
    job_profile = (v2_model.content_json or {}).get("job_profile", {})

    engine = ATSEngine()
    result = await engine.compare(resume_a, resume_b, job_profile)
    return {"comparison": result.to_dict()}


# ── Reports ──────────────────────────────────────────────

@router.get("/reports")
async def list_reports(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """List all ATS reports."""
    result = await db.execute(
        select(ATSReportModel).order_by(ATSReportModel.created_at.desc()).limit(limit)
    )
    reports = result.scalars().all()
    return {
        "total": len(reports),
        "reports": [
            {
                "id": r.id,
                "resume_version_id": r.resume_version_id,
                "score": r.score,
                "created_at": str(r.created_at) if r.created_at else None,
            }
            for r in reports
        ],
    }


@router.get("/reports/{report_id}")
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific ATS report."""
    result = await db.execute(select(ATSReportModel).where(ATSReportModel.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": report.id,
        "resume_version_id": report.resume_version_id,
        "score": report.score,
        "keyword_score": report.keyword_score,
        "formatting_score": report.formatting_score,
        "impact_score": report.impact_score,
        "readability_score": report.readability_score,
        "coverage_score": report.coverage_score,
        "report_json": report.report_json,
        "suggestions": report.suggestions,
        "created_at": str(report.created_at) if report.created_at else None,
    }


@router.post("/reports/{report_id}/export")
async def export_report(report_id: str, format: str = "json", db: AsyncSession = Depends(get_db)):
    """Export an ATS report as JSON or Markdown."""
    result = await db.execute(select(ATSReportModel).where(ATSReportModel.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if format == "markdown":
        md = _report_to_markdown(report)
        return {"markdown": md, "format": "markdown"}

    return {"json": report.report_json, "format": "json"}


def _report_to_markdown(report) -> str:
    """Convert an ATS report to Markdown."""
    data = report.report_json or {}
    lines = [
        f"# ATS Report",
        f"",
        f"**Score:** {report.score}/100",
        f"**Date:** {report.created_at}",
        f"",
        "## Scores",
        f"- Keyword: {report.keyword_score:.0f}",
        f"- Impact: {report.impact_score:.0f}",
        f"- Readability: {report.readability_score:.0f}",
        f"- Coverage: {report.coverage_score:.0f}",
        f"",
    ]

    if data.get("missing_keywords"):
        lines.append("## Missing Keywords")
        for kw in data["missing_keywords"][:10]:
            lines.append(f"- {kw}")
        lines.append("")

    if report.suggestions:
        lines.append("## Suggestions")
        for s in report.suggestions:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)
