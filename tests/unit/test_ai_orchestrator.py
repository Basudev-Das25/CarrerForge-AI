"""Unit tests for AI Orchestrator, Observability, and Prompt Registry."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai.observability import (
    AIObservation, ObservabilityTracker, estimate_cost, tracker,
)
from app.services.ai.prompt_registry import (
    load_prompt, render_prompt, list_prompts, clear_cache, validate_prompt,
)
from app.services.ai.providers.base import (
    AIProvider, ChatMessage, ChatResponse, MessageRole, ProviderHealth,
)
from app.services.agents.base import Agent, AgentResult


# ── Observability Tests ─────────────────────────────────────

def test_observation_creation():
    obs = AIObservation(
        provider="openai",
        model="gpt-4o",
        tokens_in=100,
        tokens_out=50,
        latency_ms=1500.0,
        cost_usd=0.001,
    )
    assert obs.provider == "openai"
    assert obs.success is True
    assert obs.id is not None


def test_tracker_records():
    t = ObservabilityTracker()
    obs = AIObservation(provider="openai", model="gpt-4o", tokens_in=100, tokens_out=50, cost_usd=0.001)
    t.record(obs)
    stats = t.get_stats()
    assert stats["total_requests"] == 1
    assert stats["total_cost_usd"] >= 0
    assert stats["total_tokens"] >= 0


def test_tracker_error_rate():
    t = ObservabilityTracker()
    t.record(AIObservation(success=True))
    t.record(AIObservation(success=True))
    t.record(AIObservation(success=False))
    assert t._error_rate() == pytest.approx(0.333, abs=0.01)


def test_estimate_cost():
    cost = estimate_cost("gpt-4o", 1000, 500)
    assert cost > 0
    cost_cheap = estimate_cost("gpt-4o-mini", 1000, 500)
    assert cost_cheap < cost


def test_tracker_get_recent():
    t = ObservabilityTracker()
    for i in range(5):
        t.record(AIObservation(provider="openai", model="gpt-4o"))
    recent = t.get_recent(limit=3)
    assert len(recent) == 3


# ── Prompt Registry Tests ───────────────────────────────────

def test_load_prompt():
    prompt = load_prompt("jd", "parser")
    assert "system" in prompt or "user" in prompt
    assert "metadata" in prompt


def test_render_prompt():
    rendered = render_prompt("jd", "parser", {"job_description_text": "Senior Python Developer at Google"})
    assert "Senior Python Developer" in rendered["user"]
    assert rendered["prompt_version"] is not None


def test_list_prompts():
    prompts = list_prompts()
    assert len(prompts) > 0
    categories = {p["category"] for p in prompts}
    assert "jd" in categories
    assert "resume" in categories


def test_list_prompts_by_category():
    prompts = list_prompts("ats")
    assert all(p["category"] == "ats" for p in prompts)


def test_validate_prompt():
    result = validate_prompt("jd", "parser")
    assert result["valid"] is True


def test_validate_nonexistent_prompt():
    result = validate_prompt("nonexistent", "prompt")
    assert result["valid"] is False


def test_prompt_cache():
    clear_cache()
    p1 = load_prompt("jd", "parser")
    p2 = load_prompt("jd", "parser")
    assert p1 is p2  # Same object from cache


# ── Provider Base Tests ─────────────────────────────────────

class MockProvider(AIProvider):
    @property
    def name(self):
        return "mock"

    @property
    def supported_models(self):
        return ["mock-1"]

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=4096, **kwargs):
        return ChatResponse(content="mock response", model="mock-1", usage={"total_tokens": 10})


@pytest.mark.asyncio
async def test_provider_chat():
    provider = MockProvider()
    messages = [ChatMessage(role=MessageRole.USER, content="hello")]
    response = await provider.chat(messages)
    assert response.content == "mock response"
    assert response.model == "mock-1"


@pytest.mark.asyncio
async def test_provider_health_check():
    provider = MockProvider()
    health = await provider.health_check()
    assert health.healthy is True
    assert "mock-1" in health.models_available


def test_provider_cost():
    provider = MockProvider()
    cost = provider.estimate_cost("mock-1", 1000, 500)
    assert cost == 0.0  # Mock returns 0


# ── Agent Base Tests ────────────────────────────────────────

class MockAgent(Agent):
    def __init__(self):
        super().__init__("mock_agent")

    def system_prompt(self):
        return "You are a test agent."

    def user_prompt(self, **kwargs):
        return f"Test: {kwargs.get('input', '')}"

    def parse_response(self, raw):
        return {"result": raw}


def test_agent_validation():
    agent = MockAgent()
    issues = agent.validate_input(input="hello")
    assert issues == []


def test_agent_json_parse():
    agent = MockAgent()
    result = agent._parse_json('{"key": "value"}')
    assert result["key"] == "value"


def test_agent_json_parse_markdown():
    agent = MockAgent()
    result = agent._parse_json('```json\n{"key": "value"}\n```')
    assert result["key"] == "value"


def test_agent_result():
    result = AgentResult(success=True, data={"test": 1}, latency_ms=100.0)
    d = result.to_dict()
    assert d["success"] is True
    assert d["data"]["test"] == 1


# ── Knowledge Graph Tests ───────────────────────────────────

def test_knowledge_graph_nodes():
    from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "Python"}))
    assert graph.get_node("skill", "1") is not None
    assert len(graph.get_nodes_by_type("skill")) == 1


def test_knowledge_graph_edges():
    from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode, KnowledgeEdge
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={}))
    graph.add_node(KnowledgeNode(id="project:1", entity_type="project", entity_id="1", properties={}))
    graph.add_edge(KnowledgeEdge(source_type="project", source_id="1", target_type="skill", target_id="1", relationship="uses"))
    assert len(graph.get_edges_from("project", "1")) == 1


def test_knowledge_scoring():
    from app.services.knowledge.graph import KnowledgeNode
    from app.services.knowledge.scoring import score_entity
    node = KnowledgeNode(
        id="exp:1", entity_type="experience", entity_id="1",
        properties={"title": "Engineering Manager", "company": "Google", "highlights": ["Led team of 10"]},
    )
    scores = score_entity(node)
    # "managed" and "lead" are in leadership keywords
    assert scores.get("leadership", 0) >= 0
    assert isinstance(scores, dict)


# ── Evidence Engine Tests ───────────────────────────────────

def test_evidence_item():
    from app.services.evidence.engine import EvidenceItem
    item = EvidenceItem(
        entity_type="skill", entity_id="1",
        properties={"name": "Python"},
        reason_for_selection="Matches job requirement",
        confidence_score=0.85,
    )
    d = item.to_dict()
    assert d["confidence_score"] == 0.85
    assert d["entity_type"] == "skill"


def test_evidence_bundle():
    from app.services.evidence.engine import EvidenceBundle, EvidenceItem
    bundle = EvidenceBundle(
        job_profile={"job_title": "Developer"},
        skills=[EvidenceItem(entity_type="skill", entity_id="1", properties={"name": "Python"}, reason_for_selection="Required")],
    )
    summary = bundle.summary()
    assert summary["skills"] == 1
    assert summary["experience"] == 0
