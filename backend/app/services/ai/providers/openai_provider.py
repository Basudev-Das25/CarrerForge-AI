"""OpenAI Provider — GPT-4o, GPT-4o-mini, embeddings."""

from __future__ import annotations

import time
from typing import Any

from app.services.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
)


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, base_url: str | None = None):
        self._api_key = api_key
        self._base_url = base_url

    @property
    def name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4o-turbo", "o1", "o1-mini"]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> ChatResponse:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
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
            model=response.model,
            usage={
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            },
            finish_reason=choice.finish_reason or "stop",
            latency_ms=round(latency, 1),
        )

    async def generate_embedding(self, text: str, model: str | None = None) -> EmbeddingResponse:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
        model = model or "text-embedding-3-small"

        response = await client.embeddings.create(model=model, input=text)
        return EmbeddingResponse(
            embedding=response.data[0].embedding,
            model=model,
            dimensions=len(response.data[0].embedding),
            usage={"total_tokens": response.usage.total_tokens},
        )

    def supports_embeddings(self) -> bool:
        return True

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        rates = {
            "gpt-4o": (0.0025, 0.01),
            "gpt-4o-mini": (0.00015, 0.0006),
            "gpt-4o-turbo": (0.01, 0.03),
            "o1": (0.015, 0.06),
            "o1-mini": (0.003, 0.012),
        }
        inp, out = rates.get(model, (0.0025, 0.01))
        return (tokens_in / 1000 * inp) + (tokens_out / 1000 * out)
