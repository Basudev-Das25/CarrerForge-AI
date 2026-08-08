"""Canonical Resume Model — the JSON source of truth for every generated resume.

Every sentence must be traceable back to candidate evidence.
Every bullet must reference its evidence source with confidence scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger("careerforge.resume.canonical")


@dataclass
class BulletMetadata:
    """Metadata for a single bullet point — provenance tracking."""
    evidence_source: str = ""  # "experience", "project", "achievement", etc.
    entity_id: str = ""
    confidence: float = 0.0
    reason: str = ""
    knowledge_score: float = 0.0
    similarity_score: float = 0.0
    generation_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    prompt_version: str = ""


@dataclass
class ResumeSection:
    """A single section of the resume with metadata."""
    name: str
    items: list[dict[str, Any]] = field(default_factory=list)
    order: int = 0
    word_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalResume:
    """Complete structured resume — the single source of truth.

    This JSON representation is what gets rendered into templates.
    Every piece of content is tracked with provenance metadata.
    """
    # Identity
    id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: int = 1

    # Candidate info
    candidate_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""

    # Sections
    sections: list[ResumeSection] = field(default_factory=list)

    # Metadata
    blueprint_id: str = ""
    template_name: str = "modern"
    prompt_version: str = ""
    provider: str = ""
    model: str = ""
    generation_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Validation
    validation_report: dict[str, Any] = field(default_factory=dict)
    ats_score: float = 0.0

    # ── Builder Methods ──────────────────────────────────────

    def add_section(self, name: str, order: int, items: list[dict[str, Any]] | None = None) -> None:
        """Add a section to the resume."""
        self.sections.append(ResumeSection(
            name=name,
            items=items or [],
            order=order,
            word_count=sum(len(item.get("text", "").split()) for item in (items or [])),
        ))

    def add_bullet(
        self,
        section_name: str,
        text: str,
        evidence_source: str = "",
        entity_id: str = "",
        confidence: float = 0.0,
        reason: str = "",
        knowledge_score: float = 0.0,
        similarity_score: float = 0.0,
        prompt_version: str = "",
        provenance_highlights: list[str] | None = None,
    ) -> None:
        """Add a bullet point with full provenance tracking."""
        section = self._find_section(section_name)
        if section is None:
            section = ResumeSection(name=section_name, order=len(self.sections))
            self.sections.append(section)

        bullet = {
            "text": text,
            "metadata": {
                "evidence_source": evidence_source,
                "entity_id": entity_id,
                "confidence": confidence,
                "reason": reason,
                "knowledge_score": knowledge_score,
                "similarity_score": similarity_score,
                "generation_timestamp": datetime.now(UTC).isoformat(),
                "prompt_version": prompt_version,
                "provenance_highlights": provenance_highlights or [],
            },
        }
        section.items.append(bullet)
        section.word_count += len(text.split())

    def get_section(self, name: str) -> ResumeSection | None:
        """Get a section by name."""
        return self._find_section(name)

    def total_word_count(self) -> int:
        """Get total word count across all sections."""
        return sum(s.word_count for s in self.sections)

    def evidence_coverage(self) -> dict[str, int]:
        """Count unique evidence sources used across the resume."""
        sources: dict[str, int] = {}
        for section in self.sections:
            for item in section.items:
                meta = item.get("metadata", {})
                src = meta.get("evidence_source", "")
                eid = meta.get("entity_id", "")
                if src and eid:
                    key = f"{src}:{eid}"
                    sources[key] = sources.get(key, 0) + 1
        return sources

    def _find_section(self, name: str) -> ResumeSection | None:
        for section in self.sections:
            if section.name.lower() == name.lower():
                return section
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON storage."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "version": self.version,
            "candidate_name": self.candidate_name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin_url": self.linkedin_url,
            "github_url": self.github_url,
            "portfolio_url": self.portfolio_url,
            "sections": [
                {
                    "name": s.name,
                    "items": s.items,
                    "order": s.order,
                    "word_count": s.word_count,
                }
                for s in sorted(self.sections, key=lambda x: x.order)
            ],
            "blueprint_id": self.blueprint_id,
            "template_name": self.template_name,
            "prompt_version": self.prompt_version,
            "provider": self.provider,
            "model": self.model,
            "generation_timestamp": self.generation_timestamp,
            "validation_report": self.validation_report,
            "ats_score": self.ats_score,
            "total_word_count": self.total_word_count(),
            "evidence_coverage": self.evidence_coverage(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CanonicalResume:
        sections = []
        for s in data.get("sections", []):
            sections.append(ResumeSection(
                name=s.get("name", ""),
                items=s.get("items", []),
                order=s.get("order", 0),
                word_count=s.get("word_count", 0),
            ))

        return cls(
            id=data.get("id", ""),
            created_at=data.get("created_at", ""),
            version=data.get("version", 1),
            candidate_name=data.get("candidate_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            location=data.get("location", ""),
            linkedin_url=data.get("linkedin_url", ""),
            github_url=data.get("github_url", ""),
            portfolio_url=data.get("portfolio_url", ""),
            sections=sections,
            blueprint_id=data.get("blueprint_id", ""),
            template_name=data.get("template_name", "modern"),
            prompt_version=data.get("prompt_version", ""),
            provider=data.get("provider", ""),
            model=data.get("model", ""),
            generation_timestamp=data.get("generation_timestamp", ""),
            validation_report=data.get("validation_report", {}),
            ats_score=data.get("ats_score", 0.0),
        )
