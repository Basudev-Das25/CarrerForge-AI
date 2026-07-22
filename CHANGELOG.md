# Changelog

All notable changes to CareerForge AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.5.0-alpha] - 2026-07-22

### Added
- **Candidate Profile System**: Full CRUD for 12 entity types (Education, Experience, Projects, Skills, Certificates, Achievements, Languages, Publications, Awards, Social Links)
- **Knowledge Engine**: Automatic relationship discovery, 13-dimension scoring, semantic retrieval
- **AI Orchestration**: 6 providers (OpenAI, Anthropic, OpenRouter, Ollama, Grok, HuggingFace) with failover
- **12 AI Agents**: Job Parser, Skill Extraction, Keyword, Knowledge Retrieval, Evidence, Resume Planner, Resume Writer, Resume Reviewer, ATS Evaluator, Reflection, Cover Letter, Interview
- **Resume Generation Pipeline**: JD → Blueprint → Evidence → Writing → Validation → Typst → PDF
- **4 Production Templates**: Modern, Minimal, Software Engineer, Academic CV
- **Theme System**: Customizable colors, typography, spacing per template
- **ATS Intelligence**: 7-dimension scoring, keyword analysis, iterative optimization
- **Prompt Registry**: 10 version-controlled YAML prompts
- **Desktop Update System**: Tauri updater integration, settings, history
- **Onboarding Wizard**: 4-step first-run experience
- **Backup System**: ZIP-based backup/restore with automatic indexing
- **Diagnostics**: System info, health checks, log management, export
- **Error Boundary**: Application-wide crash recovery
- **About Page**: Version, license, credits
- **Release Documentation**: README, INSTALL, RELEASE_NOTES, CHANGELOG, SECURITY, CONTRIBUTING, KNOWN_ISSUES
- **CI/CD**: GitHub Actions for lint, test, build, security audit
- **Pre-commit Hooks**: Ruff, ESLint, Prettier, mypy
- **Alembic Migrations**: Initial schema migration

### Fixed
- Python 3.13 compatibility (numpy, structlog, datetime deprecations)
- SQLAlchemy async session lifecycle in tests
- Test database path resolution (absolute paths)
- Template engine path resolution
- TypeScript type errors across all screens
- ESLint and Ruff linting errors
- All 224 tests passing

## [0.1.0] - 2026-07-21

### Added
- Initial project scaffolding
- Tauri v2 desktop shell
- React 19 frontend with TypeScript
- FastAPI Python backend
- SQLAlchemy 2.0 async database layer with SQLite
- LanceDB vector store integration
- AI provider abstraction (OpenAI, Anthropic, OpenRouter, Ollama)
- Document processing with OCR support
- Profile management CRUD endpoints
- Frontend layout with sidebar navigation
- Dashboard, Profile, Experience screens
- Zustand state management with persistence
- Tailwind CSS design system with dark mode
- Custom component library (Button, Input, Modal, Toast, EmptyState)
