"""AI Observability — execution logging, cost tracking, and telemetry.

Every AI request is logged with full context for debugging and optimization.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger("careerforge.ai.observability")


@dataclass
class AIObservation:
    """Complete record of an AI execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    provider: str = ""
    model: str = ""
    prompt_version: str = ""
    response_version: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    retries: int = 0
    cache_hit: bool = False
    cost_usd: float = 0.0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True


class ObservabilityTracker:
    """Tracks all AI executions for analysis and debugging."""

    def __init__(self):
        self._observations: list[AIObservation] = []
        self._by_provider: dict[str, list[AIObservation]] = {}
        self._by_model: dict[str, list[AIObservation]] = {}
        self._total_cost: float = 0.0
        self._total_tokens: int = 0

    def record(self, obs: AIObservation) -> None:
        """Record an AI observation."""
        self._observations.append(obs)
        self._by_provider.setdefault(obs.provider, []).append(obs)
        self._by_model.setdefault(obs.model, []).append(obs)
        self._total_cost += obs.cost_usd
        self._total_tokens += obs.tokens_in + obs.tokens_out

        log_data = {
            "obs_id": obs.id,
            "provider": obs.provider,
            "model": obs.model,
            "tokens_in": obs.tokens_in,
            "tokens_out": obs.tokens_out,
            "latency_ms": round(obs.latency_ms, 1),
            "cost_usd": round(obs.cost_usd, 6),
            "retries": obs.retries,
            "cache_hit": obs.cache_hit,
            "success": obs.success,
        }
        if obs.success:
            logger.info("ai.request", **log_data)
        else:
            logger.warning("ai.request.failed", **log_data, errors=obs.errors)

    def get_stats(self) -> dict:
        """Return aggregated statistics."""
        return {
            "total_requests": len(self._observations),
            "total_cost_usd": round(self._total_cost, 6),
            "total_tokens": self._total_tokens,
            "avg_latency_ms": self._avg_latency(),
            "by_provider": {p: len(obs) for p, obs in self._by_provider.items()},
            "by_model": {m: len(obs) for m, obs in self._by_model.items()},
            "error_rate": self._error_rate(),
            "cache_hit_rate": self._cache_hit_rate(),
        }

    def get_recent(self, limit: int = 50) -> list[dict]:
        """Return recent observations."""
        return [
            {
                "id": o.id,
                "timestamp": o.timestamp,
                "provider": o.provider,
                "model": o.model,
                "tokens_in": o.tokens_in,
                "tokens_out": o.tokens_out,
                "latency_ms": round(o.latency_ms, 1),
                "cost_usd": round(o.cost_usd, 6),
                "retries": o.retries,
                "cache_hit": o.cache_hit,
                "success": o.success,
                "prompt_version": o.prompt_version,
            }
            for o in self._observations[-limit:]
        ]

    def _avg_latency(self) -> float:
        if not self._observations:
            return 0.0
        return round(sum(o.latency_ms for o in self._observations) / len(self._observations), 1)

    def _error_rate(self) -> float:
        if not self._observations:
            return 0.0
        errors = sum(1 for o in self._observations if not o.success)
        return round(errors / len(self._observations), 3)

    def _cache_hit_rate(self) -> float:
        if not self._observations:
            return 0.0
        hits = sum(1 for o in self._observations if o.cache_hit)
        return round(hits / len(self._observations), 3)


# Cost estimation per 1K tokens (input/output)
COST_TABLE: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-haiku-4-20250514": {"input": 0.00025, "output": 0.00125},
    "claude-opus-4-20250514": {"input": 0.015, "output": 0.075},
}


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate cost in USD for a model invocation."""
    rates = COST_TABLE.get(model, {"input": 0.001, "output": 0.003})
    return (tokens_in / 1000 * rates["input"]) + (tokens_out / 1000 * rates["output"])


# Global tracker instance
tracker = ObservabilityTracker()
