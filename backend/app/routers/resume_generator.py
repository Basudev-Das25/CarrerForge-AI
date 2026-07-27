"""Resume Generation API — blueprint, generate, validate, templates, versions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.db.models import ResumeVersion as ResumeVersionModel
from app.services.resume.pipeline import ResumePipeline
from app.services.resume.validator import ResumeValidator
from app.services.templates.engine import TemplateEngine

router = APIRouter()
DEFAULT_USER_ID = "default"


class GenerateRequest(BaseModel):
    job_description: str = Field(..., min_length=20)
    template: str = "modern"
    max_iterations: int = Field(default=3, ge=1, le=10)


class BlueprintRequest(BaseModel):
    job_description: str = Field(..., min_length=20)


class ValidateRequest(BaseModel):
    resume: dict
    target_keywords: list[str] = []


# ── Blueprint ───────────────────────────────────────────────

@router.post("/blueprint")
async def generate_blueprint(
    request: BlueprintRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a resume blueprint (planning phase)."""
    pipeline = ResumePipeline(session=db, user_id=DEFAULT_USER_ID)
    result = await pipeline.generate_blueprint(request.job_description)
    return {"blueprint": result}


# ── Generate ────────────────────────────────────────────────

@router.post("/generate")
async def generate_resume(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute the full resume generation pipeline."""
    pipeline = ResumePipeline(session=db, user_id=DEFAULT_USER_ID)
    result = await pipeline.generate(
        job_description=request.job_description,
        template=request.template,
        max_iterations=request.max_iterations,
    )
    return result


# ── Validate ────────────────────────────────────────────────

@router.post("/validate")
async def validate_resume(request: ValidateRequest):
    """Validate a canonical resume."""
    validator = ResumeValidator(target_keywords=request.target_keywords)
    report = validator.validate(request.resume)
    return {"validation": report.to_dict()}


# ── Templates ───────────────────────────────────────────────

@router.get("/templates")
async def list_templates():
    """List all available resume templates."""
    engine = TemplateEngine()
    return {"templates": [t.to_dict() for t in engine.list_templates()]}


@router.get("/templates/{name}")
async def get_template(name: str):
    """Get a specific template."""
    engine = TemplateEngine()
    info = engine.get_template(name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Template '{name}' not found")
    typst = engine.get_typst_source(name)
    return {"info": info.to_dict(), "typst": typst}


@router.post("/templates/{name}/render")
async def render_template(name: str, resume: dict):
    """Render a resume to Typst using a template."""
    engine = TemplateEngine()
    try:
        typst = engine.render_to_typst(resume, name)
        return {"typst": typst, "template": name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Render failed: {e}")


# ── Version History ─────────────────────────────────────────

@router.get("/versions")
async def list_versions(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all resume versions."""
    result = await db.execute(
        select(ResumeVersionModel)
        .where(ResumeVersionModel.user_id == DEFAULT_USER_ID)
        .order_by(ResumeVersionModel.created_at.desc())
        .offset(offset).limit(limit)
    )
    versions = result.scalars().all()
    return {
        "total": len(versions),
        "versions": [
            {
                "id": v.id,
                "title": v.title,
                "template_name": v.template_name,
                "ats_score": v.ats_score,
                "created_at": str(v.created_at) if v.created_at else None,
            }
            for v in versions
        ],
    }


@router.get("/versions/{version_id}")
async def get_version(version_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific resume version."""
    result = await db.execute(
        select(ResumeVersionModel)
        .where(ResumeVersionModel.id == version_id, ResumeVersionModel.user_id == DEFAULT_USER_ID)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {
        "id": version.id,
        "title": version.title,
        "template_name": version.template_name,
        "content_json": version.content_json,
        "ats_score": version.ats_score,
        "reflection_iterations": version.reflection_iterations,
        "is_final": version.is_final,
        "created_at": str(version.created_at) if version.created_at else None,
    }


@router.delete("/versions/{version_id}", status_code=204)
async def delete_version(version_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a resume version."""
    result = await db.execute(
        select(ResumeVersionModel)
        .where(ResumeVersionModel.id == version_id, ResumeVersionModel.user_id == DEFAULT_USER_ID)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    await db.delete(version)


@router.post("/versions/compare")
async def compare_versions(v1: str, v2: str, db: AsyncSession = Depends(get_db)):
    """Compare two resume versions."""
    r1 = await db.execute(
        select(ResumeVersionModel).where(ResumeVersionModel.id == v1, ResumeVersionModel.user_id == DEFAULT_USER_ID)
    )
    r2 = await db.execute(
        select(ResumeVersionModel).where(ResumeVersionModel.id == v2, ResumeVersionModel.user_id == DEFAULT_USER_ID)
    )
    v1_model = r1.scalar_one_or_none()
    v2_model = r2.scalar_one_or_none()
    if not v1_model or not v2_model:
        raise HTTPException(status_code=404, detail="Version not found")

    return {
        "v1": {"id": v1_model.id, "title": v1_model.title, "ats_score": v1_model.ats_score},
        "v2": {"id": v2_model.id, "title": v2_model.title, "ats_score": v2_model.ats_score},
        "score_change": (v2_model.ats_score or 0) - (v1_model.ats_score or 0),
    }


# ── Export ──────────────────────────────────────────────────

@router.post("/export/typst")
async def export_typst(resume: dict, template: str = "modern"):
    """Export resume as Typst source."""
    engine = TemplateEngine()
    typst = engine.render_to_typst(resume, template)
    return {"typst": typst, "format": "typst"}


@router.post("/export/text")
async def export_text(resume: dict):
    """Export resume as plain text."""
    engine = TemplateEngine()
    text = engine.render_to_text(resume)
    return {"text": text, "format": "text"}


@router.post("/export/markdown")
async def export_markdown(resume: dict):
    """Export resume as Markdown."""
    engine = TemplateEngine()
    md = engine.render_to_markdown(resume)
    return {"markdown": md, "format": "markdown"}


@router.post("/compile")
async def compile_resume(resume: dict, template: str = "modern"):
    """Compile resume to PDF via Typst."""
    engine = TemplateEngine()
    typst = engine.render_to_typst(resume, template)
    result = engine.compile_typst(typst)
    return {"compile": result.to_dict(), "typst": typst}


@router.post("/validate-typst")
async def validate_typst(resume: dict, template: str = "modern"):
    """Validate the generated Typst source for syntax errors."""
    engine = TemplateEngine()
    typst = engine.render_to_typst(resume, template)
    errors = engine.validate_typst(typst)
    return {"valid": len(errors) == 0, "errors": errors, "typst": typst}


@router.get("/themes/{name}")
async def get_template_theme(name: str):
    """Get the theme configuration for a template."""
    engine = TemplateEngine()
    theme = engine.get_theme(name)
    if not theme:
        raise HTTPException(status_code=404, detail=f"Theme not found for template '{name}'")
    return {"template": name, "theme": theme}
