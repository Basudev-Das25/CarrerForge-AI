"""Integration tests for the FastAPI backend."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CareerForge AI"


@pytest.mark.asyncio
async def test_providers_endpoint(client):
    response = await client.get("/api/v1/ai/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_config_endpoint(client):
    response = await client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert "ai_provider" in data


@pytest.mark.asyncio
async def test_documents_list(client):
    response = await client.get("/api/v1/documents/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_resumes_list(client):
    response = await client.get("/api/v1/resumes/")
    assert response.status_code == 200
