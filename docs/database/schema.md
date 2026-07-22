# Database Schema

## Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    users     │────<│  education   │     │  experience  │
│             │────<│             │     │             │
│  id (PK)    │────<│  user_id FK │     │  user_id FK │
│  full_name  │     └─────────────┘     └─────────────┘
│  email      │
│  phone      │────<┌─────────────┐     ┌─────────────┐
│  location   │     │  projects    │     │   skills     │
│  summary    │     │             │     │             │
│  version    │     │  user_id FK │     │  user_id FK │
└──────┬──────┘     └─────────────┘     └─────────────┘
       │
       │────<┌─────────────┐     ┌─────────────┐
       │     │ certificates │     │ achievements │
       │     │             │     │             │
       │     │  user_id FK │     │  user_id FK │
       │     └─────────────┘     └─────────────┘
       │
       │────<┌─────────────┐     ┌─────────────┐
       │     │  languages   │     │ publications │
       │     │             │     │             │
       │     │  user_id FK │     │  user_id FK │
       │     └─────────────┘     └─────────────┘
       │
       │────<┌─────────────┐     ┌─────────────┐
       │     │    awards    │     │ social_links │
       │     │             │     │             │
       │     │  user_id FK │     │  user_id FK │
       │     └─────────────┘     └─────────────┘
       │
       │────<┌──────────────────┐
       │     │ profile_versions  │
       │     │                  │
       │     │  user_id FK      │
       │     └──────────────────┘
       │
       │────<┌──────────────────┐     ┌──────────────┐
       │     │ resume_versions   │────<│  ats_reports   │
       │     │                  │     │              │
       │     │  user_id FK      │     │ rv_id FK     │
       │     └──────────────────┘     └──────────────┘
       │
       │────<┌──────────────────┐
       │     │ job_descriptions  │
       │     │                  │
       │     │  user_id FK      │
       │     └──────────────────┘
       │
       │────<┌──────────────────┐
       └─────│ original_documents│
             │                  │
             └──────────────────┘
```

## Table Descriptions

### users
| Column | Type | Constraints |
|---|---|---|
| id | String(36) | PK, UUID |
| email | String(255) | UNIQUE, nullable |
| full_name | String(255) | nullable |
| phone | String(50) | nullable |
| location | String(255) | nullable |
| linkedin_url | String(512) | nullable |
| github_url | String(512) | nullable |
| portfolio_url | String(512) | nullable |
| summary | Text | nullable |
| avatar_path | String(512) | nullable |
| version | Integer | default 1 |
| deleted_at | DateTime | nullable (soft delete) |
| created_at | DateTime | auto |
| updated_at | DateTime | auto |

### education
| Column | Type | Constraints |
|---|---|---|
| id | String(36) | PK |
| user_id | String(36) | FK → users.id |
| degree | String(255) | NOT NULL |
| field_of_study | String(255) | nullable |
| institution | String(255) | NOT NULL |
| location | String(255) | nullable |
| start_date | String(20) | NOT NULL |
| end_date | String(20) | nullable |
| gpa | Float | nullable |
| description | Text | nullable |
| highlights | JSON | default [] |
| version, deleted_at, created_at, updated_at | | |

### experience
| Column | Type | Constraints |
|---|---|---|
| id | String(36) | PK |
| user_id | String(36) | FK → users.id |
| company | String(255) | NOT NULL |
| title | String(255) | NOT NULL |
| location | String(255) | nullable |
| employment_type | String(50) | nullable |
| start_date | String(20) | NOT NULL |
| end_date | String(20) | nullable |
| description | Text | nullable |
| highlights | JSON | default [] |
| skills_used | JSON | default [] |
| version, deleted_at, created_at, updated_at | | |

### projects
| Column | Type | Constraints |
|---|---|---|
| id | String(36) | PK |
| user_id | String(36) | FK → users.id |
| name | String(255) | NOT NULL |
| description | Text | nullable |
| role | String(255) | nullable |
| repo_url, live_url | String(512) | nullable |
| tech_stack, skills_used, keywords, tags, highlights | JSON | |
| industry, category, difficulty | String(100) | nullable |
| team_size | Integer | nullable |
| impact_metrics, responsibilities | JSON | |
| visibility | String(20) | default "private" |
| status | String(20) | default "completed" |
| is_featured | Boolean | default False |
| start_date, end_date | String(20) | nullable |
| version, deleted_at, created_at, updated_at | | |

### skills
| Column | Type | Constraints |
|---|---|---|
| id | String(36) | PK |
| user_id | String(36) | FK → users.id |
| name | String(255) | NOT NULL |
| category | String(100) | nullable |
| subcategory | String(100) | nullable |
| level | String(20) | nullable |
| years_experience | Float | nullable |
| last_used | String(20) | nullable |
| is_primary | Boolean | default False |
| embedding_id | String(36) | nullable |
| version, deleted_at, created_at, updated_at | | |

### certificates, achievements, languages, publications, awards, social_links
Similar pattern — each with: id (PK), user_id (FK), domain-specific fields, version, deleted_at, created_at, updated_at.

### resume_versions
| Column | Type | Constraints |
|---|---|---|
| id | String(36) | PK |
| user_id | String(36) | FK → users.id |
| title | String(255) | NOT NULL |
| template_name | String(100) | nullable |
| content_json | JSON | nullable (stores resume + blueprint + job_profile) |
| pdf_path | String(512) | nullable |
| ats_score | Float | nullable |
| reflection_iterations | Integer | default 0 |
| job_description_id | String(36) | FK → job_descriptions.id, nullable |
| is_final | Boolean | default False |
| created_at | DateTime | auto |

### ats_reports
Stores ATS analysis reports linked to resume versions.

### job_descriptions
Stores parsed job descriptions with extracted keywords and requirements.

### original_documents
Stores uploaded documents with extracted text and embedding references.

## Soft Delete

All profile entities support soft delete via `deleted_at` column:
- `deleted_at IS NULL` = active record
- `deleted_at IS NOT NULL` = soft-deleted
- Repository layer automatically filters soft-deleted records
- `soft_delete()` sets `deleted_at = datetime.now(timezone.utc)`
- `delete()` performs hard delete (rarely used)

## Migration Strategy

Alembic migrations in `backend/migrations/versions/`:
- `001_initial_schema.py` — All tables, indexes, foreign keys
- Run with: `cd backend && alembic upgrade head`
- Rollback with: `cd backend && alembic downgrade -1`

## Indexes

Created on all `user_id` foreign keys for query performance:
- `ix_education_user_id`, `ix_experience_user_id`, `ix_projects_user_id`
- `ix_skills_user_id`, `ix_certificates_user_id`, `ix_achievements_user_id`
- `ix_languages_user_id`, `ix_publications_user_id`, `ix_awards_user_id`
- `ix_social_links_user_id`
