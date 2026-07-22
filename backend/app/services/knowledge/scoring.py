"""Knowledge Scoring — compute relevance scores for every entity across dimensions.

Each entity receives a score from 0.0 to 1.0 for each scoring dimension,
based on keyword analysis, embedding similarity, and relationship traversal.
"""

from __future__ import annotations

import structlog

from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode

logger = structlog.get_logger("careerforge.knowledge.scoring")

# ── Scoring Dimensions & Keyword Maps ───────────────────────

DIMENSION_KEYWORDS: dict[str, list[str]] = {
    "leadership": [
        "lead", "leader", "managed", "management", "mentored", "mentoring",
        "directed", "directed", "supervised", "supervision", "oversaw",
        "head", "chief", "director", "vp", "principal", "staff",
        "team lead", "tech lead", "engineering manager",
    ],
    "machine_learning": [
        "machine learning", "ml", "deep learning", "neural", "nlp",
        "natural language", "computer vision", "cv", "ai", "artificial intelligence",
        "tensorflow", "pytorch", "keras", "transformer", "bert", "gpt",
        "llm", "large language model", "embedding", "classification",
        "regression", "clustering", "reinforcement learning",
    ],
    "backend": [
        "backend", "server", "api", "rest", "graphql", "database",
        "sql", "nosql", "postgresql", "mysql", "mongodb", "redis",
        "fastapi", "django", "flask", "express", "node.js", "spring",
        "microservice", "infrastructure", "orm", "migration",
    ],
    "frontend": [
        "frontend", "front-end", "ui", "ux", "user interface",
        "react", "vue", "angular", "svelte", "next.js", "nuxt",
        "tailwind", "css", "html", "javascript", "typescript",
        "responsive", "accessibility", "component", "design system",
    ],
    "cloud": [
        "cloud", "aws", "amazon web services", "gcp", "google cloud",
        "azure", "kubernetes", "k8s", "docker", "containerization",
        "serverless", "lambda", "ec2", "s3", "cloudformation",
        "terraform", "infrastructure as code", "iac", "cdn",
    ],
    "devops": [
        "devops", "ci/cd", "continuous integration", "continuous deployment",
        "jenkins", "github actions", "gitlab ci", "circleci",
        "monitoring", "observability", "logging", "alerting",
        "prometheus", "grafana", "datadog", "pagerduty",
        "deployment", "release", "infrastructure",
    ],
    "research": [
        "research", "paper", "published", "publication", "journal",
        "conference", "arxiv", "doi", "peer-reviewed", "citation",
        "hypothesis", "experiment", "methodology", "findings",
        "novel", "state-of-the-art", "sota", "benchmark",
    ],
    "data_science": [
        "data science", "data analyst", "analytics", "statistics",
        "statistical", "pandas", "numpy", "scipy", "visualization",
        "dashboard", "etl", "data pipeline", "big data", "spark",
        "hadoop", "data mining", "predictive", "forecasting",
    ],
    "management": [
        "project management", "product management", "program management",
        "agile", "scrum", "kanban", "sprint", "roadmap",
        "stakeholder", "budget", "planning", "strategy",
        "cross-functional", "prioritization", "delivery",
    ],
    "communication": [
        "communication", "presented", "presentation", "wrote", "writing",
        "technical writing", "documentation", "blog", "article",
        "public speaking", "speaking", "workshop", "training",
        "collaboration", "cross-team", "articulated", "explained",
    ],
    "ats_coverage": [],  # Scored dynamically against job descriptions
    "industry": [],      # Scored by matching industry keywords
    "seniority": [
        "senior", "sr.", "lead", "principal", "staff", "architect",
        "director", "vp", "head", "chief", "cto", "chief technology",
        "founded", "co-founded", "startup", "serial entrepreneur",
        "10+ years", "15+ years", "20+ years", "veteran",
    ],
}

# ── Scoring Functions ───────────────────────────────────────


def score_entity(node: KnowledgeNode) -> dict[str, float]:
    """Compute relevance scores for a single entity across all dimensions."""
    scores = {}
    text = _entity_text(node).lower()

    for dimension, keywords in DIMENSION_KEYWORDS.items():
        if not keywords:
            scores[dimension] = 0.0
            continue
        score = _keyword_score(text, keywords)
        scores[dimension] = round(min(score, 1.0), 3)

    # Boost scores based on entity-specific properties
    _apply_property_boosts(node, scores)

    return scores


