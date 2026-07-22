"""Integration tests for the Knowledge Engine API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_build_knowledge_graph(client):
    """Test building the knowledge graph."""
    response = await client.post("/api/v1/knowledge/build")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "built"
    assert "nodes" in data
    assert "edges" in data


@pytest.mark.asyncio
async def test_get_stats(client):
    """Test getting graph statistics."""
    response = await client.get("/api/v1/knowledge/stats")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data


@pytest.mark.asyncio
async def test_get_summary(client):
    """Test getting knowledge summary."""
    response = await client.get("/api/v1/knowledge/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_nodes" in data
    assert "entity_counts" in data
    assert "dimension_averages" in data
    assert "relationship_stats" in data


@pytest.mark.asyncio
async def test_search_empty(client):
    """Test search with no data returns empty results."""
    response = await client.post(
        "/api/v1/knowledge/search",
        json={"query": "Python", "top_k": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_search_with_data(client):
    """Test search after adding profile data."""
    # Create some data first
    await client.post("/api/v1/skills", json={"name": "Python", "category": "programming"})
    await client.post("/api/v1/projects", json={"name": "Python ML Project", "tech_stack": ["Python", "TensorFlow"]})

    response = await client.post(
        "/api/v1/knowledge/search",
        json={"query": "Python", "top_k": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_keyword_search(client):
    """Test keyword search endpoint."""
    await client.post("/api/v1/skills", json={"name": "React", "category": "framework"})

    response = await client.get("/api/v1/knowledge/search/keyword?q=React&top_k=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_relevant_projects(client):
    """Test relevant projects endpoint."""
    await client.post("/api/v1/projects", json={"name": "Web App", "tech_stack": ["React", "FastAPI"]})

    response = await client.get("/api/v1/knowledge/relevant/projects?q=React&top_k=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_relevant_skills(client):
    """Test relevant skills endpoint."""
    await client.post("/api/v1/skills", json={"name": "Python", "category": "programming"})

    response = await client.get("/api/v1/knowledge/relevant/skills?q=Python&top_k=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_relevant_experience(client):
    """Test relevant experience endpoint."""
    await client.post("/api/v1/experience", json={"company": "Google", "title": "SE", "start_date": "2022-01"})

    response = await client.get("/api/v1/knowledge/relevant/experience?q=Google&top_k=5")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_relevant_certificates(client):
    """Test relevant certificates endpoint."""
    await client.post("/api/v1/certificates", json={"title": "AWS Architect", "issuer": "AWS"})

    response = await client.get("/api/v1/knowledge/relevant/certificates?q=AWS&top_k=5")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_relevant_achievements(client):
    """Test relevant achievements endpoint."""
    await client.post("/api/v1/achievements", json={"title": "Best Paper", "category": "award"})

    response = await client.get("/api/v1/knowledge/relevant/achievements?q=Paper&top_k=5")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_relevant_entities_by_type(client):
    """Test the generic relevant entities endpoint."""
    await client.post("/api/v1/skills", json={"name": "Docker", "category": "tool"})

    response = await client.post(
        "/api/v1/knowledge/relevant/skill",
        json={"query": "Docker containerization", "top_k": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["entity_type"] == "skill"


@pytest.mark.asyncio
async def test_get_graph(client):
    """Test getting the full graph."""
    await client.post("/api/v1/skills", json={"name": "Python"})

    response = await client.get("/api/v1/knowledge/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)


@pytest.mark.asyncio
async def test_get_entity_graph(client):
    """Test getting a specific entity's graph."""
    resp = await client.post("/api/v1/skills", json={"name": "Python"})
    skill = resp.json()

    response = await client.get(f"/api/v1/knowledge/graph/skill/{skill['id']}")
    assert response.status_code == 200
    data = response.json()
    assert "entity" in data
    assert "neighbors" in data


@pytest.mark.asyncio
async def test_get_entity_scores(client):
    """Test getting entity scores."""
    resp = await client.post("/api/v1/skills", json={"name": "Python"})
    skill = resp.json()

    response = await client.get(f"/api/v1/knowledge/scores/skill/{skill['id']}")
    assert response.status_code == 200
    data = response.json()
    assert "scores" in data


@pytest.mark.asyncio
async def test_embedding_status(client):
    """Test embedding status endpoint."""
    response = await client.get("/api/v1/knowledge/embedding-status")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "with_embedding" in data


@pytest.mark.asyncio
async def test_relevant_with_scoring_dimension(client):
    """Test filtering by scoring dimension."""
    await client.post("/api/v1/skills", json={"name": "Python", "category": "programming"})

    response = await client.get("/api/v1/knowledge/relevant/skills?q=Python&dimension=backend&top_k=5")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_with_entity_type_filter(client):
    """Test search with entity type filter."""
    await client.post("/api/v1/skills", json={"name": "Python"})
    await client.post("/api/v1/projects", json={"name": "Python App"})

    response = await client.post(
        "/api/v1/knowledge/search",
        json={"query": "Python", "entity_types": ["skill"], "top_k": 10},
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["entity_type"] == "skill"


@pytest.mark.asyncio
async def test_search_with_min_score(client):
    """Test search with minimum score threshold."""
    await client.post("/api/v1/skills", json={"name": "Python"})

    response = await client.post(
        "/api/v1/knowledge/search",
        json={"query": "Python", "min_score": 0.5, "top_k": 10},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_with_relationship_expansion(client):
    """Test search with relationship expansion."""
    await client.post("/api/v1/skills", json={"name": "Python"})
    await client.post("/api/v1/projects", json={"name": "Python App", "tech_stack": ["Python"]})

    response = await client.post(
        "/api/v1/knowledge/search",
        json={"query": "Python", "expand_relationships": True, "relationship_depth": 1},
    )
    assert response.status_code == 200
