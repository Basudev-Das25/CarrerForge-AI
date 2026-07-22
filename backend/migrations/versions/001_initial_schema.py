"""Initial schema — all profile tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-07-22
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("linkedin_url", sa.String(512), nullable=True),
        sa.Column("github_url", sa.String(512), nullable=True),
        sa.Column("portfolio_url", sa.String(512), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("avatar_path", sa.String(512), nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Education
    op.create_table(
        "education",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("degree", sa.String(255), nullable=False),
        sa.Column("field_of_study", sa.String(255), nullable=True),
        sa.Column("institution", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("start_date", sa.String(20), nullable=False),
        sa.Column("end_date", sa.String(20), nullable=True),
        sa.Column("gpa", sa.Float, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("highlights", sa.JSON, nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Experience
    op.create_table(
        "experience",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("employment_type", sa.String(50), nullable=True),
        sa.Column("start_date", sa.String(20), nullable=False),
        sa.Column("end_date", sa.String(20), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("highlights", sa.JSON, nullable=True),
        sa.Column("skills_used", sa.JSON, nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("role", sa.String(255), nullable=True),
        sa.Column("repo_url", sa.String(512), nullable=True),
        sa.Column("live_url", sa.String(512), nullable=True),
        sa.Column("tech_stack", sa.JSON, nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("images", sa.JSON, nullable=True),
        sa.Column("team_size", sa.Integer, nullable=True),
        sa.Column("impact_metrics", sa.JSON, nullable=True),
        sa.Column("responsibilities", sa.JSON, nullable=True),
        sa.Column("skills_used", sa.JSON, nullable=True),
        sa.Column("keywords", sa.JSON, nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("embedding_id", sa.String(36), nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("visibility", sa.String(20), default="private"),
        sa.Column("status", sa.String(20), default="completed"),
        sa.Column("highlights", sa.JSON, nullable=True),
        sa.Column("start_date", sa.String(20), nullable=True),
        sa.Column("end_date", sa.String(20), nullable=True),
        sa.Column("is_featured", sa.Boolean, default=False),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Skills
    op.create_table(
        "skills",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("level", sa.String(20), nullable=True),
        sa.Column("years_experience", sa.Float, nullable=True),
        sa.Column("last_used", sa.String(20), nullable=True),
        sa.Column("is_primary", sa.Boolean, default=False),
        sa.Column("embedding_id", sa.String(36), nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Certificates
    op.create_table(
        "certificates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("issuer", sa.String(255), nullable=False),
        sa.Column("issue_date", sa.String(20), nullable=True),
        sa.Column("expiry_date", sa.String(20), nullable=True),
        sa.Column("credential_id", sa.String(255), nullable=True),
        sa.Column("credential_url", sa.String(512), nullable=True),
        sa.Column("skills", sa.JSON, nullable=True),
        sa.Column("level", sa.String(50), nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("verification_status", sa.String(20), default="unverified"),
        sa.Column("related_project_ids", sa.JSON, nullable=True),
        sa.Column("original_pdf_path", sa.String(512), nullable=True),
        sa.Column("thumbnail_path", sa.String(512), nullable=True),
        sa.Column("embedding_id", sa.String(36), nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Achievements
    op.create_table(
        "achievements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("date", sa.String(20), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("organization", sa.String(255), nullable=True),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Languages
    op.create_table(
        "languages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("proficiency", sa.String(20), nullable=True),
        sa.Column("years", sa.Float, nullable=True),
        sa.Column("is_native", sa.Boolean, default=False),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Publications
    op.create_table(
        "publications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("authors", sa.JSON, nullable=True),
        sa.Column("venue", sa.String(255), nullable=True),
        sa.Column("date", sa.String(20), nullable=True),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("doi", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Awards
    op.create_table(
        "awards",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("issuer", sa.String(255), nullable=True),
        sa.Column("date", sa.String(20), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Social Links
    op.create_table(
        "social_links",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("url", sa.String(512), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Profile Versions
    op.create_table(
        "profile_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("snapshot_json", sa.JSON, nullable=False),
        sa.Column("change_summary", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # Resume Versions
    op.create_table(
        "resume_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("template_name", sa.String(100), nullable=True),
        sa.Column("content_json", sa.JSON, nullable=True),
        sa.Column("pdf_path", sa.String(512), nullable=True),
        sa.Column("ats_score", sa.Float, nullable=True),
        sa.Column("reflection_iterations", sa.Integer, default=0),
        sa.Column("job_description_id", sa.String(36), sa.ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_final", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # Job Descriptions
    op.create_table(
        "job_descriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("parsed_json", sa.JSON, nullable=True),
        sa.Column("keywords", sa.JSON, nullable=True),
        sa.Column("requirements", sa.JSON, nullable=True),
        sa.Column("embedding_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ATS Reports
    op.create_table(
        "ats_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("resume_version_id", sa.String(36), sa.ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("keyword_score", sa.Float, nullable=True),
        sa.Column("formatting_score", sa.Float, nullable=True),
        sa.Column("impact_score", sa.Float, nullable=True),
        sa.Column("readability_score", sa.Float, nullable=True),
        sa.Column("coverage_score", sa.Float, nullable=True),
        sa.Column("report_json", sa.JSON, nullable=True),
        sa.Column("suggestions", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # Original Documents
    op.create_table(
        "original_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("text_content", sa.Text, nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("embedding_ids", sa.JSON, nullable=True),
        sa.Column("ocr_performed", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # Indexes
    op.create_index("ix_education_user_id", "education", ["user_id"])
    op.create_index("ix_experience_user_id", "experience", ["user_id"])
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_index("ix_skills_user_id", "skills", ["user_id"])
    op.create_index("ix_certificates_user_id", "certificates", ["user_id"])
    op.create_index("ix_achievements_user_id", "achievements", ["user_id"])
    op.create_index("ix_languages_user_id", "languages", ["user_id"])
    op.create_index("ix_publications_user_id", "publications", ["user_id"])
    op.create_index("ix_awards_user_id", "awards", ["user_id"])
    op.create_index("ix_social_links_user_id", "social_links", ["user_id"])


def downgrade() -> None:
    op.drop_table("original_documents")
    op.drop_table("ats_reports")
    op.drop_table("job_descriptions")
    op.drop_table("resume_versions")
    op.drop_table("profile_versions")
    op.drop_table("social_links")
    op.drop_table("awards")
    op.drop_table("publications")
    op.drop_table("languages")
    op.drop_table("achievements")
    op.drop_table("certificates")
    op.drop_table("skills")
    op.drop_table("projects")
    op.drop_table("experience")
    op.drop_table("education")
    op.drop_table("users")
