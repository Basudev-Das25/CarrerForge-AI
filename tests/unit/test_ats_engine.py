"""Unit tests for ATS Intelligence Engine."""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.ats.types import ATSReport, CategoryScore, OptimizationItem, OptimizationPlan, ComparisonResult
from app.services.ats.engine import ATSEngine


# ── Type Tests ───────────────────────────────────────────

def test_ats_report_creation():
    report = ATSReport(id="r1", overall_score=85.5)
    assert report.overall_score == 85.5
    assert report.id == "r1"


def test_ats_report_to_dict():
    report = ATSReport(
        id="r1", overall_score=75.0,
        matched_keywords=["python", "react"],
        missing_keywords=["kubernetes"],
        sections=[CategoryScore(name="skills", score=90, details=["3 skills"])],
        suggestions=[{"description": "Add metrics"}],
    )
    d = report.to_dict()
    assert d["overall_score"] == 75.0
    assert d["matched_keywords"] == ["python", "react"]
    assert d["missing_keywords"] == ["kubernetes"]
    assert len(d["sections"]) == 1
    assert d["sections"][0]["score"] == 90


def test_category_score():
    score = CategoryScore(name="keywords", score=85, weight=1.5, details=["test"], suggestions=["improve"])
    d = score.to_dict()
    assert d["name"] == "keywords"
    assert d["score"] == 85
    assert d["weight"] == 1.5


def test_optimization_item():
    item = OptimizationItem(
        priority="high", section="Skills", description="Add Kubernetes",
        expected_improvement=10, confidence=0.85, recruiter_impact="Cloud skills needed"
    )
    d = item.to_dict()
    assert d["priority"] == "high"
    assert d["expected_improvement"] == 10


def test_optimization_plan():
    plan = OptimizationPlan(id="p1", resume_id="r1", current_score=60, target_score=85)
    plan.items.append(OptimizationItem(priority="high", description="Fix"))
    plan.iterations.append({"iteration": 1, "score_before": 60, "score_after": 70})
    d = plan.to_dict()
    assert d["current_score"] == 60
    assert d["target_score"] == 85
    assert len(d["items"]) == 1


def test_comparison_result():
    comp = ComparisonResult(label_a="V1", label_b="V2", score_a=60, score_b=75, score_change=15)
    d = comp.to_dict()
    assert d["score_change"] == 15
    assert d["label_a"] == "V1"


# ── Engine Tests ─────────────────────────────────────────

def test_extract_full_text():
    engine = ATSEngine()
    sections = [
        {"name": "Skills", "items": [{"text": "Python"}, {"text": "React"}]},
        {"name": "Experience", "items": [{"text": "Led team at Google"}]},
    ]
    text = engine._extract_full_text(sections)
    assert "Python" in text
    assert "React" in text
    assert "Led team at Google" in text
    assert "Skills" in text


def test_keyword_analysis():
    engine = ATSEngine()
    resume_text = "Senior Python developer with React experience and AWS knowledge"
    keywords = ["python", "react", "aws", "kubernetes", "docker"]
    matched, missing, density = engine._analyze_keywords(resume_text, keywords)
    assert "python" in matched
    assert "react" in matched
    assert "aws" in matched
    assert "kubernetes" in missing
    assert "docker" in missing
    assert density == 0.6  # 3/5


def test_section_analysis():
    engine = ATSEngine()
    sections = [
        {"name": "Summary", "order": 0, "items": [{"text": "Engineer with 10 years"}], "word_count": 5},
        {"name": "Experience", "order": 1, "items": [{"text": "Led team"}], "word_count": 2},
    ]
    job_profile = {"required_sections": ["summary", "experience", "skills"]}
    results = engine._analyze_sections(sections, job_profile)
    assert len(results) == 3
    skills_score = next(r for r in results if "skills" in r.name)
    assert skills_score.score == 0  # Missing skills section


def test_formatting_analysis():
    engine = ATSEngine()
    # Well-formatted resume
    sections = [
        {"name": "Summary", "order": 0, "word_count": 50},
        {"name": "Experience", "order": 1, "word_count": 200},
        {"name": "Skills", "order": 2, "word_count": 30},
    ]
    score = engine._analyze_formatting(sections)
    assert score >= 85

    # Empty resume
    score2 = engine._analyze_formatting([])
    assert score2 < 100  # Empty resume scores lower


def test_bullet_analysis():
    engine = ATSEngine()
    sections = [{
        "name": "Experience", "items": [
            {"text": "Led team of 5 engineers on migration"},
            {"text": "Helped with the project"},
            {"text": "Reduced costs by 40% through optimization"},
        ]
    }]
    score, suggestions = engine._analyze_bullets(sections)
    assert score < 100  # "Helped" is weak
    weak = [s for s in suggestions if "weak" in s.get("description", "").lower() or "Weak" in s.get("description", "")]
    assert len(weak) >= 1


def test_recruiter_metrics():
    engine = ATSEngine()
    sections = [{"name": "Experience", "items": [
        {"text": "Led team of 5 at Google, reduced costs by 40% and improved performance by 25%"},
    ]}]
    resume_text = "Senior Engineer at Google 2020-2023. Led team of 5, reduced costs 40%, improved performance 25%"
    metrics = engine._analyze_recruiter_metrics(sections, resume_text)
    assert metrics["readability"] >= 50
    assert metrics["impact"] > 0  # Has action verbs
    assert metrics["specificity"] > 0  # Has dates and numbers


def test_evidence_verification():
    engine = ATSEngine()
    sections = [{
        "name": "Experience", "items": [
            {"text": "Led team", "metadata": {"evidence_source": "experience", "entity_id": "exp-1"}},
            {"text": "Built app", "metadata": {}},  # No evidence
        ]
    }]
    coverage, unsupported = engine._verify_evidence(sections)
    assert coverage == 0.5  # 1/2 has evidence
    assert unsupported == 1


def test_typst_escape():
    from app.services.templates.engine import _esc
    assert _esc("Hello & World") == "Hello \\& World"
    assert _esc("100%") == "100\\%"
    assert _esc("$100") == "\\$100"
