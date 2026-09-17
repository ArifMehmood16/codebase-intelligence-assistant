from collections.abc import Sequence

from codebase_assistant.application.ports import (
    CompleteAnswer,
    EmbedTexts,
    PersistChunks,
    ReadIndexedFiles,
    SearchChunks,
)
from codebase_assistant.domain import SourceChunk, SourceFile


class FakeReadIndexedFiles:
    def read_files(self, repository_id: str) -> Sequence[SourceFile]:
        return (SourceFile(path=f"{repository_id}/app.py", content="x = 1\n"),)


class FakeEmbedTexts:
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        return tuple((float(len(text)),) for text in texts)


class FakePersistChunks:
    def __init__(self) -> None:
        self.stored: list[tuple[str, tuple[SourceChunk, ...]]] = []

    def upsert(
        self,
        repository_id: str,
        chunks: Sequence[SourceChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must align")
        self.stored.append((repository_id, tuple(chunks)))


class FakeSearchChunks:
    def __init__(self, hits: Sequence[SourceChunk]) -> None:
        self._hits = tuple(hits)

    def search(
        self,
        repository_id: str,
        embedding: Sequence[float],
        limit: int,
    ) -> Sequence[SourceChunk]:
        del repository_id, embedding
        return self._hits[:limit]


class FakeCompleteAnswer:
    def complete(self, prompt: str) -> str:
        return f"echo:{len(prompt)}"


def test_read_indexed_files_fake_returns_source_files() -> None:
    port: ReadIndexedFiles = FakeReadIndexedFiles()
    files = port.read_files("repo-1")
    assert files[0].path == "repo-1/app.py"


def test_embed_texts_fake_returns_one_vector_per_text() -> None:
    port: EmbedTexts = FakeEmbedTexts()
    assert port.embed(["a", "bb"]) == ((1.0,), (2.0,))


def test_persist_chunks_fake_keeps_repository_scope() -> None:
    port = FakePersistChunks()
    chunk = SourceChunk(
        chunk_id="c1",
        repository_id="repo-1",
        file_path="app.py",
        start_line=1,
        end_line=1,
        text="x = 1",
    )
    typed: PersistChunks = port
    typed.upsert("repo-1", (chunk,), ((0.1,),))
    assert port.stored[0][0] == "repo-1"


def test_search_chunks_fake_respects_limit() -> None:
    chunks = tuple(
        SourceChunk(
            chunk_id=f"c{i}",
            repository_id="repo-1",
            file_path="app.py",
            start_line=i,
            end_line=i,
            text=str(i),
        )
        for i in range(1, 4)
    )
    port: SearchChunks = FakeSearchChunks(chunks)
    assert len(port.search("repo-1", (0.0,), 2)) == 2


def test_complete_answer_fake_returns_text() -> None:
    port: CompleteAnswer = FakeCompleteAnswer()
    assert port.complete("hello").startswith("echo:")
