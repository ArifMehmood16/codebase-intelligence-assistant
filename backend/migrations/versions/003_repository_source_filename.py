"""Add source_filename to repositories.

Revision ID: 003_repository_source_filename
Revises: 002_repository_chunks
"""

from collections.abc import Sequence

from alembic import op

revision: str = "003_repository_source_filename"
down_revision: str | None = "002_repository_chunks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE repositories
        ADD COLUMN IF NOT EXISTS source_filename TEXT
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE repositories DROP COLUMN IF EXISTS source_filename")
