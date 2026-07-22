"""OpenAI provider implementation."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.config.settings import settings
from app.providers.base import AIProvider, ChatMessage, ChatResponse
from app.providers.registry import register_provider


class OpenAIProvider(AIProvider):
    """OpenAI API provider — wraps the openai SDK."""

    @property
    def name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1", "o1-mini"]

    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        # Lazy import to avoid import errors when the key isn't configured
        import openai
        self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> ChatResponse:
        model = model or settings.openai_model
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
            raw=response.model_dump() if hasattr(response, "model_dump") else None,
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        model = model or settings.openai_model
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

    async def generate_embedding(self, text: str, model: str | None = None) -> list[float]:
        model = model or "text-embedding-3-small"
        response = await self._client.embeddings.create(model=model, input=text)
        return response.data[0].embedding


register_provider("openai", OpenAIProvider)
