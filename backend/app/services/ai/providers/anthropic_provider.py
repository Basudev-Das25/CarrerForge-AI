"""Anthropic Provider — Claude models."""

from __future__ import annotations

import time
from typing import Any

from app.services.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    MessageRole,
)


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def supported_models(self) -> list[str]:
        return ["claude-sonnet-4-20250514", "claude-haiku-4-20250514", "claude-opus-4-20250514"]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> ChatResponse:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self._api_key)
        model = model or self.default_model

        # Separate system message
        system_text = ""
        chat_messages = []
        for m in messages:
            if m.role == MessageRole.SYSTEM:
                system_text = m.content
            else:
                chat_messages.append({"role": m.role.value, "content": m.content})

        if not chat_messages:
            chat_messages = [{"role": "user", "content": "Hello"}]

        start = time.time()
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_text,
            messages=chat_messages,
            temperature=temperature,
        )
        latency = (time.time() - start) * 1000

        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        return ChatResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            finish_reason=response.stop_reason or "stop",
            latency_ms=round(latency, 1),
        )

    def supports_embeddings(self) -> bool:
        return False

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        rates = {
            "claude-sonnet-4-20250514": (0.003, 0.015),
            "claude-haiku-4-20250514": (0.00025, 0.00125),
            "claude-opus-4-20250514": (0.015, 0.075),
        }
        inp, out = rates.get(model, (0.003, 0.015))
        return (tokens_in / 1000 * inp) + (tokens_out / 1000 * out)
