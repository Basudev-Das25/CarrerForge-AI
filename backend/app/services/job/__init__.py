"""Job Intelligence — parsing, structuring, and managing job descriptions."""

from app.services.job.intelligence import JobIntelligence
from app.services.job.repository import JobRepository

__all__ = ["JobIntelligence", "JobRepository"]
