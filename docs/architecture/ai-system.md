# AI Architecture

## AI Orchestrator

The AI Orchestrator is the centralized hub for all AI operations. No module communicates directly with AI providers.

```
Application Code → AI Orchestrator → Provider → API
                         ↓
                    Cache Layer
                    Retry Logic
                    Rate Limiting
                    Observability
```

### Responsibilities
- **Provider Selection** — Configured via `AI_PROVIDER` env var, automatic fallback to next provider
- **Model Selection** — Per-request model override support
- **Retries** — Exponential backoff, max 3 retries per provider
- **Caching** — LRU response cache (1000 entries, 5min TTL)
- **Rate Limiting** — 100ms minimum between requests per provider
- **Timeout** — 60s per request
- **Concurrency Control** — Semaphore limits to 10 concurrent requests
- **Observability** — Every request logged with tokens, latency, cost, retries
- **Prompt Integration** — Render prompts from registry before sending

## Prompt Registry

Prompts are stored as version-controlled YAML files in `backend/prompts/`:

```
prompts/
├── ats/
│   ├── evaluator.yaml      # ATS score evaluation
│   └── feedback.yaml       # ATS improvement feedback
├── jd/
│   ├── parser.yaml         # JD → structured profile
│   ├── extractor.yaml      # Extract requirements
│   └── matcher.yaml        # Candidate-JD matching
├── optimizer/
│   ├── optimizer.yaml      # Resume optimization
│   └── gap_analyzer.yaml   # Gap analysis
├── reflection/
│   ├── improver.yaml       # Iterative improvement
│   └── critic.yaml         # Quality critique
└── resume/
    ├── planner.yaml        # Resume structure planning
    ├── writer.yaml         # Section content generation
    ├── summary.yaml        # Professional summary
    └── bullet_generator.yaml # Bullet point generation
```

Each prompt supports:
- Variable substitution: `{{variable_name}}`
- Provider overrides
- Model overrides
- Version tracking

## Agent Framework

Every AI capability is an `Agent` with a standardized interface:

```python
class Agent(ABC):
    async def execute(**kwargs) -> AgentResult  # Run with retries
    async def health() -> dict                   # Health check
    def metrics() -> dict                        # Usage metrics
    def validate_input(**kwargs) -> list[str]    # Input validation
    def validate_output(data) -> list[str]       # Output validation
```

### 12 Agents

| Agent | Purpose |
|---|---|
| `job_parser` | Parse raw JD into structured profile |
| `skill_extraction` | Extract skills from text |
| `keyword` | Extract ATS keywords |
| `knowledge_retrieval` | Retrieve relevant profile knowledge |
| `evidence` | Select and score evidence items |
| `resume_planner` | Plan resume structure |
| `resume_writer` | Write resume sections |
| `resume_reviewer` | Review and critique resume quality |
| `ats_evaluator` | Evaluate ATS compatibility |
| `reflection` | Iterative resume improvement |
| `cover_letter` | Generate tailored cover letters |
| `interview` | Prepare interview questions |

## Knowledge Engine

In-memory knowledge graph connecting all profile entities:

- **14 entity types**: user, education, experience, project, skill, certificate, achievement, language, publication, award, social_link, job_description, resume_version, ats_report
- **8 auto-discovered relationship types**: uses, demonstrates, involved_in, coincides_with, resulted_from, recognizes, requires, targets
- **13 scoring dimensions**: leadership, machine_learning, backend, frontend, cloud, devops, research, data_science, management, communication, ats_coverage, industry, seniority

## Resume Pipeline

```
Job Description
    ↓ (Job Intelligence)
Structured Job Profile
    ↓ (Knowledge Engine)
Knowledge Graph
    ↓ (Evidence Engine)
Evidence Bundle
    ↓ (AI Planner)
Resume Blueprint
    ↓ (AI Writer)
Canonical Resume (JSON)
    ↓ (Validator)
Validation Report
    ↓ (Reflection Loop)
Optimized Resume
    ↓ (Template Engine)
Typst Source
    ↓ (Typst Compiler)
PDF
```

## ATS Pipeline

```
Resume + Job Profile
    ↓
Keyword Analysis (density, coverage, matched/missing)
    ↓
Section Analysis (completeness, ordering, word count)
    ↓
Bullet Analysis (weak verbs, metrics, length)
    ↓
Recruiter Metrics (readability, impact, achievement, specificity)
    ↓
Evidence Verification (provenance checking)
    ↓
Weighted Overall Score (7 dimensions)
    ↓
Optimization Suggestions (AI-powered)
    ↓
Multi-pass Optimization Loop
```

## Provider Abstraction

All providers implement identical interfaces:

```python
class AIProvider(ABC):
    async def chat(messages, model, temperature, max_tokens) -> ChatResponse
    async def chat_stream(...) -> AsyncIterator[str]
    async def generate_embedding(text, model) -> EmbeddingResponse
    async def health_check() -> ProviderHealth
    def estimate_cost(model, tokens_in, tokens_out) -> float
```

6 providers: OpenAI, Anthropic, OpenRouter, Ollama, Grok, HuggingFace
