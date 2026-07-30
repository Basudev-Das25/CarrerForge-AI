"""Keyword Extractor — extracts meaningful keywords from job descriptions.

Uses a two-phase approach:
1. Statistical: n-gram frequency scoring
2. Semantic: sentence-transformers similarity to skill/requirement phrases

Reuses the same sentence-transformers model already loaded for embeddings.
"""

from __future__ import annotations

import re
import structlog
from typing import Any

from app.services.embeddings import _get_model

logger = structlog.get_logger("careerforge.keywords.extractor")

# Common technology keywords to detect (no NLP needed)
TECH_KEYWORDS: set[str] = {
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "rust", "go",
    "ruby", "php", "swift", "kotlin", "scala", "perl", "r", "matlab",
    "sql", "bash", "shell", "powershell", "dart", "lua", "haskell",
    # Frontend
    "react", "angular", "vue", "svelte", "next.js", "nuxt", "html", "css",
    "sass", "less", "tailwind", "bootstrap", "jquery", "redux", "webpack",
    "vite", "babel", "jest", "cypress",
    # Backend
    "node.js", "express", "django", "flask", "fastapi", "spring", "asp.net",
    "laravel", "rails", "graphql", "rest", "grpc", "websocket",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform",
    "ansible", "jenkins", "github actions", "gitlab ci", "ci/cd",
    "prometheus", "grafana", "elasticsearch", "datadog", "new relic",
    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "dynamodb", "cassandra", "neo4j", "sqlite", "mariadb", "oracle",
    "bigquery", "redshift", "snowflake",
    # Data & ML
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "spark", "hadoop", "kafka",
    "airflow", "dbt", "looker", "tableau",
    # Tools
    "git", "github", "jira", "confluence", "figma", "notion", "slack",
    "vscode", "intellij", "pycharm",
    # Concepts
    "agile", "scrum", "kanban", "microservices", "serverless",
    "api", "restful", "saas", "paas", "iaas",
}

STOP_WORDS: set[str] = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","as","is","was","are","were","be","been","being","have",
    "has","had","do","does","did","will","would","could","should","may",
    "might","shall","can","need","dare","ought","used","this","that","these",
    "those","it","its","they","them","their","we","us","our","you","your",
    "he","she","him","her","his","who","whom","which","what","when","where",
    "why","how","all","each","every","both","few","several","some","any",
    "no","none","not","only","own","same","so","than","too","very","just",
    "about","above","after","again","against","below","between","during",
    "before","behind","beneath","beside","besides","beyond","inside","into",
    "onto","outside","through","under","until","up","upon","within","without",
    "along","among","around","because","done","due","else","even","ever",
    "further","hence","here","hereby","herein","hereof","hereto","hereunder",
    "however","indeed","instead","likewise","maybe","moreover","namely",
    "nevertheless","next","nonetheless","notwithstanding","otherwise",
    "perhaps","please","rather","regarding","since","still","subsequently",
    "such","there","thereby","therefore","therein","thereof","thereto",
    "thereunder","thus","together","unless","unlike","versus","via",
    "whatsoever","whenever","whereas","whereby","wherein","whereof","whereto",
    "whereunder","whether","whomever","whyever", "year", "years", "experience",
    "including", "including", "related", "working", "knowledge", "ability",
    "skills", "skill", "required", "preferred", "must", "qualifications",
}

# Seed phrases for semantic relevance scoring
SKILL_SEED_PHRASES = [
    "technical requirement",
    "required skill",
    "job qualification",
    "essential criteria",
    "professional experience",
    "technical competency",
    "core responsibility",
    "key requirement",
]


class KeywordResult:
    """Structured keyword extraction result."""
    def __init__(
        self,
        must_include: list[str],
        technologies: list[str],
        nice_to_have: list[str],
        all_keywords: list[str],
    ):
        self.must_include = must_include
        self.technologies = technologies
        self.nice_to_have = nice_to_have
        self.all_keywords = all_keywords

    def to_dict(self) -> dict[str, Any]:
        return {
            "must_include": self.must_include,
            "technologies": self.technologies,
            "nice_to_have": self.nice_to_have,
            "all_keywords": self.all_keywords,
        }


