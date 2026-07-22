"""Semantic Retrieval — hybrid search, vector search, keyword search, filtering.

Provides the search capabilities that power the Knowledge Engine's retrieval APIs.
Combines vector similarity, keyword matching, metadata filtering, and relationship
expansion for comprehensive results.
"""

from __future__ import annotations

import structlog
import re
from dataclasses import dataclass, field
from typing import Any

from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode

logger = structlog.get_logger("careerforge.knowledge.retrieval")


@dataclass
class RetrievalRequest:
    """Parameters for a knowledge retrieval query."""
    query: str
    entity_types: list[str] | None = None
    top_k: int = 10
    min_score: float = 0.0
    expand_relationships: bool = False
    relationship_depth: int = 1
    metadata_filters: dict[str, Any] = field(default_factory=dict)
    scoring_dimensions: list[str] | None = None
    scoring_min: float = 0.0


@dataclass
class RetrievalItem:
    """A single result from knowledge retrieval."""
    entity_type: str
    entity_id: str
    properties: dict[str, Any]
    scores: dict[str, float]
    relevance_score: float
    match_reason: str
    related_entities: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "properties": self.properties,
            "scores": self.scores,
            "relevance_score": self.relevance_score,
            "match_reason": self.match_reason,
            "related_entities": self.related_entities,
        }


@dataclass
class RetrievalResponse:
    """Response from knowledge retrieval."""
    items: list[RetrievalItem]
    query: str
    total: int
    graph_stats: dict = field(default_factory=dict)


# ── Search Functions ────────────────────────────────────────


def hybrid_search(
    graph: KnowledgeGraph,
    request: RetrievalRequest,
) -> RetrievalResponse:
    """Combine vector similarity, keyword matching, and metadata filtering.

    This is the primary retrieval function. It:
    1. Scores all candidate nodes
    2. Applies keyword matching
    3. Applies metadata filters
    4. Applies scoring dimension filters
    5. Expands relationships if requested
    6. Ranks by weighted combination
    7. Returns top-K results
    """
    candidates = _get_candidates(graph, request)

    # Score candidates
    scored = []
    for node, keyword_score in candidates:
        # Compute relevance as weighted combination
        vector_score = _vector_similarity(node.embedding, request.query) if node.embedding else 0.0
        dimension_score = _dimension_filter_score(node, request)

        # Weighted combination: 40% keyword, 35% vector, 25% dimension
        if node.embedding:
            relevance = 0.4 * keyword_score + 0.35 * vector_score + 0.25 * dimension_score
        else:
            relevance = 0.6 * keyword_score + 0.4 * dimension_score

        if relevance >= request.min_score and dimension_score >= request.scoring_min:
            scored.append((node, relevance, keyword_score, vector_score))

    # Sort by relevance
    scored.sort(key=lambda x: x[1], reverse=True)

    # Take top-K
    top_items = scored[:request.top_k]

    # Build response items
    items = []
    for node, relevance, kw_score, vec_score in top_items:
        related = []
        if request.expand_relationships:
            related = _get_related_entities(graph, node, request.relationship_depth)

        match_reasons = []
        if kw_score > 0.3:
            match_reasons.append(f"keyword match ({kw_score:.2f})")
        if vec_score > 0.3:
            match_reasons.append(f"semantic similarity ({vec_score:.2f})")
        if not match_reasons:
            match_reasons.append("property match")

        items.append(RetrievalItem(
            entity_type=node.entity_type,
            entity_id=node.entity_id,
            properties=node.properties,
            scores=node.scores,
            relevance_score=round(relevance, 4),
            match_reason=", ".join(match_reasons),
            related_entities=related,
        ))

    return RetrievalResponse(
        items=items,
        query=request.query,
        total=len(items),
        graph_stats=graph.get_stats(),
    )


