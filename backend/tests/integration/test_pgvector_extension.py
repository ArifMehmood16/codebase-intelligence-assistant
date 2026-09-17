"""PostgreSQL has the pgvector extension after migrations."""

from __future__ import annotations

import pytest
from sqlalchemy import text

from codebase_assistant.adapters.postgres import create_db_engine, vector_extension_name
from codebase_assistant.config import load_settings


@pytest.mark.integration
def test_vector_extension_is_available() -> None:
    settings = load_settings()
    url = settings.postgres_url()
    assert url is not None
    engine = create_db_engine(url)
    assert vector_extension_name(engine) == "vector"


@pytest.mark.integration
def test_migration_creates_repository_owned_chunks() -> None:
    settings = load_settings()
    url = settings.postgres_url()
    assert url is not None
    engine = create_db_engine(url)
    with engine.connect() as connection:
        tables = set(
            connection.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            ).scalars()
        )
        assert "repositories" in tables
        assert "chunks" in tables
        embedding_type = connection.execute(
            text(
                """
                SELECT format_type(a.atttypid, a.atttypmod)
                FROM pg_attribute AS a
                JOIN pg_class AS c ON a.attrelid = c.oid
                WHERE c.relname = 'chunks' AND a.attname = 'embedding'
                """
            )
        ).scalar_one()
        assert embedding_type == "vector(768)"
        delete_action = connection.execute(
            text(
                """
                SELECT confdeltype
                FROM pg_constraint
                WHERE conrelid = 'chunks'::regclass
                  AND contype = 'f'
                """
            )
        ).scalar_one()
        assert delete_action == "c"