def score_all(graph: KnowledgeGraph) -> None:
    """Score every node in the graph. Mutates nodes in-place."""
    for node in graph._nodes.values():
        node.scores = score_entity(node)
    logger.info("scoring.complete", nodes=len(graph._nodes))


def _entity_text(node: KnowledgeNode) -> str:
    """Extract all text from an entity for scoring."""
    parts = [node.text_repr]

    for v in node.properties.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
        elif isinstance(v, dict):
            for val in v.values():
                if isinstance(val, str):
                    parts.append(val)

    return " ".join(parts)


def _keyword_score(text: str, keywords: list[str]) -> float:
    """Score text against a list of keywords. Returns 0.0-1.0."""
    if not text.strip():
        return 0.0

    matches = 0
    for kw in keywords:
        if kw in text:
            matches += 1

    # Diminishing returns: first match matters most
    if matches == 0:
        return 0.0
    return 1.0 - (1.0 / (1.0 + matches * 0.5))


def _apply_property_boosts(node: KnowledgeNode, scores: dict[str, float]) -> None:
    """Apply boosts based on entity-specific properties."""
    props = node.properties

    # Experience-specific boosts
    if node.entity_type == "experience":
        emp_type = props.get("employment_type", "")
        if emp_type == "full-time":
            scores["seniority"] = min(scores.get("seniority", 0) + 0.1, 1.0)
        if props.get("highlights"):
            scores["communication"] = min(scores.get("communication", 0) + 0.15, 1.0)

    # Project-specific boosts
    elif node.entity_type == "project":
        if props.get("is_featured"):
            for dim in scores:
                scores[dim] = min(scores[dim] + 0.05, 1.0)
        if props.get("team_size", 0) > 1:
            scores["leadership"] = min(scores.get("leadership", 0) + 0.15, 1.0)
        if props.get("impact_metrics"):
            scores["management"] = min(scores.get("management", 0) + 0.1, 1.0)

    # Skill-specific boosts
    elif node.entity_type == "skill":
        if props.get("is_primary"):
            for dim in scores:
                if scores[dim] > 0:
                    scores[dim] = min(scores[dim] + 0.1, 1.0)
        if props.get("years_experience", 0) >= 5:
            scores["seniority"] = min(scores.get("seniority", 0) + 0.15, 1.0)

    # Certificate-specific boosts
    elif node.entity_type == "certificate":
        if props.get("verification_status") == "verified":
            for dim in scores:
                if scores[dim] > 0:
                    scores[dim] = min(scores[dim] + 0.05, 1.0)

    # Publication-specific boosts
    elif node.entity_type == "publication":
        cat = props.get("category", "")
        if cat in ("journal", "conference"):
            scores["research"] = min(scores.get("research", 0) + 0.2, 1.0)

    # Language-specific boosts
    elif node.entity_type == "language":
        if props.get("is_native"):
            scores["communication"] = min(scores.get("communication", 0) + 0.1, 1.0)

    # Award-specific boosts
    elif node.entity_type == "award":
        cat = props.get("category", "")
        if cat == "academic":
            scores["research"] = min(scores.get("research", 0) + 0.15, 1.0)
        elif cat == "professional":
            scores["seniority"] = min(scores.get("seniority", 0) + 0.1, 1.0)

    # Achievement-specific boosts
    elif node.entity_type == "achievement":
        cat = props.get("category", "")
        if cat == "publication":
            scores["research"] = min(scores.get("research", 0) + 0.2, 1.0)
        elif cat == "speaking":
            scores["communication"] = min(scores.get("communication", 0) + 0.2, 1.0)


def compute_ats_score(
    node: KnowledgeNode,
    jd_keywords: list[str],
    jd_requirements: list[str],
) -> float:
    """Compute ATS coverage score for an entity against job description keywords."""
    text = _entity_text(node).lower()
    all_jd_terms = [k.lower() for k in jd_keywords + jd_requirements]

    if not all_jd_terms:
        return 0.0

    matches = sum(1 for term in all_jd_terms if term in text)
    return round(matches / len(all_jd_terms), 3) if all_jd_terms else 0.0
