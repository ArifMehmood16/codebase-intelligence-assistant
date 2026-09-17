from unittest.mock import MagicMock

from codebase_assistant.adapters.postgres import (
    as_vector_literal,
    create_db_engine,
    vector_extension_name,
)


def test_vector_extension_name_reads_pg_extension() -> None:
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    connection.execute.return_value.scalar_one_or_none.return_value = "vector"

    assert vector_extension_name(engine) == "vector"


def test_create_db_engine_uses_psycopg_url() -> None:
    engine = create_db_engine(
        "postgresql+psycopg://codebase:codebase@localhost:5432/codebase"
    )
    assert engine.url.drivername == "postgresql+psycopg"


def test_vector_literal_is_pgvector_text() -> None:
    assert as_vector_literal((1.0, 2.5, 0.0)) == "[1.0,2.5,0.0]"
