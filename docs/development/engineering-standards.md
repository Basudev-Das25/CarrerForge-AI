# Engineering Standards

## Folder Organization

### Backend

- `routers/` — HTTP endpoint definitions, thin controllers only
- `services/` — Business logic, orchestrated operations
- `db/` — Database models, repositories, migrations
- `providers/` — External service integrations (AI providers)
- `models/` — Pydantic schemas for request/response
- `utils/` — Shared utilities (logging, errors)
- `config/` — Settings and configuration

### Frontend

- `components/<feature>/` — Feature-organized components
- `components/common/` — Shared UI primitives (Button, Input, Modal)
- `components/layout/` — App shell (Sidebar, TopBar, AppLayout)
- `screens/` — Route-level page components
- `hooks/` — Custom React hooks and Zustand stores
- `services/` — API client functions
- `types/` — TypeScript type definitions
- `utils/` — Pure utility functions

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Python files | snake_case | `document_processor.py` |
| Python classes | PascalCase | `ProfileService` |
| Python functions | snake_case | `get_user_profile()` |
| Python constants | UPPER_SNAKE | `MAX_FILE_SIZE` |
| TypeScript files | PascalCase (components) or camelCase (utils) | `Button.tsx`, `api.ts` |
| TypeScript interfaces | PascalCase | `UserProfile` |
| TypeScript functions | camelCase | `useProfileStore()` |
| CSS classes | Tailwind utility classes | `bg-surface-primary` |
| API routes | kebab-case | `/api/v1/user-profile` |
| Database tables | snake_case | `user_profiles` |
| Database columns | snake_case | `created_at` |
| Git branches | type/kebab-case | `feature/profile-crud` |

## Error Handling

### Backend

```python
from app.utils.errors import CareerForgeError, NotFoundError

# Custom exception hierarchy
class CareerForgeError(Exception):
    """Base exception for all CareerForge errors."""
    pass

class NotFoundError(CareerForgeError):
    """Resource not found."""
    pass

class ValidationError(CareerForgeError):
    """Input validation failed."""
    pass

# Usage in routers
@router.get("/profile/{profile_id}")
async def get_profile(profile_id: int):
    profile = await service.get(profile_id)
    if not profile:
        raise NotFoundError(f"Profile {profile_id} not found")
    return profile
```

### Frontend

```typescript
// API errors → Toast notifications
import { useToast } from "@/hooks/useToast";

const { showError } = useToast();

try {
  await api.createProfile(data);
} catch (error) {
  showError("Failed to save profile. Please try again.");
}
```

## Logging

### Backend (structlog)

```python
import structlog

logger = structlog.get_logger()

logger.info("profile_created", user_id=user.id, profile_id=profile.id)
logger.error("profile_update_failed", error=str(e), profile_id=profile_id)
```

### Frontend

```typescript
// Development only, no console.log in production code
console.warn("Deprecated API call:", endpoint);
```

## Testing Expectations

### Backend

- Unit tests for services and utilities
- Integration tests for API endpoints
- Use pytest fixtures, async test support
- Test file naming: `test_<module>.py`
- Test function naming: `test_<behavior>`

### Frontend

- Unit tests for utility functions
- Component tests with Vitest + jsdom
- Test file naming: `<module>.test.ts` or `<module>.test.tsx`
- Co-locate tests with source files

### Coverage Targets

- Backend: 80% minimum
- Frontend: 70% minimum
- Critical paths: 95% minimum

## Documentation Expectations

- Docstrings for all public classes and functions (Google style)
- Type hints for all function signatures
- Inline comments for complex logic only
- README for each major module
- API documentation auto-generated from FastAPI

## Branch Lifecycle

1. Create from `develop` — `git checkout -b feature/my-feature develop`
2. Commit often with conventional messages
3. Push and create PR when ready for review
4. Address review feedback
5. Squash merge into `develop`
6. Delete the branch

**Target**: Feature branches live < 3 days. PRs reviewed within 24 hours.
