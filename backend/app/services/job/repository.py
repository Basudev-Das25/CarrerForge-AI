"""Job Repository — CRUD, search, and management for job descriptions.

Extends the base JobDescription model with search, comparison,
duplicate detection, and collection management.
"""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobDescription

logger = structlog.get_logger("careerforge.job.repository")


class JobRepository:
    """Repository for job description management."""

    def __init__(self, session: AsyncSession, user_id: str = "default"):
        self.session = session
        self.user_id = user_id

    async def save(
        self,
        raw_text: str,
        parsed_data: dict[str, Any],
        title: str | None = None,
        company: str | None = None,
        tags: list[str] | None = None,
    ) -> JobDescription:
        """Save a new job description."""
        jd = JobDescription(
            user_id=self.user_id,
            title=title or parsed_data.get("job_title", ""),
            company=company or parsed_data.get("company", ""),
            raw_text=raw_text,
            parsed_json=parsed_data,
            keywords=parsed_data.get("keywords", []),
            requirements=parsed_data.get("required_skills", []),
        )
        self.session.add(jd)
        await self.session.flush()
        await self.session.refresh(jd)
        logger.info("job.saved", id=jd.id, title=jd.title)
        return jd

    async def get(self, jd_id: str) -> JobDescription | None:
        """Get a job description by ID."""
        result = await self.session.execute(
            select(JobDescription).where(
                JobDescription.id == jd_id,
                JobDescription.user_id == self.user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        company: str | None = None,
    ) -> list[JobDescription]:
        """List all job descriptions."""
        query = select(JobDescription).where(JobDescription.user_id == self.user_id)
        if company:
            query = query.where(JobDescription.company.ilike(f"%{company}%"))
        query = query.order_by(JobDescription.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> list[JobDescription]:
        """Text search across job descriptions."""
        q = f"%{query}%"
        result = await self.session.execute(
            select(JobDescription).where(
                JobDescription.user_id == self.user_id,
                or_(
                    JobDescription.title.ilike(q),
                    JobDescription.company.ilike(q),
                    JobDescription.raw_text.ilike(q),
                ),
            ).order_by(JobDescription.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def find_similar(
        self,
        title: str,
        company: str,
        threshold: float = 0.8,
    ) -> list[JobDescription]:
        """Find potentially duplicate job descriptions."""
        result = await self.session.execute(
            select(JobDescription).where(
                JobDescription.user_id == self.user_id,
                or_(
                    JobDescription.title.ilike(f"%{title}%"),
                    JobDescription.company.ilike(f"%{company}%"),
                ),
            )
        )
        return result.scalars().all()

    async def compare(self, jd_id_1: str, jd_id_2: str) -> dict[str, Any]:
        """Compare two job descriptions."""
        jd1 = await self.get(jd_id_1)
        jd2 = await self.get(jd_id_2)
        if not jd1 or not jd2:
            return {"error": "Job description not found"}

        p1 = jd1.parsed_json or {}
        p2 = jd2.parsed_json or {}

        skills1 = set(p1.get("required_skills", []) + p1.get("technologies", []))
        skills2 = set(p2.get("required_skills", []) + p2.get("technologies", []))

        return {
            "jd1": {"id": jd1.id, "title": jd1.title, "company": jd1.company},
            "jd2": {"id": jd2.id, "title": jd2.title, "company": jd2.company},
            "shared_skills": list(skills1 & skills2),
            "unique_to_jd1": list(skills1 - skills2),
            "unique_to_jd2": list(skills2 - skills1),
            "skill_overlap_ratio": len(skills1 & skills2) / max(len(skills1 | skills2), 1),
            "seniority_match": p1.get("seniority") == p2.get("seniority"),
            "industry_match": p1.get("industry") == p2.get("industry"),
        }

    async def delete(self, jd_id: str) -> bool:
        """Delete a job description."""
        jd = await self.get(jd_id)
        if not jd:
            return False
        await self.session.delete(jd)
        await self.session.flush()
        return True

    async def count(self) -> int:
        """Count total job descriptions."""
        result = await self.session.execute(
            select(func.count()).select_from(JobDescription).where(
                JobDescription.user_id == self.user_id
            )
        )
        return result.scalar_one()

    async def get_stats(self) -> dict:
        """Get repository statistics."""
        total = await self.count()
        result = await self.session.execute(
            select(JobDescription).where(JobDescription.user_id == self.user_id)
        )
        all_jd = result.scalars().all()

        companies = set()
        industries = set()
        for jd in all_jd:
            if jd.company:
                companies.add(jd.company)
            p = jd.parsed_json or {}
            if p.get("industry"):
                industries.add(p["industry"])

        return {
            "total": total,
            "unique_companies": len(companies),
            "unique_industries": len(industries),
            "companies": list(companies)[:20],
        }
