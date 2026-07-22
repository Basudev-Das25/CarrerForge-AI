"""Agents API — execute AI agents for specific tasks."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.agents.job_parser import JobParserAgent
from app.services.agents.skill_extraction import SkillExtractionAgent
from app.services.agents.keyword import KeywordAgent
from app.services.agents.resume_planner import ResumePlannerAgent
from app.services.agents.resume_writer import ResumeWriterAgent
from app.services.agents.resume_reviewer import ResumeReviewerAgent
from app.services.agents.ats_evaluator import ATSEvaluatorAgent
from app.services.agents.reflection import ReflectionAgent
from app.services.agents.cover_letter import CoverLetterAgent
from app.services.agents.interview import InterviewAgent

router = APIRouter()


class JobParseRequest(BaseModel):
    job_description: str = Field(..., min_length=20)


class SkillExtractRequest(BaseModel):
    text: str
    context: str = ""


class KeywordRequest(BaseModel):
    job_description: str


class ResumePlanRequest(BaseModel):
    job_profile_json: str
    evidence_bundle_json: str
    template_style: str = "modern-professional"


class ResumeWriteRequest(BaseModel):
    section_name: str
    tone: str = "professional"
    word_count_target: int = 100
    key_themes: list[str] = []
    evidence_json: str = "[]"
    section_instructions: str = ""


class ResumeReviewRequest(BaseModel):
    resume_text: str
    job_description: str


class ATSRequest(BaseModel):
    resume_text: str
    job_description: str
    ats_keywords: list[str] = []


class ReflectionRequest(BaseModel):
    current_resume: str
    feedback_json: str = "{}"
    target_keywords: list[str] = []
    improvement_focus: str = "overall"


class CoverLetterRequest(BaseModel):
    candidate_name: str
    candidate_summary: str
    key_skills: list[str] = []
    achievements: list[str] = []
    job_title: str
    company: str
    requirements: list[str] = []


class InterviewRequest(BaseModel):
    job_title: str
    company: str
    required_skills: list[str] = []
    candidate_summary: str
    achievements: list[str] = []


# ── Agent Execution Endpoints ───────────────────────────────

@router.post("/job-parser")
async def execute_job_parser(request: JobParseRequest):
    """Parse a job description into structured data."""
    agent = JobParserAgent()
    result = await agent.execute(job_description=request.job_description)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/skill-extraction")
async def execute_skill_extraction(request: SkillExtractRequest):
    """Extract skills from text."""
    agent = SkillExtractionAgent()
    result = await agent.execute(text=request.text, context=request.context)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/keywords")
async def execute_keyword(request: KeywordRequest):
    """Extract ATS keywords from a job description."""
    agent = KeywordAgent()
    result = await agent.execute(job_description=request.job_description)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/resume-planner")
async def execute_resume_planner(request: ResumePlanRequest):
    """Plan resume structure."""
    agent = ResumePlannerAgent()
    result = await agent.execute(
        job_profile_json=request.job_profile_json,
        evidence_bundle_json=request.evidence_bundle_json,
        template_style=request.template_style,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/resume-writer")
async def execute_resume_writer(request: ResumeWriteRequest):
    """Write a resume section."""
    agent = ResumeWriterAgent()
    result = await agent.execute(
        section_name=request.section_name,
        tone=request.tone,
        word_count_target=request.word_count_target,
        key_themes=request.key_themes,
        evidence_json=request.evidence_json,
        section_instructions=request.section_instructions,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/resume-reviewer")
async def execute_resume_reviewer(request: ResumeReviewRequest):
    """Review and critique a resume."""
    agent = ResumeReviewerAgent()
    result = await agent.execute(
        resume_text=request.resume_text,
        job_description=request.job_description,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/ats-evaluator")
async def execute_ats_evaluator(request: ATSRequest):
    """Evaluate resume ATS compatibility."""
    agent = ATSEvaluatorAgent()
    result = await agent.execute(
        resume_text=request.resume_text,
        job_description=request.job_description,
        ats_keywords=request.ats_keywords,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/reflection")
async def execute_reflection(request: ReflectionRequest):
    """Improve resume based on feedback."""
    agent = ReflectionAgent()
    result = await agent.execute(
        current_resume=request.current_resume,
        feedback_json=request.feedback_json,
        target_keywords=request.target_keywords,
        improvement_focus=request.improvement_focus,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/cover-letter")
async def execute_cover_letter(request: CoverLetterRequest):
    """Generate a cover letter."""
    agent = CoverLetterAgent()
    result = await agent.execute(
        candidate_name=request.candidate_name,
        candidate_summary=request.candidate_summary,
        key_skills=request.key_skills,
        achievements=request.achievements,
        job_title=request.job_title,
        company=request.company,
        requirements=request.requirements,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


@router.post("/interview")
async def execute_interview_prep(request: InterviewRequest):
    """Prepare interview questions and talking points."""
    agent = InterviewAgent()
    result = await agent.execute(
        job_title=request.job_title,
        company=request.company,
        required_skills=request.required_skills,
        candidate_summary=request.candidate_summary,
        achievements=request.achievements,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.to_dict()


# ── Health ──────────────────────────────────────────────────

@router.get("/health")
async def agents_health():
    """Check health of all agents."""
    agents = [
        JobParserAgent(), SkillExtractionAgent(), KeywordAgent(),
        ResumePlannerAgent(), ResumeWriterAgent(), ResumeReviewerAgent(),
        ATSEvaluatorAgent(), ReflectionAgent(), CoverLetterAgent(),
        InterviewAgent(),
    ]
    results = {}
    for agent in agents:
        results[agent.name] = await agent.health()
    return results
