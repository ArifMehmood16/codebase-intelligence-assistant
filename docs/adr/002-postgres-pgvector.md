# ADR 002 — PostgreSQL with pgvector

**Status:** Accepted  
**Date:** 2026-09-04  
**Deciders:** Developer

## Context

Ingestion stores repository metadata, chunk text, line ranges and embeddings. Question answering must retrieve only chunks that belong to the uploaded repository. The project should avoid an extra datastore unless it buys a clear operational or quality advantage.

## Decision

Use PostgreSQL 16 with the pgvector extension as the single application datastore:

- Relational tables hold repository status, chunk metadata and ownership.
- Vector similarity search runs in the same database, always filtered by repository ID.
- Schema changes go through Alembic.
- Local PostgreSQL is provided by Docker Compose.

The embedding model remains a configuration value and is recorded separately when Phase 5 selects a concrete provider.

## Alternatives considered

| Alternative | Why not now |
|---|---|
| Dedicated vector database (Qdrant, Pinecone, Weaviate) | Another service to run, back up and isolate; metadata would still need PostgreSQL or equivalent. |
| SQLite plus files on disk | Weak concurrent access, weaker vector support, and a poorer production story. |
| In-memory index only | Not durable across process restart and unsuitable for a reviewer demo. |

## Consequences

- One Compose service covers metadata and retrieval.
- Integration tests can prove the vector extension and repository isolation together.
- Operators can use managed PostgreSQL later without changing the application ports.
- Hybrid lexical search is not included initially; adding it would be an evaluation-driven change, not a datastore replacement.

## Follow-up

Embedding dimension for the first persistence schema is **768**, matching the default Ollama model `nomic-embed-text`. Chunk rows use `vector(768)` and cosine HNSW. A different embedding size needs a new Alembic revision. Do not add a second vector store without a new ADR.
