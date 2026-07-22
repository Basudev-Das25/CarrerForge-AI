# CareerForge AI

**AI-powered desktop career intelligence platform for resume generation, ATS optimization, document management, and career development.**

CareerForge AI is a local-first desktop application that transforms how professionals build, optimize, and manage their career documents. It uses a sophisticated AI pipeline — orchestrated through the AI Orchestrator, Knowledge Engine, and Agent Framework — to generate production-quality, ATS-optimized resumes from a structured candidate profile.

## Features

- **Candidate Profile Management** — Complete CRUD for all professional data: Personal info, Education, Experience, Projects, Skills, Certificates, Achievements, Languages, Publications, Awards, Social Links
- **Knowledge Engine** — Semantic knowledge graph that automatically discovers relationships between profile entities, scores relevance across 13 dimensions, and powers intelligent retrieval
- **AI Orchestration** — Centralized AI gateway supporting 6 providers (OpenAI, Anthropic, OpenRouter, Ollama, Grok, HuggingFace) with automatic failover, caching, retries, and cost tracking
- **Resume Generation** — Evidence-backed resume generation pipeline: JD → Job Profile → Knowledge Graph → Evidence Bundle → Blueprint → Canonical Resume → Template → PDF
- **Professional Templates** — 4 production-quality Typst templates (Modern, Minimal, Software Engineer, Academic CV) with theme system and ATS-friendly layout
- **ATS Intelligence** — Comprehensive analysis across 7 dimensions with keyword matching, recruiter metrics, evidence verification, iterative optimization, resume comparison
- **Prompt Registry** — Version-controlled YAML prompts with variable injection, provider overrides, and validation
- **Agent Framework** — 12 AI agents with reusable execute/validate/retry/health pattern

## Repository Structure

```
AI-resume/
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── config/           # Settings (Pydantic + env vars)
│   │   ├── db/               # SQLAlchemy models, repository, migrations
│   │   ├── models/           # Pydantic request/response schemas
│   │   ├── providers/        # Legacy provider abstraction
│   │   ├── routers/          # API route definitions (12 routers)
│   │   ├── services/         # Business logic layer
│   │   │   ├── agents/       # 12 AI agents
│   │   │   ├── ai/           # Orchestrator, providers, prompts, observability
│   │   │   ├── ats/          # ATS analysis engine
│   │   │   ├── evidence/     # Evidence engine for resume generation
│   │   │   ├── job/          # Job intelligence and repository
│   │   │   ├── knowledge/    # Knowledge graph engine
│   │   │   ├── resume/       # Resume pipeline, blueprint, validator
│   │   │   ├── templates/    # Template engine (Typst, text, markdown)
│   │   │   ├── document_processor.py
│   │   │   ├── embeddings.py
│   │   │   ├── profile.py
│   │   │   └── settings.py
│   │   └── utils/            # Error handling, logging
│   ├── migrations/           # Alembic migration files
│   └── requirements.txt
├── src/                      # React/TypeScript frontend
│   ├── components/
│   │   ├── common/           # Button, Input, Modal, Toast, EmptyState
│   │   └── layout/           # AppLayout, Sidebar, TopBar
│   ├── screens/              # Route-level page components
│   └── services/             # API client, state stores
├── src-tauri/                # Tauri v2 desktop shell (Rust)
├── templates/                # 4 production Typst templates
├── tests/                    # Python test suite (186 tests)
│   ├── unit/
│   └── integration/
├── docs/                     # Comprehensive documentation
├── db/                       # Alembic configuration
│   └── migrations/
├── config/                   # Application configuration
└── prompts/                  # Version-controlled AI prompts
    ├── ats/
    ├── jd/
    ├── optimizer/
    ├── reflection/
    └── resume/
```

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript, Vite 6, Tailwind CSS 3, Zustand 5, React Router 7 |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic 2 |
| **Desktop** | Tauri v2, Rust |
| **AI** | OpenAI, Anthropic, OpenRouter, Ollama, Grok, HuggingFace |
| **Vector Store** | LanceDB with sentence-transformers embeddings |
| **PDF** | Typst (compilation), PyMuPDF (processing) |
| **Testing** | pytest (backend), Vitest (frontend) |
| **Linting** | Ruff (Python), ESLint + Prettier (TypeScript) |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Rust (for Tauri desktop build)
- Typst (for PDF compilation)

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
npm install
npm run dev
```

### Running Tests

```bash
# Backend (uses in-memory SQLite automatically)
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest

# Frontend
npm run test
```

### Building Desktop App

```bash
npm run tauri build
```

## Configuration

Configuration is managed through environment variables (see `.env.example`) and `config/default.json`:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///data/careerforge.db` | SQLite database path |
| `AI_PROVIDER` | `openai` | Default AI provider |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Documentation

See [docs/](docs/) for comprehensive documentation:

- [Architecture](docs/architecture/)
- [API Reference](docs/api/)
- [Database Schema](docs/database/)
- [AI System](docs/ai/)
- [Frontend](docs/frontend/)
- [Backend](docs/backend/)
- [Testing](docs/testing/)
- [Deployment](docs/deployment/)
- [Security](docs/security/)
- [User Guide](docs/user-guide/)
- [Development](docs/development/)

## License

CareerForge AI — All rights reserved.
