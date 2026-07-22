# CareerForge AI

<div align="center">

**AI-powered desktop career intelligence platform for resume generation, ATS optimization, and career development.**

[![Version](https://img.shields.io/badge/version-0.5.0--alpha-blue)](https://github.com/Basudev-Das/CareerForge-AI/releases)
[![License](https://img.shields.io/badge/license-proprietary-red)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)]()
[![Build](https://img.shields.io/badge/build-passing-brightgreen)](#)

</div>

---

## What is CareerForge AI?

CareerForge AI is a **local-first desktop application** that helps professionals build, optimize, and manage their career documents using AI. Unlike cloud-based resume builders, CareerForge AI keeps all your data on your device — no cloud storage, no tracking, no hidden telemetry.

**Key differentiator:** Every generated sentence is traceable back to your actual profile data. No hallucination, no fabricated experience, no invented metrics.

### How it works

```
Your Profile (Education, Experience, Skills, Projects)
        ↓
Knowledge Engine (relationship discovery, scoring)
        ↓
AI Pipeline (job parsing, evidence retrieval, writing)
        ↓
ATS-Optimized Resume (production PDF via Typst)
```

---

## Features

### Profile Management
Complete management of 12 professional data types:
- Personal Information, Education, Experience
- Projects, Skills, Certificates, Achievements
- Languages, Publications, Awards, Social Links

### AI-Powered Resume Generation
- Paste a job description → AI creates a strategic blueprint
- Evidence bundle extracted from your knowledge graph
- Every bullet point linked to profile evidence
- Iterative validation and quality scoring
- Export to PDF, Typst source, text, or Markdown

### ATS Intelligence
- 7-dimension scoring (keywords, readability, impact, specificity, etc.)
- Keyword gap analysis against job descriptions
- Recruiter-focused metrics
- Iterative optimization with score tracking
- Resume version comparison

### Professional Templates
4 production-quality Typst templates with theme system:
- **Modern** — Clean professional with Inter font
- **Minimal** — Minimalist with Georgia serif
- **Software Engineer** — Technical with JetBrains Mono
- **Academic CV** — Formal with Times New Roman

### Desktop Application
- Native Windows desktop via Tauri v2
- Onboarding wizard for first-time setup
- Automatic update checking
- Backup and restore system
- Error recovery and diagnostics

---

## Installation

### Option 1: Download the Installer (Recommended)

1. Go to [Releases](https://github.com/Basudev-Das/CareerForge-AI/releases)
2. Download `CareerForgeAI_Setup_v0.5.0-alpha.exe`
3. Run the installer
4. Launch CareerForge AI from the Start Menu or Desktop shortcut

### Option 2: Portable Version

1. Download `CareerForgeAI_Portable_v0.5.0-alpha.zip`
2. Extract to any folder
3. Run `CareerForge AI.exe`

### System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| **Operating System** | Windows 10 (64-bit) | Windows 11 |
| **RAM** | 4 GB | 8 GB |
| **Disk Space** | 500 MB | 1 GB |
| **Display** | 1280×720 | 1920×1080 |
| **Internet** | Required for AI features | Broadband |

### First Launch

1. The **Onboarding Wizard** guides you through setup
2. Choose an **AI Provider** (OpenAI, Claude, Ollama, etc.)
3. Enter your API key (or use Ollama for free local AI)
4. Select a **default resume template**
5. Start building your profile!

---

## Quick Start (Development)

### Prerequisites

- Python 3.11+
- Node.js 20+
- Rust (for desktop builds)
- Typst (for PDF generation)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
npm install
npm run dev
```

The app opens at `http://localhost:1420`.

### Desktop Build

```bash
npm run tauri build
```

Produces installers in `src-tauri/target/release/bundle/`.

### Running Tests

```bash
# Backend (in-memory SQLite — no setup needed)
cd backend
PYTHONPATH=. pytest ../tests/ -q

# Frontend
npm run test

# Full quality check
npm run lint && npm run type-check && npm run build
```

---

## AI Providers

CareerForge AI supports 6 AI providers with automatic failover:

| Provider | Models | API Key Required | Notes |
|---|---|---|---|
| **OpenAI** | GPT-4o, GPT-4o-mini | Yes | Best quality |
| **Claude** | Sonnet, Opus | Yes | Excellent for writing |
| **OpenRouter** | Multi-model gateway | Yes | Access to many models |
| **Ollama** | Llama 3, Mistral, etc. | No | Free, runs locally |
| **Grok** | Grok-2 | Yes | xAI models |
| **HuggingFace** | Free tier models | Yes | Limited free access |

**Recommended for testing:** Ollama (no API key needed, runs locally).

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///data/careerforge.db` | SQLite database |
| `AI_PROVIDER` | `openai` | Default AI provider |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Application Settings

Default settings are in `config/default.json`. User settings are stored at:
- **Windows:** `%USERPROFILE%\.careerforge\settings.json`

---

## Repository Structure

```
careerforge-ai/
├── backend/                    Python FastAPI backend
│   ├── app/
│   │   ├── services/
│   │   │   ├── ai/             AI orchestrator, providers, prompts
│   │   │   ├── ats/            ATS analysis engine
│   │   │   ├── backup/         Backup and restore
│   │   │   ├── diagnostics/    System diagnostics
│   │   │   ├── evidence/       Resume evidence engine
│   │   │   ├── job/            Job intelligence
│   │   │   ├── knowledge/      Knowledge graph engine
│   │   │   ├── resume/         Resume pipeline
│   │   │   ├── templates/      Template rendering
│   │   │   └── update/         Desktop update service
│   │   ├── routers/            API endpoints (14 routers)
│   │   ├── db/                 Database models and repository
│   │   └── models/             Pydantic schemas
│   └── requirements.txt
├── src/                        React/TypeScript frontend
│   ├── screens/                18 page components
│   ├── components/             Reusable UI components
│   └── services/               API client
├── src-tauri/                  Tauri v2 desktop shell
├── templates/                  4 Typst resume templates
├── tests/                      224 tests (142 unit + 82 integration)
├── docs/                       29 documentation files
├── prompts/                    Version-controlled AI prompts
├── .github/workflows/          CI/CD and release automation
└── scripts/                    Build and release scripts
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19 · TypeScript · Vite 6 · Tailwind CSS 3 · Zustand 5 |
| **Backend** | Python 3.11 · FastAPI · SQLAlchemy 2.0 · Pydantic 2 |
| **Desktop** | Tauri v2 · Rust |
| **AI** | OpenAI · Anthropic · OpenRouter · Ollama · Grok · HuggingFace |
| **Vector Store** | LanceDB · sentence-transformers |
| **Templates** | Typst (PDF) · PyMuPDF (processing) |
| **Database** | SQLite (async) · LanceDB (vectors) |
| **Testing** | pytest · Vitest |
| **Linting** | Ruff · ESLint · Prettier |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Tauri v2 Desktop Shell                │
├─────────────────────────────────────────────────────────┤
│  React 19 Frontend  ◄──── REST API ────►  FastAPI Backend │
├─────────────────────────────────────────────────────────┤
│                  Service Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Profile  │ │Knowledge │ │  Resume  │ │   ATS    │   │
│  │  Engine  │ │  Engine  │ │ Pipeline │ │Intelligence│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       └────────────┼───────────┼────────────┘           │
│                ┌───┴────┐ ┌───┴────┐                    │
│                │SQLite  │ │LanceDB │                    │
│                └────────┘ └────────┘                    │
├─────────────────────────────────────────────────────────┤
│              AI Orchestrator                             │
│  OpenAI │ Anthropic │ OpenRouter │ Ollama │ Grok │ HF   │
└─────────────────────────────────────────────────────────┘
```

---

## Documentation

Comprehensive documentation is available in [docs/](docs/):

| Document | Description |
|---|---|
| [Architecture Overview](docs/architecture/overview.md) | System design and component interaction |
| [Resume Pipeline](docs/architecture/resume-pipeline.md) | Full generation flow |
| [ATS Pipeline](docs/architecture/ats-pipeline.md) | Analysis and optimization flow |
| [API Reference](docs/api/endpoints.md) | All 80+ endpoints |
| [Database Schema](docs/database/schema.md) | ER diagram and table descriptions |
| [AI System](docs/ai/orchestrator.md) | Providers, agents, prompts |
| [Knowledge Engine](docs/ai/knowledge-engine.md) | Graph, scoring, retrieval |
| [Frontend](docs/architecture/frontend.md) | Component hierarchy and routing |
| [Backend](docs/backend/structure.md) | Service layer organization |
| [Deployment](docs/deployment/setup.md) | Installation and configuration |
| [Security](docs/security/overview.md) | Threat model and protections |
| [User Guide](docs/user-guide/getting-started.md) | Getting started walkthrough |
| [Development](docs/development/workflow.md) | Contributing standards |

---

## Privacy

CareerForge AI is designed with privacy-first principles:

- **Local-first** — All data stored on your device
- **No cloud storage** — Your profile never leaves your computer
- **No telemetry** — No tracking, no analytics, no hidden data collection
- **API keys local only** — Sent only to your chosen AI provider during generation
- **Optional diagnostics** — Only exported when you explicitly choose to share

See [SECURITY.md](SECURITY.md) for details.

---

## Known Issues (v0.5.0-alpha)

- PDF rendering requires Typst (bundled in installer, manual install for portable)
- Document Vault is a placeholder (coming in v0.6.0)
- Settings page is a placeholder (coming in v0.6.0)
- Windows only — macOS and Linux support planned for v0.7.0

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for the full list.

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code standards (Conventional Commits)
- Branch strategy (GitFlow)
- Testing requirements
- PR review process

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## License

CareerForge AI — All rights reserved.
