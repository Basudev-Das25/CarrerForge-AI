# Backend Architecture

## Layered Architecture

```
Routers (API) → Services (Business Logic) → Repository (Data Access) → Database
```

### Router Layer (`backend/app/routers/`)

12 API routers organized by domain:

| Router | Prefix | Endpoints |
|---|---|---|
| `admin.py` | `/api/v1` | Health, config |
| `ai.py` | `/api/v1/ai` | Chat, providers, embeddings |
| `ai_orchestrator.py` | `/api/v1/ai-orchestrator` | Chat, health, prompts, cache |
| `agents_api.py` | `/api/v1/agents` | 10 agent endpoints |
| `ats.py` | `/api/v1/ats` | Legacy ATS (stubs) |
| `ats_intelligence.py` | `/api/v1/ats-intelligence` | Analysis, optimization, comparison |
| `documents.py` | `/api/v1/documents` | Upload, list, search, delete |
| `jobs.py` | `/api/v1/jobs` | Parse, save, search, compare |
| `knowledge.py` | `/api/v1/knowledge` | Build, search, graph, scores |
| `profile.py` | `/api/v1` | CRUD for all profile entities |
| `resume_generator.py` | `/api/v1/resume` | Blueprint, generate, templates, versions |
| `resumes.py` | `/api/v1/resumes` | Legacy resume endpoints (stubs) |

### Service Layer (`backend/app/services/`)

Services contain all business logic. They never call database directly — always through the Repository.

| Service | Purpose |
|---|---|
| `profile.py` | Profile CRUD orchestrator |
| `knowledge/engine.py` | Knowledge graph builder and query engine |
| `knowledge/graph.py` | In-memory graph with indexed access |
| `knowledge/scoring.py` | 13-dimension entity scoring |
| `knowledge/relationships.py` | Auto-discovery of entity connections |
| `knowledge/retrieval.py` | Hybrid search (vector + keyword) |
| `resume/pipeline.py` | Full resume generation pipeline |
| `resume/blueprint.py` | Strategic planning before writing |
| `resume/canonical.py` | JSON source of truth with provenance |
| `resume/validator.py` | 10 quality checks |
| `templates/engine.py` | Template management + Typst rendering |
| `ats/engine.py` | ATS analysis, optimization, comparison |
| `ats/types.py` | Data classes for ATS reporting |
| `ai/orchestrator.py` | Centralized AI gateway |
| `ai/prompt_registry.py` | YAML prompt loading and rendering |
| `ai/observability.py` | Request logging and cost tracking |
| `job/intelligence.py` | JD parsing into structured profiles |
| `job/repository.py` | JD storage and search |
| `evidence/engine.py` | Evidence bundle generation |
| `agents/base.py` | Reusable agent pattern |
| `agents/*.py` | 12 specialized AI agents |
| `document_processor.py` | PDF text extraction, OCR, chunking |
| `embeddings.py` | Sentence-transformer vector generation |

### Repository Layer (`backend/app/db/`)

Generic async CRUD repository:

```python
repo = Repository(Model, session)
items = await repo.list(filters={"user_id": uid}, order_by="name", limit=50, offset=0)
item = await repo.get(id)
item = await repo.create(data)
item = await repo.update(id, data)
await repo.soft_delete(id)
count = await repo.count(filters)
```

The repository supports:
- Automatic soft-delete filtering
- Text search across fields
- Pagination (limit/offset)
- Sorting by any column
- Count with filters

### Error Handling

Custom exception hierarchy in `utils/errors.py`:

```
CareerForgeError (base)
├── DatabaseError
├── ValidationError
├── ProviderError / ProviderNotConfiguredError
├── PipelineError
├── DocumentError
├── SecurityError
├── EmbeddingError
└── NotFoundError
```

### Logging

Structured logging via `structlog` — every log line is a JSON object with timestamp, level, logger name, and context fields.
