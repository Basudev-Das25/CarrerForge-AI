"""Embedding service — generates vectors from text and stores them in LanceDB."""

from __future__ import annotations

import uuid

import structlog

from app.config.settings import settings
from app.db.lance import count_embeddings, delete_embedding, search_similar, upsert_embedding

logger = structlog.get_logger("careerforge.embeddings")

# Lazy-loaded sentence transformer model
_model = None


def _get_model():
    """Load the sentence-transformers model (once)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.embedding_model)
        logger.info("embedding.model_loaded", model=settings.embedding_model)
    return _model


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text."""
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def store_embedding(
    entity_type: str,
    entity_id: str,
    text: str,
    tags: str = "",
) -> str:
    """Generate embedding for text, store in LanceDB, return embedding ID."""
    embedding_id = str(uuid.uuid4())
    vector = generate_embedding(text)
    upsert_embedding(
        embedding_id=embedding_id,
        entity_type=entity_type,
        entity_id=entity_id,
        vector=vector,
        text=text,
        tags=tags,
    )
    logger.info("embedding.stored", entity_type=entity_type, entity_id=entity_id)
    return embedding_id


def find_similar(
    query: str,
    entity_type: str | None = None,
    top_k: int = 10,
    threshold: float = 0.5,
) -> list[dict]:
    """Find entities semantically similar to the query text."""
    query_vector = generate_embedding(query)
    return search_similar(query_vector, entity_type=entity_type, top_k=top_k, threshold=threshold)


def remove_embedding(embedding_id: str) -> None:
    """Delete an embedding from the vector store."""
    delete_embedding(embedding_id)


def get_stats() -> dict:
    """Return embedding statistics."""
    return {
        "total": count_embeddings(),
        "experiences": count_embeddings("experience"),
        "skills": count_embeddings("skill"),
        "projects": count_embeddings("project"),
        "job_descriptions": count_embeddings("jd"),
    }
