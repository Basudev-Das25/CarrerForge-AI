"""LanceDB vector store integration.

Handles embedding storage, similarity search, and metadata filtering.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from app.config.settings import settings

logger = logging.getLogger("careerforge.lancedb")

_table_name = "embeddings"


def _get_db():
    """Get or create a LanceDB connection."""
    import lancedb

    db = lancedb.connect(settings.lancedb_path)
    return db


def _get_or_create_table():
    """Get the embeddings table, creating it if it doesn't exist."""
    db = _get_db()
    table_names = db.table_names()
    if _table_name in table_names:
        return db.open_table(_table_name)
    return db.create_table(
        _table_name,
        schema={
            "id": "string",
            "entity_type": "string",
            "entity_id": "string",
            "vector": "vector[384]",
            "text": "string",
            "tags": "string",
        },
    )


def upsert_embedding(
    embedding_id: str,
    entity_type: str,
    entity_id: str,
    vector: list[float],
    text: str,
    tags: str = "",
) -> None:
    """Insert or update an embedding record."""
    table = _get_or_create_table()

    # Delete existing record with same ID if present
    try:
        table.delete(f'id = "{embedding_id}"')
    except Exception:
        pass  # Table may be empty or ID doesn't exist

    table.add(
        [{
            "id": embedding_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "vector": vector,
            "text": text,
            "tags": tags,
        }]
    )
    logger.debug("lancedb.upsert", id=embedding_id, entity_type=entity_type)


def search_similar(
    query_vector: list[float],
    entity_type: str | None = None,
    top_k: int = 10,
    threshold: float = 0.0,
) -> list[dict[str, Any]]:
    """Find embeddings most similar to the query vector.

    Returns a list of dicts with: id, entity_type, entity_id, text, tags, distance.
    """
    table = _get_or_create_table()

    query = np.array(query_vector, dtype=np.float32)

    search = table.search(query).limit(top_k)

    if entity_type:
        search = search.where(f'entity_type = "{entity_type}"')

    results = search.to_list()

    # Filter by threshold (LanceDB returns L2 distance; convert to similarity)
    output = []
    for row in results:
        distance = row.get("_distance", 1.0)
        similarity = 1.0 / (1.0 + distance)
        if similarity >= threshold:
            output.append({
                "id": row["id"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "text": row.get("text", ""),
                "tags": row.get("tags", ""),
                "distance": distance,
                "similarity": round(similarity, 4),
            })

    return output


def delete_embedding(embedding_id: str) -> None:
    """Remove an embedding by ID."""
    table = _get_or_create_table()
    try:
        table.delete(f'id = "{embedding_id}"')
        logger.debug("lancedb.delete", id=embedding_id)
    except Exception as e:
        logger.warning("lancedb.delete.failed", id=embedding_id, error=str(e))


def count_embeddings(entity_type: str | None = None) -> int:
    """Count total embeddings, optionally filtered by entity type."""
    table = _get_or_create_table()
    if entity_type:
        results = table.search().where(f'entity_type = "{entity_type}"').to_list()
        return len(results)
    return table.count_rows()
