"""In-process chunk index used by tests and the short demo."""

from __future__ import annotations

import math
from collections.abc import Sequence

from codebase_assistant.application.contracts import IngestArchiveResult
from codebase_assistant.domain import Repository, SourceChunk


class InMemoryWorkspace:
    def __init__(self) -> None:
        self._chunks: dict[str, list[tuple[SourceChunk, tuple[float, ...]]]] = {}
        self._summaries: dict[str, IngestArchiveResult] = {}

    def upsert(
        self,
        repository_id: str,
        chunks: Sequence[SourceChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must align")
        self._chunks[repository_id] = [
            (chunk, tuple(vector))
            for chunk, vector in zip(chunks, embeddings, strict=True)
        ]

    def search(
        self,
        repository_id: str,
        embedding: Sequence[float],
        limit: int,
    ) -> Sequence[SourceChunk]:
        ranked = [
            (_cosine(embedding, vector), chunk)
            for chunk, vector in self._chunks.get(repository_id, ())
        ]
        ranked.sort(key=lambda item: item[0], reverse=True)
        return tuple(chunk for _score, chunk in ranked[:limit])

    def chunks_for_paths(
        self, repository_id: str, paths: Sequence[str]
    ) -> Sequence[SourceChunk]:
        wanted = [path for path in paths if path]
        if not wanted:
            return ()
        order = {path: index for index, path in enumerate(wanted)}
        found = [
            chunk
            for chunk, _vector in self._chunks.get(repository_id, ())
            if chunk.file_path in order
        ]
        found.sort(
            key=lambda chunk: (order[chunk.file_path], chunk.start_line, chunk.chunk_id)
        )
        return tuple(found)

    def save_summary(self, result: IngestArchiveResult) -> None:
        self._summaries[result.repository.repository_id] = result

    def get_summary(self, repository_id: str) -> IngestArchiveResult | None:
        return self._summaries.get(repository_id)

    def list_summaries(self) -> Sequence[IngestArchiveResult]:
        return tuple(reversed(tuple(self._summaries.values())))

    def mark_failed(self, repository_id: str, failure_code: str) -> None:
        existing = self._summaries.get(repository_id)
        self._chunks.pop(repository_id, None)
        self._summaries[repository_id] = IngestArchiveResult(
            repository=Repository(repository_id=repository_id),
            indexed_file_count=0,
            ignored_file_count=existing.ignored_file_count if existing else 0,
            ignored_reason_counts=(existing.ignored_reason_counts if existing else ()),
            indexed_paths=(),
            status="failed",
            failure_code=failure_code,
            source_filename=existing.source_filename if existing else None,
            card=existing.card if existing else None,
        )

    def delete_repository(self, repository_id: str) -> bool:
        existed = repository_id in self._summaries or repository_id in self._chunks
        self._chunks.pop(repository_id, None)
        self._summaries.pop(repository_id, None)
        return existed


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    n_left = math.sqrt(sum(a * a for a in left))
    n_right = math.sqrt(sum(b * b for b in right))
    if n_left == 0 or n_right == 0:
        return 0.0
    return dot / (n_left * n_right)
