"""Shared test fixtures for CareerForge AI backend."""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Async HTTP test client."""
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
