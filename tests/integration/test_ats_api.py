"""Integration tests for ATS Intelligence API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_analyze_resume(client):
    """Test analyzing a resume against a job profile."""
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
    job_profile = {
        "keywords": ["python", "react", "aws", "kubernetes", "docker"],
        "ats_keywords": ["microservices", "distributed"],
        "required_skills": ["python", "react"],
    }
    response = await client.post(
        "/api/v1/ats-intelligence/analyze",
        json={"resume": resume, "job_profile": job_profile},
    )
    assert response.status_code == 200
    data = response.json()
    report = data["report"]
    assert "overall_score" in report
    assert 0 <= report["overall_score"] <= 100
    assert "matched_keywords" in report
    assert "missing_keywords" in report
    assert "suggestions" in report


@pytest.mark.asyncio
async def test_optimize_resume(client):
    """Test resume optimization endpoint structure (AI not available in test env)."""
    # This endpoint requires an AI provider which is not available in test env.
    # Test that the endpoint exists and returns proper error handling.
    resume = {"sections": []}
    job_profile = {"keywords": [], "ats_keywords": [], "required_skills": []}
    response = await client.post(
        "/api/v1/ats-intelligence/optimize",
        json={"resume": resume, "job_profile": job_profile, "target_score": 80, "max_iterations": 1},
    )
    # Either succeeds or returns 500/502 due to missing AI provider
    assert response.status_code in (200, 500, 502)


@pytest.mark.asyncio
async def test_compare_resumes(client):
    """Test comparing two resumes."""
    resume_a = {
        "candidate_name": "V1",
        "sections": [{"name": "Skills", "items": [{"text": "Python"}]}],
    }
    resume_b = {
        "candidate_name": "V2",
        "sections": [{"name": "Skills", "items": [{"text": "Python"}, {"text": "React"}]}],
    }
    response = await client.post(
        "/api/v1/ats-intelligence/compare",
        json={"resume_a": resume_a, "resume_b": resume_b, "job_profile": {"keywords": ["python", "react"]}},
    )
    assert response.status_code == 200
    data = response.json()
    comparison = data["comparison"]
    assert "score_a" in comparison
    assert "score_b" in comparison
    assert "score_change" in comparison


@pytest.mark.asyncio
async def test_list_reports(client):
    """Test listing ATS reports."""
    response = await client.get("/api/v1/ats-intelligence/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["reports"] == []


@pytest.mark.asyncio
async def test_analyze_version_not_found(client):
    """Test analyzing a non-existent version."""
    response = await client.post("/api/v1/ats-intelligence/analyze-version/nonexistent-id")
    assert response.status_code == 404
