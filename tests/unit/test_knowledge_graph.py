"""Unit tests for the Knowledge Graph, Relationships, Scoring, and Retrieval."""

import pytest
from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode, KnowledgeEdge
from app.services.knowledge.scoring import score_entity, score_all, compute_ats_score
from app.services.knowledge.relationships import (
    discover_all_relationships,
    _discover_project_skill,
    _discover_certificate_skill,
    _discover_experience_project,
    _discover_publication_skill,
)
from app.services.knowledge.retrieval import (
    RetrievalRequest, RetrievalResponse,
    hybrid_search, keyword_search,
    get_relevant_entities, get_knowledge_summary,
)


# ── Knowledge Graph Tests ───────────────────────────────────

def test_add_and_get_node():
    graph = KnowledgeGraph()
    node = KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python", "category": "programming"},
        text_repr="Python programming",
    )
    graph.add_node(node)

    retrieved = graph.get_node("skill", "1")
    assert retrieved is not None
    assert retrieved.entity_type == "skill"
    assert retrieved.properties["name"] == "Python"


def test_get_nodes_by_type():
    graph = KnowledgeGraph()
    for i in range(3):
        graph.add_node(KnowledgeNode(
            id=f"skill:{i}", entity_type="skill", entity_id=str(i),
            properties={"name": f"Skill {i}"},
        ))
    graph.add_node(KnowledgeNode(
        id="project:1", entity_type="project", entity_id="1",
        properties={"name": "Project 1"},
    ))

    skills = graph.get_nodes_by_type("skill")
    assert len(skills) == 3
    projects = graph.get_nodes_by_type("project")
    assert len(projects) == 1


def test_add_edge():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "Python"}))
    graph.add_node(KnowledgeNode(id="project:1", entity_type="project", entity_id="1", properties={"name": "Proj"}))

    edge = KnowledgeEdge(
        source_type="project", source_id="1",
        target_type="skill", target_id="1",
        relationship="uses", weight=0.9,
    )
    graph.add_edge(edge)

    edges = graph.get_edges_from("project", "1")
    assert len(edges) == 1
    assert edges[0].relationship == "uses"


def test_get_neighbors():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "Python"}))
    graph.add_node(KnowledgeNode(id="project:1", entity_type="project", entity_id="1", properties={"name": "Proj"}))
    graph.add_node(KnowledgeNode(id="experience:1", entity_type="experience", entity_id="1", properties={"title": "SE"}))

    graph.add_edge(KnowledgeEdge(source_type="project", source_id="1", target_type="skill", target_id="1", relationship="uses"))
    graph.add_edge(KnowledgeEdge(source_type="experience", source_id="1", target_type="project", target_id="1", relationship="worked_on"))

    neighbors = graph.get_neighbors("project", "1", max_depth=1)
    neighbor_types = {(n.entity_type, n.entity_id) for n in neighbors}
    assert ("skill", "1") in neighbor_types
    assert ("experience", "1") in neighbor_types


def test_remove_node():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "Python"}))
    graph.add_node(KnowledgeNode(id="project:1", entity_type="project", entity_id="1", properties={"name": "Proj"}))
    graph.add_edge(KnowledgeEdge(source_type="project", source_id="1", target_type="skill", target_id="1", relationship="uses"))

    graph.remove_node("skill", "1")
    assert graph.get_node("skill", "1") is None
    assert len(graph.get_edges_from("project", "1")) == 0


def test_graph_search():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "Python"}, text_repr="Python programming language"))
    graph.add_node(KnowledgeNode(id="skill:2", entity_type="skill", entity_id="2", properties={"name": "React"}, text_repr="React frontend framework"))

    results = graph.search("Python")
    assert len(results) >= 1
    assert results[0][0].entity_id == "1"


def test_graph_stats():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={}))
    graph.add_node(KnowledgeNode(id="project:1", entity_type="project", entity_id="1", properties={}))

    stats = graph.get_stats()
    assert stats["nodes"] == 2
    assert "skill" in stats["node_types"]


# ── Scoring Tests ───────────────────────────────────────────

def test_score_skill_programming():
    node = KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python", "category": "programming", "years_experience": 7.0, "is_primary": True},
        text_repr="Python programming",
    )
    scores = score_entity(node)
    assert scores["backend"] > 0
    assert scores["seniority"] > 0  # 7 years experience


def test_score_experience_leadership():
    node = KnowledgeNode(
        id="experience:1", entity_type="experience", entity_id="1",
        properties={
            "title": "Engineering Manager",
            "company": "Google",
            "description": "Managed a team of 10 engineers",
            "highlights": ["Led team of 10", "Mentored junior developers"],
        },
        text_repr="Engineering Manager at Google",
    )
    scores = score_entity(node)
    assert scores["leadership"] > 0
    assert scores["management"] > 0


def test_score_project_featured():
    node = KnowledgeNode(
        id="project:1", entity_type="project", entity_id="1",
        properties={
            "name": "ML Pipeline",
            "description": "Machine learning pipeline with TensorFlow",
            "tech_stack": ["Python", "TensorFlow", "AWS"],
            "is_featured": True,
            "team_size": 5,
        },
        text_repr="ML Pipeline with TensorFlow",
    )
    scores = score_entity(node)
    assert scores["machine_learning"] > 0
    assert scores["cloud"] > 0


