# Code Review Checklist

## For Reviewers

### Correctness

- [ ] Does the code do what the PR description says?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?
- [ ] Are null/undefined checks in place where needed?
- [ ] Are database transactions handled correctly?

### Security

- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Input is validated and sanitized
- [ ] SQL queries use parameterized statements (no string concatenation)
- [ ] Authentication/authorization checks are in place
- [ ] No sensitive data in logs

### Performance

- [ ] No N+1 query patterns
- [ ] Database queries use appropriate indexes
- [ ] Large datasets are paginated
- [ ] No unnecessary re-renders (React) or redundant API calls
- [ ] Caching is used where appropriate

### Code Quality

- [ ] Code is readable and self-documenting
- [ ] Functions are single-purpose and appropriately sized
- [ ] No dead code or unused imports
- [ ] Naming is clear and consistent with project conventions
- [ ] DRY — no unnecessary duplication

### Testing

- [ ] Tests cover the main happy path
- [ ] Tests cover important edge cases
- [ ] Tests are readable and maintainable
- [ ] Test names describe the behavior being tested
- [ ] Mocks are appropriate (not over-mocked)

### Architecture

- [ ] Changes fit the existing architecture
- [ ] No circular dependencies introduced
- [ ] Separation of concerns is maintained
- [ ] New abstractions are justified

### Frontend-Specific

- [ ] Components are appropriately decomposed
- [ ] State management follows project patterns (Zustand)
- [ ] Forms have proper validation and error states
- [ ] Loading states are handled
- [ ] Responsive design is considered
- [ ] Accessibility basics are met (semantic HTML, aria labels)

### Backend-Specific

- [ ] API responses follow consistent format
- [ ] Pydantic schemas validate input correctly
- [ ] Async operations are handled properly
- [ ] Database migrations are reversible
- [ ] Structured logging is used (structlog)

## Review Etiquette

- Be constructive, not critical
- Suggest alternatives, don't just point out problems
- Use "nit:" prefix for non-blocking style suggestions
- Approve with minor suggestions when appropriate
- Request changes only for blocking issues
