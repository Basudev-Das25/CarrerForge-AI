"""Knowledge Engine API — retrieval, search, scoring, and graph operations.

Provides endpoints for:
- Semantic search across all profile entities
- Relevant entity retrieval for resume generation
- Knowledge graph visualization
- Embedding management
- Knowledge scoring and summary
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.knowledge.engine import KnowledgeEngine
from app.services.knowledge.retrieval import RetrievalRequest

router = APIRouter()

DEFAULT_USER_ID = "default"


def _get_engine(db: AsyncSession = Depends(get_db)) -> KnowledgeEngine:
    return KnowledgeEngine(session=db, user_id=DEFAULT_USER_ID)


# ── Request/Response Models ─────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    entity_types: list[str] | None = None
    top_k: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    expand_relationships: bool = False
    relationship_depth: int = Field(default=1, ge=1, le=3)
    scoring_dimensions: list[str] | None = None
    scoring_min: float = Field(default=0.0, ge=0.0, le=1.0)


class RelevantRequest(BaseModel):
    query: str = Field(..., min_length=1)
    jd_keywords: list[str] | None = None
    jd_requirements: list[str] | None = None
    top_k: int = Field(default=10, ge=1, le=50)
    scoring_dimension: str | None = None


# ── Build & Status ──────────────────────────────────────────

@router.post("/build")
async def build_knowledge_graph(engine: KnowledgeEngine = Depends(_get_engine)):
    """Build the complete knowledge graph from all profile data."""
    graph = await engine.build()
    return {"status": "built", **graph.get_stats()}


@router.get("/stats")
async def get_stats(engine: KnowledgeEngine = Depends(_get_engine)):
    """Get knowledge graph statistics."""
    await engine.build()
    return engine.get_graph_stats()


@router.get("/embedding-status")
async def get_embedding_status(engine: KnowledgeEngine = Depends(_get_engine)):
    """Get embedding generation status for all entities."""
    await engine.build()
    return engine.get_embedding_status()


@router.post("/embeddings/generate")
async def generate_embeddings(engine: KnowledgeEngine = Depends(_get_engine)):
    """Generate embeddings for all entities."""
    await engine.build()
    counts = await engine.generate_all_embeddings()
    return {"status": "generated", "counts": counts}


@router.post("/embeddings/regenerate")
async def regenerate_embeddings(engine: KnowledgeEngine = Depends(_get_engine)):
    """Delete and regenerate all embeddings."""
    await engine.build()
    counts = await engine.regenerate_all_embeddings()
    return {"status": "regenerated", "counts": counts}


# ── Search ──────────────────────────────────────────────────

@router.post("/search")
async def semantic_search(request: SearchRequest, engine: KnowledgeEngine = Depends(_get_engine)):
    """Hybrid semantic search across all profile entities."""
    await engine.build()
    retrieval_request = RetrievalRequest(
        query=request.query,
        entity_types=request.entity_types,
        top_k=request.top_k,
        min_score=request.min_score,
        expand_relationships=request.expand_relationships,
        relationship_depth=request.relationship_depth,
        scoring_dimensions=request.scoring_dimensions,
        scoring_min=request.scoring_min,
    )
    response = engine.search(retrieval_request)
    return {
        "query": response.query,
        "total": response.total,
        "items": [item.to_dict() for item in response.items],
        "graph_stats": response.graph_stats,
    }


@router.get("/search/keyword")
async def keyword_search_endpoint(
    q: str = Query(..., min_length=1),
    entity_types: str | None = None,
    top_k: int = Query(default=10, ge=1, le=100),
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Keyword/text search across all entities."""
    await engine.build()
    types = entity_types.split(",") if entity_types else None
    response = engine.keyword_search(q, entity_types=types, top_k=top_k)
    return {
        "query": response.query,
        "total": response.total,
        "items": [item.to_dict() for item in response.items],
    }


