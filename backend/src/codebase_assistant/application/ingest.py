"""Ingest an admitted archive into chunked, embedded repository state."""

from __future__ import annotations

from uuid import uuid4

from codebase_assistant.application.contracts import (
    IngestArchiveRequest,
    IngestArchiveResult,
)
from codebase_assistant.application.errors import EmbeddingError
from codebase_assistant.application.ports import EmbedTexts, IngestionStore
from codebase_assistant.application.repository_card import build_repository_card
from codebase_assistant.chunking import ChunkingLimits, chunk_source_file
from codebase_assistant.domain import Repository, SourceChunk, SourceFile
from codebase_assistant.ingestion.limits import ArchiveLimits
from codebase_assistant.ingestion.summary import summarise_archive


def repository_name_key(source_filename: str | None) -> str | None:
    """Stable unique key for a repository display name (ZIP suffix ignored)."""
    if source_filename is None:
        return None
    name = source_filename.strip()
    if not name:
        return None
    if name.lower().endswith(".zip"):
        name = name[:-4]
    name = name.strip()
    return name.casefold() if name else None


def ingest_archive(
    request: IngestArchiveRequest,
    *,
    archive_limits: ArchiveLimits,
    chunk_limits: ChunkingLimits,
    embed: EmbedTexts,
    store: IngestionStore,
) -> IngestArchiveResult:
    summary = summarise_archive(request.content, request.filename, archive_limits)
    _delete_same_named_repositories(store, request.filename)
    repository_id = str(uuid4())
    card = build_repository_card(
        tuple((member.relative_path, member.text) for member in summary.accepted),
        source_filename=request.filename,
    )
    chunks: list[SourceChunk] = []
    for member in summary.accepted:
        chunks.extend(
            chunk_source_file(
                repository_id,
                SourceFile(path=member.relative_path, content=member.text),
                chunk_limits,
            )
        )
    try:
        embeddings: tuple[tuple[float, ...], ...] = ()
        if chunks:
            vectors = embed.embed([chunk.text for chunk in chunks])
            embeddings = tuple(tuple(vector) for vector in vectors)
        store.upsert(repository_id, chunks, embeddings)
    except EmbeddingError:
        failed = IngestArchiveResult(
            repository=Repository(repository_id=repository_id),
            indexed_file_count=0,
            ignored_file_count=summary.ignored_file_count,
            ignored_reason_counts=summary.ignored_reason_counts,
            indexed_paths=(),
            status="failed",
            failure_code="embedding_failed",
            source_filename=request.filename,
            card=card,
        )
        store.mark_failed(repository_id, "embedding_failed")
        # Preserve upload name on the stored failed summary.
        store.save_summary(failed)
        return failed
    result = IngestArchiveResult(
        repository=Repository(repository_id=repository_id),
        indexed_file_count=summary.indexed_file_count,
        ignored_file_count=summary.ignored_file_count,
        ignored_reason_counts=summary.ignored_reason_counts,
        indexed_paths=tuple(member.relative_path for member in summary.accepted),
        status="completed",
        source_filename=request.filename,
        card=card,
    )
    store.save_summary(result)
    return result


def _delete_same_named_repositories(store: IngestionStore, filename: str) -> None:
    key = repository_name_key(filename)
    if key is None:
        return
    for existing in tuple(store.list_summaries()):
        if repository_name_key(existing.source_filename) == key:
            store.delete_repository(existing.repository.repository_id)
