from codebase_assistant.adapters.persistence import persistence_metadata

EMBEDDING_DIMENSIONS = 768


def test_persistence_schema_owns_chunks_by_repository() -> None:
    repositories = persistence_metadata.tables["repositories"]
    chunks = persistence_metadata.tables["chunks"]

    assert repositories.c.repository_id.primary_key
    assert repositories.c.status is not None
    assert chunks.c.chunk_id.primary_key
    assert chunks.c.embedding.type.dim == EMBEDDING_DIMENSIONS

    fks = list(chunks.c.repository_id.foreign_keys)
    assert len(fks) == 1
    assert fks[0].column.table.name == "repositories"
    assert fks[0].ondelete == "CASCADE"


def test_pgvector_column_renders_fixed_dimension() -> None:
    from codebase_assistant.adapters.persistence import PgVector

    assert PgVector(768).get_col_spec() == "vector(768)"
