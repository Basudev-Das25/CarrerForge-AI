"""ATS Intelligence Engine — comprehensive resume analysis and optimization.

Analyzes resumes against job descriptions, generates detailed reports,
optimizes content iteratively, and validates every recommendation against evidence.
"""

from __future__ import annotations

import re
import uuid
import structlog
from typing import Any

from app.services.ai.orchestrator import orchestrator
from app.services.ai.providers.base import ChatMessage, MessageRole
from app.services.ats.types import ATSReport, CategoryScore, OptimizationItem, OptimizationPlan, ComparisonResult

logger = structlog.get_logger("careerforge.ats.engine")

# ── Keyword Extraction Patterns ──────────────────────────

ACTION_VERBS = [
    "achieved", "accelerated", "architected", "automated", "built", "conceptualized",
    "consolidated", "constructed", "decreased", "delivered", "designed", "developed",
    "directed", "drove", "eliminated", "engineered", "established", "expanded",
    "facilitated", "formulated", "generated", "grew", "headquartered", "hired",
    "identified", "implemented", "improved", "increased", "initiated", "integrated",
    "introduced", "investigated", "launched", "led", "lowered", "managed",
    "maximized", "mentored", "minimized", "modernized", "negotiated", "optimized",
    "orchestrated", "organized", "oversaw", "pioneered", "planned", "produced",
    "programmed", "proposed", "provided", "reduced", "redesigned", "refactored",
    "reinforced", "reorganized", "replaced", "restored", "revamped", "revitalized",
    "saved", "spearheaded", "standardized", "streamlined", "strengthened",
    "structured", "supervised", "surpassed", "transformed", "troubleshot",
    "unified", "upgraded", "utilized", "validating", "validated", "varied",
    "verified", "virtualized", "won",
]


