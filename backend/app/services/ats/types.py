"""ATS Intelligence types — data structures for analysis, scoring, and optimization."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class CategoryScore:
    """Score for a single analysis category."""
    name: str
    score: float  # 0-100
    weight: float = 1.0
    details: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "score": round(self.score, 1), "weight": self.weight,
                "details": self.details, "suggestions": self.suggestions}


@dataclass
class ATSReport:
    """Complete ATS analysis report."""
    id: str = ""
    resume_id: str = ""
    job_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Overall
    overall_score: float = 0.0
    sections: list[CategoryScore] = field(default_factory=list)

    # Keyword analysis
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    keyword_density: float = 0.0

    # Semantic matching
    semantic_score: float = 0.0
    skill_similarity: float = 0.0
    experience_relevance: float = 0.0
    industry_alignment: float = 0.0

    # Recruiter metrics
    readability_score: float = 0.0
    impact_score: float = 0.0
    achievement_score: float = 0.0
    specificity_score: float = 0.0

    # Evidence
    evidence_coverage: float = 0.0
    unsupported_claims: int = 0

    # Suggestions
    suggestions: list[dict[str, Any]] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "resume_id": self.resume_id, "job_id": self.job_id,
            "timestamp": self.timestamp, "overall_score": round(self.overall_score, 1),
            "sections": [s.to_dict() for s in self.sections],
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "keyword_density": round(self.keyword_density, 3),
            "semantic_score": round(self.semantic_score, 1),
            "skill_similarity": round(self.skill_similarity, 1),
            "experience_relevance": round(self.experience_relevance, 1),
            "industry_alignment": round(self.industry_alignment, 1),
            "readability_score": round(self.readability_score, 1),
            "impact_score": round(self.impact_score, 1),
            "achievement_score": round(self.achievement_score, 1),
            "specificity_score": round(self.specificity_score, 1),
            "evidence_coverage": round(self.evidence_coverage, 3),
            "unsupported_claims": self.unsupported_claims,
            "suggestions": self.suggestions,
            "missing_sections": self.missing_sections,
        }


@dataclass
class OptimizationItem:
    """A single optimization suggestion."""
    priority: str = "medium"  # high, medium, low
    section: str = ""
    category: str = ""
    description: str = ""
    expected_improvement: float = 0.0
    evidence_used: list[str] = field(default_factory=list)
    confidence: float = 0.0
    recruiter_impact: str = ""

    def to_dict(self) -> dict:
        return {
            "priority": self.priority, "section": self.section, "category": self.category,
            "description": self.description,
            "expected_improvement": round(self.expected_improvement, 1),
            "evidence_used": self.evidence_used,
            "confidence": round(self.confidence, 2),
            "recruiter_impact": self.recruiter_impact,
        }


@dataclass
class OptimizationPlan:
    """Full optimization plan for a resume."""
    id: str = ""
    resume_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    current_score: float = 0.0
    target_score: float = 0.0
    items: list[OptimizationItem] = field(default_factory=list)
    iterations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "resume_id": self.resume_id, "timestamp": self.timestamp,
            "current_score": round(self.current_score, 1),
            "target_score": round(self.target_score, 1),
            "items": [i.to_dict() for i in self.items],
            "iterations": self.iterations,
        }


@dataclass
class ComparisonResult:
    """Result of comparing two resumes or a resume vs a job."""
    label_a: str = ""
    label_b: str = ""
    score_a: float = 0.0
    score_b: float = 0.0
    score_change: float = 0.0
    added_keywords: list[str] = field(default_factory=list)
    removed_keywords: list[str] = field(default_factory=list)
    section_diffs: list[dict[str, Any]] = field(default_factory=list)
    semantic_improvement: float = 0.0
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "label_a": self.label_a, "label_b": self.label_b,
            "score_a": round(self.score_a, 1), "score_b": round(self.score_b, 1),
            "score_change": round(self.score_change, 1),
            "added_keywords": self.added_keywords,
            "removed_keywords": self.removed_keywords,
            "section_diffs": self.section_diffs,
            "semantic_improvement": round(self.semantic_improvement, 1),
            "summary": self.summary,
        }
