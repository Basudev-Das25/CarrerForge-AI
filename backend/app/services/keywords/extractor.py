"""Keyword Extractor — extracts meaningful, GROUNDED keywords from job descriptions.

Three tiers, all grounded in the actual JD text:

1. Tech dictionary matching — reliable detection of concrete technologies,
   frameworks, and libraries mentioned verbatim in the JD.
2. LLM extraction (when an AI provider is configured) — domain-agnostic,
   recruiter-quality keywords for ANY industry (marketing, healthcare,
   finance, sales, etc.). The LLM is instructed to use only terms verbatim
   from the JD, and the output is still grounded below.
3. KeyBERT semantic scoring — a curated, domain-agnostic candidate pool is
   scored by cosine similarity to the document. Fallback when no LLM.

GROUNDING GUARANTEE: after every tier, each keyword must appear in the JD
text (case-insensitive substring match, hyphens/underscores normalized).
Any keyword NOT present in the JD is dropped — nothing imaginary is ever
reported as a requirement.
"""

from __future__ import annotations

import json
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

# Words that are too generic to be meaningful keywords on their own.
# Used to filter noisy n-grams/phrases so we keep concrete terms only.
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
    "whereunder","whether","whomever","whyever",
    # Role-description / framing filler
    "year", "years", "experience", "seeking", "enthusiastic", "fresh",
    "graduates", "join", "team", "assist", "developing", "training",
    "testing", "under", "guidance", "senior", "professionals", "including",
    "related", "working", "knowledge", "ability", "skills", "skill",
    "required", "preferred", "must", "qualifications", "responsible",
    "responsibilities", "role", "summary", "title", "strong", "excellent",
    "good", "great", "proven", "track", "record", "like", "tools", "learn",
    "integrate", "contribute", "collaborate", "perform", "conduct", "ensure",
    "stay", "updated", "latest", "trends", "industry", "building", "models",
    "using", "familiarity", "understanding", "basic", "passion", "technologies",
    "ability", "environment", "hands", "e.g.", "certification", "certifications",
    # More framing / fragment markers
    "while", "needed", "essential", "manner", "systems", "frameworks",
    "include", "responsible", "optimize", "collaborating", "solutions",
}

# ── Domain-agnostic candidate pool for KeyBERT fallback scoring ──
# Covers many industries so non-tech roles still get meaningful keywords
# when no AI provider is configured. Every candidate is still GROUNDED
# (must appear in the JD) before it is reported.
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
    # Cloud / DevOps / Software
    "cloud computing", "cloud platforms", "devops", "ci/cd", "version control",
    "continuous integration", "continuous deployment", "infrastructure", "linux",
    "software engineering", "software development", "software design",
    "object-oriented programming", "api development", "rest apis", "microservices",
    "system design", "software testing", "unit testing", "automation testing",
    "debugging", "code review", "agile development", "technical documentation",
    "requirements analysis", "architecture", "database design",
    # Marketing
    "seo", "content strategy", "social media", "social media management",
    "email marketing", "brand management", "campaign management",
    "campaign analytics", "paid advertising", "google ads", "copywriting",
    "audience segmentation", "conversion rate", "conversion rate optimization",
    "marketing automation", "market research", "public relations", "growth marketing",
    "a/b testing", "content creation", "digital marketing", "brand awareness",
    # Healthcare
    "patient care", "patient assessment", "patient education", "medication administration",
    "wound care", "clinical documentation", "emergency response", "infection control",
    "critical care", "electronic health records", "hipaa", "care plans", "triage",
    "patient safety", "diagnostic testing", "treatment planning", "medical records",
    "nursing", "acute care", "intensive care", "home health", "telehealth",
    # Finance / Accounting
    "financial analysis", "financial reporting", "budgeting", "forecasting",
    "tax preparation", "auditing", "financial modeling", "risk management",
    "compliance", "accounts payable", "accounts receivable", "financial planning",
    "cash flow management", "general ledger", "reconciliation", "financial statements",
    "cost analysis", "revenue forecasting", "internal controls", "sox compliance",
    # Sales / Business
    "sales pipeline", "lead generation", "customer relationship management",
    "negotiation", "cold outreach", "closing deals", "sales forecasting",
    "account management", "business development", "crm", "proposal writing",
    "contract negotiation", "quota attainment", "customer acquisition",
    "client relationship", "revenue growth", "territory management",
    # Education
    "curriculum development", "lesson planning", "student assessment",
    "classroom management", "instructional design", "differentiated instruction",
    "educational technology", "academic advising", "student engagement",
    # HR
    "recruitment", "onboarding", "employee relations", "performance management",
    "talent acquisition", "hr compliance", "benefits administration", "payroll",
    "talent development", "employee engagement", "workforce planning",
    # Legal
    "contract review", "legal research", "litigation", "due diligence",
    "case management", "regulatory affairs", "legal compliance", "intellectual property",
    # Customer service / Operations
    "customer support", "conflict resolution", "customer satisfaction",
    "call center", "technical support", "ticketing systems", "customer retention",
    "supply chain", "inventory management", "logistics", "procurement",
    "process improvement", "quality assurance", "vendor management", "operations",
    "project coordination", "data entry", "scheduling", "customer onboarding",
    # General professional
    "time management", "prioritization", "stakeholder management", "report writing",
    "presentation skills", "negotiation skills", "critical thinking", "communication",
    "collaboration", "teamwork", "leadership", "project management", "mentorship",
    "problem solving", "analytical skills", "decision making", "attention to detail",
    "organizational skills", "multitasking", "customer-facing", "cross-functional",
    # Domains / activities
    "kaggle", "hackathons", "internships", "research", "prototyping", "strategic planning",
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


