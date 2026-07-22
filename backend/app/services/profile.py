"""Profile service — orchestrates all profile-related CRUD operations.

This is the business logic layer. It coordinates between
the repository layer and the API layer.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from app.db.models import (
    User, Education, Experience, Project, Skill,
    Certificate, Achievement, Language, Publication,
    Award, SocialLink, OriginalDocument, ResumeVersion,
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
        self.languages = Repository(Language, session)
        self.publications = Repository(Publication, session)
        self.awards = Repository(Award, session)
        self.social_links = Repository(SocialLink, session)
        self.documents = Repository(OriginalDocument, session)
        self.resumes = Repository(ResumeVersion, session)

    # ── User Profile ────────────────────────────────────────

    async def get_or_create_user(self) -> User:
        user = await self.users.get(self.user_id)
        if user is None:
            user = await self.users.create({"id": self.user_id, "full_name": "New User"})
        return user

    async def update_profile(self, data: dict[str, Any]) -> User:
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
            "projects": await self.projects.count({"user_id": self.user_id}) > 0,
            "certificates": await self.certificates.count({"user_id": self.user_id}) > 0,
            "languages": await self.languages.count({"user_id": self.user_id}) > 0,
        }

        completed = sum(1 for v in checks.values() if v)
        return round((completed / len(checks)) * 100, 1)

    # ── Education ───────────────────────────────────────────

    async def list_education(self) -> list:
        return await self.education.list(filters={"user_id": self.user_id}, order_by="start_date")

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
        return await self.education.soft_delete(edu_id)

    # ── Experience ──────────────────────────────────────────

    async def list_experience(self) -> list:
        return await self.experience.list(filters={"user_id": self.user_id}, order_by="start_date")

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
        return await self.experience.soft_delete(exp_id)

    # ── Projects ────────────────────────────────────────────

    async def list_projects(self) -> list:
        return await self.projects.list(filters={"user_id": self.user_id}, order_by="created_at")

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
        return await self.projects.soft_delete(project_id)

    # ── Skills ──────────────────────────────────────────────

    async def list_skills(self) -> list:
        return await self.skills.list(filters={"user_id": self.user_id})

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
        return await self.skills.soft_delete(skill_id)

    # ── Certificates ────────────────────────────────────────

    async def list_certificates(self) -> list:
        return await self.certificates.list(filters={"user_id": self.user_id})

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
        return await self.certificates.soft_delete(cert_id)

    # ── Achievements ────────────────────────────────────────

    async def list_achievements(self) -> list:
        return await self.achievements.list(filters={"user_id": self.user_id})

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
        return await self.achievements.soft_delete(ach_id)

    # ── Languages ───────────────────────────────────────────

    async def list_languages(self) -> list:
        return await self.languages.list(filters={"user_id": self.user_id})

    async def get_language(self, lang_id: str):
        lang = await self.languages.get(lang_id)
        if lang is None or lang.user_id != self.user_id:
            return None
        return lang

    async def create_language(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.languages.create(data)

    async def update_language(self, lang_id: str, data: dict):
        lang = await self.get_language(lang_id)
        if lang is None:
            return None
        return await self.languages.update(lang_id, data)

    async def delete_language(self, lang_id: str) -> bool:
        lang = await self.get_language(lang_id)
        if lang is None:
            return False
        return await self.languages.soft_delete(lang_id)

    # ── Publications ────────────────────────────────────────

    async def list_publications(self) -> list:
        return await self.publications.list(filters={"user_id": self.user_id})

    async def get_publication(self, pub_id: str):
        pub = await self.publications.get(pub_id)
        if pub is None or pub.user_id != self.user_id:
            return None
        return pub

    async def create_publication(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.publications.create(data)

    async def update_publication(self, pub_id: str, data: dict):
        pub = await self.get_publication(pub_id)
        if pub is None:
            return None
        return await self.publications.update(pub_id, data)

    async def delete_publication(self, pub_id: str) -> bool:
        pub = await self.get_publication(pub_id)
        if pub is None:
            return False
        return await self.publications.soft_delete(pub_id)

    # ── Awards ──────────────────────────────────────────────

    async def list_awards(self) -> list:
        return await self.awards.list(filters={"user_id": self.user_id})

    async def get_award(self, award_id: str):
        award = await self.awards.get(award_id)
        if award is None or award.user_id != self.user_id:
            return None
        return award

    async def create_award(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.awards.create(data)

    async def update_award(self, award_id: str, data: dict):
        award = await self.get_award(award_id)
        if award is None:
            return None
        return await self.awards.update(award_id, data)

    async def delete_award(self, award_id: str) -> bool:
        award = await self.get_award(award_id)
        if award is None:
            return False
        return await self.awards.soft_delete(award_id)

    # ── Social Links ────────────────────────────────────────

    async def list_social_links(self) -> list:
        return await self.social_links.list(filters={"user_id": self.user_id})

    async def get_social_link(self, link_id: str):
        link = await self.social_links.get(link_id)
        if link is None or link.user_id != self.user_id:
            return None
        return link

    async def create_social_link(self, data: dict) -> Any:
        data["user_id"] = self.user_id
        return await self.social_links.create(data)

    async def update_social_link(self, link_id: str, data: dict):
        link = await self.get_social_link(link_id)
        if link is None:
            return None
        return await self.social_links.update(link_id, data)

    async def delete_social_link(self, link_id: str) -> bool:
        link = await self.get_social_link(link_id)
        if link is None:
            return False
        return await self.social_links.soft_delete(link_id)

    # ── Global Search ───────────────────────────────────────

    async def global_search(self, query: str) -> list[dict]:
        """Search across all profile entities."""
        results = []
        q = f"%{query}%"

        # Search education
        from sqlalchemy import select
        edu_results = await self.session.execute(
            select(Education).where(
                Education.user_id == self.user_id,
                Education.deleted_at.is_(None),
                or_(
                    Education.degree.ilike(q),
                    Education.institution.ilike(q),
                    Education.field_of_study.ilike(q),
                    Education.description.ilike(q),
                )
            )
        )
        for edu in edu_results.scalars().all():
            results.append({
                "id": edu.id, "type": "education", "title": f"{edu.degree} — {edu.institution}",
                "subtitle": f"{edu.start_date} — {edu.end_date or 'Present'}",
            })

        # Search experience
        exp_results = await self.session.execute(
            select(Experience).where(
                Experience.user_id == self.user_id,
                Experience.deleted_at.is_(None),
                or_(
                    Experience.title.ilike(q),
                    Experience.company.ilike(q),
                    Experience.description.ilike(q),
                )
            )
        )
        for exp in exp_results.scalars().all():
            results.append({
                "id": exp.id, "type": "experience", "title": f"{exp.title} at {exp.company}",
                "subtitle": f"{exp.start_date} — {exp.end_date or 'Present'}",
            })

        # Search projects
        proj_results = await self.session.execute(
            select(Project).where(
                Project.user_id == self.user_id,
                Project.deleted_at.is_(None),
                or_(
                    Project.name.ilike(q),
                    Project.description.ilike(q),
                )
            )
        )
        for proj in proj_results.scalars().all():
            results.append({
                "id": proj.id, "type": "project", "title": proj.name,
                "subtitle": proj.description[:100] if proj.description else "",
            })

        # Search skills
        skill_results = await self.session.execute(
            select(Skill).where(
                Skill.user_id == self.user_id,
                Skill.deleted_at.is_(None),
                Skill.name.ilike(q),
            )
        )
        for skill in skill_results.scalars().all():
            results.append({
                "id": skill.id, "type": "skill", "title": skill.name,
                "subtitle": skill.category or "",
            })

        # Search certificates
        cert_results = await self.session.execute(
            select(Certificate).where(
                Certificate.user_id == self.user_id,
                Certificate.deleted_at.is_(None),
                or_(
                    Certificate.title.ilike(q),
                    Certificate.issuer.ilike(q),
                )
            )
        )
        for cert in cert_results.scalars().all():
            results.append({
                "id": cert.id, "type": "certificate", "title": cert.title,
                "subtitle": cert.issuer,
            })

        # Search achievements
        ach_results = await self.session.execute(
            select(Achievement).where(
                Achievement.user_id == self.user_id,
                Achievement.deleted_at.is_(None),
                or_(
                    Achievement.title.ilike(q),
                    Achievement.description.ilike(q),
                )
            )
        )
        for ach in ach_results.scalars().all():
            results.append({
                "id": ach.id, "type": "achievement", "title": ach.title,
                "subtitle": ach.organization or "",
            })

        # Search languages
        lang_results = await self.session.execute(
            select(Language).where(
                Language.user_id == self.user_id,
                Language.deleted_at.is_(None),
                Language.name.ilike(q),
            )
        )
        for lang in lang_results.scalars().all():
            results.append({
                "id": lang.id, "type": "language", "title": lang.name,
                "subtitle": lang.proficiency or "",
            })

        # Search publications
        pub_results = await self.session.execute(
            select(Publication).where(
                Publication.user_id == self.user_id,
                Publication.deleted_at.is_(None),
                or_(
                    Publication.title.ilike(q),
                    Publication.venue.ilike(q),
                    Publication.description.ilike(q),
                )
            )
        )
        for pub in pub_results.scalars().all():
            results.append({
                "id": pub.id, "type": "publication", "title": pub.title,
                "subtitle": pub.venue or "",
            })

        # Search awards
        award_results = await self.session.execute(
            select(Award).where(
                Award.user_id == self.user_id,
                Award.deleted_at.is_(None),
                or_(
                    Award.title.ilike(q),
                    Award.issuer.ilike(q),
                    Award.description.ilike(q),
                )
            )
        )
        for award in award_results.scalars().all():
            results.append({
                "id": award.id, "type": "award", "title": award.title,
                "subtitle": award.issuer or "",
            })

        # Search social links
        link_results = await self.session.execute(
            select(SocialLink).where(
                SocialLink.user_id == self.user_id,
                SocialLink.deleted_at.is_(None),
                or_(
                    SocialLink.platform.ilike(q),
                    SocialLink.username.ilike(q),
                    SocialLink.display_name.ilike(q),
                )
            )
        )
        for link in link_results.scalars().all():
            results.append({
                "id": link.id, "type": "social_link", "title": f"{link.platform}: {link.username or link.display_name or ''}",
                "subtitle": link.url,
            })

        return results

    # ── Dashboard Aggregation ───────────────────────────────

    async def get_dashboard_data(self) -> dict:
        user = await self.get_or_create_user()
        completion = await self.calculate_profile_completion()

        return {
            "profile": user,
            "total_education": await self.education.count({"user_id": self.user_id}),
            "total_experience": await self.experience.count({"user_id": self.user_id}),
            "total_projects": await self.projects.count({"user_id": self.user_id}),
            "total_skills": await self.skills.count({"user_id": self.user_id}),
            "total_certificates": await self.certificates.count({"user_id": self.user_id}),
            "total_achievements": await self.achievements.count({"user_id": self.user_id}),
            "total_languages": await self.languages.count({"user_id": self.user_id}),
            "total_publications": await self.publications.count({"user_id": self.user_id}),
            "total_awards": await self.awards.count({"user_id": self.user_id}),
            "total_social_links": await self.social_links.count({"user_id": self.user_id}),
            "total_documents": await self.documents.count(),
            "total_resumes": await self.resumes.count({"user_id": self.user_id}),
            "profile_completion": completion,
        }
