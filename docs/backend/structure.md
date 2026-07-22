# Backend Project Structure

## Directory Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, router registration
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # Pydantic settings, env vars, defaults
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # Engine, session factory, get_db dependency
│   │   ├── models.py        # SQLAlchemy ORM models (14 tables)
│   │   ├── repository.py    # Generic async CRUD repository
│   │   └── lance.py         # LanceDB vector store operations
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── providers/           # Legacy provider abstraction
│   ├── routers/             # 12 API routers
│   ├── services/            # Business logic (see below)
│   └── utils/
│       ├── errors.py        # Custom exception hierarchy
│       └── logger.py        # Structured logging with structlog
├── migrations/
│   ├── env.py               # Alembic async environment
│   ├── script.py.mako       # Migration template
│   └── versions/
│       └── 001_initial_schema.py
├── prompts/                 # Version-controlled AI prompts
│   ├── ats/
│   ├── jd/
│   ├── optimizer/
│   ├── reflection/
│   └── resume/
├── pyproject.toml           # Ruff + mypy configuration
└── requirements.txt         # Python dependencies
```

## Service Layer Organization

```
services/
├── ai/
│   ├── __init__.py
│   ├── orchestrator.py      # Central AI gateway
│   ├── prompt_registry.py   # YAML prompt loading
│   ├── observability.py     # Request logging, cost tracking
│   └── providers/           # 6 AI provider implementations
│       ├── base.py          # Abstract provider interface
│       ├── openai_provider.py
│       ├── anthropic_provider.py
│       ├── openrouter_provider.py
│       ├── ollama_provider.py
│       ├── grok_provider.py
│       └── huggingface_provider.py
├── agents/
│   ├── base.py              # Agent base class
│   └── *.py                 # 12 specialized agents
├── ats/
│   ├── engine.py            # ATS analysis engine
│   └── types.py             # ATS data classes
├── evidence/
│   └── engine.py            # Evidence bundle generation
├── job/
│   ├── intelligence.py       # JD parsing
│   └── repository.py        # JD storage
├── knowledge/
│   ├── engine.py            # Knowledge graph orchestrator
│   ├── graph.py             # Graph data structure
│   ├── scoring.py           # Entity scoring
│   ├── relationships.py     # Relationship discovery
│   └── retrieval.py         # Hybrid search
├── resume/
│   ├── blueprint.py         # Strategic planning
│   ├── canonical.py         # Resume JSON model
│   ├── pipeline.py          # Full pipeline orchestration
│   └── validator.py         # Quality checks
├── templates/
│   └── engine.py            # Template management + Typst
├── profile.py               # Profile CRUD service
├── document_processor.py    # PDF/OCR processing
├── embeddings.py            # Sentence-transformer vectors
└── settings.py              # User settings service
```

## Dependency Injection

FastAPI `Depends()` for all dependencies:
- `get_db()` — Yields async SQLAlchemy session
- `get_profile_service()` — Yields ProfileService with session
- `KnowledgeEngine(session, user_id)` — Created per request

## Error Handling

All endpoints return structured errors via HTTPException.
Custom exceptions in `utils/errors.py` provide error codes and messages.
