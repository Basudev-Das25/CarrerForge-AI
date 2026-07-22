"""Profile service — orchestrates all profile-related CRUD operations.

This is the business logic layer. It coordinates between
the repository layer and the API layer.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    User, Education, Experience, Project, Skill,
    Certificate, Achievement, OriginalDocument, ResumeVersion,
)
from app.db.repository import Repository
from app.utils.errors import ValidationError, DatabaseError


class ProfileService:
    """Service for managing a user's complete professional profile."""

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

        # Repositories
        self.users = Repository(User, session)
        self.education = Repository(Education, session)
        self.experience = Repository(Experience, session)
        self.projects = Repository(Project, session)
        self.skills = Repository(Skill, session)
        self.certificates = Repository(Certificate, session)
        self.achievements = Repository(Achievement, session)
        self.documents = Repository(OriginalDocument, session)
        self.resumes = Repository(ResumeVersion, session)

    # ── User Profile ────────────────────────────────────────

    async def get_or_create_user(self) -> User:
        """Get the current user profile, creating a default one if needed."""
        user = await self.users.get(self.user_id)
        if user is None:
            user = await self.users.create({"id": self.user_id, "full_name": "New User"})
        return user

    async def update_profile(self, data: dict[str, Any]) -> User:
        """Update the user profile fields."""
        user = await self.users.get(self.user_id)
        if user is None:
            user = await self.users.create({"id": self.user_id, **data})
        else:
            updated = await self.users.update(self.user_id, data)
            if updated is None:
                raise DatabaseError("Failed to update profile")
            user = updated
        return user

    async def calculate_profile_completion(self) -> float:
        """Calculate profile completion percentage (0-100)."""
        user = await self.users.get(self.user_id)
        if user is None:
            return 0.0

        checks = {
            "full_name": bool(user.full_name and user.full_name != "New User"),
            "email": bool(user.email),
            "phone": bool(user.phone),
            "location": bool(user.location),
            "summary": bool(user.summary and len(user.summary) > 20),
            "education": await self.education.count({"user_id": self.user_id}) > 0,
            "experience": await self.experience.count({"user_id": self.user_id}) > 0,
            "skills": await self.skills.count({"user_id": self.user_id}) > 0,
        }

        completed = sum(1 for v in checks.values() if v)
        return round((completed / len(checks)) * 100, 1)

    # ── Education ───────────────────────────────────────────

    async def list_education(self) -> list:
        return await self.education.list(
            filters={"user_id": self.user_id},
            order_by="start_date",
        )

    async def get_education(self, edu_id: str):
        edu = await self.education.get(edu_id)
        if edu is None or edu.user_id != self.user_id:
            return None
        return edu

    async def create_education(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.education.create(data)

    async def update_education(self, edu_id: str, data: dict):
        edu = await self.get_education(edu_id)
        if edu is None:
            return None
        return await self.education.update(edu_id, data)

    async def delete_education(self, edu_id: str) -> bool:
        edu = await self.get_education(edu_id)
        if edu is None:
            return False
        return await self.education.delete(edu_id)

    # ── Experience ──────────────────────────────────────────

    async def list_experience(self) -> list:
        return await self.experience.list(
            filters={"user_id": self.user_id},
            order_by="start_date",
        )

    async def get_experience(self, exp_id: str):
        exp = await self.experience.get(exp_id)
        if exp is None or exp.user_id != self.user_id:
            return None
        return exp

    async def create_experience(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.experience.create(data)

    async def update_experience(self, exp_id: str, data: dict):
        exp = await self.get_experience(exp_id)
        if exp is None:
            return None
        return await self.experience.update(exp_id, data)

    async def delete_experience(self, exp_id: str) -> bool:
        exp = await self.get_experience(exp_id)
        if exp is None:
            return False
        return await self.experience.delete(exp_id)

    # ── Projects ────────────────────────────────────────────

    async def list_projects(self) -> list:
        return await self.projects.list(
            filters={"user_id": self.user_id},
            order_by="created_at",
        )

    async def get_project(self, project_id: str):
        project = await self.projects.get(project_id)
        if project is None or project.user_id != self.user_id:
            return None
        return project

    async def create_project(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.projects.create(data)

    async def update_project(self, project_id: str, data: dict):
        project = await self.get_project(project_id)
        if project is None:
            return None
        return await self.projects.update(project_id, data)

    async def delete_project(self, project_id: str) -> bool:
        project = await self.get_project(project_id)
        if project is None:
            return False
        return await self.projects.delete(project_id)

    # ── Skills ──────────────────────────────────────────────

    async def list_skills(self) -> list:
        return await self.skills.list(
            filters={"user_id": self.user_id},
        )

    async def get_skill(self, skill_id: str):
        skill = await self.skills.get(skill_id)
        if skill is None or skill.user_id != self.user_id:
            return None
        return skill

    async def create_skill(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.skills.create(data)

    async def update_skill(self, skill_id: str, data: dict):
        skill = await self.get_skill(skill_id)
        if skill is None:
            return None
        return await self.skills.update(skill_id, data)

    async def delete_skill(self, skill_id: str) -> bool:
        skill = await self.get_skill(skill_id)
        if skill is None:
            return False
        return await self.skills.delete(skill_id)

    # ── Certificates ────────────────────────────────────────

    async def list_certificates(self) -> list:
        return await self.certificates.list(
            filters={"user_id": self.user_id},
        )

    async def get_certificate(self, cert_id: str):
        cert = await self.certificates.get(cert_id)
        if cert is None or cert.user_id != self.user_id:
            return None
        return cert

    async def create_certificate(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.certificates.create(data)

    async def update_certificate(self, cert_id: str, data: dict):
        cert = await self.get_certificate(cert_id)
        if cert is None:
            return None
        return await self.certificates.update(cert_id, data)

    async def delete_certificate(self, cert_id: str) -> bool:
        cert = await self.get_certificate(cert_id)
        if cert is None:
            return False
        return await self.certificates.delete(cert_id)

    # ── Achievements ────────────────────────────────────────

    async def list_achievements(self) -> list:
        return await self.achievements.list(
            filters={"user_id": self.user_id},
        )

    async def get_achievement(self, ach_id: str):
        ach = await self.achievements.get(ach_id)
        if ach is None or ach.user_id != self.user_id:
            return None
        return ach

    async def create_achievement(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.achievements.create(data)

    async def update_achievement(self, ach_id: str, data: dict):
        ach = await self.get_achievement(ach_id)
        if ach is None:
            return None
        return await self.achievements.update(ach_id, data)

    async def delete_achievement(self, ach_id: str) -> bool:
        ach = await self.get_achievement(ach_id)
        if ach is None:
            return False
        return await self.achievements.delete(ach_id)

    # ── Dashboard Aggregation ───────────────────────────────

    async def get_dashboard_data(self) -> dict:
        """Aggregate data for the dashboard."""
        user = await self.get_or_create_user()
        completion = await self.calculate_profile_completion()

        recent_docs = await self.documents.list(
            filters={"user_id": self.user_id} if hasattr(OriginalDocument, "user_id") else None,
            limit=5,
        )

        return {
            "profile": user,
            "total_education": await self.education.count({"user_id": self.user_id}),
            "total_experience": await self.experience.count({"user_id": self.user_id}),
            "total_projects": await self.projects.count({"user_id": self.user_id}),
            "total_skills": await self.skills.count({"user_id": self.user_id}),
            "total_certificates": await self.certificates.count({"user_id": self.user_id}),
            "total_achievements": await self.achievements.count({"user_id": self.user_id}),
            "total_documents": await self.documents.count(),
            "total_resumes": await self.resumes.count({"user_id": self.user_id}),
            "recent_documents": recent_docs,
            "profile_completion": completion,
        }
