# CareerForge AI — Claude Instructions

## Project Overview

AI-powered desktop career intelligence platform. Tauri v2 desktop app with React/TypeScript frontend, Python FastAPI backend, SQLite + LanceDB vector store.

## Development Phase

Implementation Phase: ACTIVE

- Architecture: LOCKED
- Product Specification: LOCKED
- Roadmap: LOCKED

## What Claude Should Do

- Implement features, refactor code, write tests, fix bugs, improve performance
- Follow conventional commits (see docs/development/commit-convention.md)
- Create feature branches from develop, never commit to main
- Use the engineering standards in docs/development/engineering-standards.md

## What Claude Should NOT Do

- Create new architecture documents or rewrite the roadmap
- Produce planning documents or TODO lists
- Commit directly to main or develop branches

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite 6, Tailwind CSS, Zustand, React Router 7
- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Pydantic 2
- **Desktop**: Tauri 2, Rust
- **AI**: OpenAI, Anthropic, OpenRouter, Ollama (provider registry pattern)
- **Vector Store**: LanceDB with sentence-transformers embeddings
- **Testing**: Vitest (frontend), pytest (backend)
- **Linting**: ESLint + Prettier (frontend), Ruff + mypy (backend)

## Project Structure

- `src/` — React/TypeScript frontend
- `backend/app/` — Python FastAPI backend
- `src-tauri/` — Rust/Tauri desktop shell
- `tests/` — Python test suite
- `docs/development/` — Development documentation

## Key Conventions

- **Commits**: Conventional Commits format — `feat(scope): description`
- **Branches**: GitFlow — feature branches from develop, PRs for all changes
- **Quality**: Pre-commit hooks enforce linting, formatting, type checking
- **Testing**: Write tests for new features, maintain coverage
- **Backend patterns**: Generic Repository, Provider Registry, Pydantic schemas
- **Frontend patterns**: Feature-based component organization, Zustand stores
- **Error handling**: Custom exception hierarchy in backend, Toast notifications in frontend
- **Logging**: structlog in backend, console in frontend

## Commands

```bash
# Frontend
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # ESLint check
npm run format       # Prettier format
npm run type-check   # TypeScript check
npm run test         # Run tests

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest               # Run tests
ruff check .         # Lint
ruff format .        # Format
mypy app/            # Type check
```

## Branch Strategy

- `main` — production releases only
- `develop` — primary integration branch
- `feature/*` — new features (from develop)
- `bugfix/*` — bug fixes (from develop)
- `hotfix/*` — critical fixes (from main)
- `release/*` — release preparation (from develop)
