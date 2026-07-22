"""Knowledge Engine — the main orchestrator.

Builds the knowledge graph from all profile entities, generates embeddings,
discovers relationships, scores relevance, and provides retrieval APIs.
This is the central intelligence layer that powers resume generation and ATS analysis.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import (
    User, Education, Experience, Project, Skill,
    Certificate, Achievement, Language, Publication,
    Award, SocialLink, JobDescription, ResumeVersion, ATSReport,
)
from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode
from app.services.knowledge.relationships import discover_all_relationships
from app.services.knowledge.scoring import score_all, compute_ats_score
from app.services.knowledge.retrieval import (
    RetrievalRequest, RetrievalResponse,
    hybrid_search, vector_search, keyword_search,
    get_relevant_entities, get_knowledge_summary,
)

logger = logging.getLogger("careerforge.knowledge.engine")


class KnowledgeEngine:
    """Builds and queries the knowledge graph for a user's profile."""

    def __init__(self, session: AsyncSession, user_id: str = "default"):
        self.session = session
        self.user_id = user_id
        self.graph = KnowledgeGraph()

    # ── Build ───────────────────────────────────────────────

    async def build(self) -> KnowledgeGraph:
        """Build the complete knowledge graph from all profile data."""
        logger.info("engine.build.start", user_id=self.user_id)

        # Load all entities
        await self._load_entities()

        # Discover relationships
        edge_count = discover_all_relationships(self.graph)

        # Score all entities
        score_all(self.graph)

        stats = self.graph.get_stats()
        logger.info("engine.build.complete", **stats, edges=edge_count)
        return self.graph

    async def _load_entities(self) -> None:
        """Load all profile entities into the knowledge graph."""
        entity_loaders = [
            ("user", self._load_users),
            ("education", self._load_education),
            ("experience", self._load_experience),
            ("project", self._load_projects),
            ("skill", self._load_skills),
            ("certificate", self._load_certificates),
            ("achievement", self._load_achievements),
            ("language", self._load_languages),
            ("publication", self._load_publications),
            ("award", self._load_awards),
            ("social_link", self._load_social_links),
            ("job_description", self._load_job_descriptions),
            ("resume_version", self._load_resume_versions),
            ("ats_report", self._load_ats_reports),
        ]

        for entity_type, loader in entity_loaders:
            try:
                count = await loader()
                logger.debug("engine.load", entity_type=entity_type, count=count)
            except Exception as e:
                logger.warning("engine.load.error", entity_type=entity_type, error=str(e))

    async def _load_users(self) -> int:
        result = await self.session.execute(
            select(User).where(User.id == self.user_id)
        )
        users = result.scalars().all()
        for user in users:
            text = f"{user.full_name or ''} {user.summary or ''} {user.email or ''} {user.location or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"user:{user.id}", entity_type="user", entity_id=user.id,
                properties={
                    "full_name": user.full_name, "email": user.email,
                    "phone": user.phone, "location": user.location,
                    "summary": user.summary,
                    "linkedin_url": user.linkedin_url, "github_url": user.github_url,
                    "portfolio_url": user.portfolio_url,
                },
                text_repr=text.strip(),
            ))
        return len(users)

    async def _load_education(self) -> int:
        result = await self.session.execute(
            select(Education).where(Education.user_id == self.user_id, Education.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for edu in items:
            text = f"{edu.degree} {edu.field_of_study or ''} {edu.institution} {edu.description or ''} {' '.join(edu.highlights or [])}"
            self.graph.add_node(KnowledgeNode(
                id=f"education:{edu.id}", entity_type="education", entity_id=edu.id,
                properties={
                    "degree": edu.degree, "field_of_study": edu.field_of_study,
                    "institution": edu.institution, "location": edu.location,
                    "start_date": edu.start_date, "end_date": edu.end_date,
                    "gpa": edu.gpa, "description": edu.description,
                    "highlights": edu.highlights or [],
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_experience(self) -> int:
        result = await self.session.execute(
            select(Experience).where(Experience.user_id == self.user_id, Experience.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for exp in items:
            text = f"{exp.title} at {exp.company} {exp.description or ''} {' '.join(exp.highlights or [])} {' '.join(exp.skills_used or [])}"
            self.graph.add_node(KnowledgeNode(
                id=f"experience:{exp.id}", entity_type="experience", entity_id=exp.id,
                properties={
                    "company": exp.company, "title": exp.title,
                    "location": exp.location, "employment_type": exp.employment_type,
                    "start_date": exp.start_date, "end_date": exp.end_date,
                    "description": exp.description,
                    "highlights": exp.highlights or [], "skills_used": exp.skills_used or [],
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_projects(self) -> int:
        result = await self.session.execute(
            select(Project).where(Project.user_id == self.user_id, Project.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for proj in items:
            text = f"{proj.name} {proj.description or ''} {proj.role or ''} {' '.join(proj.tech_stack or [])} {' '.join(proj.skills_used or [])} {' '.join(proj.keywords or [])} {' '.join(proj.tags or [])} {proj.industry or ''} {proj.category or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"project:{proj.id}", entity_type="project", entity_id=proj.id,
                properties={
                    "name": proj.name, "description": proj.description,
                    "role": proj.role, "repo_url": proj.repo_url,
                    "live_url": proj.live_url, "tech_stack": proj.tech_stack or [],
                    "industry": proj.industry, "category": proj.category,
                    "team_size": proj.team_size, "difficulty": proj.difficulty,
                    "tags": proj.tags or [], "keywords": proj.keywords or [],
                    "responsibilities": proj.responsibilities or [],
                    "impact_metrics": proj.impact_metrics or [],
                    "skills_used": proj.skills_used or [],
                    "highlights": proj.highlights or [],
                    "visibility": proj.visibility, "status": proj.status,
                    "start_date": proj.start_date, "end_date": proj.end_date,
                    "is_featured": proj.is_featured,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_skills(self) -> int:
        result = await self.session.execute(
            select(Skill).where(Skill.user_id == self.user_id, Skill.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for skill in items:
            text = f"{skill.name} {skill.category or ''} {skill.subcategory or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"skill:{skill.id}", entity_type="skill", entity_id=skill.id,
                properties={
                    "name": skill.name, "category": skill.category,
                    "subcategory": skill.subcategory, "level": skill.level,
                    "years_experience": skill.years_experience,
                    "last_used": skill.last_used, "is_primary": skill.is_primary,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_certificates(self) -> int:
        result = await self.session.execute(
            select(Certificate).where(Certificate.user_id == self.user_id, Certificate.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for cert in items:
            text = f"{cert.title} {cert.issuer} {' '.join(cert.skills or [])} {' '.join(cert.tags or [])} {cert.level or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"certificate:{cert.id}", entity_type="certificate", entity_id=cert.id,
                properties={
                    "title": cert.title, "issuer": cert.issuer,
                    "issue_date": cert.issue_date, "expiry_date": cert.expiry_date,
                    "credential_id": cert.credential_id,
                    "credential_url": cert.credential_url,
                    "skills": cert.skills or [], "level": cert.level,
                    "tags": cert.tags or [],
                    "verification_status": cert.verification_status,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_achievements(self) -> int:
        result = await self.session.execute(
            select(Achievement).where(Achievement.user_id == self.user_id, Achievement.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for ach in items:
            text = f"{ach.title} {ach.description or ''} {ach.organization or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"achievement:{ach.id}", entity_type="achievement", entity_id=ach.id,
                properties={
                    "title": ach.title, "description": ach.description,
                    "date": ach.date, "category": ach.category,
                    "organization": ach.organization, "url": ach.url,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_languages(self) -> int:
        result = await self.session.execute(
            select(Language).where(Language.user_id == self.user_id, Language.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for lang in items:
            text = f"{lang.name} {lang.proficiency or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"language:{lang.id}", entity_type="language", entity_id=lang.id,
                properties={
                    "name": lang.name, "proficiency": lang.proficiency,
                    "years": lang.years, "is_native": lang.is_native,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_publications(self) -> int:
        result = await self.session.execute(
            select(Publication).where(Publication.user_id == self.user_id, Publication.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for pub in items:
            text = f"{pub.title} {pub.description or ''} {pub.venue or ''} {' '.join(pub.authors or [])}"
            self.graph.add_node(KnowledgeNode(
                id=f"publication:{pub.id}", entity_type="publication", entity_id=pub.id,
                properties={
                    "title": pub.title, "authors": pub.authors or [],
                    "venue": pub.venue, "date": pub.date,
                    "url": pub.url, "doi": pub.doi,
                    "description": pub.description, "category": pub.category,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_awards(self) -> int:
        result = await self.session.execute(
            select(Award).where(Award.user_id == self.user_id, Award.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for award in items:
            text = f"{award.title} {award.description or ''} {award.issuer or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"award:{award.id}", entity_type="award", entity_id=award.id,
                properties={
                    "title": award.title, "issuer": award.issuer,
                    "date": award.date, "category": award.category,
                    "description": award.description, "url": award.url,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_social_links(self) -> int:
        result = await self.session.execute(
            select(SocialLink).where(SocialLink.user_id == self.user_id, SocialLink.deleted_at.is_(None))
        )
        items = result.scalars().all()
        for link in items:
            text = f"{link.platform} {link.username or ''} {link.display_name or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"social_link:{link.id}", entity_type="social_link", entity_id=link.id,
                properties={
                    "platform": link.platform, "url": link.url,
                    "username": link.username, "display_name": link.display_name,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_job_descriptions(self) -> int:
        result = await self.session.execute(
            select(JobDescription).where(JobDescription.user_id == self.user_id)
        )
        items = result.scalars().all()
        for jd in items:
            text = f"{jd.title or ''} {jd.company or ''} {jd.raw_text}"
            self.graph.add_node(KnowledgeNode(
                id=f"job_description:{jd.id}", entity_type="job_description", entity_id=jd.id,
                properties={
                    "title": jd.title, "company": jd.company,
                    "raw_text": jd.raw_text,
                    "parsed_json": jd.parsed_json,
                    "keywords": jd.keywords or [],
                    "requirements": jd.requirements or [],
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_resume_versions(self) -> int:
        result = await self.session.execute(
            select(ResumeVersion).where(ResumeVersion.user_id == self.user_id)
        )
        items = result.scalars().all()
        for rv in items:
            text = f"{rv.title} {rv.template_name or ''}"
            self.graph.add_node(KnowledgeNode(
                id=f"resume_version:{rv.id}", entity_type="resume_version", entity_id=rv.id,
                properties={
                    "title": rv.title, "template_name": rv.template_name,
                    "ats_score": rv.ats_score,
                    "reflection_iterations": rv.reflection_iterations,
                    "job_description_id": rv.job_description_id,
                    "is_final": rv.is_final,
                },
                text_repr=text.strip(),
            ))
        return len(items)

    async def _load_ats_reports(self) -> int:
        result = await self.session.execute(
            select(ATSReport).join(ResumeVersion).where(ResumeVersion.user_id == self.user_id)
        )
        items = result.scalars().all()
        for ats in items:
            text = f"ATS Report score {ats.score}"
            self.graph.add_node(KnowledgeNode(
                id=f"ats_report:{ats.id}", entity_type="ats_report", entity_id=ats.id,
                properties={
                    "resume_version_id": ats.resume_version_id,
                    "score": ats.score,
                    "keyword_score": ats.keyword_score,
                    "formatting_score": ats.formatting_score,
                    "impact_score": ats.impact_score,
                    "readability_score": ats.readability_score,
                    "coverage_score": ats.coverage_score,
                    "suggestions": ats.suggestions or [],
                },
                text_repr=text.strip(),
            ))
        return len(items)

    # ── Retrieval APIs ──────────────────────────────────────

    def search(self, request: RetrievalRequest) -> RetrievalResponse:
        """Hybrid search across the knowledge graph."""
        return hybrid_search(self.graph, request)

    def vector_search(self, query: str, entity_types: list[str] | None = None, top_k: int = 10) -> RetrievalResponse:
        """Vector similarity search."""
        return vector_search(self.graph, query, entity_types=entity_types, top_k=top_k)

    def keyword_search(self, query: str, entity_types: list[str] | None = None, top_k: int = 10) -> RetrievalResponse:
        """Keyword/text search."""
        return keyword_search(self.graph, query, entity_types=entity_types, top_k=top_k)

    def get_relevant(
        self,
        entity_type: str,
        query: str,
        jd_keywords: list[str] | None = None,
        jd_requirements: list[str] | None = None,
        top_k: int = 10,
        scoring_dimension: str | None = None,
    ) -> list[dict]:
        """Get most relevant entities of a specific type."""
        return get_relevant_entities(
            self.graph, query, entity_type,
            jd_keywords=jd_keywords, jd_requirements=jd_requirements,
            top_k=top_k, scoring_dimension=scoring_dimension,
        )

    def get_summary(self, dimensions: list[str] | None = None) -> dict:
        """Get comprehensive knowledge summary."""
        return get_knowledge_summary(self.graph, dimensions=dimensions)

    def get_graph_stats(self) -> dict:
        """Get graph statistics."""
        return self.graph.get_stats()

    def get_node(self, entity_type: str, entity_id: str) -> KnowledgeNode | None:
        """Get a specific node."""
        return self.graph.get_node(entity_type, entity_id)

    def get_neighbors(self, entity_type: str, entity_id: str, depth: int = 1) -> list[dict]:
        """Get related entities."""
        neighbors = self.graph.get_neighbors(entity_type, entity_id, max_depth=depth)
        return [
            {
                "entity_type": n.entity_type,
                "entity_id": n.entity_id,
                "scores": n.scores,
                "properties": {k: v for k, v in n.properties.items() if isinstance(v, (str, int, float, bool))},
            }
            for n in neighbors
        ]

    # ── Embedding Management ────────────────────────────────

    async def generate_all_embeddings(self) -> dict:
        """Generate embeddings for all entities. Returns counts per type."""
        from app.services.embeddings import generate_embedding, store_embedding

        counts = {}
        for node in self.graph._nodes.values():
            if not node.text_repr.strip():
                continue
            try:
                embedding_id = store_embedding(
                    entity_type=node.entity_type,
                    entity_id=node.entity_id,
                    text=node.text_repr,
                    tags=f"{node.entity_type},{','.join(str(v) for v in node.properties.values() if isinstance(v, str))[:200]}",
                )
                node.embedding_id = embedding_id
                node.embedding = generate_embedding(node.text_repr)
                counts[node.entity_type] = counts.get(node.entity_type, 0) + 1
            except Exception as e:
                logger.warning("engine.embedding.error", entity_type=node.entity_type, entity_id=node.entity_id, error=str(e))

        logger.info("engine.embeddings.generated", **counts)
        return counts

    async def update_entity_embedding(self, entity_type: str, entity_id: str) -> bool:
        """Regenerate embedding for a single entity after it changes."""
        from app.services.embeddings import generate_embedding, store_embedding

        node = self.graph.get_node(entity_type, entity_id)
        if not node:
            return False

        try:
            embedding_id = store_embedding(
                entity_type=entity_type,
                entity_id=entity_id,
                text=node.text_repr,
            )
            node.embedding_id = embedding_id
            node.embedding = generate_embedding(node.text_repr)
            return True
        except Exception as e:
            logger.warning("engine.embedding.update.error", entity_type=entity_type, error=str(e))
            return False

    async def regenerate_all_embeddings(self) -> dict:
        """Delete and regenerate all embeddings."""
        from app.db.lance import delete_embedding, count_embeddings

        # Delete existing embeddings
        for node in self.graph._nodes.values():
            if node.embedding_id:
                try:
                    delete_embedding(node.embedding_id)
                except Exception:
                    pass
                node.embedding_id = ""

        # Regenerate
        return await self.generate_all_embeddings()

    def get_embedding_status(self) -> dict:
        """Get embedding status for all entities."""
        status = {"total": 0, "with_embedding": 0, "without_embedding": 0, "by_type": {}}
        for node in self.graph._nodes.values():
            status["total"] += 1
            has_emb = bool(node.embedding_id)
            if has_emb:
                status["with_embedding"] += 1
            else:
                status["without_embedding"] += 1

            if node.entity_type not in status["by_type"]:
                status["by_type"][node.entity_type] = {"total": 0, "embedded": 0}
            status["by_type"][node.entity_type]["total"] += 1
            if has_emb:
                status["by_type"][node.entity_type]["embedded"] += 1

        return status