def vector_search(
    graph: KnowledgeGraph,
    query: str,
    entity_types: list[str] | None = None,
    top_k: int = 10,
) -> RetrievalResponse:
    """Pure vector similarity search across all nodes with embeddings."""
    scored = []
    for node in graph._nodes.values():
        if not node.embedding:
            continue
        if entity_types and node.entity_type not in entity_types:
            continue
        sim = _vector_similarity(node.embedding, query)
        if sim > 0:
            scored.append((node, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    items = [
        RetrievalItem(
            entity_type=n.entity_type, entity_id=n.entity_id,
            properties=n.properties, scores=n.scores,
            relevance_score=round(s, 4),
            match_reason=f"vector similarity ({s:.4f})",
        )
        for n, s in scored[:top_k]
    ]
    return RetrievalResponse(items=items, query=query, total=len(items), graph_stats=graph.get_stats())


def keyword_search(
    graph: KnowledgeGraph,
    query: str,
    entity_types: list[str] | None = None,
    top_k: int = 10,
) -> RetrievalResponse:
    """Pure keyword/text search across all nodes."""
    results = graph.search(query, entity_types=entity_types)
    items = [
        RetrievalItem(
            entity_type=n.entity_type, entity_id=n.entity_id,
            properties=n.properties, scores=n.scores,
            relevance_score=round(s / max(r[1] for r in results) if results else 0, 4),
            match_reason=f"keyword match ({s:.2f})",
        )
        for n, s in results[:top_k]
    ]
    return RetrievalResponse(items=items, query=query, total=len(items), graph_stats=graph.get_stats())


def get_relevant_entities(
    graph: KnowledgeGraph,
    query: str,
    entity_type: str,
    jd_keywords: list[str] | None = None,
    jd_requirements: list[str] | None = None,
    top_k: int = 10,
    scoring_dimension: str | None = None,
) -> list[dict]:
    """Get the most relevant entities of a specific type for a query.

    This is the primary function used by resume generation to retrieve
    the best-matching entities for each section.
    """
    candidates = graph.get_nodes_by_type(entity_type)
    scored = []

    for node in candidates:
        # Keyword relevance
        kw_score = _keyword_match_score(node, query)

        # ATS coverage if JD provided
        ats_score = 0.0
        if jd_keywords or jd_requirements:
            text = _node_text(node).lower()
            terms = [t.lower() for t in (jd_keywords or []) + (jd_requirements or [])]
            if terms:
                ats_score = sum(1 for t in terms if t in text) / len(terms)

        # Dimension score
        dim_score = node.scores.get(scoring_dimension, 0.0) if scoring_dimension else 0.0

        # Combined relevance
        if jd_keywords or jd_requirements:
            relevance = 0.3 * kw_score + 0.5 * ats_score + 0.2 * dim_score
        else:
            relevance = 0.6 * kw_score + 0.4 * dim_score

        if relevance > 0:
            scored.append((node, relevance, kw_score, ats_score, dim_score))

    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for node, relevance, kw, ats, dim in scored[:top_k]:
        results.append({
            "entity_type": entity_type,
            "entity_id": node.entity_id,
            "properties": node.properties,
            "scores": node.scores,
            "relevance": round(relevance, 4),
            "keyword_match": round(kw, 4),
            "ats_coverage": round(ats, 4),
            "dimension_score": round(dim, 4),
        })

    return results


def get_knowledge_summary(
    graph: KnowledgeGraph,
    dimensions: list[str] | None = None,
) -> dict:
    """Generate a comprehensive knowledge summary across all entities."""
    summary = {
        "total_nodes": len(graph._nodes),
        "total_edges": len(graph._edges),
        "entity_counts": {},
        "dimension_averages": {},
        "top_entities_per_dimension": {},
        "relationship_stats": {},
    }

    # Entity counts
    for node_type in graph._by_type:
        summary["entity_counts"][node_type] = len(graph._by_type[node_type])

    # Dimension averages
    dims = dimensions or list(DIMENSION_KEYS)
    for dim in dims:
        scores = []
        for node in graph._nodes.values():
            if dim in node.scores and node.scores[dim] > 0:
                scores.append(node.scores[dim])
        if scores:
            summary["dimension_averages"][dim] = round(sum(scores) / len(scores), 3)
        else:
            summary["dimension_averages"][dim] = 0.0

    # Top entities per dimension
    for dim in dims:
        ranked = sorted(
            [(n, n.scores.get(dim, 0)) for n in graph._nodes.values() if n.scores.get(dim, 0) > 0],
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        summary["top_entities_per_dimension"][dim] = [
            {"type": n.entity_type, "id": n.entity_id, "score": round(s, 3)}
            for n, s in ranked
        ]

    # Relationship stats
    edge_types = {}
    for edge in graph._edges.values():
        rel = edge.relationship
        edge_types[rel] = edge_types.get(rel, 0) + 1
    summary["relationship_stats"] = edge_types

    return summary


# ── Internal Helpers ────────────────────────────────────────

DIMENSION_KEYS = list([
    "leadership", "machine_learning", "backend", "frontend",
    "cloud", "devops", "research", "data_science",
    "management", "communication", "ats_coverage", "industry", "seniority",
])


def _get_candidates(
    graph: KnowledgeGraph,
    request: RetrievalRequest,
) -> list[tuple[KnowledgeNode, float]]:
    """Get and pre-score all candidate nodes."""
    candidates = []
    query_lower = request.query.lower()
    query_words = set(re.findall(r'\w+', query_lower))

    for node in graph._nodes.values():
        if request.entity_types and node.entity_type not in request.entity_types:
            continue

        # Apply metadata filters
        if not _metadata_matches(node, request.metadata_filters):
            continue

        # Keyword score
        kw_score = _keyword_match_score(node, request.query)
        if kw_score > 0:
            candidates.append((node, kw_score))

    return candidates


def _keyword_match_score(node: KnowledgeNode, query: str) -> float:
    """Score how well a node matches the query text."""
    text = _node_text(node).lower()
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))

    if not text or not query_words:
        return 0.0

    # Exact phrase match
    if query_lower in text:
        return 1.0

    # Word overlap
    text_words = set(re.findall(r'\w+', text))
    overlap = query_words & text_words
    if overlap:
        return len(overlap) / len(query_words)

    return 0.0


def _vector_similarity(embedding: list[float], query: str) -> float:
    """Compute cosine similarity between an embedding and a query.
    Uses simple keyword-based approximation when embedding model is unavailable.
    """
    if not embedding:
        return 0.0
    # For now, return a placeholder — real vector similarity
    # is handled by LanceDB in the embeddings service
    return 0.0


def _metadata_matches(node: KnowledgeNode, filters: dict[str, Any]) -> bool:
    """Check if a node matches all metadata filters."""
    for key, value in filters.items():
        node_val = node.properties.get(key)
        if node_val is None:
            return False
        if isinstance(value, list):
            if node_val not in value:
                return False
        elif node_val != value:
            return False
    return True


def _dimension_filter_score(node: KnowledgeNode, request: RetrievalRequest) -> float:
    """Score based on requested scoring dimensions."""
    if not request.scoring_dimensions:
        return 1.0  # No dimension filter, pass all

    scores = []
    for dim in request.scoring_dimensions:
        scores.append(node.scores.get(dim, 0.0))
    return max(scores) if scores else 0.0


def _get_related_entities(
    graph: KnowledgeGraph,
    node: KnowledgeNode,
    depth: int,
) -> list[dict]:
    """Get related entities up to specified depth."""
    neighbors = graph.get_neighbors(node.entity_type, node.entity_id, max_depth=depth)
    return [
        {
            "entity_type": n.entity_type,
            "entity_id": n.entity_id,
            "properties": {k: v for k, v in n.properties.items() if isinstance(v, (str, int, float, bool))},
        }
        for n in neighbors[:10]  # Limit to 10 related entities
    ]


def _node_text(node: KnowledgeNode) -> str:
    """Get all text from a node."""
    parts = [node.text_repr]
    for v in node.properties.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
    return " ".join(parts)
