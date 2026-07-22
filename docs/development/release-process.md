# Release Process

## Overview

CareerForge AI follows [Semantic Versioning](versioning-strategy.md).

## Release Steps

### 1. Create Release Branch

```bash
git checkout develop
git pull origin develop
git checkout -b release/X.Y.Z
```

### 2. Prepare Release

```bash
# Update version numbers
# - package.json: "version": "X.Y.Z"
# - src-tauri/Cargo.toml: version = "X.Y.Z"
# - src-tauri/tauri.conf.json: version

# Update CHANGELOG.md
# Run all tests one final time
npm run test
cd backend && pytest

# Commit preparation
git add .
git commit -m "chore(release): prepare release X.Y.Z"
```

### 3. Finalize Release

```bash
# Merge into main
git checkout main
git merge --no-ff release/X.Y.Z
git tag -a vX.Y.Z -m "Release X.Y.Z"

# Back-merge into develop
git checkout develop
git merge --no-ff release/X.Y.Z

# Push everything
git push origin main --tags
git push origin develop

# Clean up
git branch -d release/X.Y.Z
git push origin --delete release/X.Y.Z
```

### 4. Create GitHub Release

1. Go to GitHub Releases
2. Create new release from the tag
3. Add release notes from CHANGELOG.md
4. Attach build artifacts if applicable

## Hotfix Process

```bash
# Branch from main
git checkout main
git checkout -b hotfix/fix-description

# Fix and commit
git commit -m "fix(scope): description"

# Merge into main AND develop
git checkout main
git merge --no-ff hotfix/fix-description
git tag -a vX.Y.Z+1 -m "Hotfix X.Y.Z+1"

git checkout develop
git merge --no-ff hotfix/fix-description

# Push and clean up
git push origin main --tags
git push origin develop
git branch -d hotfix/fix-description
```

## Pre-Release Checklist

- [ ] All CI checks pass on `develop`
- [ ] All tests pass locally
- [ ] Version numbers updated everywhere
- [ ] CHANGELOG.md updated
- [ ] No known critical bugs
- [ ] Documentation is current
