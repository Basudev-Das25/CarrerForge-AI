"""Pydantic schemas for all CareerForge AI entities.

These schemas handle request validation, response serialization,
and database model conversion.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ── Base ────────────────────────────────────────────────────

class OrmModel(BaseModel):
    """Base schema that reads from ORM attributes."""
    model_config = ConfigDict(from_attributes=True)


# ── User / Profile ──────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    summary: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    summary: str | None = None


class UserResponse(OrmModel):
    id: str
    full_name: str | None
    email: str | None
    phone: str | None
    location: str | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
    summary: str | None
    created_at: datetime
    updated_at: datetime


# ── Education ───────────────────────────────────────────────

class EducationCreate(BaseModel):
    degree: str = Field(..., min_length=1, max_length=255)
    field_of_study: str | None = None
    institution: str = Field(..., min_length=1, max_length=255)
    location: str | None = None
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    gpa: float | None = Field(None, ge=0, le=4.0)
    description: str | None = None
    highlights: list[str] = []


class EducationUpdate(BaseModel):
    degree: str | None = Field(None, min_length=1, max_length=255)
    field_of_study: str | None = None
    institution: str | None = Field(None, min_length=1, max_length=255)
    location: str | None = None
    start_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    gpa: float | None = Field(None, ge=0, le=4.0)
    description: str | None = None
    highlights: list[str] | None = None


class EducationResponse(OrmModel):
    id: str
    user_id: str
    degree: str
    field_of_study: str | None
    institution: str
    location: str | None
    start_date: str
    end_date: str | None
    gpa: float | None
    description: str | None
    highlights: list[str]


# ── Experience ──────────────────────────────────────────────

class ExperienceCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    location: str | None = None
    employment_type: str | None = Field(None, pattern=r"^(full-time|part-time|contract|internship|freelance)$")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    description: str | None = None
    highlights: list[str] = []
    skills_used: list[str] = []


class ExperienceUpdate(BaseModel):
    company: str | None = Field(None, min_length=1, max_length=255)
    title: str | None = Field(None, min_length=1, max_length=255)
    location: str | None = None
    employment_type: str | None = Field(None, pattern=r"^(full-time|part-time|contract|internship|freelance)$")
    start_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    description: str | None = None
    highlights: list[str] | None = None
    skills_used: list[str] | None = None


class ExperienceResponse(OrmModel):
    id: str
    user_id: str
    company: str
    title: str
    location: str | None
    employment_type: str | None
    start_date: str
    end_date: str | None
    description: str | None
    highlights: list[str]
    skills_used: list[str]


# ── Project ─────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    repo_url: str | None = None
    live_url: str | None = None
    tech_stack: list[str] = []
    highlights: list[str] = []
    start_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    is_featured: bool = False


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    repo_url: str | None = None
    live_url: str | None = None
    tech_stack: list[str] | None = None
    highlights: list[str] | None = None
    start_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    is_featured: bool | None = None


class ProjectResponse(OrmModel):
    id: str
    user_id: str
    name: str
    description: str | None
    repo_url: str | None
    live_url: str | None
    tech_stack: list[str]
    highlights: list[str]
    start_date: str | None
    end_date: str | None
    is_featured: bool


# ── Skill ───────────────────────────────────────────────────

class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str | None = Field(None, pattern=r"^(programming|framework|tool|soft|domain)$")
    level: str | None = Field(None, pattern=r"^(beginner|intermediate|advanced|expert)$")
    years_experience: float | None = Field(None, ge=0)
    is_primary: bool = False


class SkillUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, pattern=r"^(programming|framework|tool|soft|domain)$")
    level: str | None = Field(None, pattern=r"^(beginner|intermediate|advanced|expert)$")
    years_experience: float | None = Field(None, ge=0)
    is_primary: bool | None = None


class SkillResponse(OrmModel):
    id: str
    user_id: str
    name: str
    category: str | None
    level: str | None
    years_experience: float | None
    is_primary: bool


# ── Certificate ─────────────────────────────────────────────

class CertificateCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    issuer: str = Field(..., min_length=1, max_length=255)
    issue_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    expiry_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    credential_id: str | None = None
    credential_url: str | None = None
    skills: list[str] = []


class CertificateUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    issuer: str | None = Field(None, min_length=1, max_length=255)
    issue_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    expiry_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    credential_id: str | None = None
    credential_url: str | None = None
    skills: list[str] | None = None


class CertificateResponse(OrmModel):
    id: str
    user_id: str
    title: str
    issuer: str
    issue_date: str | None
    expiry_date: str | None
    credential_id: str | None
    credential_url: str | None
    skills: list[str]


# ── Achievement ─────────────────────────────────────────────

class AchievementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    category: str | None = Field(None, pattern=r"^(award|publication|patent|speaking|other)$")
    organization: str | None = None
    url: str | None = None


class AchievementUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    date: str | None = Field(None, pattern=r"^\d{4}-\d{2}(-\d{2})?$")
    category: str | None = Field(None, pattern=r"^(award|publication|patent|speaking|other)$")
    organization: str | None = None
    url: str | None = None


class AchievementResponse(OrmModel):
    id: str
    user_id: str
    title: str
    description: str | None
    date: str | None
    category: str | None
    organization: str | None
    url: str | None


# ── Document ────────────────────────────────────────────────

class DocumentResponse(OrmModel):
    id: str
    file_path: str
    original_name: str
    mime_type: str | None
    file_size: int | None
    category: str | None
    ocr_performed: bool
    embedding_ids: list[str]
    created_at: datetime


# ── Resume ──────────────────────────────────────────────────

class ResumeGenerateRequest(BaseModel):
    job_description: str = Field(..., min_length=10)
    template_name: str | None = None
    max_iterations: int = Field(default=5, ge=1, le=10)


class ResumeVersionResponse(OrmModel):
    id: str
    user_id: str
    title: str
    template_name: str | None
    ats_score: float | None
    reflection_iterations: int
    is_final: bool
    created_at: datetime


# ── Dashboard ───────────────────────────────────────────────

class DashboardData(BaseModel):
    profile: UserResponse | None
    total_experiences: int = 0
    total_projects: int = 0
    total_skills: int = 0
    total_documents: int = 0
    total_resumes: int = 0
    recent_documents: list[DocumentResponse] = []
    recent_resumes: list[ResumeVersionResponse] = []
    profile_completion: float = 0.0
