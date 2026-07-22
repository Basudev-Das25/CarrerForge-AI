"""Unit tests for error hierarchy."""

import pytest

from app.utils.errors import (
    CareerForgeError,
    ConfigError,
    DatabaseError,
    ProviderError,
    ProviderNotConfiguredError,
    PipelineError,
    ValidationError,
    DocumentError,
    SecurityError,
    EmbeddingError,
)


def test_base_error():
    err = CareerForgeError("something broke")
    assert str(err) == "something broke"
    assert err.code == "UNKNOWN"


def test_config_error():
    err = ConfigError("bad config")
    assert err.code == "CONFIG_ERROR"


def test_database_error():
    err = DatabaseError("table missing")
    assert err.code == "DB_ERROR"


def test_provider_error():
    err = ProviderError("timeout", provider="openai")
    assert err.code == "PROVIDER_ERROR"
    assert err.provider == "openai"


def test_provider_not_configured():
    err = ProviderNotConfiguredError("openai")
    assert "not configured" in err.message
    assert err.provider == "openai"


def test_pipeline_error():
    err = PipelineError("generation failed", step="resume_gen")
    assert err.step == "resume_gen"


def test_validation_error():
    err = ValidationError("missing field")
    assert err.code == "VALIDATION_ERROR"


def test_document_error():
    err = DocumentError("OCR failed")
    assert err.code == "DOC_ERROR"


def test_security_error():
    err = SecurityError("key missing")
    assert err.code == "SECURITY_ERROR"


def test_embedding_error():
    err = EmbeddingError("model not loaded")
    assert err.code == "EMBEDDING_ERROR"
