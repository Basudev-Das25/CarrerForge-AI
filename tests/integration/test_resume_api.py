"""Integration tests for Resume Generation API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_templates(client):
    """Test listing available resume templates."""
    response = await client.get("/api/v1/resume/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) >= 3
    names = {t["name"] for t in data["templates"]}
    assert "modern" in names
    assert "minimal" in names


@pytest.mark.asyncio
async def test_get_template(client):
    """Test getting a specific template."""
    response = await client.get("/api/v1/resume/templates/modern")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert data["info"]["name"] == "modern"


@pytest.mark.asyncio
async def test_get_template_not_found(client):
    """Test getting a nonexistent template."""
    response = await client.get("/api/v1/resume/templates/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_versions_empty(client):
    """Test listing resume versions when none exist."""
    response = await client.get("/api/v1/resume/versions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["versions"] == []


@pytest.mark.asyncio
async def test_validate_resume(client):
    """Test validating a resume."""
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
    response = await client.post(
        "/api/v1/resume/validate",
        json={"resume": resume, "target_keywords": ["python", "react", "aws"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "validation" in data
    assert data["validation"]["score"] >= 70


@pytest.mark.asyncio
async def test_export_typst(client):
    """Test exporting resume as Typst."""
    resume = {
        "candidate_name": "John Doe",
        "email": "john@test.com",
        "phone": "555-0100",
        "location": "NYC",
        "sections": [
            {"name": "Skills", "order": 1, "items": [{"text": "Python"}, {"text": "React"}]},
        ],
    }
    response = await client.post(
        "/api/v1/resume/export/typst",
        json=resume,
    )
    assert response.status_code == 200
    data = response.json()
    assert "typst" in data
    assert "John Doe" in data["typst"]


@pytest.mark.asyncio
async def test_export_text(client):
    """Test exporting resume as plain text."""
    resume = {
        "candidate_name": "Jane Smith",
        "email": "jane@test.com",
        "phone": "555-0200",
        "location": "SF",
        "sections": [
            {"name": "Skills", "order": 1, "items": [{"text": "Python"}, {"text": "React"}]},
        ],
    }
    response = await client.post(
        "/api/v1/resume/export/text",
        json=resume,
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "Jane Smith" in data["text"]


@pytest.mark.asyncio
async def test_render_template(client):
    """Test rendering resume with a specific template."""
    resume = {
        "candidate_name": "Test User",
        "email": "test@test.com",
        "phone": "555-0300",
        "location": "Test City",
        "sections": [
            {"name": "Skills", "order": 1, "items": [{"text": "Python"}]},
        ],
    }
    response = await client.post(
        "/api/v1/resume/templates/modern/render",
        json=resume,
    )
    assert response.status_code == 200
    data = response.json()
    assert "typst" in data
    assert "modern" in data["template"]
