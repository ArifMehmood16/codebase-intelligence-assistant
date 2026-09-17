# ADR 001 — Modular monolith

**Status:** Accepted  
**Date:** 2026-09-04  
**Deciders:** Developer

## Context

The project is a conversational code assistant. It needs clear backend boundaries, a small frontend, a datastore and model-provider substitution for tests. It also needs to stay operable by a new contributor with Docker Compose.

A distributed shape (separate ingest, retrieve and answer services) would demonstrate more moving parts than the problem requires and would make local setup, testing and failure diagnosis harder.

## Decision

Build one deployable backend as a modular monolith:

- Domain and application logic stay independent of FastAPI, SQLAlchemy and provider SDKs.
- HTTP, archive I/O, PostgreSQL/pgvector and model providers sit behind narrow ports.
- The React app is a separate frontend package that talks to an explicit HTTP contract.
- Local operation uses Docker Compose, not Kubernetes.

## Alternatives considered

| Alternative | Why not now |
|---|---|
| Microservices | Extra network, deployment and observability cost without a scaling requirement. |
| Single mixed package (routes containing business rules) | Faster to start, harder to test ingestion, retrieval and answering in isolation. |
| Next.js full-stack | Mixes UI and server concerns; the planned API contract would be less visible. |

## Consequences

- Reviewers run one API process, one web process and PostgreSQL.
- Provider fakes can replace embeddings and LLM calls without changing use cases.
- Production evolution (object storage, a queue, managed PostgreSQL) does not require splitting the modular boundaries first.
- We must keep modules honest: domain/application must not import web or ORM libraries.

## Follow-up

None until a production constraint forces a split. Any such change needs a new ADR.
