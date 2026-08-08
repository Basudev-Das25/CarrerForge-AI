"""AI Orchestrator API — chat, health, stats, and provider management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai.orchestrator import orchestrator
from app.services.ai.prompt_registry import list_prompts, render_prompt, validate_prompt
from app.services.ai.providers.base import ChatMessage, MessageRole

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    provider: str | None = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    use_cache: bool = True


class PromptRenderRequest(BaseModel):
    category: str
    name: str
    variables: dict = {}
    version: str = "latest"


# ── Chat ────────────────────────────────────────────────────

@router.post("/chat")
async def chat(request: ChatRequest):
    """Execute a chat completion through the orchestrator."""
    messages = [
        ChatMessage(role=MessageRole(m["role"]), content=m["content"])
        for m in request.messages
    ]
    try:
        response = await orchestrator.chat(
            messages=messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_cache=request.use_cache,
        )
        return {
            "content": response.content,
            "model": response.model,
            "usage": response.usage,
            "finish_reason": response.finish_reason,
            "latency_ms": response.latency_ms,
            "cached": response.cached,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail="AI chat error")


# ── Health & Stats ──────────────────────────────────────────

@router.get("/health")
async def health():
    """Check health of all registered providers."""
    results = await orchestrator.health_all()
    return {
        name: {
            "healthy": h.healthy,
            "latency_ms": h.latency_ms,
            "error": h.error,
            "models": h.models_available,
        }
        for name, h in results.items()
    }


@router.get("/stats")
async def stats():
    """Get orchestrator statistics."""
    return orchestrator.get_stats()


@router.post("/cache/clear")
async def clear_cache():
    """Clear the response cache."""
    orchestrator.clear_cache()
    return {"status": "cleared"}


# ── Prompts ─────────────────────────────────────────────────

@router.get("/prompts")
async def get_prompts(category: str | None = None):
    """List available prompts."""
    return {"prompts": list_prompts(category)}


@router.post("/prompts/render")
async def render_prompt_endpoint(request: PromptRenderRequest):
    """Render a prompt with variables."""
    try:
        rendered = render_prompt(request.category, request.name, request.variables, request.version)
        return rendered
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/prompts/{category}/{name}/validate")
async def validate_prompt_endpoint(category: str, name: str):
    """Validate a prompt file."""
    return validate_prompt(category, name)
