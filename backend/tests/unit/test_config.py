import pytest

from codebase_assistant.config import load_settings


def test_load_settings_reads_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://codebase:codebase@localhost:5432/codebase",
    )
    settings = load_settings()
    assert settings.database_url is not None
    assert settings.database_url.endswith("/codebase")
    assert settings.postgres_url() is not None


def test_load_settings_builds_url_from_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("DATABASE_USER", "alice")
    monkeypatch.setenv("DATABASE_PASSWORD", "p@ss")
    monkeypatch.setenv("DATABASE_NAME", "codebase")
    monkeypatch.setenv("DATABASE_HOST", "db.example")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    settings = load_settings()
    assert (
        settings.postgres_url()
        == "postgresql+psycopg://alice:p%40ss@db.example:5432/codebase"
    )


def test_load_settings_reads_llm_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://codebase:codebase@localhost:5433/codebase",
    )
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    monkeypatch.setenv("OLLAMA_CHAT_MODEL", "llama3.2")
    monkeypatch.setenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("LLM_MAX_OUTPUT_TOKENS", "512")
    monkeypatch.setenv("COMPLETION_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MAX_RETRIES", "3")
    monkeypatch.setenv("MAX_QUESTION_CHARS", "100")
    monkeypatch.setenv("MAX_CONTEXT_CHARS", "500")
    monkeypatch.setenv("MAX_EXCERPT_CHARS", "50")
    monkeypatch.setenv("MAX_ARCHIVE_BYTES", "2048")
    monkeypatch.setenv("MAX_ARCHIVE_FILE_COUNT", "10")
    settings = load_settings()
    assert settings.ollama_host == "http://127.0.0.1:11434"
    assert settings.ollama_chat_model == "llama3.2"
    assert settings.ollama_embed_model == "nomic-embed-text"
    assert settings.ollama_timeout_seconds == 30.0
    assert settings.ollama_embed_batch_size == 16
    assert settings.completion_provider == "ollama"
    assert settings.llm_temperature == 0.2
    assert settings.llm_max_output_tokens == 512
    assert settings.llm_max_retries == 3
    assert settings.max_question_chars == 100
    assert settings.max_context_chars == 500
    assert settings.max_excerpt_chars == 50
    assert settings.max_archive_bytes == 2048
    assert settings.max_archive_file_count == 10
