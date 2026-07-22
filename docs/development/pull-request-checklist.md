# Pull Request Checklist

## Before Opening a PR

- [ ] Branch is created from latest `develop`
- [ ] Branch follows [naming convention](branch-naming.md)
- [ ] Code compiles/builds without errors
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Linting passes (`npm run lint` / `ruff check backend/`)
- [ ] Formatting is correct (`npm run format:check` / `ruff format --check backend/`)
- [ ] Type checking passes (`npm run type-check` / `mypy backend/`)
- [ ] No console.log or print debugging left in code
- [ ] No commented-out code (unless intentional with TODO)

## PR Description

```markdown
## What

Brief description of the change.

## Why

Context on why this change is needed.

## How

Key implementation details (if non-obvious).

## Testing

How this was tested.

Closes #<issue-number>
```

## Code Quality

- [ ] Code follows project [engineering standards](../engineering-standards.md)
- [ ] No duplicate logic — functions/classes are reused appropriately
- [ ] Error handling is comprehensive
- [ ] Input validation is in place
- [ ] No hardcoded values — use configuration or constants
- [ ] Logging is appropriate for the change
- [ ] No security issues (SQL injection, XSS, secrets in code)

## Documentation

- [ ] API changes documented (if applicable)
- [ ] README updated (if applicable)
- [ ] Code comments explain complex logic
- [ ] Docstrings for new public functions/classes

## Final Check

- [ ] PR is small and focused (ideally < 400 lines changed)
- [ ] PR has a clear, descriptive title
- [ ] Self-reviewed the diff before requesting review
- [ ] Ready for review (not a draft unless explicitly work-in-progress)
