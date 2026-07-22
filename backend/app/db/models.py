"""SQLAlchemy ORM models for CareerForge AI."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime,
    ForeignKey, JSON, Boolean, Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    resume_versions = relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="education")


class Experience(Base):
    __tablename__ = "experience"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    employment_type = Column(String(50), nullable=True)  # full-time, part-time, contract, internship
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=True)  # null = present
    description = Column(Text, nullable=True)
    highlights = Column(JSON, default=list)
    skills_used = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="experience")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    repo_url = Column(String(512), nullable=True)
    live_url = Column(String(512), nullable=True)
    tech_stack = Column(JSON, default=list)
    highlights = Column(JSON, default=list)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)  # programming, framework, tool, soft, domain
    level = Column(String(20), nullable=True)  # beginner, intermediate, advanced, expert
    years_experience = Column(Float, nullable=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="skills")


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
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="certificates")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String(20), nullable=True)
    category = Column(String(100), nullable=True)  # award, publication, patent, speaking, other
    organization = Column(String(255), nullable=True)
    url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")


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
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resume_versions")
    ats_reports = relationship("ATSReport", back_populates="resume_version", cascade="all, delete-orphan")
    job_description = relationship("JobDescription", back_populates="resume_versions")


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
    created_at = Column(DateTime, default=datetime.utcnow)

    resume_version = relationship("ResumeVersion", back_populates="ats_reports")


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
    embedding_id = Column(String(36), nullable=True)  # FK to LanceDB
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="job_descriptions")
    resume_versions = relationship("ResumeVersion", back_populates="job_description")


class OriginalDocument(Base):
    __tablename__ = "original_documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    file_path = Column(String(512), nullable=False)
    original_name = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    text_content = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True)  # resume, certificate, reference, other
    embedding_ids = Column(JSON, default=list)
    ocr_performed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
