"""Create repository and chunk tables with cascade ownership.

Revision ID: 002_repository_chunks
Revises: 001_enable_pgvector
"""

from collections.abc import Sequence

from alembic import op

revision: str = "002_repository_chunks"
down_revision: str | None = "001_enable_pgvector"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE repositories (
            repository_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            indexed_file_count INTEGER NOT NULL DEFAULT 0,
            ignored_file_count INTEGER NOT NULL DEFAULT 0,
            ignored_reason_counts JSONB NOT NULL DEFAULT '[]'::jsonb,
            indexed_paths JSONB NOT NULL DEFAULT '[]'::jsonb,
            failure_code TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT repositories_status_check
                CHECK (status IN ('pending', 'indexing', 'completed', 'failed'))
        )
        """
    )
    op.execute(
        """
        CREATE TABLE chunks (
            chunk_id TEXT PRIMARY KEY,
            repository_id TEXT NOT NULL
                REFERENCES repositories (repository_id) ON DELETE CASCADE,
            file_path TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            language TEXT NOT NULL DEFAULT 'unknown',
            symbol TEXT,
            content_hash TEXT NOT NULL DEFAULT '',
            body TEXT NOT NULL,
            embedding vector(768) NOT NULL
        )
        """
    )
    op.execute("CREATE INDEX ix_chunks_repository_id ON chunks (repository_id)")
    op.execute(
        """
        CREATE INDEX chunks_embedding_cosine_idx
        ON chunks USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS chunks")
    op.execute("DROP TABLE IF EXISTS repositories")
