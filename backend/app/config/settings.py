"""Application settings loaded from environment and config files."""

import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR.parent / "config"


def _load_default_config() -> dict:
    """Load default.json from the config directory."""
    default_path = CONFIG_DIR / "default.json"
    if default_path.exists():
        return json.loads(default_path.read_text(encoding="utf-8"))
    return {}


class Settings(BaseSettings):
    """CareerForge AI settings — populated from env vars and config/default.json."""

    # App
    app_name: str = "CareerForge AI"
    app_version: str = "0.1.0"
    debug: bool = Field(default=True, alias="APP_DEBUG")
    data_dir: str = Field(default="~/.careerforge", alias="DATA_DIR")

    # API
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # AI Provider
    ai_provider: str = Field(default="openai", alias="AI_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", alias="ANTHROPIC_MODEL")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="anthropic/claude-sonnet-4", alias="OPENROUTER_MODEL")
    grok_api_key: str = Field(default="", alias="GROK_API_KEY")
    grok_model: str = Field(default="grok-2", alias="GROK_MODEL")
    huggingface_api_key: str = Field(default="", alias="HUGGINGFACE_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///data/careerforge.db", alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # LanceDB
    lancedb_path: str = Field(default="./vector_store", alias="LANCEDB_PATH")

    # Embeddings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=384, alias="EMBEDDING_DIMENSIONS")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/careerforge.log", alias="LOG_FILE")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def resolved_data_dir(self) -> Path:
        return Path(self.data_dir).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
