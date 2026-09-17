"""Ingest an archive, then answer only from retrieved and verified citations."""

import io
import zipfile

from codebase_assistant.adapters.extractive import ExtractiveCompleter
from codebase_assistant.adapters.lexical import LexicalEmbedder
from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.application.ask import ask_question
from codebase_assistant.application.contracts import (
    AskQuestionRequest,
    IngestArchiveRequest,
)
from codebase_assistant.application.errors import EmbeddingError
from codebase_assistant.application.ingest import ingest_archive
from codebase_assistant.chunking import ChunkingLimits
from codebase_assistant.ingestion.limits import ArchiveLimits

_LIMITS = ArchiveLimits(max_upload_bytes=1024 * 1024)
_CHUNKS = ChunkingLimits(max_lines=40, overlap_lines=0)


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def test_ingest_indexes_source_and_omits_secrets() -> None:
    workspace = InMemoryWorkspace()
    result = ingest_archive(
        IngestArchiveRequest(
            filename="repo.zip",
            content=_zip_bytes(
                {
                    "src/app.py": b"def greet():\n    return 'hello'\n",
                    "config/.env": b"SECRET=super-secret\n",
                }
            ),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=LexicalEmbedder(),
        store=workspace,
    )
    assert result.indexed_file_count == 1
    assert result.ignored_file_count == 1
    assert result.indexed_paths == ("src/app.py",)
    assert result.ignored_reason_counts == (("secret_file", 1),)
    assert "super-secret" not in repr(result)


def test_ingest_attaches_extractive_repository_card() -> None:
    workspace = InMemoryWorkspace()
    result = ingest_archive(
        IngestArchiveRequest(
            filename="inventory.zip",
            content=_zip_bytes(
                {
                    "README.md": b"# Inventory service\nStores stock items.\n",
                    "src/api/handlers.py": b"def list_items():\n    return []\n",
                    "package.json": (
                        b'{"name":"inventory-web","description":"Stock UI",'
                        b'"dependencies":{"react":"18.2.0"}}\n'
                    ),
                }
            ),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=LexicalEmbedder(),
        store=workspace,
    )
    card = result.card
    assert card is not None
    assert card.display_name == "inventory"
    assert card.readme_path == "README.md"
    assert "inventory" in card.readme_excerpt.lower()
    assert "src/api/handlers.py" in card.outline_paths
    assert card.manifest_name == "inventory-web"
    stored = workspace.get_summary(result.repository.repository_id)
    assert stored is not None
    assert stored.card == card


def test_ask_returns_verified_citation_from_retrieved_source() -> None:
    workspace = InMemoryWorkspace()
    embed = LexicalEmbedder()
    ingested = ingest_archive(
        IngestArchiveRequest(
            filename="repo.zip",
            content=_zip_bytes({"src/app.py": b"def greet():\n    return 'hello'\n"}),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=embed,
        store=workspace,
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="Where is greet defined?",
        ),
        embed=embed,
        search=workspace,
        complete=ExtractiveCompleter(),
    )
    assert answer.answer.insufficient_evidence is False
    citation = answer.answer.citations[0]
    assert citation.file_path == "src/app.py"
    assert "greet" in answer.answer.text


def test_failed_embedding_does_not_mark_ingest_completed() -> None:
    workspace = InMemoryWorkspace()

    class BoomEmbedder:
        def embed(self, texts: object) -> object:
            raise EmbeddingError("embedding provider timed out")

    result = ingest_archive(
        IngestArchiveRequest(
            filename="repo.zip",
            content=_zip_bytes({"src/app.py": b"def greet():\n    return 'hello'\n"}),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=BoomEmbedder(),
        store=workspace,
    )
    assert result.status == "failed"
    stored = workspace.get_summary(result.repository.repository_id)
    assert stored is not None
    assert stored.status == "failed"
    assert stored.failure_code == "embedding_failed"
    assert workspace.search(result.repository.repository_id, (0.0,), 5) == ()


def test_reingest_same_repository_name_replaces_previous() -> None:
    workspace = InMemoryWorkspace()
    first = ingest_archive(
        IngestArchiveRequest(
            filename="demo.zip",
            content=_zip_bytes({"src/old.py": b"def old():\n    return 1\n"}),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=LexicalEmbedder(),
        store=workspace,
    )
    second = ingest_archive(
        IngestArchiveRequest(
            filename="Demo.ZIP",
            content=_zip_bytes({"src/new.py": b"def new():\n    return 2\n"}),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=LexicalEmbedder(),
        store=workspace,
    )
    listed = workspace.list_summaries()
    assert len(listed) == 1
    assert listed[0].repository.repository_id == second.repository.repository_id
    assert listed[0].indexed_paths == ("src/new.py",)
    assert listed[0].card is not None
    assert listed[0].card.outline_paths == ("src/new.py",)
    assert "src/old.py" not in listed[0].card.outline_paths
    assert workspace.get_summary(first.repository.repository_id) is None
    assert workspace.search(first.repository.repository_id, (0.0,), 5) == ()


def test_ask_without_evidence_does_not_fabricate_citations() -> None:
    workspace = InMemoryWorkspace()
    embed = LexicalEmbedder()
    ingested = ingest_archive(
        IngestArchiveRequest(
            filename="repo.zip",
            content=_zip_bytes({"readme.md": b"unrelated notes\n"}),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=embed,
        store=workspace,
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="How does authentication work?",
        ),
        embed=embed,
        search=workspace,
        complete=ExtractiveCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()
