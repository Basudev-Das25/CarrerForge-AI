"""OpenRouter provider — routes to many models via a single API key."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.config.settings import settings
from app.providers.base import AIProvider, ChatMessage, ChatResponse
from app.providers.registry import register_provider


class OpenRouterProvider(AIProvider):
    """OpenRouter provider — uses the OpenAI-compatible API."""

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def supported_models(self) -> list[str]:
        return [
            "anthropic/claude-sonnet-4",
            "openai/gpt-4o",
            "meta-llama/llama-3-70b-instruct",
            "mistralai/mixtral-8x22b-instruct",
            "google/gemini-pro",
        ]

    def __init__(self):
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        import openai
        self._client = openai.AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> ChatResponse:
        model = model or settings.openrouter_model
        oai_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        response = await self._client.chat.completions.create(
            model=model,
            messages=oai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        choice = response.choices[0]
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return ChatResponse(
            content=choice.message.content or "",
            model=response.model,
            usage=usage,
            finish_reason=choice.finish_reason or "stop",
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        model = model or settings.openrouter_model
        oai_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        stream = await self._client.chat.completions.create(
            model=model,
            messages=oai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


register_provider("openrouter", OpenRouterProvider)
