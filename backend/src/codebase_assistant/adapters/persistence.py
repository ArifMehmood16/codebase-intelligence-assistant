"""SQLAlchemy tables for repository metadata and pgvector chunks.

Domain types stay independent of this module. Schema dimension matches
nomic-embed-text (768). A different embedding size needs a new migration.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import UserDefinedType

EMBEDDING_DIMENSIONS = 768

persistence_metadata = MetaData()


class PgVector(UserDefinedType[list[float]]):
    cache_ok = True

    def __init__(self, dim: int) -> None:
        self.dim = dim

    def get_col_spec(self, **_: object) -> str:
        return f"vector({self.dim})"


repositories = Table(
    "repositories",
    persistence_metadata,
    Column("repository_id", Text, primary_key=True),
    Column("status", Text, nullable=False),
    Column("indexed_file_count", Integer, nullable=False, server_default="0"),
    Column("ignored_file_count", Integer, nullable=False, server_default="0"),
    Column(
        "ignored_reason_counts",
        JSONB,
        nullable=False,
        server_default="'[]'::jsonb",
    ),
    Column("indexed_paths", JSONB, nullable=False, server_default="'[]'::jsonb"),
    Column(
        "repository_card",
        JSONB,
        nullable=False,
        server_default="'{}'::jsonb",
    ),
    Column("failure_code", Text, nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    CheckConstraint(
        "status IN ('pending', 'indexing', 'completed', 'failed')",
        name="repositories_status_check",
    ),
)

chunks = Table(
    "chunks",
    persistence_metadata,
    Column("chunk_id", Text, primary_key=True),
    Column(
        "repository_id",
        Text,
        ForeignKey("repositories.repository_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("file_path", Text, nullable=False),
    Column("start_line", Integer, nullable=False),
    Column("end_line", Integer, nullable=False),
    Column("language", Text, nullable=False, server_default="unknown"),
    Column("symbol", Text, nullable=True),
    Column("content_hash", Text, nullable=False, server_default=""),
    Column("body", Text, nullable=False),
    Column("embedding", PgVector(EMBEDDING_DIMENSIONS), nullable=False),
)
