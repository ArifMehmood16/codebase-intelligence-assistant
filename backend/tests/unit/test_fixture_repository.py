"""Controlled fixture repository used by Phase 9 evaluation and demos."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from codebase_assistant.adapters.lexical import LexicalEmbedder
from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.application.contracts import IngestArchiveRequest
from codebase_assistant.application.ingest import ingest_archive
from codebase_assistant.chunking import ChunkingLimits
from codebase_assistant.ingestion.limits import ArchiveLimits

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FIXTURE_ROOT = _REPO_ROOT / "sample-data" / "fixture-repository"

_REQUIRED_RELATIVE_PATHS = (
    "README.md",
    "pyproject.toml",
    "config/settings.toml",
    "src/api/handlers.py",
    "src/api/ItemController.py",
    "src/services/inventory.py",
    "src/models/item.py",
    "docs/architecture.md",
    "scripts/seed_demo_data.py",
    "config/credentials.json",
    "vendor/leftpad.js",
)

_EXPECTED_INDEXED = frozenset(
    {
        "README.md",
        "pyproject.toml",
        "config/settings.toml",
        "src/api/handlers.py",
        "src/api/ItemController.py",
        "src/services/inventory.py",
        "src/models/item.py",
        "docs/architecture.md",
        "scripts/seed_demo_data.py",
    }
)


def _zip_fixture() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for path in sorted(_FIXTURE_ROOT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(_FIXTURE_ROOT).as_posix())
    return buffer.getvalue()


def test_fixture_repository_contains_required_layout() -> None:
    assert _FIXTURE_ROOT.is_dir(), "sample-data/fixture-repository must exist"
    missing = [
        relative
        for relative in _REQUIRED_RELATIVE_PATHS
        if not (_FIXTURE_ROOT / relative).is_file()
    ]
    assert missing == [], f"missing fixture files: {missing}"


def test_fixture_repository_has_no_real_secrets_or_proprietary_markers() -> None:
    forbidden = ("BEGIN PRIVATE KEY", "sk-proj-", "AKIA", "ghp_", "xoxb-")
    for path in _FIXTURE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        assert "copyright" not in lower or "fixture" in lower
        for token in forbidden:
            assert token not in text


def test_ingesting_fixture_indexes_sources_and_ignores_noise() -> None:
    result = ingest_archive(
        IngestArchiveRequest(filename="fixture-repository.zip", content=_zip_fixture()),
        archive_limits=ArchiveLimits(max_upload_bytes=2_000_000),
        chunk_limits=ChunkingLimits(max_lines=40, overlap_lines=0),
        embed=LexicalEmbedder(),
        store=InMemoryWorkspace(),
    )
    indexed = frozenset(result.indexed_paths)
    assert _EXPECTED_INDEXED <= indexed
    assert "config/credentials.json" not in indexed
    assert "vendor/leftpad.js" not in indexed
    reasons = dict(result.ignored_reason_counts)
    assert reasons.get("secret_file", 0) >= 1
    assert reasons.get("excluded_directory", 0) >= 1
    assert result.card is not None
    assert result.card.readme_path == "README.md"
    assert "src/api/handlers.py" in result.card.outline_paths
    assert "config/credentials.json" not in result.card.outline_paths
    assert "Placeholder credentials file" not in repr(result)