@router.get("/search/vector")
async def vector_search_endpoint(
    q: str = Query(..., min_length=1),
    entity_types: str | None = None,
    top_k: int = Query(default=10, ge=1, le=100),
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Vector similarity search across all entities."""
    await engine.build()
    types = entity_types.split(",") if entity_types else None
    response = engine.vector_search(q, entity_types=types, top_k=top_k)
    return {
        "query": response.query,
        "total": response.total,
        "items": [item.to_dict() for item in response.items],
    }


# ── Relevant Entity Retrieval ───────────────────────────────

@router.post("/relevant/{entity_type}")
async def get_relevant_entities(
    entity_type: str,
    request: RelevantRequest,
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get the most relevant entities of a specific type."""
    await engine.build()
    results = engine.get_relevant(
        entity_type=entity_type,
        query=request.query,
        jd_keywords=request.jd_keywords,
        jd_requirements=request.jd_requirements,
        top_k=request.top_k,
        scoring_dimension=request.scoring_dimension,
    )
    return {"entity_type": entity_type, "total": len(results), "items": results}


@router.get("/relevant/projects")
async def relevant_projects(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    dimension: str | None = None,
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get most relevant projects for a query."""
    await engine.build()
    return {"items": engine.get_relevant("project", q, top_k=top_k, scoring_dimension=dimension)}


@router.get("/relevant/skills")
async def relevant_skills(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    dimension: str | None = None,
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get most relevant skills for a query."""
    await engine.build()
    return {"items": engine.get_relevant("skill", q, top_k=top_k, scoring_dimension=dimension)}


@router.get("/relevant/experience")
async def relevant_experience(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    dimension: str | None = None,
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get most relevant experience entries for a query."""
    await engine.build()
    return {"items": engine.get_relevant("experience", q, top_k=top_k, scoring_dimension=dimension)}


@router.get("/relevant/certificates")
async def relevant_certificates(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get most relevant certificates for a query."""
    await engine.build()
    return {"items": engine.get_relevant("certificate", q, top_k=top_k)}


@router.get("/relevant/achievements")
async def relevant_achievements(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get most relevant achievements for a query."""
    await engine.build()
    return {"items": engine.get_relevant("achievement", q, top_k=top_k)}


# ── Knowledge Graph ─────────────────────────────────────────

@router.get("/graph")
async def get_graph(engine: KnowledgeEngine = Depends(_get_engine)):
    """Get the full knowledge graph structure."""
    await engine.build()
    nodes = []
    for node in engine.graph._nodes.values():
        nodes.append({
            "type": node.entity_type,
            "id": node.entity_id,
            "scores": node.scores,
            "properties": {k: v for k, v in node.properties.items() if isinstance(v, (str, int, float, bool))},
        })

    edges = []
    for edge in engine.graph._edges.values():
        edges.append({
            "source_type": edge.source_type,
            "source_id": edge.source_id,
            "target_type": edge.target_type,
            "target_id": edge.target_id,
            "relationship": edge.relationship,
            "weight": edge.weight,
        })

    return {"nodes": nodes, "edges": edges, "stats": engine.graph.get_stats()}


@router.get("/graph/{entity_type}/{entity_id}")
async def get_entity_graph(
    entity_type: str,
    entity_id: str,
    depth: int = Query(default=1, ge=1, le=3),
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get a specific entity and its neighbors."""
    await engine.build()
    node = engine.get_node(entity_type, entity_id)
    if node is None:
        return {"error": "Entity not found"}

    return {
        "entity": {
            "type": node.entity_type,
            "id": node.entity_id,
            "scores": node.scores,
            "properties": node.properties,
        },
        "neighbors": engine.get_neighbors(entity_type, entity_id, depth=depth),
    }


# ── Summary & Scoring ───────────────────────────────────────

@router.get("/summary")
async def get_summary(
    dimensions: str | None = None,
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get comprehensive knowledge summary."""
    await engine.build()
    dims = dimensions.split(",") if dimensions else None
    return engine.get_summary(dimensions=dims)


@router.get("/scores/{entity_type}/{entity_id}")
async def get_entity_scores(
    entity_type: str,
    entity_id: str,
    engine: KnowledgeEngine = Depends(_get_engine),
):
    """Get scoring breakdown for a specific entity."""
    await engine.build()
    node = engine.get_node(entity_type, entity_id)
    if node is None:
        return {"error": "Entity not found"}
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "scores": node.scores,
        "text_preview": node.text_repr[:200],
    }
