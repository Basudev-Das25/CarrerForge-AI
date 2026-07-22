"""Custom exception hierarchy for CareerForge AI.

All application errors derive from CareerForgeError.
The global exception handler in main.py converts these to JSON responses.
"""

from __future__ import annotations


class CareerForgeError(Exception):
    """Base exception for all CareerForge errors."""

    def __init__(self, message: str = "An unexpected error occurred", code: str = "UNKNOWN"):
        self.message = message
        self.code = code
        super().__init__(message)


class ConfigError(CareerForgeError):
    """Configuration or settings error."""

    def __init__(self, message: str = "Configuration error"):
        super().__init__(message=message, code="CONFIG_ERROR")


class DatabaseError(CareerForgeError):
    """Database operation failure."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, code="DB_ERROR")


class ProviderError(CareerForgeError):
    """AI provider call failure."""

    def __init__(self, message: str = "AI provider error", provider: str = ""):
        self.provider = provider
        super().__init__(message=message, code="PROVIDER_ERROR")


class ProviderNotConfiguredError(ProviderError):
    """Provider is not configured or API key is missing."""

    def __init__(self, provider: str = ""):
        super().__init__(message=f"Provider '{provider}' is not configured", provider=provider)


class PipelineError(CareerForgeError):
    """Resume generation pipeline failure."""

    def __init__(self, message: str = "Pipeline error", step: str = ""):
        self.step = step
        super().__init__(message=message, code="PIPELINE_ERROR")


class ValidationError(CareerForgeError):
    """Input validation failure."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, code="VALIDATION_ERROR")


class DocumentError(CareerForgeError):
    """Document processing failure."""

    def __init__(self, message: str = "Document processing error"):
        super().__init__(message=message, code="DOC_ERROR")


class SecurityError(CareerForgeError):
    """Security-related error (encryption, auth)."""

    def __init__(self, message: str = "Security error"):
        super().__init__(message=message, code="SECURITY_ERROR")


class EmbeddingError(CareerForgeError):
    """Vector embedding generation or search failure."""

    def __init__(self, message: str = "Embedding error"):
        super().__init__(message=message, code="EMBEDDING_ERROR")


class NotFoundError(CareerForgeError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code="NOT_FOUND")
