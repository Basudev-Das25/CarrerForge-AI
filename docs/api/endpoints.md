# API Reference

All endpoints are prefixed with `/api/v1`. The API runs on `http://127.0.0.1:8000` during development.

## Authentication

No authentication — local-first single-user application. User ID is always `"default"`.

## Profile Endpoints

### GET /api/v1/profile
Get user profile.

### PUT /api/v1/profile
Update user profile.

### GET /api/v1/dashboard
Get dashboard data (counts, profile completion).

### GET /api/v1/completion
Get profile completion percentage.

### GET /api/v1/search?q=keyword
Global search across all profile entities.

### CRUD Endpoints

Each entity has: `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`

| Entity | Base Path |
|---|---|
| Education | `/api/v1/education` |
| Experience | `/api/v1/experience` |
| Projects | `/api/v1/projects` |
| Skills | `/api/v1/skills` |
| Certificates | `/api/v1/certificates` |
| Achievements | `/api/v1/achievements` |
| Languages | `/api/v1/languages` |
| Publications | `/api/v1/publications` |
| Awards | `/api/v1/awards` |
| Social Links | `/api/v1/social-links` |

## Resume Generation

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/resume/generate` | Full pipeline execution |
| POST | `/api/v1/resume/blueprint` | Planning only |
| POST | `/api/v1/resume/validate` | Validation check |
| GET | `/api/v1/resume/templates` | List templates |
| GET | `/api/v1/resume/templates/{name}` | Get template details |
| POST | `/api/v1/resume/templates/{name}/render` | Render Typst |
| GET | `/api/v1/resume/themes/{name}` | Get template theme |
| GET | `/api/v1/resume/versions` | Version history |
| GET | `/api/v1/resume/versions/{id}` | Get version |
| DELETE | `/api/v1/resume/versions/{id}` | Delete version |
| POST | `/api/v1/resume/versions/compare` | Compare versions |
| POST | `/api/v1/resume/export/typst` | Export Typst source |
| POST | `/api/v1/resume/export/text` | Export plain text |
| POST | `/api/v1/resume/export/markdown` | Export Markdown |
| POST | `/api/v1/resume/compile` | Compile to PDF |
| POST | `/api/v1/resume/validate-typst` | Validate Typst syntax |

## ATS Intelligence

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/ats-intelligence/analyze` | Full ATS analysis |
| POST | `/api/v1/ats-intelligence/analyze-version/{id}` | Analyze stored version |
| POST | `/api/v1/ats-intelligence/optimize` | Iterative optimization |
| POST | `/api/v1/ats-intelligence/compare` | Compare two resumes |
| POST | `/api/v1/ats-intelligence/compare-versions` | Compare stored versions |
| GET | `/api/v1/ats-intelligence/reports` | List reports |
| GET | `/api/v1/ats-intelligence/reports/{id}` | Get report |
| POST | `/api/v1/ats-intelligence/reports/{id}/export` | Export report |

## AI Orchestrator

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/ai-orchestrator/chat` | Chat completion |
| GET | `/api/v1/ai-orchestrator/health` | Provider health |
| GET | `/api/v1/ai-orchestrator/stats` | Usage statistics |
| GET | `/api/v1/ai-orchestrator/prompts` | List prompts |
| POST | `/api/v1/ai-orchestrator/prompts/render` | Render prompt |
| GET | `/api/v1/ai-orchestrator/prompts/{cat}/{name}/validate` | Validate prompt |
| POST | `/api/v1/ai-orchestrator/cache/clear` | Clear response cache |

## Agents

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/agents/job-parser` | Parse job description |
| POST | `/api/v1/agents/skill-extraction` | Extract skills |
| POST | `/api/v1/agents/keywords` | Extract ATS keywords |
| POST | `/api/v1/agents/resume-planner` | Plan resume structure |
| POST | `/api/v1/agents/resume-writer` | Write resume section |
| POST | `/api/v1/agents/resume-reviewer` | Review resume |
| POST | `/api/v1/agents/ats-evaluator` | Evaluate ATS compatibility |
| POST | `/api/v1/agents/reflection` | Improve resume |
| POST | `/api/v1/agents/cover-letter` | Generate cover letter |
| POST | `/api/v1/agents/interview` | Prepare interview questions |
| GET | `/api/v1/agents/health` | All agents health |

## Knowledge Engine

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/knowledge/build` | Build knowledge graph |
| GET | `/api/v1/knowledge/stats` | Graph statistics |
| POST | `/api/v1/knowledge/search` | Hybrid search |
| GET | `/api/v1/knowledge/summary` | Knowledge summary |
| GET | `/api/v1/knowledge/embedding-status` | Embedding status |
| POST | `/api/v1/knowledge/embeddings/generate` | Generate embeddings |
| POST | `/api/v1/knowledge/embeddings/regenerate` | Regenerate embeddings |
| GET | `/api/v1/knowledge/relevant/{type}` | Relevant entities |

## Job Intelligence

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/jobs/parse` | Parse JD with AI |
| POST | `/api/v1/jobs/save` | Save JD to database |
| GET | `/api/v1/jobs/` | List saved JDs |
| GET | `/api/v1/jobs/search?q=keyword` | Search JDs |
| GET | `/api/v1/jobs/{id}` | Get JD |
| DELETE | `/api/v1/jobs/{id}` | Delete JD |
| POST | `/api/v1/jobs/compare` | Compare two JDs |
