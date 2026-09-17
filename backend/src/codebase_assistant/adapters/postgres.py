from collections.abc import Mapping, Sequence
from json import dumps, loads
from typing import Any

from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Engine

from codebase_assistant.adapters.persistence import EMBEDDING_DIMENSIONS
from codebase_assistant.application.contracts import IngestArchiveResult
from codebase_assistant.application.repository_card import (
    card_from_payload,
    card_to_payload,
)
from codebase_assistant.domain import Repository, SourceChunk

_UPSERT_REPOSITORY = """
INSERT INTO repositories (
    repository_id, status, indexed_file_count, ignored_file_count,
    ignored_reason_counts, indexed_paths, failure_code, source_filename,
    repository_card, updated_at
) VALUES (
    :repository_id, :status, :indexed_file_count, :ignored_file_count,
    CAST(:ignored_reason_counts AS jsonb), CAST(:indexed_paths AS jsonb),
    :failure_code, :source_filename, CAST(:repository_card AS jsonb), now()
)
ON CONFLICT (repository_id) DO UPDATE SET
    status = EXCLUDED.status,
    indexed_file_count = EXCLUDED.indexed_file_count,
    ignored_file_count = EXCLUDED.ignored_file_count,
    ignored_reason_counts = EXCLUDED.ignored_reason_counts,
    indexed_paths = EXCLUDED.indexed_paths,
    failure_code = EXCLUDED.failure_code,
    source_filename = EXCLUDED.source_filename,
    repository_card = EXCLUDED.repository_card,
    updated_at = now()
"""


def create_db_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def as_vector_literal(values: Sequence[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def _as_list(value: object) -> list[object]:
    if isinstance(value, str):
        loaded = loads(value)
        return loaded if isinstance(loaded, list) else []
    if isinstance(value, list):
        return value
    return []


def _as_dict(value: object) -> dict[str, object]:
    if isinstance(value, str):
        loaded = loads(value)
        return loaded if isinstance(loaded, dict) else {}
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def vector_extension_name(engine: Engine) -> str | None:
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        ).scalar_one_or_none()


class PostgresWorkspace:
    """Repository-scoped chunk store. Search never crosses repository_id."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def upsert(
        self,
        repository_id: str,
        chunks: Sequence[SourceChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must align")
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO repositories (repository_id, status)
                    VALUES (:repository_id, 'indexing')
                    ON CONFLICT (repository_id) DO UPDATE SET
                        status = 'indexing',
                        updated_at = now()
                    """
                ),
                {"repository_id": repository_id},
            )
            connection.execute(
                text("DELETE FROM chunks WHERE repository_id = :repository_id"),
                {"repository_id": repository_id},
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True):
                if len(embedding) != EMBEDDING_DIMENSIONS:
                    raise ValueError(
                        f"embedding dimension must be {EMBEDDING_DIMENSIONS}"
                    )
                connection.execute(
                    text(
                        """
                        INSERT INTO chunks (
                            chunk_id, repository_id, file_path,
                            start_line, end_line, language, symbol,
                            content_hash, body, embedding
                        ) VALUES (
                            :chunk_id, :repository_id, :file_path,
                            :start_line, :end_line,
                            :language, :symbol, :content_hash, :body,
                            CAST(:embedding AS vector)
                        )
                        """
                    ),
                    {
                        "chunk_id": chunk.chunk_id,
                        "repository_id": repository_id,
                        "file_path": chunk.file_path,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "language": chunk.language,
                        "symbol": chunk.symbol,
                        "content_hash": chunk.content_hash,
                        "body": chunk.text,
                        "embedding": as_vector_literal(embedding),
                    },
                )

    def search(
        self,
        repository_id: str,
        embedding: Sequence[float],
        limit: int,
    ) -> Sequence[SourceChunk]:
        if len(embedding) != EMBEDDING_DIMENSIONS:
            raise ValueError(f"embedding dimension must be {EMBEDDING_DIMENSIONS}")
        with self._engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT chunk_id, repository_id, file_path,
                           start_line, end_line, language, symbol,
                           content_hash, body
                    FROM chunks
                    WHERE repository_id = :repository_id
                    ORDER BY embedding <=> CAST(:query AS vector)
                    LIMIT :limit
                    """
                ),
                {
                    "repository_id": repository_id,
                    "query": as_vector_literal(embedding),
                    "limit": limit,
                },
            ).mappings()
            return tuple(_chunk_from_row(row) for row in rows)

    def chunks_for_paths(
        self, repository_id: str, paths: Sequence[str]
    ) -> Sequence[SourceChunk]:
        wanted = tuple(path for path in paths if path)
        if not wanted:
            return ()
        with self._engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT chunk_id, repository_id, file_path,
                           start_line, end_line, language, symbol,
                           content_hash, body
                    FROM chunks
                    WHERE repository_id = :repository_id
                      AND file_path IN :paths
                    """
                ).bindparams(bindparam("paths", expanding=True)),
                {"repository_id": repository_id, "paths": wanted},
            ).mappings()
            found = [_chunk_from_row(row) for row in rows]
        order = {path: index for index, path in enumerate(wanted)}
        found.sort(
            key=lambda chunk: (order[chunk.file_path], chunk.start_line, chunk.chunk_id)
        )
        return tuple(found)

    def save_summary(self, result: IngestArchiveResult) -> None:
        reasons = [
            {"reason": reason, "count": count}
            for reason, count in result.ignored_reason_counts
        ]
        with self._engine.begin() as connection:
            connection.execute(
                text(_UPSERT_REPOSITORY),
                {
                    "repository_id": result.repository.repository_id,
                    "status": result.status,
                    "indexed_file_count": result.indexed_file_count,
                    "ignored_file_count": result.ignored_file_count,
                    "ignored_reason_counts": dumps(reasons),
                    "indexed_paths": dumps(list(result.indexed_paths)),
                    "failure_code": result.failure_code,
                    "source_filename": result.source_filename,
                    "repository_card": dumps(
                        card_to_payload(result.card) if result.card is not None else {}
                    ),
                },
            )

    def get_summary(self, repository_id: str) -> IngestArchiveResult | None:
        with self._engine.connect() as connection:
            row = (
                connection.execute(
                    text(
                        """
                    SELECT repository_id, status, indexed_file_count,
                           ignored_file_count, ignored_reason_counts,
                           indexed_paths, failure_code, source_filename,
                           repository_card
                    FROM repositories
                    WHERE repository_id = :repository_id
                    """
                    ),
                    {"repository_id": repository_id},
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return _row_to_summary(dict(row))

    def list_summaries(self) -> Sequence[IngestArchiveResult]:
        with self._engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT repository_id, status, indexed_file_count,
                           ignored_file_count, ignored_reason_counts,
                           indexed_paths, failure_code, source_filename,
                           repository_card
                    FROM repositories
                    ORDER BY updated_at DESC
                    """
                )
            ).mappings()
            return tuple(_row_to_summary(dict(row)) for row in rows)

    def mark_failed(self, repository_id: str, failure_code: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO repositories (
                        repository_id, status, failure_code, updated_at
                    ) VALUES (
                        :repository_id, 'failed', :failure_code, now()
                    )
                    ON CONFLICT (repository_id) DO UPDATE SET
                        status = 'failed',
                        failure_code = EXCLUDED.failure_code,
                        indexed_file_count = 0,
                        indexed_paths = CAST('[]' AS jsonb),
                        repository_card = CAST('{}' AS jsonb),
                        updated_at = now()
                    """
                ),
                {"repository_id": repository_id, "failure_code": failure_code},
            )
            connection.execute(
                text("DELETE FROM chunks WHERE repository_id = :repository_id"),
                {"repository_id": repository_id},
            )

    def delete_repository(self, repository_id: str) -> bool:
        with self._engine.begin() as connection:
            result = connection.execute(
                text("DELETE FROM repositories WHERE repository_id = :repository_id"),
                {"repository_id": repository_id},
            )
            return bool(result.rowcount)