# ── Grounding helpers ─────────────────────────────────────────

def _normalize_for_grounding(text: str) -> str:
    """Normalize text for grounding comparison: lowercase, collapse separators."""
    return re.sub(r"[\s_\-]+", " ", text.strip().lower())


def _is_grounded(keyword: str, jd_norm: str) -> bool:
    """Check that a keyword literally appears in the job description.

    Normalizes hyphens/underscores to spaces so 'critical-care' and
    'critical care' match, but never invents content absent from the JD.
    """
    return bool(keyword) and _normalize_for_grounding(keyword) in jd_norm


def _ground(keywords: list[str], jd_norm: str) -> list[str]:
    """Drop any keyword that does not appear verbatim in the JD."""
    seen: set[str] = set()
    result: list[str] = []
    for kw in keywords:
        norm = _normalize_for_grounding(kw)
        if norm in jd_norm and norm not in seen:
            seen.add(norm)
            result.append(kw)
    return result


class KeywordExtractor:
    """Three-tier, GROUNDED keyword extractor."""

    # ── Public API ─────────────────────────────────────────

    def extract(self, jd_text: str, max_keywords: int = 40) -> KeywordResult:
        """Sync extraction (tech dict + KeyBERT). Always grounded."""
        return self._build_result(jd_text, max_keywords, llm_extract=None)

    async def extract_async(self, jd_text: str, max_keywords: int = 40) -> KeywordResult:
        """Async extraction (tech dict + LLM, KeyBERT fallback). Always grounded."""
        try:
            from app.services.ai.orchestrator import orchestrator
            if orchestrator._providers:
                return await self._build_result_async(jd_text, max_keywords)
        except Exception as exc:
            logger.warning("keyword.llm_unavailable", error=str(exc))
        return self._build_result(jd_text, max_keywords, llm_extract=None)

    # ── Result assembly (sync path) ────────────────────────

    def _build_result(self, jd_text: str, max_keywords: int, llm_extract=None) -> KeywordResult:
        if not jd_text or len(jd_text) < 20:
            return KeywordResult([], [], [], [])
        jd_norm = _normalize_for_grounding(jd_text)

        # Tier 1: tech dictionary
        technologies = self._detect_technologies(jd_text)

        # Tier 3: KeyBERT (fallback when no LLM)
        try:
            must_include, nice_to_have = self._keybert_extract(jd_text)
        except Exception as exc:
            logger.warning("keybert_scoring.failed", error=str(exc))
            must_include, nice_to_have = self._frequency_fallback(jd_text)

        # Grounding: drop anything not verbatim in the JD
        must_include = _ground(must_include, jd_norm)
        nice_to_have = _ground(nice_to_have, jd_norm)
        technologies = _ground(technologies, jd_norm)

        all_keywords = must_include + technologies + nice_to_have
        return KeywordResult(
            must_include=must_include,
            technologies=technologies,
            nice_to_have=nice_to_have,
            all_keywords=all_keywords[:max_keywords],
        )

    # ── Result assembly (async / LLM path) ─────────────────

    async def _build_result_async(self, jd_text: str, max_keywords: int) -> KeywordResult:
        if not jd_text or len(jd_text) < 20:
            return KeywordResult([], [], [], [])
        jd_norm = _normalize_for_grounding(jd_text)

        technologies = self._detect_technologies(jd_text)

        try:
            must_include, nice_to_have = await self._llm_extract(jd_text)
        except Exception as exc:
            logger.warning("keyword.llm_failed", error=str(exc))
            try:
                must_include, nice_to_have = self._keybert_extract(jd_text)
            except Exception as exc2:
                logger.warning("keybert_scoring.failed", error=str(exc2))
                must_include, nice_to_have = self._frequency_fallback(jd_text)

        must_include = _ground(must_include, jd_norm)
        nice_to_have = _ground(nice_to_have, jd_norm)
        technologies = _ground(technologies, jd_norm)

        all_keywords = must_include + technologies + nice_to_have
        return KeywordResult(
            must_include=must_include,
            technologies=technologies,
            nice_to_have=nice_to_have,
            all_keywords=all_keywords[:max_keywords],
        )

    # ── Tier 1: tech dictionary ────────────────────────────

    def _detect_technologies(self, jd_text: str) -> list[str]:
        jd_lower = jd_text.lower()
        detected = []
        for t in TECH_KEYWORDS:
            pattern = re.compile(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])")
            if pattern.search(jd_lower):
                detected.append(t)
        return sorted(detected)

    # ── Tier 2: LLM extraction ─────────────────────────────

    async def _llm_extract(self, jd_text: str) -> tuple[list[str], list[str]]:
        from app.services.ai.orchestrator import orchestrator
        from app.services.ai.providers.base import ChatMessage, MessageRole

        prompt = (
            "You extract keywords from job descriptions for resume optimization. "
            "Extract the concrete skills, qualifications, tools, and requirements "
            "a candidate MUST have for this role.\n\n"
            "CRITICAL RULES:\n"
            "1. ONLY use terms that appear VERBATIM in the job description.\n"
            "2. Do NOT add, infer, or 'fill in' any skill or requirement that is "
            "not explicitly written in the job description.\n"
            "3. Exclude generic filler words (experience, team, required, etc.).\n"
            "4. Return ONLY valid JSON in this exact shape:\n"
            '{"must_include": ["term1", "term2"], "nice_to_have": ["term3"]}\n'
            "must_include: 8-15 essential items. nice_to_have: 0-8 preferred items.\n\n"
            f"JOB DESCRIPTION:\n{jd_text[:6000]}"
        )

        response = await orchestrator.chat(
            messages=[
                ChatMessage(role=MessageRole.SYSTEM, content=prompt),
            ],
            temperature=0.0,
            max_tokens=1024,
            use_cache=False,
        )

        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end]) if start >= 0 else {}

        must_include = [str(x).strip() for x in data.get("must_include", []) if str(x).strip()]
        nice_to_have = [str(x).strip() for x in data.get("nice_to_have", []) if str(x).strip()]
        return must_include, nice_to_have

    # ── Tier 3: KeyBERT candidate scoring + frequency phrases ──

    def _keybert_extract(self, jd_text: str) -> tuple[list[str], list[str]]:
        model = _get_model()
        from keybert import KeyBERT

        kw_model = KeyBERT(model=model)
        tech_set = {t.lower() for t in self._detect_technologies(jd_text)}
        must_include: list[str] = []
        nice_to_have: list[str] = []

        # (a) Candidate pool scoring — clean, curated skills across domains.
        scored = kw_model.extract_keywords(jd_text, candidates=SKILL_CANDIDATES, top_n=40)
        for phrase, score in scored:
            if phrase.lower() in tech_set:
                continue
            if score >= 0.08:
                must_include.append(phrase)
            elif score >= 0.04:
                nice_to_have.append(phrase)

        # (b) Frequency-based domain phrases — clean, comma/sentence aware,
        #     captures domain terms not in any pool ("patient assessment",
        #     "sales pipeline"). No fragments; grounding runs later.
        freq_must, freq_nice = self._frequency_fallback(jd_text)
        for phrase in freq_must:
            if phrase.lower() not in tech_set and phrase not in must_include:
                must_include.append(phrase)

        return must_include[:20], nice_to_have[:10]

    # ── Fallback frequency extraction (comma/sentence aware) ──

    def _frequency_fallback(self, jd_text: str) -> tuple[list[str], list[str]]:
        """Domain-agnostic n-gram extraction that respects comma/sentence
        boundaries so list items like 'patient assessment, medication
        administration' stay as clean phrases instead of sliding overlaps.
        """
        candidates: dict[str, float] = {}
        for segment in _segment_phrases(jd_text):
            for n, weight in ((2, 1.5), (3, 2.0)):
                for token in _extract_ngrams(segment, n):
                    norm = _normalize(token)
                    parts = norm.split()
                    if len(parts) == n and not any(p in STOP_WORDS for p in parts):
                        candidates[norm] = candidates.get(norm, 0) + weight

        ranked = sorted(candidates.items(), key=lambda x: (-x[1], len(x[0])))
        # Prefer shorter, distinct phrases; drop longer overlaps that are
        # substrings of an already-kept phrase.
        kept: list[str] = []
        for phrase, _score in ranked:
            if any(phrase in k for k in kept):
                continue
            kept.append(phrase)

        must_include = kept[:15]
        nice_to_have = kept[15:25]
        return must_include, nice_to_have


# ── Legacy fallback helpers ──────────────────────────────────

def _segment_phrases(text: str) -> list[str]:
    """Split text into phrase segments on commas, list separators, and
    sentence boundaries so list items remain clean phrases."""
    segments: list[str] = []
    for raw in re.split(r"[,;:\n\r]+", text):
        for part in re.split(r"(?<=[.!?])\s+", raw.strip()):
            part = part.strip()
            if part:
                segments.append(part)
    return segments


def _extract_ngrams(text: str, n: int) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./]*", text.lower())
    clean = [w.rstrip(".,;:!?") for w in words if w.rstrip(".,;:!?")]
    return [" ".join(clean[i:i+n]) for i in range(len(clean) - n + 1)]


def _normalize(token: str) -> str:
    token = token.strip().lower()
    token = re.sub(r"[^a-zA-Z0-9+#./-]", " ", token)
    return " ".join(token.split())
