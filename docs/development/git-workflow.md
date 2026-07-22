# Git Workflow

CareerForge AI uses a **GitFlow-inspired** branching model.

## Branch Overview

```
main ──────────────────────────────────────────●───────●─── (releases)
                                                 \   /
develop ──●──●──●──●──●──●──●──●──●──●──●──●──●──●──●── (integration)
            \        /          \        /
feature/*    ●──●──●             ●──●──●               (features)
                  \              /
bugfix/*           ●──●──────────                     (bug fixes)

hotfix/*                             ●──●              (critical fixes)
release/*                                ●──●          (release prep)
```

## Branch Types

| Branch | Base | Merges Into | Purpose |
|---|---|---|---|
| `main` | — | — | Production-ready releases only |
| `develop` | `main` | `main` | Primary integration branch |
| `feature/*` | `develop` | `develop` | New features |
| `bugfix/*` | `develop` | `develop` | Non-critical bug fixes |
| `hotfix/*` | `main` | `main` + `develop` | Critical production fixes |
| `release/*` | `develop` | `main` + `develop` | Release preparation |

## Daily Workflow

### Starting Work

```bash
# Sync with remote
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/profile-crud

# Work, commit often with conventional commits
git add .
git commit -m "feat(profile): add user profile CRUD endpoints"

# Push and create PR
git push -u origin feature/profile-crud
```

### Completing Work

1. Ensure all CI checks pass
2. Get code review approval
3. Squash merge into `develop`
4. Delete the feature branch

### Release Process

```bash
# Create release branch
git checkout develop
git checkout -b release/0.2.0

# Bump versions, final fixes
git commit -m "chore(release): bump version to 0.2.0"

# Merge into main and develop
git checkout main
git merge --no-ff release/0.2.0
git tag -a v0.2.0 -m "Release 0.2.0"

git checkout develop
git merge --no-ff release/0.2.0

# Clean up
git branch -d release/0.2.0
git push origin main --tags
```

## Rules

- **`main`** is always deployable
- **`develop`** is the integration branch — all features merge here first
- Never commit directly to `main` or `develop`
- All changes go through Pull Requests
- Use conventional commit messages (see [commit-convention.md](commit-convention.md))
- Delete branches after merging
