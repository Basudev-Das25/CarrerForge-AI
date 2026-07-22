"""Shared test fixtures for CareerForge AI backend.

Automatically uses an in-memory SQLite database for isolation.
No configuration required — just run pytest.
"""

import os
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

# ── Critical: Set test database BEFORE any app imports ──────
# This must happen at module import time, before any module
# that imports `engine` from app.db.base executes.
os.environ.setdefault("TEST_DATABASE_URL", "sqlite+aiosqlite://")

# Now safe to import app
from app.main import app
from app.db.base import engine, Base, _get_database_url
from app.config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once per test session.

    Uses the in-memory SQLite database set via TEST_DATABASE_URL.
    Tables are created before any test and dropped after all tests.
    """
    # Verify we're using the test database
    db_url = _get_database_url()
    assert "sqlite+aiosqlite://" in db_url, f"Using non-test database: {db_url}"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(autouse=True)
async def cleanup_db():
    """Clean data between tests — delete all rows from every table."""
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def client():
    """Async HTTP test client with in-memory database isolation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_user_data():
    return {
        "full_name": "Alex Rivera",
        "email": "alex@example.com",
        "phone": "+1-555-0100",
        "location": "San Francisco, CA",
        "summary": "Senior ML Engineer with 5+ years building production AI systems.",
    }


@pytest.fixture
def sample_experience_data():
    return {
        "company": "Acme Labs",
        "title": "Senior ML Engineer",
        "start_date": "2021-03",
        "end_date": "2024-01",
        "description": "Built and deployed production ML pipelines serving 10M+ daily predictions.",
        "highlights": [
            "Reduced inference latency by 40% through model optimization",
            "Led team of 4 engineers on recommendation system",
        ],
        "skills_used": ["Python", "PyTorch", "Kubernetes", "AWS"],
    }


@pytest.fixture
def sample_job_description():
    return """
    Senior Machine Learning Engineer

    We are looking for a Senior ML Engineer to join our AI team.

    Requirements:
    - 5+ years of experience in machine learning
    - Strong proficiency in Python, PyTorch, or TensorFlow
    - Experience with cloud platforms (AWS, GCP, Azure)
    - Knowledge of MLOps practices and CI/CD
    - Excellent communication skills

    Nice to have:
    - Experience with LLMs and RAG systems
    - Publications in ML conferences
    - Experience with Kubernetes
    """
