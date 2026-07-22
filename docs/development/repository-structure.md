# Repository Structure Guide

## Top-Level Layout

```
AI-resume/
├── backend/              # Python FastAPI backend
├── src/                  # React/TypeScript frontend
├── src-tauri/            # Rust/Tauri desktop shell
├── config/               # Application configuration
├── db/                   # Database migrations (Alembic)
├── docs/                 # Project documentation
├── plugins/              # Plugin system (future)
├── scripts/              # Utility scripts
├── tests/                # Python test suite
├── typst-templates/      # Resume templates (Typst)
├── .github/              # CI/CD workflows
├── package.json          # Node.js dependencies
└── CLAUDE.md             # AI assistant instructions
```

## Backend (`backend/`)

```
backend/
├── app/
│   ├── main.py           # FastAPI application entry point
│   ├── config/
│   │   └── settings.py   # Pydantic settings (env-based)
│   ├── db/
│   │   ├── base.py       # SQLAlchemy async engine/session
│   │   ├── models.py     # SQLAlchemy ORM models
│   │   ├── repository.py # Generic async CRUD repository
│   │   └── lance.py      # LanceDB vector store
│   ├── models/
│   │   └── schemas.py    # Pydantic request/response schemas
│   ├── providers/
│   │   ├── base.py       # AI provider abstract base class
│   │   ├── registry.py   # Provider registry pattern
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── openrouter_provider.py
│   │   └── ollama_provider.py
│   ├── routers/
│   │   ├── admin.py      # Health, config endpoints
│   │   ├── ai.py         # AI provider endpoints
│   │   ├── documents.py  # Document vault CRUD
│   │   ├── profile.py    # Profile management CRUD
│   │   ├── resumes.py    # Resume generation
│   │   └── ats.py        # ATS scoring
│   ├── services/
│   │   ├── profile.py    # Profile business logic
│   │   ├── embeddings.py # Embedding generation
│   │   ├── document_processor.py
│   │   └── settings.py   # Settings service
│   ├── utils/
│   │   ├── errors.py     # Custom exception hierarchy
│   │   └── logger.py     # Structlog configuration
│   └── plugins/
│       └── __init__.py   # Plugin system (future)
├── requirements.txt      # Python dependencies
└── pyproject.toml        # Ruff, mypy, pytest config
```

## Frontend (`src/`)

```
src/
├── main.tsx              # React entry point
├── App.tsx               # Router and layout setup
├── styles/
│   └── globals.css       # Tailwind + design system
├── types/
│   └── index.ts          # TypeScript type definitions
├── hooks/
│   └── useStore.ts       # Zustand state stores
├── services/
│   └── api.ts            # HTTP client (fetch-based)
├── utils/
│   └── cn.ts             # clsx + twMerge utility
├── components/
│   ├── layout/           # AppLayout, Sidebar, TopBar
│   ├── common/           # Button, Input, Modal, Toast
│   ├── profile/          # Profile forms
│   ├── resume/           # Resume generator UI
│   ├── ats/              # ATS scoring UI
│   ├── documents/        # Document vault UI
│   ├── dashboard/        # Dashboard widgets
│   ├── settings/         # Settings panels
│   └── help/             # Help section
└── screens/              # Route-level page components
```

## Desktop Shell (`src-tauri/`)

```
src-tauri/
├── Cargo.toml            # Rust dependencies
├── tauri.conf.json       # Tauri configuration
├── build.rs              # Build script
├── capabilities/
│   └── default.json      # Permissions
└── src/
    ├── main.rs           # Entry point
    ├── lib.rs            # Plugin setup
    ├── state.rs          # App state
    ├── errors.rs         # Error types
    └── commands/
        ├── mod.rs
        ├── greet.rs
        └── health.rs
```

## Key Conventions

- **Route files** in `routers/` map 1:1 to API endpoint groups
- **Services** contain business logic, never called directly from routers without going through service layer
- **Repository** is a generic async CRUD pattern — all DB access goes through it
- **Providers** implement `AIProvider` ABC — new AI services plug in via registry
- **Components** are organized by feature domain, not by type
- **Screens** are top-level route components, one per route
