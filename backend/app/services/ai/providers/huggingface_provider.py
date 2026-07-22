"""HuggingFace Provider — Inference API."""

from __future__ import annotations

import time
from typing import Any

import httpx

from app.services.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
    MessageRole,
)


class HuggingFaceProvider(AIProvider):
    """HuggingFace Inference API provider."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "huggingface"

    @property
    def supported_models(self) -> list[str]:
        return [
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "google/gemma-2-9b-it",
        ]

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> ChatResponse:
        model = model or self.default_model

        # Build prompt from messages
        prompt = ""
        for m in messages:
            if m.role == MessageRole.SYSTEM:
                prompt += f"<|system|>\n{m.content}\n"
            elif m.role == MessageRole.USER:
                prompt += f"<|user|>\n{m.content}\n"
            elif m.role == MessageRole.ASSISTANT:
                prompt += f"<|assistant|>\n{m.content}\n"
        prompt += "<|assistant|>\n"

        start = time.time()
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature,
                        "return_full_text": False,
                    },
                },
            )
            response.raise_for_status()
        latency = (time.time() - start) * 1000

        data = response.json()
        content = data[0].get("generated_text", "") if isinstance(data, list) else str(data)

        return ChatResponse(
            content=content,
            model=model,
            usage={"total_tokens": len(content.split())},  # Approximate
            finish_reason="stop",
            latency_ms=round(latency, 1),
        )

    def supports_embeddings(self) -> bool:
        return True

    async def generate_embedding(self, text: str, model: str | None = None) -> EmbeddingResponse:
        model = model or "sentence-transformers/all-MiniLM-L6-v2"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"inputs": text},
            )
            response.raise_for_status()
        data = response.json()
        embedding = data if isinstance(data, list) else data.get("embedding", [])
        return EmbeddingResponse(embedding=embedding, model=model, dimensions=len(embedding))

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        return 0.0  # Free tier models
