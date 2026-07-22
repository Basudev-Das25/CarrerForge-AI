# Versioning Strategy

CareerForge AI follows [Semantic Versioning 2.0.0](https://semver.org/).

## Format

```
MAJOR.MINOR.PATCH
```

| Component | When to Increment | Examples |
|---|---|---|
| **MAJOR** | Breaking API changes, incompatible changes | 1.0.0 → 2.0.0 |
| **MINOR** | New features, backwards-compatible | 0.1.0 → 0.2.0 |
| **PATCH** | Bug fixes, backwards-compatible | 0.1.0 → 0.1.1 |

## Current Phase

The project is in **pre-release** (0.x.y). During this phase:

- `MINOR` versions may include breaking changes
- `PATCH` versions are always backwards-compatible
- The API is not considered stable until 1.0.0

## Version Locations

All version numbers must be updated together:

| File | Field |
|---|---|
| `package.json` | `"version"` |
| `src-tauri/Cargo.toml` | `version` |
| `src-tauri/tauri.conf.json` | `version` |
| `CHANGELOG.md` | Release header |

## Commit-to-Version Mapping

Conventional Commits automatically determine the next version:

```
fix(...)      → patch bump (0.1.0 → 0.1.1)
feat(...)     → minor bump (0.1.0 → 0.2.0)
feat!(...)    → major bump (0.1.0 → 1.0.0)
```

## Tags

Tags follow the `v` prefix format:

```
v0.1.0
v0.2.0
v1.0.0
```

## CHANGELOG

Maintain a `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [0.2.0] - 2026-08-15

### Added
- Profile CRUD endpoints
- Resume generation pipeline

### Fixed
- Date parsing in experience forms

### Changed
- Migrated to SQLAlchemy 2.0 async

## [0.1.0] - 2026-07-21

### Added
- Initial project scaffolding
- Frontend layout and navigation
- Backend API structure
- AI provider abstraction layer
```
