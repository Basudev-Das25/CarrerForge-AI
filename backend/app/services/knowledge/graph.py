"""Knowledge Graph — nodes, edges, and graph operations.

The knowledge graph connects all profile entities through weighted
relationships, enabling semantic traversal and relationship-aware retrieval.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("careerforge.knowledge.graph")


# ── Data Classes ────────────────────────────────────────────

@dataclass
class KnowledgeNode:
    """A node in the knowledge graph representing a profile entity."""
    id: str
    entity_type: str  # project, skill, certificate, experience, etc.
    entity_id: str    # DB primary key
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)
    embedding_id: str = ""
    scores: dict[str, float] = field(default_factory=dict)
    text_repr: str = ""  # Text representation for embedding

    def __hash__(self):
        return hash((self.entity_type, self.entity_id))

    def __eq__(self, other):
        return self.entity_type == other.entity_type and self.entity_id == other.entity_id


@dataclass
class KnowledgeEdge:
    """An edge in the knowledge graph connecting two entities."""
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relationship: str  # uses, earned_from, worked_on, requires, etc.
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.source_type}:{self.source_id}->{self.target_type}:{self.target_id}:{self.relationship}"

    def __hash__(self):
        return hash(self.key)


class KnowledgeGraph:
    """In-memory knowledge graph with indexed access."""

    def __init__(self):
        self._nodes: dict[str, KnowledgeNode] = {}
        self._edges: dict[str, KnowledgeEdge] = {}
        # Indexes for fast lookup
        self._by_type: dict[str, set[str]] = {}
        self._by_entity: dict[str, str] = {}  # "type:id" -> node_key
        self._adjacency: dict[str, set[str]] = {}  # node_key -> set of edge keys
        self._reverse_adjacency: dict[str, set[str]] = {}

    # ── Node Operations ─────────────────────────────────────

    def add_node(self, node: KnowledgeNode) -> None:
        """Add a node to the graph."""
        key = self._node_key(node)
        self._nodes[key] = node
        self._by_entity[f"{node.entity_type}:{node.entity_id}"] = key
        if node.entity_type not in self._by_type:
            self._by_type[node.entity_type] = set()
        self._by_type[node.entity_type].add(key)

    def get_node(self, entity_type: str, entity_id: str) -> KnowledgeNode | None:
        """Get a node by entity type and ID."""
        key = self._by_entity.get(f"{entity_type}:{entity_id}")
        return self._nodes.get(key) if key else None

    def get_nodes_by_type(self, entity_type: str) -> list[KnowledgeNode]:
        """Get all nodes of a given type."""
        keys = self._by_type.get(entity_type, set())
        return [self._nodes[k] for k in keys]

    def update_node(self, entity_type: str, entity_id: str, **kwargs) -> None:
        """Update properties of a node."""
        node = self.get_node(entity_type, entity_id)
        if node:
            for k, v in kwargs.items():
                if hasattr(node, k):
                    setattr(node, k, v)
                else:
                    node.properties[k] = v

    def remove_node(self, entity_type: str, entity_id: str) -> None:
        """Remove a node and all its edges."""
        key = self._by_entity.pop(f"{entity_type}:{entity_id}", None)
        if key is None:
            return
        node = self._nodes.pop(key, None)
        if node is None:
            return
        self._by_type.get(node.entity_type, set()).discard(key)
        # Remove connected edges
        for edge_key in list(self._adjacency.get(key, set())):
            self._remove_edge_by_key(edge_key)
        for edge_key in list(self._reverse_adjacency.get(key, set())):
            self._remove_edge_by_key(edge_key)
        self._adjacency.pop(key, None)
        self._reverse_adjacency.pop(key, None)

    # ── Edge Operations ─────────────────────────────────────

    def add_edge(self, edge: KnowledgeEdge) -> None:
        """Add an edge to the graph."""
        src_key = self._by_entity.get(f"{edge.source_type}:{edge.source_id}")
        tgt_key = self._by_entity.get(f"{edge.target_type}:{edge.target_id}")
        if src_key is None or tgt_key is None:
            return  # Both nodes must exist

        self._edges[edge.key] = edge
        if src_key not in self._adjacency:
            self._adjacency[src_key] = set()
        self._adjacency[src_key].add(edge.key)
        if tgt_key not in self._reverse_adjacency:
            self._reverse_adjacency[tgt_key] = set()
        self._reverse_adjacency[tgt_key].add(edge.key)

    def get_edges_from(self, entity_type: str, entity_id: str) -> list[KnowledgeEdge]:
        """Get all outgoing edges from a node."""
        key = self._by_entity.get(f"{entity_type}:{entity_id}")
        if key is None:
            return []
        return [self._edges[k] for k in self._adjacency.get(key, set())]

    def get_edges_to(self, entity_type: str, entity_id: str) -> list[KnowledgeEdge]:
        """Get all incoming edges to a node."""
        key = self._by_entity.get(f"{entity_type}:{entity_id}")
        if key is None:
            return []
        return [self._edges[k] for k in self._reverse_adjacency.get(key, set())]

    def get_neighbors(self, entity_type: str, entity_id: str, max_depth: int = 1) -> list[KnowledgeNode]:
        """Get neighboring nodes up to max_depth hops."""
        visited = set()
        result = []
        frontier = [(entity_type, entity_id, 0)]

        while frontier:
            et, eid, depth = frontier.pop(0)
            key = f"{et}:{eid}"
            if key in visited:
                continue
            visited.add(key)

            if depth > 0:
                node = self.get_node(et, eid)
                if node:
                    result.append(node)

            if depth < max_depth:
                # Outgoing edges
                for edge in self.get_edges_from(et, eid):
                    tgt = f"{edge.target_type}:{edge.target_id}"
                    if tgt not in visited:
                        frontier.append((edge.target_type, edge.target_id, depth + 1))
                # Incoming edges
                for edge in self.get_edges_to(et, eid):
                    src = f"{edge.source_type}:{edge.source_id}"
                    if src not in visited:
                        frontier.append((edge.source_type, edge.source_id, depth + 1))

        return result

    def _remove_edge_by_key(self, edge_key: str) -> None:
        """Remove an edge by its key string."""
        edge = self._edges.pop(edge_key, None)
        if edge is None:
            return
        src_key = self._by_entity.get(f"{edge.source_type}:{edge.source_id}")
        tgt_key = self._by_entity.get(f"{edge.target_type}:{edge.target_id}")
        if src_key:
            self._adjacency.get(src_key, set()).discard(edge_key)
        if tgt_key:
            self._reverse_adjacency.get(tgt_key, set()).discard(edge_key)

    # ── Query Operations ────────────────────────────────────

    def search(self, query_text: str, entity_types: list[str] | None = None) -> list[tuple[KnowledgeNode, float]]:
        """Simple text search across node text representations."""
        results = []
        query_lower = query_text.lower()
        for node in self._nodes.values():
            if entity_types and node.entity_type not in entity_types:
                continue
            score = 0.0
            # Check text representation
            if query_lower in node.text_repr.lower():
                score += 1.0
            # Check properties
            for v in node.properties.values():
                if isinstance(v, str) and query_lower in v.lower():
                    score += 0.5
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str) and query_lower in item.lower():
                            score += 0.5
            if score > 0:
                results.append((node, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def get_stats(self) -> dict:
        """Return graph statistics."""
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "node_types": {t: len(k) for t, k in self._by_type.items()},
        }

    def _node_key(self, node: KnowledgeNode) -> str:
        return f"{node.entity_type}:{node.entity_id}"
