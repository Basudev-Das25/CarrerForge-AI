"""Resume Pipeline — orchestrates the complete resume generation flow.

Job Description → Blueprint → Evidence → Writing → Validation → Typst → PDF
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.orchestrator import orchestrator
from app.services.ai.providers.base import ChatMessage, MessageRole
from app.services.evidence.engine import EvidenceEngine
from app.services.job.intelligence import JobIntelligence, JobProfile
from app.services.knowledge.engine import KnowledgeEngine
from app.services.resume.blueprint import ResumeBlueprint
from app.services.resume.canonical import CanonicalResume
from app.services.resume.validator import ResumeValidator

logger = structlog.get_logger("careerforge.resume.pipeline")


class ResumePipeline:
    """Complete resume generation pipeline.

    Transforms a Job Description into a professional, ATS-optimized,
    evidence-backed resume. Every sentence is traceable.
    """

    def __init__(self, session: AsyncSession, user_id: str = "default"):
        self.session = session
        self.user_id = user_id
        self.job_intelligence = JobIntelligence()

    async def generate(self, job_description: str, template: str = "modern", max_iterations: int = 3) -> dict[str, Any]:
        """Execute the full resume generation pipeline.

        Returns dict with: blueprint, resume, validation, versions.
        """
        logger.info("pipeline.start")

        # Step 1: Parse Job Description
        jd_profile = await self.job_intelligence.parse_job_description(job_description)
        logger.info("pipeline.jd_parsed", title=jd_profile.job_title, company=jd_profile.company)

        # Step 2: Build Knowledge Graph
        ke = KnowledgeEngine(session=self.session, user_id=self.user_id)
        await ke.build()

        # Step 3: Generate Evidence Bundle
        evidence_engine = EvidenceEngine(ke)
        evidence_bundle = await evidence_engine.generate_evidence_bundle(jd_profile)
        logger.info("pipeline.evidence_built", total=evidence_bundle.metadata.get("total_evidence", 0))

        # Step 4: Generate Blueprint
        blueprint = await self._generate_blueprint(jd_profile, evidence_bundle)
        logger.info("pipeline.blueprint_generated", sections=len(blueprint.sections))

        # Step 5: Write Resume
        resume = await self._write_resume(blueprint, jd_profile, evidence_bundle, template)
        logger.info("pipeline.resume_written", words=resume.total_word_count())

        # Step 6: Validate
        validator = ResumeValidator(target_keywords=jd_profile.keywords + jd_profile.ats_keywords)
        validation = validator.validate(resume.to_dict())
        resume.validation_report = validation.to_dict()
        resume.ats_score = validation.score
        logger.info("pipeline.validated", score=validation.score, errors=sum(1 for i in validation.issues if i.severity == "error"))

        # Step 7: Reflection loop (if needed and errors exist)
        iteration = 0
        while not validation.passed and iteration < max_iterations:
            iteration += 1
            logger.info("pipeline.reflect", iteration=iteration)
            resume = await self._reflect(resume, validation, jd_profile, evidence_bundle)
            validation = validator.validate(resume.to_dict())
            resume.validation_report = validation.to_dict()
            resume.ats_score = validation.score

        # Step 8: Store version
        version_id = await self._store_version(resume, blueprint, jd_profile, template)

        logger.info("pipeline.complete", ats_score=resume.ats_score, word_count=resume.total_word_count())

        return {
            "version_id": version_id,
            "blueprint": blueprint.to_dict(),
            "resume": resume.to_dict(),
            "validation": validation.to_dict(),
        }

    async def generate_blueprint(self, job_description: str) -> dict[str, Any]:
        """Generate only the blueprint without writing the resume."""
        jd_profile = await self.job_intelligence.parse_job_description(job_description)
        ke = KnowledgeEngine(session=self.session, user_id=self.user_id)
        await ke.build()
        evidence_engine = EvidenceEngine(ke)
        evidence_bundle = await evidence_engine.generate_evidence_bundle(jd_profile)
        blueprint = await self._generate_blueprint(jd_profile, evidence_bundle)
        return blueprint.to_dict()

    async def _generate_blueprint(self, jd_profile: JobProfile, evidence_bundle: Any) -> ResumeBlueprint:
        """Generate the resume blueprint via AI."""
        evidence_summary = evidence_bundle.to_dict()

        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an expert resume strategist for CareerForge AI. "
                        "Given a job profile and candidate evidence, plan the optimal resume structure. "
                        "Return a JSON object with: "
                        "target_role, target_industry, resume_strategy (technical/executive/career-change), "
                        "summary_focus, tone (professional/casual/academic), "
                        "sections (list of {name, priority, word_count_target, key_themes, evidence_ids}), "
                        "keywords_to_emphasize, keywords_missing, "
                        "ats_coverage_estimate (0-100), confidence_score (0-1), reasoning. "
                        "Return ONLY valid JSON."
                    ),
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=f"Job Profile:\n{jd_profile.to_dict()}\n\nEvidence:\n{evidence_summary}",
                ),
            ],
            temperature=0.2,
            max_tokens=4096,
            use_cache=False,
        )

        # Parse AI response
        import json
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            plan_data = json.loads(text[start:end]) if start >= 0 else {}
        except (json.JSONDecodeError, ValueError):
            plan_data = {}

        # Build blueprint
        blueprint = ResumeBlueprint(
            id=str(uuid.uuid4()),
            target_role=plan_data.get("target_role", jd_profile.job_title),
            target_industry=plan_data.get("target_industry", jd_profile.industry),
            company=jd_profile.company,
            resume_strategy=plan_data.get("resume_strategy", "technical"),
            summary_focus=plan_data.get("summary_focus", ""),
            tone=plan_data.get("tone", "professional"),
            sections=plan_data.get("sections", []),
            keywords_to_emphasize=plan_data.get("keywords_to_emphasize", jd_profile.keywords),
            keywords_missing=plan_data.get("keywords_missing", []),
            ats_coverage_estimate=plan_data.get("ats_coverage_estimate", 0),
            confidence_score=plan_data.get("confidence_score", 0.5),
            reasoning=plan_data.get("reasoning", ""),
            prompt_version="1.0",
            model_used=response.model,
        )

        return blueprint

    async def _write_resume(
        self,
        blueprint: ResumeBlueprint,
        jd_profile: JobProfile,
        evidence_bundle: Any,
        template: str,
    ) -> CanonicalResume:
        """Write resume content section by section using the blueprint."""
        # Get candidate info
        from sqlalchemy import select

        from app.db.models import User
        result = await self.session.execute(select(User).where(User.id == self.user_id))
        user = result.scalar_one_or_none()

        resume = CanonicalResume(
            id=str(uuid.uuid4()),
            candidate_name=user.full_name if user else "",
            email=user.email if user else "",
            phone=user.phone if user else "",
            location=user.location if user else "",
            linkedin_url=user.linkedin_url if user else "",
            github_url=user.github_url if user else "",
            portfolio_url=user.portfolio_url if user else "",
            blueprint_id=blueprint.id,
            template_name=template,
        )

        # Write each section
        sections_to_write = blueprint.sections or [
            {"name": "Summary", "word_count_target": 60},
            {"name": "Experience", "word_count_target": 200},
            {"name": "Projects", "word_count_target": 150},
            {"name": "Skills", "word_count_target": 50},
            {"name": "Education", "word_count_target": 40},
            {"name": "Certificates", "word_count_target": 40},
        ]

        for i, section_plan in enumerate(sections_to_write):
            section_name = section_plan.get("name", "")
            word_target = section_plan.get("word_count_target", 100)

            if section_name.lower() in ("skills", "education", "certificates", "languages", "links"):
                # These sections are written directly from evidence
                await self._write_structured_section(resume, section_name, evidence_bundle, jd_profile, i)
            else:
                # Summary, Experience, Projects use AI writing
                await self._write_ai_section(resume, section_name, word_target, evidence_bundle, jd_profile, blueprint, i)

        return resume

    async def _write_ai_section(
        self,
        resume: CanonicalResume,
        section_name: str,
        word_count: int,
        evidence_bundle: Any,
        jd_profile: JobProfile,
        blueprint: ResumeBlueprint,
        order: int,
    ) -> None:
        """Use AI to write a resume section."""
        # Gather relevant evidence
        evidence_items = []
        if section_name.lower() == "summary":
            evidence_items = [{"text": f"Candidate: {resume.candidate_name}, experience summary: {jd_profile.summary}"}]
        elif section_name.lower() == "experience":
            for ev in evidence_bundle.experience:
                p = ev.properties
                evidence_items.append({
                    "text": f"{p.get('title', '')} at {p.get('company', '')} ({p.get('start_date', '')} - {p.get('end_date', 'Present')}): {p.get('description', '')}",
                    "highlights": p.get("highlights", []),
                    "skills": p.get("skills_used", []),
                    "confidence": ev.confidence_score,
                })
        elif section_name.lower() == "projects":
            for ev in evidence_bundle.projects:
                p = ev.properties
                evidence_items.append({
                    "text": f"{p.get('name', '')}: {p.get('description', '')}",
                    "tech": p.get("tech_stack", []),
                    "highlights": p.get("highlights", []),
                    "confidence": ev.confidence_score,
                })

        evidence_str = str(evidence_items)[:3000]
        keywords = ", ".join(blueprint.keywords_to_emphasize[:20])

        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an expert resume writer. Write the resume section below. "
                        "Rules: Use strong action verbs, quantify achievements, "
                        "incorporate keywords naturally, do NOT fabricate. "
                        "Return structured text with clear bullet points."
                    ),
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=(
                        f"Section: {section_name}\n"
                        f"Target words: {word_count}\n"
                        f"Tone: {blueprint.tone}\n"
                        f"Keywords to include: {keywords}\n"
                        f"Evidence:\n{evidence_str}"
                    ),
                ),
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        # Parse bullets from response
        lines = response.content.strip().split("\n")
        bullets = []
        for line in lines:
            line = line.strip()
            if line.startswith(("•", "-", "*", "–")):
                text = line.lstrip("•-*– ").strip()
                if text:
                    bullets.append(text)
            elif line and len(line) > 20 and not line.startswith("#"):
                bullets.append(line)

        if not bullets:
            bullets = [response.content.strip()[:500]]

        # Add bullets with provenance
        for text in bullets:
            resume.add_bullet(
                section_name=section_name,
                text=text,
                evidence_source="ai_generated",
                prompt_version="1.0",
            )

    async def _write_structured_section(
        self,
        resume: CanonicalResume,
        section_name: str,
        evidence_bundle: Any,
        jd_profile: JobProfile,
        order: int,
    ) -> None:
        """Write sections that can be generated directly from evidence (no AI needed)."""
        section_lower = section_name.lower()

        if section_lower == "skills":
            seen = set()
            for ev in evidence_bundle.skills:
                name = ev.properties.get("name", "")
                if name and name not in seen:
                    level = ev.properties.get("level", "")
                    text = f"{name}" + (f" ({level})" if level else "")
                    resume.add_bullet("Skills", text, "skill", ev.entity_id, ev.confidence_score, "from profile")
                    seen.add(name)

        elif section_lower == "education":
            for ev in evidence_bundle.skills:  # Skills also come from education
                pass  # Education is already in the user profile
            # Add from the actual education evidence if available
            from sqlalchemy import select

            from app.db.models import Education
            result = await self.session.execute(
                select(Education).where(Education.user_id == self.user_id, Education.deleted_at.is_(None))
            )
            for edu in result.scalars().all():
                text = f"{edu.degree}"
                if edu.field_of_study:
                    text += f" in {edu.field_of_study}"
                text += f" — {edu.institution}"
                if edu.gpa:
                    text += f" (GPA: {edu.gpa})"
                resume.add_bullet("Education", text, "education", edu.id, 1.0, "from profile")

        elif section_lower == "certificates":
            for ev in evidence_bundle.certificates:
                p = ev.properties
                text = f"{p.get('title', '')} — {p.get('issuer', '')}"
                if p.get("issue_date"):
                    text += f" ({p.get('issue_date', '')})"
                resume.add_bullet("Certificates", text, "certificate", ev.entity_id, ev.confidence_score, "from profile")

        elif section_lower == "languages":
            for ev in evidence_bundle.languages:
                p = ev.properties
                text = f"{p.get('name', '')}"
                if p.get("proficiency"):
                    text += f" — {p.get('proficiency', '')}"
                if p.get("is_native"):
                    text += " (Native)"
                resume.add_bullet("Languages", text, "language", ev.entity_id, ev.confidence_score, "from profile")

        elif section_lower == "achievements":
            for ev in evidence_bundle.achievements:
                p = ev.properties
                text = p.get("title", "")
                if p.get("organization"):
                    text += f" — {p.get('organization', '')}"
                if p.get("date"):
                    text += f" ({p.get('date', '')})"
                resume.add_bullet("Achievements", text, "achievement", ev.entity_id, ev.confidence_score, "from profile")

        elif section_lower == "awards":
            for ev in evidence_bundle.awards:
                p = ev.properties
                text = p.get("title", "")
                if p.get("issuer"):
                    text += f" — {p.get('issuer', '')}"
                resume.add_bullet("Awards", text, "award", ev.entity_id, ev.confidence_score, "from profile")

        elif section_lower == "publications":
            for ev in evidence_bundle.publications:
                p = ev.properties
                text = p.get("title", "")
                if p.get("venue"):
                    text += f" — {p.get('venue', '')}"
                if p.get("date"):
                    text += f" ({p.get('date', '')})"
                resume.add_bullet("Publications", text, "publication", ev.entity_id, ev.confidence_score, "from profile")

        elif section_lower == "links":
            for ev in evidence_bundle.publications:
                pass  # Links come from user profile social_links
            from sqlalchemy import select

            from app.db.models import SocialLink
            result = await self.session.execute(
                select(SocialLink).where(SocialLink.user_id == self.user_id, SocialLink.deleted_at.is_(None))
            )
            for link in result.scalars().all():
                text = f"{link.platform}: {link.url}"
                resume.add_bullet("Links", text, "social_link", link.id, 1.0, "from profile")

    async def _reflect(
        self,
        resume: CanonicalResume,
        validation: Any,
        jd_profile: JobProfile,
        evidence_bundle: Any,
    ) -> CanonicalResume:
        """Improve resume based on validation feedback."""
        import json

        feedback = validation.to_dict()
        current = json.dumps(resume.to_dict())[:3000]

        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "Improve this resume based on validation feedback. "
                        "Fix errors, strengthen weak bullets, incorporate missing keywords. "
                        "Return the full improved resume as a JSON object with the same structure."
                    ),
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=f"Resume:\n{current}\n\nFeedback:\n{json.dumps(feedback)[:2000]}",
                ),
            ],
            temperature=0.3,
            max_tokens=4096,
        )

        # Try to parse improved resume
        try:
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            start = text.find("{")
            end = text.rfind("}") + 1
            improved = json.loads(text[start:end])
            return CanonicalResume.from_dict({**resume.to_dict(), **improved})
        except Exception:
            # If parsing fails, return original with minor improvements
            logger.warning("pipeline.reflect.parse_failed")
            return resume

    async def _store_version(self, resume: CanonicalResume, blueprint: ResumeBlueprint, jd_profile: JobProfile, template: str) -> str:
        """Store the generated resume as a version in the database."""

        from app.db.models import ResumeVersion

        version = ResumeVersion(
            user_id=self.user_id,
            title=f"Resume for {jd_profile.job_title or 'Unknown Position'} at {jd_profile.company or 'Unknown Company'}",
            template_name=template,
            content_json={
                "resume": resume.to_dict(),
                "blueprint": blueprint.to_dict(),
                "job_profile": jd_profile.to_dict(),
            },
            ats_score=resume.ats_score,
            reflection_iterations=0,
        )
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version.id
