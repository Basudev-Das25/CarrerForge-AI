# Contributing to CareerForge AI

Thank you for your interest in contributing! This document explains how to get started.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Run tests: `pytest` (backend), `npm test` (frontend)
6. Commit with conventional commits
7. Push and create a Pull Request

## Development Setup

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
npm install
npm run dev
```

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(profile): add language CRUD
fix(ats): correct keyword scoring
docs(readme): update installation guide
refactor(api): simplify provider registry
test(backup): add restore tests
chore(deps): update dependencies
```

## Branch Strategy

- `main` — production releases only
- `develop` — integration branch
- `feature/*` — new features
- `bugfix/*` — bug fixes
- `hotfix/*` — critical fixes
- `release/*` — release preparation

## Code Standards

- **Python**: Ruff linting, type hints, docstrings
- **TypeScript**: ESLint, Prettier, strict mode
- **Commits**: Conventional Commits format
- **PRs**: Link to issue, describe changes, include tests

## Testing

```bash
# Backend (from repo root)
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest

# Frontend
npm test
```

## Code Review

All PRs require at least one review. Focus areas:
- Code quality and readability
- Test coverage
- Security implications
- Performance impact
- Documentation updates

## Issues

- Use GitHub Issues for bugs and feature requests
- Check existing issues before creating new ones
- Include reproduction steps for bugs
- Describe your use case for feature requests

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
