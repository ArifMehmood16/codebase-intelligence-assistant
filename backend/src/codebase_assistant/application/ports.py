from collections.abc import Sequence
from typing import Protocol

from codebase_assistant.application.contracts import IngestArchiveResult
from codebase_assistant.domain import SourceChunk, SourceFile


class ReadIndexedFiles(Protocol):
    def read_files(self, repository_id: str) -> Sequence[SourceFile]: ...


class EmbedTexts(Protocol):
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...


class PersistChunks(Protocol):
    def upsert(
        self,
        repository_id: str,
        chunks: Sequence[SourceChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None: ...


class SearchChunks(Protocol):
    def search(
        self,
        repository_id: str,
        embedding: Sequence[float],
        limit: int,
    ) -> Sequence[SourceChunk]: ...


class LoadPinnedChunks(Protocol):
    def get_summary(self, repository_id: str) -> IngestArchiveResult | None: ...

    def chunks_for_paths(
        self, repository_id: str, paths: Sequence[str]
    ) -> Sequence[SourceChunk]: ...


class CompleteAnswer(Protocol):
    def complete(self, prompt: str) -> str: ...


class IngestionStore(PersistChunks, SearchChunks, LoadPinnedChunks, Protocol):
    def save_summary(self, result: IngestArchiveResult) -> None: ...

    def get_summary(self, repository_id: str) -> IngestArchiveResult | None: ...

    def list_summaries(self) -> Sequence[IngestArchiveResult]: ...

    def mark_failed(self, repository_id: str, failure_code: str) -> None: ...

    def delete_repository(self, repository_id: str) -> bool: ...
