"""Unit tests for the Resume Pipeline — Blueprint, Canonical, Validator."""

import json
import pytest

from app.services.resume.blueprint import ResumeBlueprint, EvidenceMapping
from app.services.resume.canonical import CanonicalResume, ResumeSection
from app.services.resume.validator import ResumeValidator, ValidationReport


# ── Blueprint Tests ─────────────────────────────────────────

def test_blueprint_creation():
    bp = ResumeBlueprint(
        target_role="Software Engineer",
        target_industry="Tech",
        company="Google",
        resume_strategy="technical",
        tone="professional",
    )
    assert bp.target_role == "Software Engineer"
    assert bp.company == "Google"


def test_blueprint_to_dict():
    bp = ResumeBlueprint(target_role="Developer", sections=[
        {"name": "Summary", "word_count_target": 60},
    ])
    d = bp.to_dict()
    assert d["target_role"] == "Developer"
    assert len(d["sections"]) == 1


def test_blueprint_from_dict():
    bp = ResumeBlueprint(
        target_role="Engineer",
        target_industry="Tech",
        evidence_mappings=[
            EvidenceMapping(section="Experience", evidence_type="experience", evidence_ids=["exp-1"], priority=1),
        ],
    )
    d = bp.to_dict()
    bp2 = ResumeBlueprint.from_dict(d)
    assert bp2.target_role == "Engineer"
    assert len(bp2.evidence_mappings) == 1
    assert bp2.evidence_mappings[0].section == "Experience"


# ── Canonical Resume Tests ─────────────────────────────────

def test_canonical_resume_creation():
    resume = CanonicalResume(candidate_name="John Doe", email="john@test.com")
    assert resume.candidate_name == "John Doe"
    assert resume.version == 1


def test_canonical_add_section():
    resume = CanonicalResume(candidate_name="John")
    resume.add_section("Experience", order=1, items=[
        {"text": "Led team at Google"},
        {"text": "Built ML pipeline"},
    ])
    section = resume.get_section("Experience")
    assert section is not None
    assert len(section.items) == 2
    assert section.word_count == 7  # "Led team at Google Built ML pipeline"


def test_canonical_add_bullet():
    resume = CanonicalResume(candidate_name="John")
    resume.add_bullet(
        section_name="Skills",
        text="Python (Expert)",
        evidence_source="skill",
        entity_id="skill-1",
        confidence=0.95,
    )
    section = resume.get_section("Skills")
    assert section is not None
    assert len(section.items) == 1
    assert section.items[0]["metadata"]["confidence"] == 0.95


def test_canonical_to_dict():
    resume = CanonicalResume(
        candidate_name="Jane",
        email="jane@test.com",
        template_name="modern",
    )
    resume.add_section("Summary", order=0, items=[{"text": "Senior engineer with 10 years experience"}])
    d = resume.to_dict()
    assert d["candidate_name"] == "Jane"
    assert d["template_name"] == "modern"
    assert len(d["sections"]) == 1
    assert d["total_word_count"] == 6


def test_canonical_evidence_coverage():
    resume = CanonicalResume(candidate_name="John")
    resume.add_bullet("Skills", "Python", "skill", "s1", 0.9, "matched")
    resume.add_bullet("Skills", "React", "skill", "s2", 0.8, "matched")
    resume.add_bullet("Skills", "Python", "skill", "s1", 0.9, "matched")
    coverage = resume.evidence_coverage()
    assert coverage["skill:s1"] == 2
    assert coverage["skill:s2"] == 1


def test_canonical_to_dict():
    resume = CanonicalResume(
        candidate_name="Jane",
        email="jane@test.com",
        template_name="modern",
    )
    resume.add_section("Summary", order=0, items=[{"text": "Senior engineer with 10 years experience"}])
    d = resume.to_dict()
    assert d["candidate_name"] == "Jane"
    assert d["template_name"] == "modern"
    assert len(d["sections"]) == 1
    assert d["total_word_count"] == 6


def test_canonical_from_dict():
    resume = CanonicalResume(candidate_name="Test")
    resume.add_section("Skills", order=2, items=[{"text": "Python"}])
    d = resume.to_dict()
    resume2 = CanonicalResume.from_dict(d)
    assert resume2.candidate_name == "Test"
    assert len(resume2.sections) == 1
    assert resume2.sections[0].name == "Skills"


# ── Validator Tests ─────────────────────────────────────────

