# Conflict Resolution Guide

## Prevention

Most merge conflicts are preventable:

1. **Pull frequently** — `git pull origin develop` before starting work
2. **Keep branches short-lived** — merge within 2-3 days
3. **Small PRs** — fewer files touched = fewer conflicts
4. **Communicate** — coordinate when working on the same files
5. **Use feature flags** — merge incomplete features behind flags

## Resolution Steps

### 1. Identify the Conflict

```bash
git merge feature/branch
# CONFLICT (content): Merge conflict in src/components/Dashboard.tsx
```

### 2. Find All Conflicted Files

```bash
git diff --name-only --diff-filter=U
```

### 3. Open and Resolve

Conflicted files contain markers:

```
<<<<<<< HEAD
const theme = "dark";
=======
const theme = "light";
>>>>>>> feature/new-theme
```

Choose the correct version, remove all markers.

### 4. Complete the Merge

```bash
git add <resolved-files>
git commit
```

## Resolution Strategies

### Code Conflicts

- **Understand both changes** — don't just pick one blindly
- **Combine if possible** — both changes may be needed
- **Test after resolving** — ensure the merged code works
- **Ask the original author** if unsure about intent

### Configuration Conflicts

- **JSON files** — manually merge, validate structure
- **YAML files** — be careful with indentation
- **package.json** — merge dependencies from both sides

### Large Refactor Conflicts

If a major refactor conflicts with ongoing work:

1. Complete the refactor on `develop` first
2. Rebase the feature branch onto updated `develop`
3. Resolve conflicts during rebase

```bash
git checkout feature/my-work
git rebase develop
# Resolve conflicts as they appear
git rebase --continue
```

## Tools

- **VS Code** — built-in merge conflict editor
- **`git mergetool`** — configure your preferred merge tool
- **`git log --merge --oneline --left-right`** — see commits from both sides

## After Resolution

1. Run the full test suite
2. Verify the application starts correctly
3. Check the specific feature that was being developed
4. If in doubt, create a backup branch before resolving:

```bash
git checkout -b backup/pre-resolve
git checkout feature/branch
git merge develop
```
