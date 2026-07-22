"""Ollama (local) provider — connects to a local Ollama instance."""

from __future__ import annotations

import httpx

from app.providers.base import AIProvider, ChatMessage, ChatResponse
from app.providers.registry import register_provider
from app.config.settings import settings


class OllamaProvider(AIProvider):
    """Ollama local provider — communicates via its HTTP API."""

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def supported_models(self) -> list[str]:
        return ["llama3", "llama3:70b", "mistral", "codellama", "phi3"]

    def __init__(self):
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> ChatResponse:
        model = model or self._model
        ollama_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": model,
                    "messages": ollama_messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

        return ChatResponse(
            content=data.get("message", {}).get("content", ""),
            model=data.get("model", model),
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            },
            finish_reason="stop",
            raw=data,
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


register_provider("ollama", OllamaProvider)
