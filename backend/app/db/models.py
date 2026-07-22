"""SQLAlchemy ORM models for CareerForge AI."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime,
    ForeignKey, JSON, Boolean,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


def utcnow():
    return datetime.utcnow()


# ── User ────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    github_url = Column(String(512), nullable=True)
    portfolio_url = Column(String(512), nullable=True)
    summary = Column(Text, nullable=True)
    avatar_path = Column(String(512), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    languages = relationship("Language", back_populates="user", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="user", cascade="all, delete-orphan")
    awards = relationship("Award", back_populates="user", cascade="all, delete-orphan")
    social_links = relationship("SocialLink", back_populates="user", cascade="all, delete-orphan")
    resume_versions = relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    profile_versions = relationship("ProfileVersion", back_populates="user", cascade="all, delete-orphan")


# ── Profile Version History ─────────────────────────────────

class ProfileVersion(Base):
    __tablename__ = "profile_versions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    snapshot_json = Column(JSON, nullable=False)
    change_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="profile_versions")


# ── Education ───────────────────────────────────────────────

class Education(Base):
    __tablename__ = "education"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    institution = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=True)
    gpa = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    highlights = Column(JSON, default=list)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="education")


# ── Experience ──────────────────────────────────────────────

class Experience(Base):
    __tablename__ = "experience"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    employment_type = Column(String(50), nullable=True)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    highlights = Column(JSON, default=list)
    skills_used = Column(JSON, default=list)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="experience")


# ── Project ─────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    role = Column(String(255), nullable=True)
    repo_url = Column(String(512), nullable=True)
    live_url = Column(String(512), nullable=True)
    tech_stack = Column(JSON, default=list)
    industry = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    images = Column(JSON, default=list)
    team_size = Column(Integer, nullable=True)
    impact_metrics = Column(JSON, default=list)
    responsibilities = Column(JSON, default=list)
    skills_used = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    difficulty = Column(String(20), nullable=True)
    embedding_id = Column(String(36), nullable=True)
    tags = Column(JSON, default=list)
    visibility = Column(String(20), default="private")
    status = Column(String(20), default="completed")
    highlights = Column(JSON, default=list)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    is_featured = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="projects")


# ── Skill ───────────────────────────────────────────────────

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    level = Column(String(20), nullable=True)
    years_experience = Column(Float, nullable=True)
    last_used = Column(String(20), nullable=True)
    is_primary = Column(Boolean, default=False)
    embedding_id = Column(String(36), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="skills")


# ── Certificate ─────────────────────────────────────────────

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    issue_date = Column(String(20), nullable=True)
    expiry_date = Column(String(20), nullable=True)
    credential_id = Column(String(255), nullable=True)
    credential_url = Column(String(512), nullable=True)
    skills = Column(JSON, default=list)
    level = Column(String(50), nullable=True)
    tags = Column(JSON, default=list)
    verification_status = Column(String(20), default="unverified")
    related_project_ids = Column(JSON, default=list)
    original_pdf_path = Column(String(512), nullable=True)
    thumbnail_path = Column(String(512), nullable=True)
    embedding_id = Column(String(36), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="certificates")


# ── Achievement ─────────────────────────────────────────────

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String(20), nullable=True)
    category = Column(String(100), nullable=True)
    organization = Column(String(255), nullable=True)
    url = Column(String(512), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="achievements")


# ── Language ────────────────────────────────────────────────

class Language(Base):
    __tablename__ = "languages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    proficiency = Column(String(20), nullable=True)
    years = Column(Float, nullable=True)
    is_native = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="languages")


# ── Publication ─────────────────────────────────────────────

class Publication(Base):
    __tablename__ = "publications"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, default=list)
    venue = Column(String(255), nullable=True)
    date = Column(String(20), nullable=True)
    url = Column(String(512), nullable=True)
    doi = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="publications")


# ── Award ───────────────────────────────────────────────────

class Award(Base):
    __tablename__ = "awards"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    date = Column(String(20), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(512), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="awards")


# ── Social Link ─────────────────────────────────────────────

class SocialLink(Base):
    __tablename__ = "social_links"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    url = Column(String(512), nullable=False)
    username = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    version = Column(Integer, default=1)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="social_links")


# ── Resume Version ──────────────────────────────────────────

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    template_name = Column(String(100), nullable=True)
    content_json = Column(JSON, nullable=True)
    pdf_path = Column(String(512), nullable=True)
    ats_score = Column(Float, nullable=True)
    reflection_iterations = Column(Integer, default=0)
    job_description_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="resume_versions")
    ats_reports = relationship("ATSReport", back_populates="resume_version", cascade="all, delete-orphan")
    job_description = relationship("JobDescription", back_populates="resume_versions")


# ── ATS Report ──────────────────────────────────────────────

class ATSReport(Base):
    __tablename__ = "ats_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    resume_version_id = Column(String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    keyword_score = Column(Float, nullable=True)
    formatting_score = Column(Float, nullable=True)
    impact_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    coverage_score = Column(Float, nullable=True)
    report_json = Column(JSON, nullable=True)
    suggestions = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)

    resume_version = relationship("ResumeVersion", back_populates="ats_reports")


# ── Job Description ─────────────────────────────────────────

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_json = Column(JSON, nullable=True)
    keywords = Column(JSON, default=list)
    requirements = Column(JSON, default=list)
    embedding_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="job_descriptions")
    resume_versions = relationship("ResumeVersion", back_populates="job_description")


# ── Original Document ───────────────────────────────────────

class OriginalDocument(Base):
    __tablename__ = "original_documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    file_path = Column(String(512), nullable=False)
    original_name = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    text_content = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True)
    embedding_ids = Column(JSON, default=list)
    ocr_performed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
