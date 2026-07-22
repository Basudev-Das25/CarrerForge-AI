# Branch Naming Convention

## Format

```
<type>/<short-description>
```

## Types

| Type | Purpose | Example |
|---|---|---|
| `feature/` | New functionality | `feature/profile-crud` |
| `bugfix/` | Non-critical fixes | `bugfix/fix-date-parsing` |
| `hotfix/` | Critical production fixes | `hotfix/fix-auth-crash` |
| `release/` | Release preparation | `release/0.2.0` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |
| `docs/` | Documentation only | `docs/api-reference` |
| `refactor/` | Code restructuring | `refactor/provider-registry` |
| `test/` | Test additions/fixes | `test/add-profile-tests` |
| `ci/` | CI/CD changes | `ci/add-lint-workflow` |

## Rules

1. **Lowercase only** — `feature/ProfileCRUD` is invalid
2. **Hyphens as separators** — `feature/user_profile` is invalid, use `feature/user-profile`
3. **Short and descriptive** — `feature/add-the-ability-to-create-user-profiles` is too long
4. **No issue numbers in branch name** — reference issues in PR descriptions instead
5. **Maximum 50 characters** after the type prefix

## Examples

```
feature/profile-crud
feature/resume-generator
feature/ats-scoring
bugfix/fix-migration-error
bugfix/null-pointer-dashboard
hotfix/fix-data-loss
release/0.3.0
chore/update-python-deps
docs/development-guide
refactor/simplify-provider-registry
test/integration-profile-api
ci/add-security-scan
```

## Issue Linking

Reference issues in your PR description, not branch names:

```markdown
Closes #42
Fixes #17
Resolves #88
```
