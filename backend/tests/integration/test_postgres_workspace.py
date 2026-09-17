from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from codebase_assistant.adapters.persistence import EMBEDDING_DIMENSIONS
from codebase_assistant.adapters.postgres import PostgresWorkspace, create_db_engine
from codebase_assistant.application.contracts import IngestArchiveResult
from codebase_assistant.application.repository_card import RepositoryCard
from codebase_assistant.config import load_settings
from codebase_assistant.domain import Repository, SourceChunk


def _axis(index: int) -> tuple[float, ...]:
    values = [0.0] * EMBEDDING_DIMENSIONS
    values[index] = 1.0
    return tuple(values)


def _chunk(repository_id: str, path: str, token: str) -> SourceChunk:
    return SourceChunk(
        chunk_id=f"{repository_id}:{path}",
        repository_id=repository_id,
        file_path=path,
        start_line=1,
        end_line=1,
        text=token,
        language="python",
        content_hash=token,
    )


@pytest.mark.integration
def test_postgres_workspace_search_is_repository_scoped() -> None:
    url = load_settings().postgres_url()
    assert url is not None
    engine = create_db_engine(url)
    store = PostgresWorkspace(engine)
    repo_a = str(uuid4())
    repo_b = str(uuid4())
    chunk_a = _chunk(repo_a, "a.py", "alpha")
    chunk_b = _chunk(repo_b, "b.py", "beta")
    try:
        store.upsert(repo_a, [chunk_a], [_axis(0)])
        store.upsert(repo_b, [chunk_b], [_axis(1)])
        store.save_summary(
            IngestArchiveResult(
                repository=Repository(repository_id=repo_a),
                indexed_file_count=1,
                ignored_file_count=0,
                indexed_paths=("a.py",),
                card=RepositoryCard(
                    display_name="alpha",
                    outline_paths=("a.py",),
                    languages=(("python", 1),),
                ),
            )
        )
        found = store.search(repo_a, _axis(0), limit=5)
        assert [chunk.file_path for chunk in found] == ["a.py"]
        summary_a = store.get_summary(repo_a)
        summary_b = store.get_summary(repo_b)
        assert summary_a is not None
        assert summary_a.status == "completed"
        assert summary_a.card is not None
        assert summary_a.card.display_name == "alpha"
        assert summary_a.card.outline_paths == ("a.py",)
        assert summary_b is not None
        assert summary_b.status == "indexing"
    finally:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM repositories WHERE repository_id IN (:a, :b)"),
                {"a": repo_a, "b": repo_b},
            )


@pytest.mark.integration
def test_postgres_workspace_reingest_replaces_chunks() -> None:
    url = load_settings().postgres_url()
    assert url is not None
    engine = create_db_engine(url)
    store = PostgresWorkspace(engine)
    repo_id = str(uuid4())
    first = _chunk(repo_id, "old.py", "old")
    second = _chunk(repo_id, "new.py", "new")
    try:
        store.upsert(repo_id, [first], [_axis(2)])
        store.upsert(repo_id, [second], [_axis(3)])
        found = store.search(repo_id, _axis(3), limit=5)
        assert [chunk.file_path for chunk in found] == ["new.py"]
    finally:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM repositories WHERE repository_id = :id"),
                {"id": repo_id},
            )