def _extract_ngrams(text: str, n: int) -> list[str]:
    """Extract n-grams from text."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9.#+/]+", text.lower())
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]


def _normalize(token: str) -> str:
    """Normalize a keyword token."""
    token = token.strip().lower()
    token = re.sub(r"[^a-zA-Z0-9+#./]", " ", token)
    return " ".join(token.split())


class KeywordExtractor:
    """Two-phase keyword extractor using statistics + semantics."""

    def extract(self, jd_text: str, max_keywords: int = 40) -> KeywordResult:
        """Extract and rank keywords from a job description."""
        if not jd_text or len(jd_text) < 20:
            return KeywordResult([], [], [], [])

        # Phase 1: N-gram extraction and frequency scoring
        candidates: dict[str, float] = {}

        # Single words
        for token in _extract_ngrams(jd_text, 1):
            norm = _normalize(token)
            if norm and len(norm) > 2 and norm not in STOP_WORDS:
                candidates[norm] = candidates.get(norm, 0) + 1

        # Bigrams
        for token in _extract_ngrams(jd_text, 2):
            norm = _normalize(token)
            parts = norm.split()
            if len(parts) == 2 and not all(p in STOP_WORDS for p in parts):
                candidates[norm] = candidates.get(norm, 0) + 1.5

        # Trigrams
        for token in _extract_ngrams(jd_text, 3):
            norm = _normalize(token)
            parts = norm.split()
            if len(parts) == 3 and not all(p in STOP_WORDS for p in parts):
                candidates[norm] = candidates.get(norm, 0) + 2

        if not candidates:
            return KeywordResult([], [], [], [])

        # Phase 2: Detect technologies (exact match against known dictionary)
        jd_lower = jd_text.lower()
        detected_techs = sorted(
            t for t in TECH_KEYWORDS 
            if t in jd_lower or t.replace("-", " ") in jd_lower or t.replace(".", r"\.") in jd_lower
        )[:15]

        # Phase 3: Semantic scoring using sentence-transformers
        # Rank candidates by similarity to skill/requirement seed phrases
        try:
            model = _get_model()
            candidate_list = sorted(candidates.items(), key=lambda x: -x[1])[:80]
            candidate_texts = [c[0] for c in candidate_list]

            # Encode seed phrases once
            seed_embeddings = model.encode(SKILL_SEED_PHRASES, normalize_embeddings=True)
            # Average seed embedding
            import numpy as np
            seed_vector = np.mean(seed_embeddings, axis=0)

            # Encode candidates and compute similarity to seed
            candidate_embeddings = model.encode(candidate_texts, normalize_embeddings=True)
            similarities = np.dot(candidate_embeddings, seed_vector)

            # Combine frequency score with semantic score
            max_freq = max(candidates.values()) if candidates else 1
            scored = []
            for (text, freq), sim in zip(candidate_list, similarities):
                freq_score = freq / max_freq
                semantic_score = max(0, float(sim))
                combined = 0.4 * freq_score + 0.6 * semantic_score
                scored.append((text, combined))

            scored.sort(key=lambda x: -x[1])

            # Split into categories
            tech_set = {t.lower() for t in detected_techs}
            must_include = []
            nice_to_have = []

            for text, score in scored:
                if text in tech_set:
                    continue  # will be in technologies
                if len(must_include) < 20:
                    must_include.append(text)
                elif len(nice_to_have) < 20:
                    nice_to_have.append(text)
                else:
                    break

        except Exception as exc:
            logger.warning("semantic_scoring.failed", error=str(exc))
            # Fallback: use frequency-only scoring
            ranked = sorted(candidates.items(), key=lambda x: -x[1])
            must_include = [t for t, _ in ranked[:20]]
            nice_to_have = []

        all_keywords = must_include + detected_techs + nice_to_have

        return KeywordResult(
            must_include=must_include,
            technologies=detected_techs,
            nice_to_have=nice_to_have,
            all_keywords=all_keywords[:max_keywords],
        )
