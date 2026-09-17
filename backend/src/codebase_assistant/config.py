"""Runtime settings loaded at the composition root. Domain code must not import this."""

from pathlib import Path
from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]
_APP_ENV = _REPO_ROOT / "config" / "app.env"
_DOTENV = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=tuple(path for path in (_APP_ENV, _DOTENV) if path.is_file()),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str | None = None
    database_user: str | None = None
    database_password: str | None = None
    database_name: str | None = None
    database_host: str = "localhost"
    database_port: int = 5432
    cors_allow_origin: str = "http://localhost:3000"
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_chat_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"
    ollama_timeout_seconds: float = 30.0
    ollama_embed_batch_size: int = 16
    embedding_provider: str = "lexical"
    completion_provider: str = "extractive"
    llm_temperature: float = 0.0
    llm_max_output_tokens: int = 1024
    llm_max_retries: int = 2
    max_question_chars: int = 2_000
    max_context_chars: int = 12_000
    max_excerpt_chars: int = 2_000
    max_archive_bytes: int = 10_485_760
    max_archive_file_count: int = 500
    max_archive_file_bytes: int = 1_048_576
    max_archive_extracted_bytes: int = 20_971_520
    max_archive_compression_ratio: float = 100.0

    def postgres_url(self) -> str | None:
        if self.database_url:
            return self.database_url
        if self.database_user and self.database_name:
            user = quote(self.database_user, safe="")
            password = quote(self.database_password or "", safe="")
            return (
                "postgresql+psycopg://"
                f"{user}:{password}@{self.database_host}:{self.database_port}"
                f"/{self.database_name}"
            )
        return None


def load_settings() -> Settings:
    return Settings()
