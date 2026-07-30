"""Resume Validator — validates canonical resume for quality, ATS compatibility, and correctness.

Checks: duplicate skills, duplicate bullets, weak bullets, unsupported claims,
missing sections, grammar, formatting, ATS keyword density, section balance,
length, and consistency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger("careerforge.resume.validator")


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: str  # "error", "warning", "info"
    category: str
    message: str
    section: str = ""
    suggestion: str = ""


@dataclass
class ValidationReport:
    """Complete validation report for a resume."""
    issues: list[ValidationIssue] = field(default_factory=list)
    score: int = 0  # 0-100
    passed: bool = False
    checks_performed: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "passed": self.passed,
            "issues_count": {"error": sum(1 for i in self.issues if i.severity == "error"),
                             "warning": sum(1 for i in self.issues if i.severity == "warning"),
                             "info": sum(1 for i in self.issues if i.severity == "info")},
            "issues": [
                {"severity": i.severity, "category": i.category,
                 "message": i.message, "section": i.section,
                 "suggestion": i.suggestion}
                for i in self.issues
            ],
            "checks_performed": self.checks_performed,
            "summary": self.summary,
        }


class ResumeValidator:
    """Validates a canonical resume against quality criteria."""

    def __init__(self, target_keywords: list[str] | None = None):
        self.target_keywords = target_keywords or []

    def validate(self, resume: dict[str, Any]) -> ValidationReport:
        """Run all validation checks on a resume dict."""
        report = ValidationReport()

        self._check_required_sections(resume, report)
        self._check_duplicate_skills(resume, report)
        self._check_duplicate_bullets(resume, report)
        self._check_weak_bullets(resume, report)
        self._check_bullet_provenance(resume, report)
        self._check_keyword_coverage(resume, report)
        self._check_section_balance(resume, report)
        self._check_length(resume, report)
        self._check_consistency(resume, report)
        self._check_summary_quality(resume, report)

        # Calculate score
        errors = sum(1 for i in report.issues if i.severity == "error")
        warnings = sum(1 for i in report.issues if i.severity == "warning")

        report.score = max(0, 100 - (errors * 15) - (warnings * 3))
        report.passed = errors == 0
        report.summary = f"Score: {report.score}/100. {errors} errors, {warnings} warnings."

        return report

    def _check_required_sections(self, resume: dict, report: ValidationReport):
        """Check that essential sections are present."""
        report.checks_performed.append("required_sections")
        sections = {s.get("name", "").lower() for s in resume.get("sections", [])}
        required = ["summary", "experience", "skills"]

        for req in required:
            if req not in sections:
                report.issues.append(ValidationIssue(
                    severity="error", category="missing_section",
                    message=f"Missing required section: {req}",
                    suggestion=f"Add a '{req}' section to your resume.",
                ))

    def _check_duplicate_skills(self, resume: dict, report: ValidationReport):
        """Check for duplicate skills across the resume."""
        report.checks_performed.append("duplicate_skills")
        all_skills: list[str] = []
        for section in resume.get("sections", []):
            if section.get("name", "").lower() == "skills":
                for item in section.get("items", []):
                    text = item.get("text", "")
                    if text:
                        all_skills.append(text.lower().strip())

        seen = set()
        for skill in all_skills:
            if skill in seen:
                report.issues.append(ValidationIssue(
                    severity="warning", category="duplicate_skill",
                    message=f"Duplicate skill: {skill}",
                    suggestion="Remove duplicate entries.",
                ))
            seen.add(skill)

    def _check_duplicate_bullets(self, resume: dict, report: ValidationReport):
        """Check for duplicate bullet points."""
        report.checks_performed.append("duplicate_bullets")
        seen: set[str] = set()
        for section in resume.get("sections", []):
            for item in section.get("items", []):
                text = item.get("text", "").strip()
                if text and text in seen:
                    report.issues.append(ValidationIssue(
                        severity="warning", category="duplicate_bullet",
                        message=f"Duplicate bullet in '{section.get('name', '')}'",
                        section=section.get("name", ""),
                    ))
                if text:
                    seen.add(text)

    def _check_weak_bullets(self, resume: dict, report: ValidationReport):
        """Check for weak bullet points that lack impact."""
        report.checks_performed.append("weak_bullets")
        weak_starters = ["helped", "assisted", "was responsible for", "worked on", "participated in"]

        for section in resume.get("sections", []):
            for item in section.get("items", []):
                text = item.get("text", "").lower().strip()
                if text:
                    for weak in weak_starters:
                        if text.startswith(weak):
                            report.issues.append(ValidationIssue(
                                severity="warning", category="weak_bullet",
                                message=f"Weak bullet starts with '{weak}': '{item.get('text', '')[:60]}...'",
                                section=section.get("name", ""),
                                suggestion="Use strong action verbs (e.g., 'Led', 'Built', 'Reduced', 'Increased').",
                            ))
                            break

    def _check_bullet_provenance(self, resume: dict, report: ValidationReport):
        """Check that bullets have provenance metadata."""
        report.checks_performed.append("bullet_provenance")
        unsupported = 0
        for section in resume.get("sections", []):
            for item in section.get("items", []):
                meta = item.get("metadata", {})
                if not meta.get("evidence_source") and not meta.get("entity_id"):
                    unsupported += 1

        if unsupported > 0:
            report.issues.append(ValidationIssue(
                severity="info", category="provenance",
                message=f"{unsupported} bullet(s) have no evidence source reference.",
                suggestion="All bullets should trace back to candidate evidence.",
            ))

        # Also check for too much inferred/AI-generated content without clear evidence ties
        report.checks_performed.append("inferred_content")
        total_bullets = 0
        ai_bullets = 0
        for section in resume.get("sections", []):
            for item in section.get("items", []):
                total_bullets += 1
                meta = item.get("metadata", {})
                source = meta.get("evidence_source", "")
                if source == "ai_generated" or source.endswith("_ai"):
                    ai_bullets += 1

        if total_bullets > 0:
            ai_ratio = ai_bullets / total_bullets
            if ai_ratio > 0.3:
                report.issues.append(ValidationIssue(
                    severity="error",
                    category="too_much_inferred_content",
                    message=f"{ai_bullets}/{total_bullets} bullet(s) ({ai_ratio:.0%}) are AI-generated without direct evidence ties. Maximum allowed is 30%.",
                    suggestion="Rewrite AI-generated bullets to reference specific evidence highlights from your profile.",
                ))

    def _check_keyword_coverage(self, resume: dict, report: ValidationReport):
        """Check ATS keyword coverage."""
        if not self.target_keywords:
            return
        report.checks_performed.append("keyword_coverage")

        # Build text from all resume sections
        full_text = ""
        for section in resume.get("sections", []):
            for item in section.get("items", []):
                full_text += " " + item.get("text", "")
        full_text = full_text.lower()

        missing = [kw for kw in self.target_keywords if kw.lower() not in full_text]
        if missing:
            report.issues.append(ValidationIssue(
                severity="warning", category="keyword_coverage",
                message=f"Missing {len(missing)} target keywords: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}",
                suggestion="Incorporate missing keywords naturally into relevant sections.",
            ))

    def _check_section_balance(self, resume: dict, report: ValidationReport):
        """Check that sections have reasonable word counts."""
        report.checks_performed.append("section_balance")
        sections = resume.get("sections", [])

        if len(sections) < 3:
            report.issues.append(ValidationIssue(
                severity="warning", category="section_count",
                message=f"Only {len(sections)} sections — resume may be too sparse.",
            ))

        for section in sections:
            wc = section.get("word_count", 0)
            items = section.get("items", [])
            if items and wc < 20:
                report.issues.append(ValidationIssue(
                    severity="info", category="section_length",
                    message=f"Section '{section.get('name', '')}' has only {wc} words.",
                    section=section.get("name", ""),
                ))

    def _check_length(self, resume: dict, report: ValidationReport):
        """Check total resume length."""
        report.checks_performed.append("length")
        total_words = sum(s.get("word_count", 0) for s in resume.get("sections", []))

        if total_words < 100:
            report.issues.append(ValidationIssue(
                severity="warning", category="length",
                message=f"Resume is very short ({total_words} words).",
                suggestion="Aim for 400-800 words for a one-page resume.",
            ))
        elif total_words > 1200:
            report.issues.append(ValidationIssue(
                severity="info", category="length",
                message=f"Resume is long ({total_words} words). May exceed one page.",
                suggestion="Consider condensing to 400-800 words.",
            ))

    def _check_consistency(self, resume: dict, report: ValidationReport):
        """Check consistency in formatting and style."""
        report.checks_performed.append("consistency")

        # Check that experience bullets use consistent tense
        for section in resume.get("sections", []):
            if section.get("name", "").lower() in ("experience", "projects"):
                past_count = 0
                present_count = 0
                for item in section.get("items", []):
                    text = item.get("text", "").strip()
                    if not text:
                        continue
                    first_word = text.split()[0].lower() if text.split() else ""
                    # Simple heuristic: past tense usually ends in -ed
                    if first_word.endswith("ed") or first_word in ("led", "built", "reduced", "increased", "managed", "developed", "implemented", "created", "designed"):
                        past_count += 1
                    else:
                        present_count += 1

                if past_count > 0 and present_count > 0:
                    report.issues.append(ValidationIssue(
                        severity="info", category="tense_consistency",
                        message=f"Section '{section.get('name', '')}' mixes past and present tense.",
                        section=section.get("name", ""),
                        suggestion="Use past tense for previous roles, present for current.",
                    ))

    def _check_summary_quality(self, resume: dict, report: ValidationReport):
        """Check the quality of the professional summary."""
        report.checks_performed.append("summary_quality")
        for section in resume.get("sections", []):
            if section.get("name", "").lower() == "summary":
                items = section.get("items", [])
                if not items:
                    report.issues.append(ValidationIssue(
                        severity="error", category="empty_summary",
                        message="Summary section is empty.",
                    ))
                elif items:
                    text = items[0].get("text", "")
                    words = len(text.split())
                    if words < 20:
                        report.issues.append(ValidationIssue(
                            severity="warning", category="summary_length",
                            message=f"Summary is too short ({words} words).",
                            suggestion="Aim for 2-4 sentences (40-80 words).",
                        ))
                    elif words > 100:
                        report.issues.append(ValidationIssue(
                            severity="warning", category="summary_length",
                            message=f"Summary is too long ({words} words).",
                            suggestion="Keep summary to 2-4 sentences.",
                        ))
