"""Unit tests for the AI provider abstraction."""

import pytest

from app.services.ai.providers.base import AIProvider, ChatMessage, ChatResponse, MessageRole


class DummyProvider(AIProvider):
    """Test provider implementation."""

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def supported_models(self) -> list[str]:
        return ["dummy-1", "dummy-2"]

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=4096, **kwargs):
        return ChatResponse(
            content="test response",
            model="dummy-1",
            usage={"total_tokens": 10},
        )


def test_chat_message_creation():
    msg = ChatMessage(role=MessageRole.USER, content="hello")
    assert msg.role == MessageRole.USER
    assert msg.content == "hello"


def test_chat_response_creation():
    resp = ChatResponse(content="hi", model="test", usage={"total_tokens": 5})
    assert resp.content == "hi"
    assert resp.model == "test"


@pytest.mark.asyncio
async def test_provider_chat():
    provider = DummyProvider()
    messages = [ChatMessage(role=MessageRole.USER, content="hello")]
    response = await provider.chat(messages)
    assert response.content == "test response"
    assert response.model == "dummy-1"


def test_provider_name():
    provider = DummyProvider()
    assert provider.name == "dummy"


def test_provider_models():
    provider = DummyProvider()
    assert "dummy-1" in provider.supported_models