def _chunk_from_row(row: Any) -> SourceChunk:
    start = row["start_line"]
    end = row["end_line"]
    if not isinstance(start, int) or not isinstance(end, int):
        raise TypeError("chunk line numbers must be integers")
    return SourceChunk(
        chunk_id=str(row["chunk_id"]),
        repository_id=str(row["repository_id"]),
        file_path=str(row["file_path"]),
        start_line=start,
        end_line=end,
        text=str(row["body"]),
        language=str(row["language"]),
        symbol=str(row["symbol"]) if row["symbol"] is not None else None,
        content_hash=str(row["content_hash"]),
    )


def _row_to_summary(row: Mapping[str, object]) -> IngestArchiveResult:
    reasons_raw = _as_list(row["ignored_reason_counts"])
    reasons = tuple(
        (str(item["reason"]), int(item["count"]))
        for item in reasons_raw
        if isinstance(item, dict)
    )
    paths = tuple(str(path) for path in _as_list(row["indexed_paths"]))
    filename = row.get("source_filename")
    failure = row.get("failure_code")
    indexed = row["indexed_file_count"]
    ignored = row["ignored_file_count"]
    return IngestArchiveResult(
        repository=Repository(repository_id=str(row["repository_id"])),
        indexed_file_count=int(indexed) if isinstance(indexed, (int, str)) else 0,
        ignored_file_count=int(ignored) if isinstance(ignored, (int, str)) else 0,
        ignored_reason_counts=reasons,
        indexed_paths=paths,
        status=str(row["status"]),
        failure_code=str(failure) if failure is not None else None,
        source_filename=str(filename) if filename is not None else None,
        card=card_from_payload(_as_dict(row.get("repository_card"))),
    )
