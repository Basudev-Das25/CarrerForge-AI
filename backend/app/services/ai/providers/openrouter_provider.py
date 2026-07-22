"""OpenRouter Provider — multi-model gateway."""

from __future__ import annotations

import time
from typing import Any

from app.services.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
)


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider — routes to multiple model providers."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def supported_models(self) -> list[str]:
        return [
            "anthropic/claude-sonnet-4",
            "openai/gpt-4o",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-405b",
            "mistralai/mixtral-8x7b",
        ]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> ChatResponse:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=self._api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        model = model or self.default_model

        start = time.time()
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": m.role.value, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = (time.time() - start) * 1000

        choice = response.choices[0]
        usage = response.usage
        return ChatResponse(
            content=choice.message.content or "",
            model=response.model or model,
            usage={
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            },
            finish_reason=choice.finish_reason or "stop",
            latency_ms=round(latency, 1),
        )

    def supports_embeddings(self) -> bool:
        return False

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        return (tokens_in / 1000 * 0.003) + (tokens_out / 1000 * 0.015)