def test_score_publication_research():
    node = KnowledgeNode(
        id="publication:1", entity_type="publication", entity_id="1",
        properties={
            "title": "Novel Approach to NLP",
            "venue": "IEEE Conference",
            "category": "conference",
        },
        text_repr="Novel Approach to NLP at IEEE Conference",
    )
    scores = score_entity(node)
    assert scores["research"] > 0


def test_score_all():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python"}, text_repr="Python",
    ))
    graph.add_node(KnowledgeNode(
        id="project:1", entity_type="project", entity_id="1",
        properties={"name": "Web App", "tech_stack": ["React", "FastAPI"]},
        text_repr="Web App React FastAPI",
    ))
    score_all(graph)
    assert graph.get_node("skill", "1").scores is not None
    assert graph.get_node("project", "1").scores is not None


def test_compute_ats_score():
    node = KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python"},
        text_repr="Python programming language",
    )
    score = compute_ats_score(node, ["python", "react"], ["backend", "api"])
    assert 0 <= score <= 1


# ── Relationship Tests ──────────────────────────────────────

def test_discover_project_skill():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="project:1", entity_type="project", entity_id="1",
        properties={"tech_stack": ["Python", "React"], "skills_used": ["FastAPI"]},
    ))
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "Python"}))
    graph.add_node(KnowledgeNode(id="skill:2", entity_type="skill", entity_id="2", properties={"name": "React"}))
    graph.add_node(KnowledgeNode(id="skill:3", entity_type="skill", entity_id="3", properties={"name": "FastAPI"}))
    graph.add_node(KnowledgeNode(id="skill:4", entity_type="skill", entity_id="4", properties={"name": "Docker"}))

    count = _discover_project_skill(graph)
    assert count == 3  # Python, React, FastAPI
    edges = graph.get_edges_from("project", "1")
    assert len(edges) == 3


def test_discover_certificate_skill():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="certificate:1", entity_type="certificate", entity_id="1",
        properties={"skills": ["AWS", "Cloud"], "tags": ["infrastructure"]},
    ))
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "AWS"}))
    graph.add_node(KnowledgeNode(id="skill:2", entity_type="skill", entity_id="2", properties={"name": "Cloud"}))

    count = _discover_certificate_skill(graph)
    assert count == 2


def test_discover_experience_project():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="experience:1", entity_type="experience", entity_id="1",
        properties={"company": "Google", "skills_used": ["Python", "React"]},
    ))
    graph.add_node(KnowledgeNode(
        id="project:1", entity_type="project", entity_id="1",
        properties={"tech_stack": ["Python", "FastAPI"]},
    ))

    count = _discover_experience_project(graph)
    assert count >= 1  # Python shared


def test_discover_all_relationships():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="skill:1", entity_type="skill", entity_id="1", properties={"name": "Python"}))
    graph.add_node(KnowledgeNode(id="project:1", entity_type="project", entity_id="1", properties={"tech_stack": ["Python"]}))
    graph.add_node(KnowledgeNode(id="certificate:1", entity_type="certificate", entity_id="1", properties={"skills": ["Python"]}))

    count = discover_all_relationships(graph)
    assert count >= 2


# ── Retrieval Tests ─────────────────────────────────────────

def test_keyword_search():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python"}, text_repr="Python programming",
    ))
    graph.add_node(KnowledgeNode(
        id="skill:2", entity_type="skill", entity_id="2",
        properties={"name": "React"}, text_repr="React frontend",
    ))

    response = keyword_search(graph, "Python")
    assert response.total >= 1
    assert response.items[0].entity_id == "1"


def test_get_relevant_entities():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python", "category": "programming"},
        text_repr="Python programming", scores={"backend": 0.8},
    ))
    graph.add_node(KnowledgeNode(
        id="skill:2", entity_type="skill", entity_id="2",
        properties={"name": "React", "category": "framework"},
        text_repr="React frontend", scores={"frontend": 0.9},
    ))

    results = get_relevant_entities(graph, "Python backend", "skill")
    assert len(results) >= 1
    assert results[0]["entity_id"] == "1"


def test_get_knowledge_summary():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python"},
        text_repr="Python",
        scores={"backend": 0.8, "machine_learning": 0.5},
    ))
    graph.add_node(KnowledgeNode(
        id="project:1", entity_type="project", entity_id="1",
        properties={"name": "Web App"},
        text_repr="Web App",
        scores={"frontend": 0.7},
    ))
    graph.add_edge(KnowledgeEdge(
        source_type="project", source_id="1",
        target_type="skill", target_id="1",
        relationship="uses",
    ))

    summary = get_knowledge_summary(graph)
    assert summary["total_nodes"] == 2
    assert summary["total_edges"] == 1
    assert "skill" in summary["entity_counts"]
    assert "project" in summary["entity_counts"]


def test_hybrid_search_filters_by_type():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(
        id="skill:1", entity_type="skill", entity_id="1",
        properties={"name": "Python"}, text_repr="Python programming",
    ))
    graph.add_node(KnowledgeNode(
        id="project:1", entity_type="project", entity_id="1",
        properties={"name": "Python Project"}, text_repr="Python Project",
    ))

    request = RetrievalRequest(query="Python", entity_types=["skill"], top_k=10)
    response = hybrid_search(graph, request)
    for item in response.items:
        assert item.entity_type == "skill"
