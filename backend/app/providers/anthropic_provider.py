"""Anthropic (Claude) provider implementation."""

from __future__ import annotations

from typing import AsyncIterator

from app.providers.base import AIProvider, ChatMessage, ChatResponse
from app.providers.registry import register_provider
from app.config.settings import settings


class AnthropicProvider(AIProvider):
    """Anthropic API provider — wraps the anthropic SDK."""

    @property
    def name(self) -> str:
        return "claude"

    @property
    def supported_models(self) -> list[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ]

    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        import anthropic  # noqa: F401
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> ChatResponse:
        model = model or settings.anthropic_model

        # Anthropic requires system as a separate parameter
        system_msg = ""
        chat_msgs = []
        for m in messages:
            if m.role.value == "system":
                system_msg = m.content
            else:
                chat_msgs.append({"role": m.role.value, "content": m.content})

        params = {
            "model": model,
            "messages": chat_msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            params["system"] = system_msg

        response = await self._client.messages.create(**params)

        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

        return ChatResponse(
            content=content,
            model=response.model,
            usage=usage,
            finish_reason=response.stop_reason or "end_turn",
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        model = model or settings.anthropic_model

        system_msg = ""
        chat_msgs = []
        for m in messages:
            if m.role.value == "system":
                system_msg = m.content
            else:
                chat_msgs.append({"role": m.role.value, "content": m.content})

        params: dict = {
            "model": model,
            "messages": chat_msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            params["system"] = system_msg

        async with self._client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text


register_provider("claude", AnthropicProvider)
