"""Compose backend must receive the same provider and archive settings as app.env."""

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_COMPOSE = (_REPO_ROOT / "compose.yaml").read_text(encoding="utf-8")


def _backend_environment_block() -> str:
    start = _COMPOSE.index("  backend:")
    rest = _COMPOSE[start:]
    env_start = rest.index("    environment:")
    after_env = rest[env_start:]
    # Next top-level key under backend after environment is usually ports.
    end = after_env.index("\n    ports:")
    return after_env[:end]


def test_compose_backend_passes_embedding_provider_and_timeouts() -> None:
    block = _backend_environment_block()
    assert "EMBEDDING_PROVIDER:" in block
    assert "COMPLETION_PROVIDER:" in block
    assert "OLLAMA_TIMEOUT_SECONDS:" in block
    assert "OLLAMA_EMBED_BATCH_SIZE:" in block
    assert "LLM_MAX_RETRIES:" in block


def test_compose_backend_passes_answer_limits() -> None:
    block = _backend_environment_block()
    assert "MAX_QUESTION_CHARS:" in block
    assert "MAX_CONTEXT_CHARS:" in block
    assert "MAX_EXCERPT_CHARS:" in block


def test_compose_backend_passes_archive_limits() -> None:
    block = _backend_environment_block()
    assert "MAX_ARCHIVE_BYTES:" in block
    assert "MAX_ARCHIVE_FILE_COUNT:" in block
    assert "MAX_ARCHIVE_FILE_BYTES:" in block
    assert "MAX_ARCHIVE_EXTRACTED_BYTES:" in block
    assert "MAX_ARCHIVE_COMPRESSION_RATIO:" in block
