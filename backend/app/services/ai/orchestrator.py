"""AI Orchestrator — centralized hub for all AI operations.

Every AI request passes through here. Handles provider selection,
fallbacks, retries, caching, rate limiting, and observability.
No module should communicate directly with any AI provider.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import structlog
import time
from collections.abc import AsyncIterator
from typing import Any

from app.config.settings import settings
from app.services.ai.observability import AIObservation, tracker
from app.services.ai.prompt_registry import render_prompt
from app.services.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    MessageRole,
    ProviderHealth,
)

logger = structlog.get_logger("careerforge.ai.orchestrator")

# ── Response Cache ──────────────────────────────────────────

class ResponseCache:
    """Simple in-memory LRU cache for AI responses."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self._cache: dict[str, tuple[ChatResponse, float]] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds

    def _key(self, messages: list[ChatMessage], model: str, temperature: float) -> str:
        content = json.dumps([
            {"role": m.role.value, "content": m.content} for m in messages
        ]) + f":{model}:{temperature}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get(self, messages: list[ChatMessage], model: str, temperature: float) -> ChatResponse | None:
        key = self._key(messages, model, temperature)
        if key in self._cache:
            response, ts = self._cache[key]
            if time.time() - ts < self._ttl:
                cached = ChatResponse(
                    content=response.content,
                    model=response.model,
                    usage=response.usage,
                    finish_reason=response.finish_reason,
                    latency_ms=0.0,
                    cached=True,
                )
                return cached
            del self._cache[key]
        return None

    def set(self, messages: list[ChatMessage], model: str, temperature: float, response: ChatResponse) -> None:
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest]
        key = self._key(messages, model, temperature)
        self._cache[key] = (response, time.time())

    def clear(self) -> None:
        self._cache.clear()


# ── Orchestrator ────────────────────────────────────────────

class AIOrchestrator:
    """Central orchestrator for all AI operations."""

    def __init__(self):
        self._providers: dict[str, AIProvider] = {}
        self._fallback_order: list[str] = ["openai", "anthropic", "openrouter", "ollama"]
        self._cache = ResponseCache()
        self._rate_limiters: dict[str, float] = {}
        self._max_retries = 3
        self._retry_delay = 1.0
        self._timeout = 60.0
        self._semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

    def register_provider(self, provider: AIProvider) -> None:
        """Register an AI provider."""
        self._providers[provider.name] = provider
        logger.info("orchestrator.provider.registered", provider=provider.name)

    def get_provider(self, name: str | None = None) -> AIProvider:
        """Get a provider by name, or the default."""
        if name and name in self._providers:
            return self._providers[name]
        # Try the configured provider
        if settings.ai_provider in self._providers:
            return self._providers[settings.ai_provider]
        # Fallback to first available
        for fallback in self._fallback_order:
            if fallback in self._providers:
                return self._providers[fallback]
        raise RuntimeError("No AI providers registered")

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_cache: bool = True,
        prompt_key: str | None = None,
        prompt_variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Execute a chat completion through the orchestrator.

        Supports:
        - Provider selection and fallback
        - Caching
        - Rate limiting
        - Retries with exponential backoff
        - Timeout handling
        - Concurrency control
        - Observability
        """
        # If using prompt registry, render the prompt
        if prompt_key and prompt_variables:
            parts = prompt_key.split("/")
            if len(parts) == 2:
                rendered = render_prompt(parts[0], parts[1], prompt_variables)
                messages = []
                if rendered["system"]:
                    messages.append(ChatMessage(role=MessageRole.SYSTEM, content=rendered["system"]))
                messages.append(ChatMessage(role=MessageRole.USER, content=rendered["user"]))

        # Check cache
        resolved_model = model or self.get_provider(provider).default_model
        if use_cache:
            cached = self._cache.get(messages, resolved_model, temperature)
            if cached:
                return cached

        # Rate limit check
        provider_name = provider or settings.ai_provider
        self._check_rate_limit(provider_name)

        # Execute with fallback
        last_error = None
        providers_to_try = [provider_name] + [p for p in self._fallback_order if p != provider_name]

        for attempt, prov_name in enumerate(providers_to_try):
            if prov_name not in self._providers:
                continue

            p = self._providers[prov_name]
            for retry in range(self._max_retries):
                try:
                    async with self._semaphore:
                        obs = AIObservation(provider=prov_name, model=resolved_model)
                        response = await asyncio.wait_for(
                            p.chat(messages, model=resolved_model, temperature=temperature, max_tokens=max_tokens, **kwargs),
                            timeout=self._timeout,
                        )

                        # Track observability
                        obs.tokens_in = response.usage.get("prompt_tokens", response.usage.get("input_tokens", 0))
                        obs.tokens_out = response.usage.get("completion_tokens", response.usage.get("output_tokens", 0))
                        obs.latency_ms = response.latency_ms
                        obs.retries = retry
                        obs.cost_usd = p.estimate_cost(resolved_model, obs.tokens_in, obs.tokens_out)
                        tracker.record(obs)

                        # Cache the response
                        if use_cache and not response.cached:
                            self._cache.set(messages, resolved_model, temperature, response)

                        return response

                except TimeoutError:
                    last_error = f"Timeout after {self._timeout}s"
                    logger.warning("orchestrator.timeout", provider=prov_name, retry=retry)
                except Exception as e:
                    last_error = str(e)
                    logger.warning("orchestrator.error", provider=prov_name, retry=retry, error=str(e))

                if retry < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (2 ** retry))

        # Record failure
        obs = AIObservation(provider=provider_name, model=resolved_model, success=False)
        obs.errors.append(last_error or "All providers failed")
        tracker.record(obs)

        raise RuntimeError(f"All providers failed. Last error: {last_error}")

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a chat completion."""
        prov = self.get_provider(provider)
        resolved_model = model or prov.default_model
        async for chunk in prov.chat_stream(messages, model=resolved_model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield chunk

    async def health_all(self) -> dict[str, ProviderHealth]:
        """Check health of all registered providers."""
        results = {}
        for name, provider in self._providers.items():
            try:
                results[name] = await provider.health_check()
            except Exception as e:
                results[name] = ProviderHealth(healthy=False, error=str(e))
        return results

    def get_stats(self) -> dict:
        """Get orchestrator and provider statistics."""
        return {
            "providers": list(self._providers.keys()),
            "cache_size": len(self._cache._cache),
            "observability": tracker.get_stats(),
        }

    def clear_cache(self) -> None:
        """Clear response cache."""
        self._cache.clear()

    def _check_rate_limit(self, provider: str) -> None:
        """Basic rate limiting — 1 request per second per provider."""
        now = time.time()
        last = self._rate_limiters.get(provider, 0)
        if now - last < 0.1:  # 100ms minimum between requests
            import time as _time
            _time.sleep(0.1 - (now - last))
        self._rate_limiters[provider] = time.time()


# Global orchestrator instance
orchestrator = AIOrchestrator()
