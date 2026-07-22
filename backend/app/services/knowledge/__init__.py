"""Knowledge Engine — the semantic intelligence layer for CareerForge AI.

Builds a knowledge graph from all profile entities, generates embeddings,
discovers relationships, scores relevance, and provides retrieval APIs.
"""

from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode, KnowledgeEdge
from app.services.knowledge.engine import KnowledgeEngine

__all__ = ["KnowledgeGraph", "KnowledgeNode", "KnowledgeEdge", "KnowledgeEngine"]
