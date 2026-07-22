# Commit Convention

CareerForge AI follows [Conventional Commits](https://www.conventionalcommits.org/).

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | When to Use | Version Impact |
|---|---|---|
| `feat` | New feature | Minor bump |
| `fix` | Bug fix | Patch bump |
| `docs` | Documentation only | None |
| `style` | Formatting, no code change | None |
| `refactor` | Code restructuring, no feature/fix | None |
| `perf` | Performance improvement | Patch bump |
| `test` | Adding or updating tests | None |
| `ci` | CI/CD configuration | None |
| `chore` | Maintenance, dependencies | None |
| `revert` | Reverts a previous commit | Depends |

## Scopes

| Scope | Area |
|---|---|
| `profile` | User profile management |
| `resume` | Resume generation |
| `ats` | ATS scoring and analysis |
| `documents` | Document vault |
| `ai` | AI provider integration |
| `database` | Database and migrations |
| `api` | Backend API routes |
| `ui` | Frontend components |
| `layout` | App layout/navigation |
| `config` | Configuration |
| `deps` | Dependencies |
| `actions` | GitHub Actions / CI |
| `release` | Release process |

## Examples

```bash
# Features
git commit -m "feat(profile): add user profile CRUD endpoints"
git commit -m "feat(resume): implement ATS-optimized resume generation"
git commit -m "feat(ui): add dark mode toggle to settings"

# Bug Fixes
git commit -m "fix(database): resolve migration ordering issue"
git commit -m "fix(api): handle empty profile gracefully"

# Breaking Changes
git commit -m "feat(api)!: redesign resume endpoint response format

BREAKING CHANGE: The resume API response structure has changed.
The 'content' field is now nested under 'data.attributes'."

# With Body
git commit -m "feat(ats): add keyword density analysis

Implements TF-IDF based keyword density scoring against
the target job description. Includes visualization of
keyword coverage in the ATS report dashboard.

Closes #42"
```

## Rules

1. **Subject line**: imperative mood, lowercase, no period, max 72 characters
2. **Body**: wrap at 80 characters, explain _what_ and _why_ (not _how_)
3. **Footer**: reference issues with `Closes #`, `Fixes #`, `Resolves #`
4. **Breaking changes**: add `!` after type/scope and `BREAKING CHANGE:` footer
5. **One logical change per commit** — don't mix unrelated changes
