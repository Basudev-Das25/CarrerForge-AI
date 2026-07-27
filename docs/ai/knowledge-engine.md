# Knowledge Engine

## Overview

The Knowledge Engine builds an in-memory graph connecting all profile entities through weighted relationships. It scores every entity across 13 dimensions and powers semantic retrieval for resume generation.

## Building the Graph

```python
from app.services.knowledge.engine import KnowledgeEngine

ke = KnowledgeEngine(session=db, user_id="default")
graph = await ke.build()
```

Build process:
1. Load all 14 entity types from database
2. Auto-discover relationships (8 types)
3. Score every entity across 13 dimensions

## 13 Scoring Dimensions

| Dimension | What It Measures |
|---|---|
| `leadership` | Management, team leading, mentoring |
| `machine_learning` | ML/AI skills and projects |
| `backend` | Server-side, API, database skills |
| `frontend` | UI, React, CSS, component skills |
| `cloud` | AWS, GCP, Azure, Kubernetes |
| `devops` | CI/CD, monitoring, infrastructure |
| `research` | Publications, papers, academic work |
| `data_science` | Analytics, statistics, data pipelines |
| `management` | Project management, planning, strategy |
| `communication` | Writing, presenting, documentation |
| `ats_coverage` | Matched ATS keywords (dynamic) |
| `industry` | Industry-specific keywords |
| `seniority` | Years, leadership titles, senior roles |

## Relationship Discovery

8 automatic relationship types:
- **uses** — Project → Skill (from tech_stack, skills_used)
- **demonstrates** — Certificate → Skill (from skills field)
- **involved_in** — Experience → Project (from shared skills)
- **coincides_with** — Achievement → Experience (from dates)
- **resulted_from** — Achievement → Experience (from shared org)
- **recognizes** — Award → Achievement (from shared org)
- **requires** — JobDescription → Skill (from keywords)
- **targets** — ResumeVersion → JobDescription

## Semantic Retrieval

```python
# Hybrid search
from app.services.knowledge.retrieval import RetrievalRequest
request = RetrievalRequest(query="Senior Python Developer", top_k=10)
response = ke.search(request)

# Get relevant entities
results = ke.get_relevant("skill", "Python backend", top_k=5)
```

Search types: hybrid (keyword + scoring), keyword-only, vector-only.
