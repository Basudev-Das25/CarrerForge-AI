"""Keyword Extractor — extracts meaningful keywords from job descriptions.

Uses a hybrid two-tier approach:
1. Tech dictionary matching — reliable detection of concrete technologies,
   frameworks, platforms, and libraries mentioned verbatim in the JD.
2. KeyBERT semantic scoring — a curated pool of clean skill phrases is
   scored by cosine similarity against the document, so concepts like
   "data preprocessing" or "model evaluation" are ranked by relevance.

The KeyBERT candidate pool avoids the fragment/noise problem of raw
n-gram extraction (no "seeking", "enthusiastic", "graduates" filler).

Reuses the same sentence-transformers model already loaded for embeddings.
"""

from __future__ import annotations

import re
import structlog
from typing import Any

from app.services.embeddings import _get_model

logger = structlog.get_logger("careerforge.keywords.extractor")

# Common technology keywords to detect via exact/substring matching (no NLP needed)
TECH_KEYWORDS: set[str] = {
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "rust", "go",
    "ruby", "php", "swift", "kotlin", "scala", "perl", "matlab",
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
    "pandas", "numpy", "scikit-learn", "scikit learn", "spark", "hadoop", "kafka",
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
    "including", "related", "working", "knowledge", "ability",
    "skills", "skill", "required", "preferred", "must", "qualifications",
}

# Curated pool of clean skill phrases used for semantic relevance scoring.
# These are well-formed phrases (not n-gram fragments) so KeyBERT returns
# meaningful keywords instead of noise like "seeking" or "enthusiastic".
SKILL_CANDIDATES: list[str] = sorted({
    # AI / ML / Data
    "machine learning", "deep learning", "artificial intelligence", "data science",
    "data preprocessing", "feature engineering", "model evaluation", "model testing",
    "model training", "model deployment", "data collection", "data cleaning",
    "data structures", "algorithms", "computer science", "neural networks",
    "natural language processing", "computer vision", "reinforcement learning",
    "data analysis", "data visualization", "statistical analysis", "data mining",
    "big data", "data engineering", "data modeling", "data quality",
    "predictive modeling", "recommendation systems", "generative ai", "llm",
    # Cloud / DevOps
    "cloud computing", "cloud platforms", "devops", "ci/cd", "version control",
    "continuous integration", "continuous deployment", "infrastructure", "linux",
    # Software engineering
    "software engineering", "software development", "software design",
    "object-oriented programming", "api development", "rest apis", "microservices",
    "system design", "software testing", "unit testing", "automation testing",
    "debugging", "code review", "agile development", "technical documentation",
    "requirements analysis", "architecture", "database design",
    # Domains
    "kaggle", "hackathons", "internships", "research", "prototyping",
    # Professional / soft skills
    "problem solving", "analytical skills", "communication", "collaboration",
    "teamwork", "leadership", "project management", "critical thinking",
    "mentorship", "stakeholder management", "time management",
} | TECH_KEYWORDS)


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


# ── Legacy fallback helpers (only used if KeyBERT is unavailable) ──────────

def _extract_ngrams(text: str, n: int) -> list[str]:
    """Extract n-grams from text, stripping punctuation from tokens."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./]*", text.lower())
    clean = [w.rstrip(".,;:!?") for w in words if w.rstrip(".,;:!?")]
    return [" ".join(clean[i:i+n]) for i in range(len(clean) - n + 1)]


def _normalize(token: str) -> str:
    """Normalize a keyword token."""
    token = token.strip().lower()
    token = re.sub(r"[^a-zA-Z0-9+#./-]", " ", token)
    return " ".join(token.split())


def _contains_stop_word(tokens: list[str]) -> bool:
    """Check if any token is a stop word."""
    return any(t in STOP_WORDS for t in tokens)


class KeywordExtractor:
    """Hybrid keyword extractor: tech dictionary + KeyBERT semantic scoring."""

    def extract(self, jd_text: str, max_keywords: int = 40) -> KeywordResult:
        """Extract and rank keywords from a job description."""
        if not jd_text or len(jd_text) < 20:
            return KeywordResult([], [], [], [])

        # ── Tier 1: Tech dictionary matching (authoritative) ──
        jd_lower = jd_text.lower()
        detected_techs = sorted(
            t for t in TECH_KEYWORDS
            if re.compile(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])").search(jd_lower)
        )

        # ── Tier 2: KeyBERT semantic scoring of curated candidate pool ──
        must_include: list[str] = []
        nice_to_have: list[str] = []

        try:
            model = _get_model()
            from keybert import KeyBERT
            kw_model = KeyBERT(model=model)
            scored = kw_model.extract_keywords(
                jd_text,
                candidates=SKILL_CANDIDATES,
                top_n=40,
            )

            tech_set = {t.lower() for t in detected_techs}
            for phrase, score in scored:
                phrase_lower = phrase.lower()
                if phrase_lower in tech_set:
                    continue  # already reported as a technology
                if score >= 0.10:
                    must_include.append(phrase)
                elif score >= 0.05:
                    nice_to_have.append(phrase)
                if len(must_include) >= 20 and len(nice_to_have) >= 10:
                    break

        except Exception as exc:
            logger.warning("keybert_scoring.failed", error=str(exc))
            # Fallback: frequency-based n-gram extraction
            must_include, nice_to_have = self._frequency_fallback(jd_text)

        all_keywords = must_include + detected_techs + nice_to_have
        return KeywordResult(
            must_include=must_include,
            technologies=detected_techs,
            nice_to_have=nice_to_have,
            all_keywords=all_keywords[:max_keywords],
        )

    def _frequency_fallback(self, jd_text: str) -> tuple[list[str], list[str]]:
        """Legacy frequency-based extraction used when KeyBERT is unavailable."""
        candidates: dict[str, float] = {}

        for token in _extract_ngrams(jd_text, 1):
            norm = _normalize(token)
            if norm and len(norm) > 2 and norm not in STOP_WORDS:
                candidates[norm] = candidates.get(norm, 0) + 1

        for token in _extract_ngrams(jd_text, 2):
            norm = _normalize(token)
            parts = norm.split()
            if len(parts) == 2 and not _contains_stop_word(parts):
                candidates[norm] = candidates.get(norm, 0) + 1.5

        for token in _extract_ngrams(jd_text, 3):
            norm = _normalize(token)
            parts = norm.split()
            if len(parts) == 3 and not _contains_stop_word(parts):
                candidates[norm] = candidates.get(norm, 0) + 2

        ranked = sorted(candidates.items(), key=lambda x: -x[1])
        must_include = [t for t, _ in ranked[:20]]
        nice_to_have = [t for t, _ in ranked[20:30]]
        return must_include, nice_to_have
