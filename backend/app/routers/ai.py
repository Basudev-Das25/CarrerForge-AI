"""AI provider router — chat, streaming, embeddings."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.providers.base import ChatMessage, MessageRole
from app.providers.registry import get_provider, list_providers

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
    return list_providers()


@router.post("/chat")
async def chat(request: ChatRequest):
    provider = get_provider()
    messages = [ChatMessage(role=MessageRole(m["role"]), content=m["content"]) for m in request.messages]
    response = await provider.chat(
        messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    return {
        "content": response.content,
        "model": response.model,
        "usage": response.usage,
        "finish_reason": response.finish_reason,
    }


@router.post("/embed")
async def embed(request: EmbeddingRequest):
    provider = get_provider()
    vector = await provider.generate_embedding(request.text, model=request.model)
    return {"embedding": vector, "dimensions": len(vector)}