def test_validator_passes_good_resume():
    validator = ResumeValidator()
    resume = {
        "sections": [
            {"name": "Summary", "word_count": 50, "items": [
                {"text": "Senior engineer with 8 years building distributed systems", "metadata": {}},
            ]},
            {"name": "Experience", "word_count": 200, "items": [
                {"text": "Led team of 5 engineers on microservices migration", "metadata": {"evidence_source": "experience"}},
                {"text": "Reduced latency by 40% through optimization", "metadata": {"evidence_source": "experience"}},
            ]},
            {"name": "Skills", "word_count": 30, "items": [
                {"text": "Python"}, {"text": "React"}, {"text": "AWS"},
            ]},
        ]
    }
    report = validator.validate(resume)
    assert report.score >= 80
    assert report.passed is True


def test_validator_catches_missing_sections():
    validator = ResumeValidator()
    resume = {"sections": [{"name": "Projects", "word_count": 50, "items": []}]}
    report = validator.validate(resume)
    assert report.passed is False
    errors = [i for i in report.issues if i.severity == "error"]
    assert len(errors) >= 2  # Missing Summary and Experience and Skills


def test_validator_catches_weak_bullets():
    validator = ResumeValidator()
    resume = {
        "sections": [
            {"name": "Summary", "word_count": 50, "items": [{"text": "A professional with experience in software development and engineering", "metadata": {}}]},
            {"name": "Experience", "word_count": 30, "items": [
                {"text": "Helped with the project", "metadata": {"evidence_source": "exp"}},
                {"text": "Assisted in building the application", "metadata": {"evidence_source": "exp"}},
                {"text": "Built scalable microservices architecture", "metadata": {"evidence_source": "exp"}},
            ]},
            {"name": "Skills", "word_count": 10, "items": [{"text": "Python"}]},
        ]
    }
    report = validator.validate(resume)
    warnings = [i for i in report.issues if i.severity == "warning"]
    assert len(warnings) >= 1
    weak = [i for i in warnings if i.category == "weak_bullet"]
    assert len(weak) == 2  # "helped" and "assisted"


def test_validator_catches_duplicate_skills():
    validator = ResumeValidator()
    resume = {
        "sections": [
            {"name": "Summary", "word_count": 50, "items": [{"text": "Engineer with Python expertise", "metadata": {}}]},
            {"name": "Experience", "word_count": 30, "items": [{"text": "Built things", "metadata": {"evidence_source": "exp"}}]},
            {"name": "Skills", "word_count": 10, "items": [
                {"text": "Python"}, {"text": "python"}, {"text": "Python"},
            ]},
        ]
    }
    report = validator.validate(resume)
    warnings = [i for i in report.issues if i.category == "duplicate_skill"]
    assert len(warnings) >= 1


def test_validator_keyword_coverage():
    validator = ResumeValidator(target_keywords=["kubernetes", "docker", "terraform"])
    resume = {
        "sections": [
            {"name": "Summary", "word_count": 50, "items": [{"text": "Cloud engineer with Kubernetes and Docker expertise", "metadata": {}}]},
            {"name": "Experience", "word_count": 30, "items": [{"text": "Managed Kubernetes clusters", "metadata": {"evidence_source": "exp"}}]},
            {"name": "Skills", "word_count": 10, "items": [{"text": "Docker"}]},
        ]
    }
    report = validator.validate(resume)
    keyword_warnings = [i for i in report.issues if i.category == "keyword_coverage"]
    assert len(keyword_warnings) >= 1  # terraform missing


def test_validator_to_dict():
    report = ValidationReport()
    report.score = 85
    report.passed = True
    d = report.to_dict()
    assert d["score"] == 85
    assert d["passed"] is True
    assert d["issues_count"]["error"] == 0


def test_validator_tense_consistency():
    validator = ResumeValidator()
    resume = {
        "sections": [
            {"name": "Summary", "word_count": 50, "items": [{"text": "Engineer with experience", "metadata": {}}]},
            {"name": "Experience", "word_count": 30, "items": [
                {"text": "Built microservices", "metadata": {"evidence_source": "exp"}},
                {"text": "Develop new features", "metadata": {"evidence_source": "exp"}},
            ]},
            {"name": "Skills", "word_count": 10, "items": [{"text": "Python"}]},
        ]
    }
    report = validator.validate(resume)
    tense_issues = [i for i in report.issues if i.category == "tense_consistency"]
    assert len(tense_issues) >= 1


def test_validator_empty_summary():
    validator = ResumeValidator()
    resume = {
        "sections": [
            {"name": "Summary", "word_count": 0, "items": []},
            {"name": "Experience", "word_count": 30, "items": [{"text": "Worked at Google", "metadata": {}}]},
            {"name": "Skills", "word_count": 10, "items": [{"text": "Python"}]},
        ]
    }
    report = validator.validate(resume)
    errors = [i for i in report.issues if i.category == "empty_summary"]
    assert len(errors) == 1
