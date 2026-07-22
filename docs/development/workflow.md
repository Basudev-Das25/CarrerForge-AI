# Development Workflow

## Git Workflow

CareerForge AI uses a GitFlow-inspired branching model.

### Branches

| Branch | Purpose | Protected |
|---|---|---|
| `main` | Production releases | Yes |
| `develop` | Integration branch | Yes |
| `feature/*` | New features | No |
| `bugfix/*` | Bug fixes | No |
| `hotfix/*` | Critical fixes | No |
| `release/*` | Release preparation | No |

### Daily Workflow

```bash
# 1. Sync with develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Work with conventional commits
git commit -m "feat(scope): description"

# 4. Push and create PR
git push -u origin feature/my-feature

# 5. After approval, merge into develop
git checkout develop
git merge --no-ff feature/my-feature

# 6. Delete feature branch
git branch -d feature/my-feature
```

## Commit Convention

```
<type>(<scope>): <description>
```

| Type | Use Case |
|---|---|
| `feat` | New feature (minor bump) |
| `fix` | Bug fix (patch bump) |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `test` | Adding tests |
| `ci` | CI/CD changes |
| `chore` | Maintenance, dependencies |

## Coding Standards

### Python
- **Formatter/Linter**: Ruff (replaces Black, isort, flake8)
- **Type Checker**: mypy strict mode
- **Line Length**: 100 characters
- **Imports**: Sorted by ruff isort
- **Naming**: snake_case for functions/variables, PascalCase for classes

### TypeScript/React
- **Formatter**: Prettier (double quotes, trailing commas, 100 char width)
- **Linter**: ESLint with TypeScript and React plugins
- **Type Safety**: Strict TypeScript, no `any` except where necessary
- **Naming**: PascalCase for components, camelCase for functions/variables

## Testing Strategy

```bash
# Run all tests
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest

# Run specific category
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest tests/unit/ -v
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest tests/integration/ -v
```

- Unit tests for all services, utilities, and business logic
- Integration tests for all API endpoints
- Tests use in-memory SQLite (no manual setup)
- Every new feature requires tests
- Every bug fix requires a regression test
