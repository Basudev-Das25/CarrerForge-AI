"""Ollama Provider — local model inference."""

from __future__ import annotations

import time
from typing import Any

import httpx

from app.services.ai.providers.base import (
    AIProvider, ChatMessage, ChatResponse, MessageRole,
)


class OllamaProvider(AIProvider):
    """Ollama local model provider."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self._base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def supported_models(self) -> list[str]:
        return ["llama3", "mistral", "codellama", "phi3", "gemma2"]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> ChatResponse:
        model = model or self.default_model

        payload = {
            "model": model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        start = time.time()
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self._base_url}/api/chat", json=payload)
            response.raise_for_status()
        latency = (time.time() - start) * 1000

        data = response.json()
        return ChatResponse(
            content=data.get("message", {}).get("content", ""),
            model=model,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            },
            finish_reason="stop",
            latency_ms=round(latency, 1),
        )

    async def health_check(self):
        from app.services.ai.providers.base import ProviderHealth
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                resp.raise_for_status()
            latency = (time.time() - start) * 1000
            return ProviderHealth(healthy=True, latency_ms=round(latency, 1))
        except Exception as e:
            latency = (time.time() - start) * 1000
            return ProviderHealth(healthy=False, latency_ms=round(latency, 1), error=str(e))

    def supports_embeddings(self) -> bool:
        return True

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        return 0.0  # Local models are free
