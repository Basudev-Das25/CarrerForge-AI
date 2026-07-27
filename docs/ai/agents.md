# Agent Framework

## Overview

Every AI capability in CareerForge AI is implemented as an `Agent`. The base class provides a standardized interface with automatic retry, validation, and error handling.

## Base Class

```python
from app.services.agents.base import Agent, AgentResult

class MyAgent(Agent):
    def __init__(self):
        super().__init__("my_agent", max_retries=2)

    def system_prompt(self) -> str:
        return "You are a ..."

    def user_prompt(self, **kwargs) -> str:
        return f"Task: {kwargs.get('input', '')}"

    def parse_response(self, raw: str) -> dict:
        return self._parse_json(raw)
```

## Agent Lifecycle

```
execute(**kwargs)
    → validate_input()
    → Build prompts (system + user)
    → Call AI Orchestrator
    → parse_response()
    → validate_output()
    → Return AgentResult
    → On failure: retry with backoff
```

## AgentResult

```python
@dataclass
class AgentResult:
    success: bool
    data: dict
    raw_response: str
    prompt_version: str
    provider: str
    model: str
    tokens_used: int
    latency_ms: float
    error: str
    retry_count: int
```

## 12 Agents

| Agent | Prompt | Purpose |
|---|---|---|
| `job_parser` | jd/parser | Parse raw JD into structured profile |
| `skill_extraction` | — | Extract skills from text |
| `keyword` | — | Extract ATS keywords |
| `knowledge_retrieval` | — | Retrieve relevant knowledge |
| `evidence` | — | Select evidence items |
| `resume_planner` | resume/planner | Plan resume structure |
| `resume_writer` | resume/writer | Write resume sections |
| `resume_reviewer` | reflection/critic | Review resume quality |
| `ats_evaluator` | ats/evaluator | Evaluate ATS compatibility |
| `reflection` | reflection/improver | Iterative improvement |
| `cover_letter` | — | Generate cover letters |
| `interview` | — | Prepare interview questions |
