"""Store extractive repository card JSON on repositories.

Revision ID: 004_repository_card
Revises: 003_repository_source_filename
"""

from collections.abc import Sequence

from alembic import op

revision: str = "004_repository_card"
down_revision: str | None = "003_repository_source_filename"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE repositories
        ADD COLUMN IF NOT EXISTS repository_card JSONB NOT NULL DEFAULT '{}'::jsonb
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE repositories DROP COLUMN IF EXISTS repository_card")
