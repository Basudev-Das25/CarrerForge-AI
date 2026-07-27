# AI Orchestrator

## Overview

The AI Orchestrator is the centralized gateway for all AI operations. No module communicates directly with AI providers — every request flows through the orchestrator.

## Features

- **Provider Selection** — Configured via `AI_PROVIDER` env var
- **Automatic Failover** — Falls back to next provider on failure
- **Response Caching** — LRU cache (1000 entries, 5min TTL)
- **Retry Logic** — Exponential backoff, max 3 retries
- **Rate Limiting** — 100ms minimum between requests per provider
- **Timeout** — 60s per request
- **Concurrency Control** — Semaphore limits to 10 concurrent
- **Observability** — Full request logging with tokens, latency, cost
- **Prompt Integration** — Render prompts from registry before sending

## Usage

```python
from app.services.ai.orchestrator import orchestrator
from app.services.ai.providers.base import ChatMessage, MessageRole

response = await orchestrator.chat(
    messages=[
        ChatMessage(role=MessageRole.SYSTEM, content="You are helpful."),
        ChatMessage(role=MessageRole.USER, content="Hello"),
    ],
    model="gpt-4o",
    temperature=0.7,
)
```

## Providers

| Provider | Models | Cost (input/output per 1K) |
|---|---|---|
| OpenAI | gpt-4o, gpt-4o-mini, o1 | $0.0025 / $0.01 |
| Anthropic | claude-sonnet-4, claude-haiku-4, claude-opus-4 | $0.003 / $0.015 |
| OpenRouter | Multi-model gateway | $0.003 / $0.015 |
| Ollama | Local models | Free |
| Grok | grok-2, grok-2-mini | $0.002 / $0.01 |
| HuggingFace | Open models | Free (inference API) |
