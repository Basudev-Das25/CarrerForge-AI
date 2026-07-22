# CareerForge AI — Project Status

## Current State

| Metric | Status |
|---|---|
| **Current branch** | `feature/resume-generation-pipeline` |
| **Latest commit** | 3b8b66a (plus stabilization changes) |
| **Backend build** | ✅ Python imports OK |
| **Frontend build** | ✅ Vite build passes (325KB JS, 29KB CSS) |
| **TypeScript** | ✅ Clean (no errors) |
| **Ruff lint** | ✅ Clean (0 errors) |
| **pytest** | **123/123 passed** (0 warnings) |
| **Working tree** | Clean |

## Test Count by Category

| Category | Tests | Status |
|---|---|---|
| integration/test_api | 6 | ✅ All pass |
| integration/test_ai_api | 12 | ✅ All pass |
| integration/test_knowledge_api | 20 | ✅ All pass |
| integration/test_profile_api | 17 | ✅ All pass |
| unit/test_ai_orchestrator | 24 | ✅ All pass |
| unit/test_errors | 10 | ✅ All pass |
| unit/test_knowledge_graph | 20 | ✅ All pass |
| unit/test_profile_service | 12 | ✅ All pass |
| unit/test_providers | 5 | ✅ All pass |
| **Total** | **123** | **✅ 123/123** |

## Technical Debt

- **Test infrastructure**: In-memory SQLite now used for tests via `TEST_DATABASE_URL` env var
- **Integration tests**: 41 integration tests were stabilized (SQLAlchemy async session lifecycle, test database path)
- **Lint fixes**: 105+ ruff auto-fixes applied across 42 files
- **Legacy providers**: Old `app/providers/` module exists alongside new `app/services/ai/` module; both work independently
- **Deprecation warnings**: All `datetime.utcnow()` replaced with timezone-aware alternatives

## Test Infrastructure

Tests use an in-memory SQLite database, set via:
```bash
TEST_DATABASE_URL="sqlite+aiosqlite://" pytest
```

The conftest.py fixture:
1. Sets `TEST_DATABASE_URL` at module import time (before app imports)
2. Creates all tables once per session
3. Cleans data between tests via `cleanup_db` autouse fixture
4. Drops all tables after session
5. No file system or configuration needed

## Branch Strategy

- `main` — Stable, reviewed code
- `develop` — Integration branch
- `feature/resume-generation-pipeline` — Current active feature
