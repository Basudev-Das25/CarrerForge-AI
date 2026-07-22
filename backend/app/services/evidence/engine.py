"""Resume Evidence Engine — retrieves and scores evidence for resume generation.

Given a Job Profile, retrieves relevant entities from the Knowledge Engine
and bundles them with confidence scores and relationship paths.
The Resume Generator consumes ONLY evidence bundles — never the database directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

from app.services.job.intelligence import JobProfile
from app.services.knowledge.engine import KnowledgeEngine

logger = structlog.get_logger("careerforge.evidence")


@dataclass
class EvidenceItem:
    """A single piece of evidence for resume generation."""
    entity_type: str
    entity_id: str
    properties: dict[str, Any]
    reason_for_selection: str
    similarity_score: float = 0.0
    knowledge_score: float = 0.0
    confidence_score: float = 0.0
    relationship_path: list[str] = field(default_factory=list)
    supporting_keywords: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "properties": self.properties,
            "reason_for_selection": self.reason_for_selection,
            "similarity_score": round(self.similarity_score, 4),
            "knowledge_score": round(self.knowledge_score, 4),
            "confidence_score": round(self.confidence_score, 4),
            "relationship_path": self.relationship_path,
            "supporting_keywords": self.supporting_keywords,
            "scores": self.scores,
        }


@dataclass
class EvidenceBundle:
    """Complete evidence bundle for resume generation."""
    job_profile: dict[str, Any]
    projects: list[EvidenceItem] = field(default_factory=list)
    skills: list[EvidenceItem] = field(default_factory=list)
    experience: list[EvidenceItem] = field(default_factory=list)
    certificates: list[EvidenceItem] = field(default_factory=list)
    achievements: list[EvidenceItem] = field(default_factory=list)
    awards: list[EvidenceItem] = field(default_factory=list)
    languages: list[EvidenceItem] = field(default_factory=list)
    publications: list[EvidenceItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "job_profile": self.job_profile,
            "evidence": {
                "projects": [e.to_dict() for e in self.projects],
                "skills": [e.to_dict() for e in self.skills],
                "experience": [e.to_dict() for e in self.experience],
                "certificates": [e.to_dict() for e in self.certificates],
                "achievements": [e.to_dict() for e in self.achievements],
                "awards": [e.to_dict() for e in self.awards],
                "languages": [e.to_dict() for e in self.languages],
                "publications": [e.to_dict() for e in self.publications],
            },
            "metadata": self.metadata,
        }

    def summary(self) -> dict[str, int]:
        """Count evidence items per type."""
        return {
            "projects": len(self.projects),
            "skills": len(self.skills),
            "experience": len(self.experience),
            "certificates": len(self.certificates),
            "achievements": len(self.achievements),
            "awards": len(self.awards),
            "languages": len(self.languages),
            "publications": len(self.publications),
        }


class EvidenceEngine:
    """Generates evidence bundles from job profiles and knowledge graph."""

    def __init__(self, knowledge_engine: KnowledgeEngine):
        self.ke = knowledge_engine

    async def generate_evidence_bundle(
        self,
        job_profile: JobProfile,
        max_per_type: int = 10,
    ) -> EvidenceBundle:
        """Generate a complete evidence bundle for resume generation.

        Uses the Knowledge Engine to find the most relevant entities
        for each section of the resume.
        """
        logger.info("evidence.bundle.start", job=job_profile.job_title)
        query = f"{job_profile.job_title} {job_profile.summary} {' '.join(job_profile.required_skills)}"
        jd_keywords = job_profile.keywords + job_profile.ats_keywords
        jd_requirements = job_profile.required_skills + job_profile.technologies

        bundle = EvidenceBundle(job_profile=job_profile.to_dict())

        # Retrieve evidence for each entity type
        bundle.experience = await self._retrieve_evidence(
            "experience", query, jd_keywords, jd_requirements,
            max_per_type, "backend",
        )
        bundle.projects = await self._retrieve_evidence(
            "project", query, jd_keywords, jd_requirements,
            max_per_type, "backend",
        )
        bundle.skills = await self._retrieve_evidence(
            "skill", query, jd_keywords, jd_requirements,
            max_per_type, None,
        )
        bundle.certificates = await self._retrieve_evidence(
            "certificate", query, jd_keywords, jd_requirements,
            max_per_type, None,
        )
        bundle.achievements = await self._retrieve_evidence(
            "achievement", query, jd_keywords, jd_requirements,
            max_per_type, None,
        )
        bundle.awards = await self._retrieve_evidence(
            "award", query, jd_keywords, jd_requirements,
            max_per_type, None,
        )
        bundle.languages = await self._retrieve_evidence(
            "language", query, jd_keywords, jd_requirements,
            max_per_type, "communication",
        )
        bundle.publications = await self._retrieve_evidence(
            "publication", query, jd_keywords, jd_requirements,
            max_per_type, "research",
        )

        # Calculate overall confidence
        all_items = (
            bundle.experience + bundle.projects + bundle.skills +
            bundle.certificates + bundle.achievements + bundle.awards
        )
        avg_confidence = (
            sum(item.confidence_score for item in all_items) / len(all_items)
            if all_items else 0.0
        )

        bundle.metadata = {
            "total_evidence": sum(bundle.summary().values()),
            "avg_confidence": round(avg_confidence, 4),
            "job_title": job_profile.job_title,
            "company": job_profile.company,
            "required_skills_count": len(job_profile.required_skills),
            "ats_keywords_count": len(job_profile.ats_keywords),
        }

        logger.info("evidence.bundle.complete", **bundle.summary())
        return bundle

    async def _retrieve_evidence(
        self,
        entity_type: str,
        query: str,
        jd_keywords: list[str],
        jd_requirements: list[str],
        max_items: int,
        scoring_dimension: str | None,
    ) -> list[EvidenceItem]:
        """Retrieve and score evidence for a specific entity type."""
        results = self.ke.get_relevant(
            entity_type=entity_type,
            query=query,
            jd_keywords=jd_keywords,
            jd_requirements=jd_requirements,
            top_k=max_items,
            scoring_dimension=scoring_dimension,
        )

        items = []
        for r in results:
            # Compute confidence as weighted combination
            similarity = r.get("keyword_match", 0.0)
            ats_coverage = r.get("ats_coverage", 0.0)
            dim_score = r.get("dimension_score", 0.0)
            knowledge_score = max(r.get("scores", {}).values()) if r.get("scores") else 0.0

            confidence = 0.3 * similarity + 0.3 * ats_coverage + 0.2 * knowledge_score + 0.2 * dim_score

            # Find supporting keywords from the entity text
            entity_text = " ".join(
                str(v) for v in r.get("properties", {}).values()
                if isinstance(v, str)
            ).lower()
            supporting = [kw for kw in jd_keywords if kw.lower() in entity_text]

            # Get relationship path
            neighbors = self.ke.get_neighbors(entity_type, r["entity_id"], depth=1)
            rel_path = [
                f"{n['entity_type']}:{n['entity_id']}"
                for n in neighbors[:3]
            ]

            items.append(EvidenceItem(
                entity_type=entity_type,
                entity_id=r["entity_id"],
                properties=r.get("properties", {}),
                reason_for_selection=f"Matched {len(supporting)} keywords, ATS coverage {ats_coverage:.1%}",
                similarity_score=similarity,
                knowledge_score=knowledge_score,
                confidence_score=round(confidence, 4),
                relationship_path=rel_path,
                supporting_keywords=supporting,
                scores=r.get("scores", {}),
            ))

        return items