class ATSEngine:
    """Comprehensive ATS analysis, scoring, and optimization engine."""

    def __init__(self):
        pass

    # ── Full Analysis Pipeline ───────────────────────────

    async def analyze(
        self,
        resume: dict[str, Any],
        job_profile: dict[str, Any],
    ) -> ATSReport:
        """Run complete ATS analysis pipeline."""
        report = ATSReport(
            id=str(uuid.uuid4()),
            resume_id=resume.get("id", ""),
        )

        sections_data = resume.get("sections", [])
        jd_keywords = job_profile.get("keywords", []) + job_profile.get("ats_keywords", [])
        jd_required = job_profile.get("required_skills", []) + job_profile.get("technologies", [])

        # 1. Build full text from resume
        resume_text = self._extract_full_text(sections_data)

        # 2. Keyword analysis
        matched, missing, density = self._analyze_keywords(resume_text, jd_keywords + jd_required)
        report.matched_keywords = matched
        report.missing_keywords = missing
        report.keyword_density = density

        # 3. Section completeness
        section_report = self._analyze_sections(sections_data, job_profile)
        report.sections = section_report

        # 4. Format quality
        format_score = self._analyze_formatting(sections_data)

        # 5. Bullet quality
        bullet_score, bullet_suggestions = self._analyze_bullets(sections_data)

        # 6. Recruiter metrics
        recruiter = self._analyze_recruiter_metrics(sections_data, resume_text)
        report.readability_score = recruiter["readability"]
        report.impact_score = recruiter["impact"]
        report.achievement_score = recruiter["achievement"]
        report.specificity_score = recruiter["specificity"]

        # 7. Evidence verification
        evidence_cov, unsupported = self._verify_evidence(sections_data)
        report.evidence_coverage = evidence_cov
        report.unsupported_claims = unsupported

        # 8. Compute overall score (weighted)
        scores = {
            "keywords": min(len(matched) / max(len(jd_keywords + jd_required), 1) * 100, 100),
            "sections": sum(s.score for s in section_report) / max(len(section_report), 1),
            "formatting": format_score,
            "bullets": bullet_score,
            "readability": recruiter["readability"],
            "impact": recruiter["impact"],
            "specificity": recruiter["specificity"],
        }
        weights = {"keywords": 0.25, "sections": 0.15, "formatting": 0.10,
                    "bullets": 0.15, "readability": 0.10, "impact": 0.15, "specificity": 0.10}
        report.overall_score = sum(scores[k] * weights[k] for k in scores)

        # 9. Missing sections
        required = set(job_profile.get("required_sections", []))
        present = {s.get("name", "").lower() for s in sections_data}
        report.missing_sections = list(required - present)

        # 10. Suggestions
        report.suggestions = bullet_suggestions

        return report

    async def optimize(
        self,
        resume: dict[str, Any],
        job_profile: dict[str, Any],
        report: ATSReport,
        target_score: float = 85.0,
        max_iterations: int = 3,
    ) -> tuple[dict[str, Any], OptimizationPlan]:
        """Run iterative optimization until target score or max iterations."""
        plan = OptimizationPlan(
            id=str(uuid.uuid4()),
            resume_id=resume.get("id", ""),
            current_score=report.overall_score,
            target_score=target_score,
        )

        current_resume = resume.copy()
        current_score = report.overall_score
        current_report = report

        for iteration in range(max_iterations):
            if current_score >= target_score:
                break

            # Generate optimization plan with full analysis context
            opt_items = await self._generate_optimization_plan(
                current_resume, job_profile, current_report, current_score, target_score
            )
            plan.items.extend(opt_items)

            # Apply optimizations
            improved = await self._apply_optimizations(current_resume, opt_items, job_profile)

            # Re-analyze
            current_report = await self.analyze(improved, job_profile)
            new_score = current_report.overall_score

            # Record iteration
            plan.iterations.append({
                "iteration": iteration + 1,
                "score_before": round(current_score, 1),
                "score_after": round(new_score, 1),
                "improvement": round(new_score - current_score, 1),
                "optimizations_applied": len(opt_items),
            })

            # Only accept improvement
            if new_score > current_score:
                current_resume = improved
                current_score = new_score
            else:
                break

        return current_resume, plan

    # ── Keyword Analysis ─────────────────────────────────

    def _analyze_keywords(self, resume_text: str, jd_keywords: list[str]) -> tuple[list[str], list[str], float]:
        """Match resume text against job keywords."""
        resume_lower = resume_text.lower()
        matched = []
        missing = []

        for kw in set(jd_keywords):
            kw_lower = kw.lower().strip()
            if kw_lower and kw_lower in resume_lower:
                matched.append(kw)
            elif kw_lower:
                missing.append(kw)

        density = len(matched) / max(len(set(jd_keywords)), 1)
        return matched, missing, density

    # ── Section Analysis ─────────────────────────────────

    def _analyze_sections(self, sections: list[dict], job_profile: dict) -> list[CategoryScore]:
        """Analyze section completeness and quality."""
        results = []
        required = job_profile.get("required_sections", ["summary", "experience", "skills"])
        present_names = {s.get("name", "").lower() for s in sections}

        for req in required:
            if req.lower() in present_names:
                section = next(s for s in sections if s.get("name", "").lower() == req.lower())
                items = section.get("items", [])
                wc = section.get("word_count", sum(len(i.get("text", "").split()) for i in items))

                score = 100
                suggestions = []

                if wc < 20:
                    score -= 30
                    suggestions.append(f"Section '{req}' is very short ({wc} words). Add more content.")
                elif wc < 40 and req in ("experience", "projects"):
                    score -= 15
                    suggestions.append(f"Section '{req}' could use more detail.")

                if len(items) == 0:
                    score = 0
                    suggestions.append(f"Section '{req}' has no items.")

                results.append(CategoryScore(
                    name=f"section:{req}", score=max(0, score),
                    details=[f"{len(items)} items, {wc} words"],
                    suggestions=suggestions,
                ))
            else:
                results.append(CategoryScore(
                    name=f"section:{req}", score=0,
                    details=[f"Missing required section: {req}"],
                    suggestions=[f"Add a '{req}' section to your resume."],
                ))

        return results

    # ── Formatting Analysis ──────────────────────────────

    def _analyze_formatting(self, sections: list[dict]) -> float:
        """Analyze resume formatting quality."""
        score = 100

        # Check section ordering
        orders = [s.get("order", 0) for s in sections]
        if orders != sorted(orders):
            score -= 10

        # Check for excessive word count
        total_words = sum(s.get("word_count", 0) for s in sections)
        if total_words > 1200:
            score -= 15
        elif total_words < 100:
            score -= 20

        # Check section count
        if len(sections) < 3:
            score -= 15

        return max(0, score)

    # ── Bullet Analysis ──────────────────────────────────

    def _analyze_bullets(self, sections: list[dict]) -> tuple[float, list[dict]]:
        """Analyze bullet point quality and generate suggestions."""
        score = 100
        suggestions = []
        weak_verbs = ["helped", "assisted", "was responsible for", "worked on",
                      "participated in", "involved in", "contributed to"]

        for section in sections:
            for item in section.get("items", []):
                text = item.get("text", "").strip().lower()
                if not text:
                    continue

                # Check weak verbs
                for weak in weak_verbs:
                    if text.startswith(weak):
                        score -= 3
                        suggestions.append({
                            "priority": "medium", "section": section.get("name", ""),
                            "description": f"Weak bullet: '{item.get('text', '')[:50]}'",
                            "expected_improvement": 3,
                            "recruiter_impact": "Strong action verbs demonstrate initiative and impact.",
                        })
                        break

                # Check for numbers/metrics (good practice)
                has_numbers = bool(re.search(r'\d+', text))
                if not has_numbers and section.get("name", "").lower() in ("experience", "projects"):
                    score -= 1
                    suggestions.append({
                        "priority": "low", "section": section.get("name", ""),
                        "description": f"Bullet lacks quantified metrics: '{item.get('text', '')[:50]}'",
                        "expected_improvement": 1,
                        "recruiter_impact": "Quantified achievements demonstrate measurable impact.",
                    })

                # Check length
                words = len(text.split())
                if words < 5:
                    score -= 2
                    suggestions.append({
                        "priority": "medium", "section": section.get("name", ""),
                        "description": f"Very short bullet ({words} words): '{item.get('text', '')[:50]}'",
                        "expected_improvement": 2,
                        "recruiter_impact": "Detailed bullets show depth of experience.",
                    })

        return max(0, score), suggestions

    # ── Recruiter Analysis ───────────────────────────────

    def _analyze_recruiter_metrics(self, sections: list[dict], resume_text: str) -> dict[str, float]:
        """Compute recruiter-focused metrics."""
        text_lower = resume_text.lower()

        # Readability: sentence length, jargon density
        words = resume_text.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
        readability = min(100, max(0, 80 - (avg_word_len - 5) * 10))

        # Impact: action verbs, quantified results
        action_verb_count = sum(1 for verb in ACTION_VERBS if verb in text_lower)
        number_count = len(re.findall(r'\d+', resume_text))
        impact = min(100, action_verb_count * 5 + number_count * 2)

        # Achievement orientation
        achievement_words = ["achieved", "increased", "reduced", "improved", "saved",
                            "delivered", "launched", "grew", "built", "designed"]
        achievement_count = sum(1 for w in achievement_words if w in text_lower)
        achievement = min(100, achievement_count * 10)

        # Specificity
        has_companies = bool(re.search(r'\b(google|microsoft|amazon|apple|meta|netflix)\b', text_lower))
        has_dates = bool(re.search(r'\b(20\d{2})\b', resume_text))
        has_numbers = len(re.findall(r'\d+', resume_text)) > 3
        specificity = (30 if has_companies else 0) + (30 if has_dates else 0) + (40 if has_numbers else 0)

        return {
            "readability": round(min(100, readability), 1),
            "impact": round(min(100, impact), 1),
            "achievement": round(min(100, achievement), 1),
            "specificity": round(min(100, specificity), 1),
        }

    # ── Evidence Verification ─────────────────────────────

    def _verify_evidence(self, sections: list[dict]) -> tuple[float, int]:
        """Check evidence coverage across resume bullets."""
        total = 0
        with_evidence = 0

        for section in sections:
            for item in section.get("items", []):
                meta = item.get("metadata", {})
                total += 1
                if meta.get("evidence_source") or meta.get("entity_id"):
                    with_evidence += 1

        coverage = with_evidence / max(total, 1)
        unsupported = total - with_evidence
        return coverage, unsupported

    # ── Text Extraction ──────────────────────────────────

    def _extract_full_text(self, sections: list[dict]) -> str:
        """Extract all text from resume sections."""
        parts = []
        for section in sections:
            parts.append(section.get("name", ""))
            for item in section.get("items", []):
                parts.append(item.get("text", ""))
        return " ".join(parts)

    # ── Optimization Planning ─────────────────────────────

    async def _generate_optimization_plan(
        self,
        resume: dict[str, Any],
        job_profile: dict[str, Any],
        report: ATSReport,
        current_score: float,
        target_score: float,
    ) -> list[OptimizationItem]:
        """Generate optimization suggestions via AI with full analysis context."""
        # Build comprehensive JD context — prefer raw_jd if available
        jd_text = job_profile.get("raw_jd", "")
        if not jd_text:
            jd_parts = []
            if job_profile.get("summary"):
                jd_parts.append(f"Summary: {job_profile['summary']}")
            if job_profile.get("required_skills"):
                jd_parts.append(f"Required Skills: {', '.join(job_profile['required_skills'])}")
            if job_profile.get("technologies"):
                jd_parts.append(f"Technologies: {', '.join(job_profile['technologies'])}")
            if job_profile.get("keywords"):
                jd_parts.append(f"Keywords: {', '.join(job_profile['keywords'][:30])}")
            jd_text = "\n".join(jd_parts) or str(job_profile)

        # Build detailed resume context with sections
        sections = resume.get("sections", [])
        resume_detail = []
        for s in sections:
            items_text = "; ".join(i.get("text", "")[:150] for i in s.get("items", [])[:5])
            resume_detail.append(f"[{s.get('name', 'Section')}] {items_text}")
        resume_text = "\n".join(resume_detail)

        # Build missing keyword context from the analysis report
        missing_kw = report.missing_keywords[:20] if report.missing_keywords else []
        matched_kw = report.matched_keywords[:10] if report.matched_keywords else []
        suggestions_ctx = ""
        if report.suggestions:
            suggestions_ctx = "\n\nAnalyzer suggestions:\n" + "\n".join(
                f"- [{s.get('priority', 'medium')}] {s.get('description', '')}"
                for s in report.suggestions[:8]
            )

        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an expert ATS resume optimizer. Your job is to produce SPECIFIC, ACTIONABLE "
                        "optimization items that will measurably increase the ATS score.\n\n"
                        "For each item, you must:\n"
                        "1. Identify the EXACT section to modify\n"
                        "2. Name the SPECIFIC missing keywords to incorporate\n"
                        "3. Describe the EXACT rewrite (not generic advice)\n"
                        "4. Estimate realistic improvement (0-10 scale)\n\n"
                        "Return a JSON array of optimization items, each with:\n"
                        "priority (high/medium/low), section, category (keyword|bullet|structure|format),\n"
                        "description (specific rewrite instruction), keywords_to_add (list of exact keywords),\n"
                        "expected_improvement (0-10), confidence (0-1), recruiter_impact.\n"
                        "Return ONLY valid JSON array."
                    ),
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=(
                        f"## Current ATS Score: {current_score:.1f}/100 | Target: {target_score}/100\n\n"
                        f"## Job Description\n{jd_text[:2000]}\n\n"
                        f"## MISSING Keywords (must incorporate)\n{', '.join(missing_kw)}\n\n"
                        f"## Matched Keywords (already present)\n{', '.join(matched_kw)}\n\n"
                        f"## Resume Content\n{resume_text[:3000]}"
                        f"{suggestions_ctx}"
                    ),
                ),
            ],
            temperature=0.2,
            max_tokens=4096,
        )

        # Parse response
        import json
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        try:
            start = text.find("[")
            end = text.rfind("]") + 1
            items_data = json.loads(text[start:end]) if start >= 0 else []
        except (json.JSONDecodeError, ValueError):
            items_data = []

        return [
            OptimizationItem(
                priority=item.get("priority", "medium"),
                section=item.get("section", ""),
                category=item.get("category", ""),
                description=item.get("description", ""),
                keywords_to_add=item.get("keywords_to_add", []),
                expected_improvement=item.get("expected_improvement", 5),
                confidence=item.get("confidence", 0.5),
                recruiter_impact=item.get("recruiter_impact", ""),
            )
            for item in items_data
        ]

    async def _apply_optimizations(
        self,
        resume: dict[str, Any],
        items: list[OptimizationItem],
        job_profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply optimization suggestions to the resume using AI."""
        import json

        # Build detailed instruction per optimization item
        instructions = []
        all_keywords_to_add = set()
        for i, item in enumerate(items[:10]):
            kw_part = ""
            if hasattr(item, "keywords_to_add") and item.keywords_to_add:
                kw_part = f"\n   Keywords to incorporate: {', '.join(item.keywords_to_add)}"
                all_keywords_to_add.update(item.keywords_to_add)
            instructions.append(
                f"{i+1}. [{item.priority.upper()}] Section: '{item.section}' | Category: {item.category}\n"
                f"   Action: {item.description}{kw_part}"
            )

        # Build resume with full section structure
        sections = resume.get("sections", [])
        resume_parts = []
        for s in sections:
            items_text = []
            for it in s.get("items", []):
                items_text.append(f"  - {it.get('text', '')}")
            resume_parts.append(f"[{s.get('name', 'Section')}]\n" + "\n".join(items_text))
        resume_str = "\n".join(resume_parts)

        response = await orchestrator.chat(
            messages=[
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an expert ATS resume rewriter. You MUST actively rewrite and improve "
                        "the resume content — not just suggest changes.\n\n"
                        "RULES:\n"
                        "1. REWRITE weak bullets with stronger action verbs and quantified metrics\n"
                        "2. INCORPORATE the specified missing keywords naturally into relevant sections\n"
                        "3. EXPAND thin sections with more detail and specificity\n"
                        "4. PRESERVE the user's actual experience — do NOT fabricate jobs or degrees\n"
                        "5. IMPROVE every bullet the suggestions mention\n\n"
                        "Return a JSON object with a 'sections' array. Each section has 'name' and 'items' "
                        "(array of objects with 'text' key). Keep the same section names and order.\n"
                        "Return ONLY valid JSON."
                    ),
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=(
                        f"## Optimization Instructions\n\n"
                        + "\n\n".join(instructions)
                        + f"\n\n## Keywords to weave into content\n{', '.join(all_keywords_to_add) if all_keywords_to_add else 'None specified'}\n\n"
                        f"## Current Resume\n{resume_str[:4000]}"
                    ),
                ),
            ],
            temperature=0.3,
            max_tokens=4096,
        )

        # Parse improved resume
        try:
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            start = text.find("{")
            end = text.rfind("}") + 1
            improved = json.loads(text[start:end])
            result = resume.copy()
            if isinstance(improved, dict) and "sections" in improved:
                result["sections"] = improved["sections"]
            elif isinstance(improved, list):
                result["sections"] = improved
            return result
        except Exception:
            logger.warning("ats.optimize.parse_failed")
            return resume

    # ── Comparison ────────────────────────────────────────

    async def compare(
        self,
        resume_a: dict[str, Any],
        resume_b: dict[str, Any],
        job_profile: dict[str, Any] | None = None,
    ) -> ComparisonResult:
        """Compare two resume versions."""
        report_a = await self.analyze(resume_a, job_profile or {})
        report_b = await self.analyze(resume_b, job_profile or {})

        text_a = self._extract_full_text(resume_a.get("sections", []))
        text_b = self._extract_full_text(resume_b.get("sections", []))

        kw_a = set(re.findall(r'\b\w{3,}\b', text_a.lower()))
        kw_b = set(re.findall(r'\b\w{3,}\b', text_b.lower()))

        return ComparisonResult(
            label_a=resume_a.get("candidate_name", "Version A"),
            label_b=resume_b.get("candidate_name", "Version B"),
            score_a=report_a.overall_score,
            score_b=report_b.overall_score,
            score_change=report_b.overall_score - report_a.overall_score,
            added_keywords=list(kw_b - kw_a)[:20],
            removed_keywords=list(kw_a - kw_b)[:20],
            semantic_improvement=report_b.readability_score - report_a.readability_score,
            summary=f"Score changed from {report_a.overall_score:.1f} to {report_b.overall_score:.1f}",
        )
