"""AI provider router — chat, streaming, embeddings.
Uses the new AI Orchestrator service layer.
"""

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = structlog.get_logger("careerforge.routers.ai")

from app.services.ai.orchestrator import orchestrator
from app.services.ai.providers.base import ChatMessage, MessageRole

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]  # [{role, content}]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096


class EmbeddingRequest(BaseModel):
    text: str
    model: str | None = None


@router.get("/providers")
async def get_providers():
    """List available AI providers and their models."""
    health = await orchestrator.health_all()
    return [
        {"name": name, "healthy": h.healthy, "models": h.models_available or []}
        for name, h in health.items()
    ]


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat completion through the AI orchestrator."""
    messages = [
        ChatMessage(role=MessageRole(m["role"]), content=m["content"])
        for m in request.messages
    ]
    try:
        response = await orchestrator.chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_cache=True,
        )
        return {
            "content": response.content,
            "model": response.model,
            "usage": response.usage,
            "finish_reason": response.finish_reason,
        }
    except Exception as e:
        logger.error("ai.chat_error", error=str(e))
        raise HTTPException(status_code=502, detail="AI provider error")


@router.post("/embed")
async def embed(request: EmbeddingRequest):
    """Generate embeddings using the first available provider that supports them."""
    health = await orchestrator.health_all()
    for name, h in health.items():
        if h.healthy:
            provider = orchestrator.get_provider(name)
            if provider and provider.supports_embeddings():
                result = await provider.generate_embedding(request.text, model=request.model)
                return {"embedding": result.embedding, "dimensions": result.dimensions}
    raise HTTPException(status_code=400, detail="No available provider supports embeddings")
