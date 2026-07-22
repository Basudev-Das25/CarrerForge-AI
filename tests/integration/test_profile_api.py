"""Integration tests for the Profile API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_get_profile(client):
    """Test getting the user profile."""
    response = await client.get("/api/v1/profile")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "full_name" in data


@pytest.mark.asyncio
async def test_update_profile(client):
    """Test updating the user profile."""
    response = await client.put(
        "/api/v1/profile",
        json={"full_name": "Test User Updated", "email": "test@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Test User Updated"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_dashboard(client):
    """Test getting dashboard data."""
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "total_education" in data
    assert "total_experience" in data
    assert "total_skills" in data
    assert "total_languages" in data
    assert "total_publications" in data
    assert "total_awards" in data
    assert "total_social_links" in data
    assert "profile_completion" in data


@pytest.mark.asyncio
async def test_get_completion(client):
    """Test profile completion endpoint."""
    response = await client.get("/api/v1/completion")
    assert response.status_code == 200
    data = response.json()
    assert "completion" in data
    assert 0 <= data["completion"] <= 100


@pytest.mark.asyncio
async def test_education_crud(client):
    """Test education CRUD endpoints."""
    # Create
    response = await client.post(
        "/api/v1/education",
        json={
            "degree": "B.S. Computer Science",
            "institution": "MIT",
            "start_date": "2018-09",
            "end_date": "2022-06",
        },
    )
    assert response.status_code == 201
    edu = response.json()
    edu_id = edu["id"]
    assert edu["degree"] == "B.S. Computer Science"

    # List
    response = await client.get("/api/v1/education")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Get
    response = await client.get(f"/api/v1/education/{edu_id}")
    assert response.status_code == 200
    assert response.json()["institution"] == "MIT"

    # Update
    response = await client.put(
        f"/api/v1/education/{edu_id}",
        json={"gpa": 3.9},
    )
    assert response.status_code == 200
    assert response.json()["gpa"] == 3.9

    # Delete
    response = await client.delete(f"/api/v1/education/{edu_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_experience_crud(client):
    """Test experience CRUD endpoints."""
    response = await client.post(
        "/api/v1/experience",
        json={
            "company": "Google",
            "title": "Software Engineer",
            "start_date": "2022-06",
            "employment_type": "full-time",
        },
    )
    assert response.status_code == 201
    exp = response.json()
    exp_id = exp["id"]

    response = await client.get("/api/v1/experience")
    assert response.status_code == 200

    response = await client.put(
        f"/api/v1/experience/{exp_id}",
        json={"description": "Building amazing things"},
    )
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/experience/{exp_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_projects_crud(client):
    """Test projects CRUD endpoints."""
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "CareerForge AI",
            "description": "AI-powered career platform",
            "tech_stack": ["React", "Python", "FastAPI"],
            "status": "completed",
        },
    )
    assert response.status_code == 201
    proj = response.json()
    proj_id = proj["id"]

    response = await client.get("/api/v1/projects")
    assert response.status_code == 200

    response = await client.put(
        f"/api/v1/projects/{proj_id}",
        json={"is_featured": True},
    )
    assert response.status_code == 200
    assert response.json()["is_featured"] is True

    response = await client.delete(f"/api/v1/projects/{proj_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_skills_crud(client):
    """Test skills CRUD endpoints."""
    response = await client.post(
        "/api/v1/skills",
        json={
            "name": "Python",
            "category": "programming",
            "level": "advanced",
            "years_experience": 5.0,
        },
    )
    assert response.status_code == 201
    skill = response.json()
    skill_id = skill["id"]

    response = await client.get("/api/v1/skills")
    assert response.status_code == 200

    response = await client.put(
        f"/api/v1/skills/{skill_id}",
        json={"years_experience": 7.0},
    )
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/skills/{skill_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_certificates_crud(client):
    """Test certificates CRUD endpoints."""
    response = await client.post(
        "/api/v1/certificates",
        json={
            "title": "AWS Solutions Architect",
            "issuer": "Amazon Web Services",
            "issue_date": "2024-01",
        },
    )
    assert response.status_code == 201
    cert = response.json()
    cert_id = cert["id"]

    response = await client.get("/api/v1/certificates")
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/certificates/{cert_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_achievements_crud(client):
    """Test achievements CRUD endpoints."""
    response = await client.post(
        "/api/v1/achievements",
        json={
            "title": "Best Paper Award",
            "category": "award",
            "organization": "IEEE",
        },
    )
    assert response.status_code == 201
    ach = response.json()
    ach_id = ach["id"]

    response = await client.get("/api/v1/achievements")
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/achievements/{ach_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_languages_crud(client):
    """Test languages CRUD endpoints."""
    response = await client.post(
        "/api/v1/languages",
        json={
            "name": "English",
            "proficiency": "native",
            "is_native": True,
        },
    )
    assert response.status_code == 201
    lang = response.json()
    lang_id = lang["id"]
    assert lang["name"] == "English"

    response = await client.get("/api/v1/languages")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response = await client.get(f"/api/v1/languages/{lang_id}")
    assert response.status_code == 200

    response = await client.put(
        f"/api/v1/languages/{lang_id}",
        json={"proficiency": "fluent"},
    )
    assert response.status_code == 200
    assert response.json()["proficiency"] == "fluent"

    response = await client.delete(f"/api/v1/languages/{lang_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_publications_crud(client):
    """Test publications CRUD endpoints."""
    response = await client.post(
        "/api/v1/publications",
        json={
            "title": "A Novel Approach to AI",
            "authors": ["John Doe", "Jane Smith"],
            "venue": "IEEE Conference",
            "date": "2024-06",
        },
    )
    assert response.status_code == 201
    pub = response.json()
    pub_id = pub["id"]
    assert pub["title"] == "A Novel Approach to AI"

    response = await client.get("/api/v1/publications")
    assert response.status_code == 200

    response = await client.get(f"/api/v1/publications/{pub_id}")
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/publications/{pub_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_awards_crud(client):
    """Test awards CRUD endpoints."""
    response = await client.post(
        "/api/v1/awards",
        json={
            "title": "Innovation Award",
            "issuer": "Tech Corp",
            "category": "professional",
        },
    )
    assert response.status_code == 201
    award = response.json()
    award_id = award["id"]

    response = await client.get("/api/v1/awards")
    assert response.status_code == 200

    response = await client.get(f"/api/v1/awards/{award_id}")
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/awards/{award_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_social_links_crud(client):
    """Test social links CRUD endpoints."""
    response = await client.post(
        "/api/v1/social-links",
        json={
            "platform": "GitHub",
            "url": "https://github.com/testuser",
            "username": "testuser",
        },
    )
    assert response.status_code == 201
    link = response.json()
    link_id = link["id"]
    assert link["platform"] == "GitHub"

    response = await client.get("/api/v1/social-links")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response = await client.get(f"/api/v1/social-links/{link_id}")
    assert response.status_code == 200

    response = await client.put(
        f"/api/v1/social-links/{link_id}",
        json={"display_name": "Test User"},
    )
    assert response.status_code == 200

    response = await client.delete(f"/api/v1/social-links/{link_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_global_search(client):
    """Test global search across all entities."""
    # Create some data to search
    await client.post(
        "/api/v1/skills",
        json={"name": "Python", "category": "programming"},
    )
    await client.post(
        "/api/v1/education",
        json={"degree": "B.S. Computer Science", "institution": "MIT", "start_date": "2018-09"},
    )

    response = await client.get("/api/v1/search?q=Python")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Python"
    assert isinstance(data["results"], list)

    response = await client.get("/api/v1/search?q=MIT")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_not_found_returns_404(client):
    """Test that non-existent resources return 404."""
    response = await client.get("/api/v1/education/non-existent-id")
    assert response.status_code == 404

    response = await client.get("/api/v1/experience/non-existent-id")
    assert response.status_code == 404

    response = await client.get("/api/v1/skills/non-existent-id")
    assert response.status_code == 404

    response = await client.get("/api/v1/languages/non-existent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validation_errors(client):
    """Test that validation errors are returned for invalid data."""
    response = await client.post(
        "/api/v1/education",
        json={"degree": "", "institution": "MIT", "start_date": "2018-09"},
    )
    assert response.status_code == 422

    response = await client.post(
        "/api/v1/skills",
        json={"name": ""},
    )
    assert response.status_code == 422
