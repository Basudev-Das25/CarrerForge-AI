"""Integration tests for AI Orchestrator, Jobs, and Agents APIs."""

import pytest


@pytest.mark.asyncio
async def test_ai_health(client):
    """Test AI orchestrator health endpoint."""
    response = await client.get("/api/v1/ai-orchestrator/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_ai_stats(client):
    """Test AI orchestrator stats endpoint."""
    response = await client.get("/api/v1/ai-orchestrator/stats")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "observability" in data


@pytest.mark.asyncio
async def test_list_prompts(client):
    """Test listing prompts."""
    response = await client.get("/api/v1/ai-orchestrator/prompts")
    assert response.status_code == 200
    data = response.json()
    assert "prompts" in data
    assert len(data["prompts"]) > 0


@pytest.mark.asyncio
async def test_render_prompt(client):
    """Test rendering a prompt."""
    response = await client.post(
        "/api/v1/ai-orchestrator/prompts/render",
        json={"category": "jd", "name": "parser", "variables": {"job_description_text": "Senior Developer at Google"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert "system" in data or "user" in data


@pytest.mark.asyncio
async def test_validate_prompt(client):
    """Test validating a prompt."""
    response = await client.get("/api/v1/ai-orchestrator/prompts/jd/parser/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_validate_nonexistent_prompt(client):
    """Test validating a nonexistent prompt."""
    response = await client.get("/api/v1/ai-orchestrator/prompts/nonexistent/missing/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False


@pytest.mark.asyncio
async def test_clear_cache(client):
    """Test clearing the cache."""
    response = await client.post("/api/v1/ai-orchestrator/cache/clear")
    assert response.status_code == 200
    assert response.json()["status"] == "cleared"


@pytest.mark.asyncio
async def test_list_jobs(client):
    """Test listing jobs."""
    response = await client.get("/api/v1/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data


@pytest.mark.asyncio
async def test_job_stats(client):
    """Test job stats."""
    response = await client.get("/api/v1/jobs/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data


@pytest.mark.asyncio
async def test_search_jobs_empty(client):
    """Test searching jobs with no data."""
    response = await client.get("/api/v1/jobs/search?q=Python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_agents_health(client):
    """Test agents health endpoint."""
    response = await client.get("/api/v1/agents/health")
    assert response.status_code == 200
    data = response.json()
    assert "job_parser" in data
    assert "ats_evaluator" in data
    assert "resume_planner" in data
    assert "reflection" in data
    assert "cover_letter" in data
    assert "interview" in data
