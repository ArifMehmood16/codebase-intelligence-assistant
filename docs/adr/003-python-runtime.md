# ADR 003 — Python 3.14 runtime

**Status:** Accepted  
**Date:** 2026-09-04  
**Deciders:** Developer  
**Supersedes:** PLAN.md original backend runtime of Python 3.12

## Context

The initial plan pinned Python 3.12 as a conservative, widely supported FastAPI baseline. Inspection of the implementation machine found `python3` **3.14.4** and no `python` on `PATH`.

The developer approved using the newest Python runtime available on this machine rather than installing or containerising 3.12 only to match the first draft.

## Decision

The project runtime is **Python 3.14**.

- Local backend work uses the host 3.14 interpreter (observed 3.14.4).
- Phase 1 containers, `requires-python` and CI must pin Python 3.14, not 3.12.
- Patch-level drift (3.14.x) is acceptable; a major/minor change is not.

## Alternatives considered

| Alternative | Why not now |
|---|---|
| Keep Python 3.12 via pyenv or a 3.12 image only | Rejected by the developer in favour of the machine's current runtime. |
| Python 3.13 as a middle ground | Still not the approved host runtime; would add another version without a compatibility investigation. |

## Consequences

- Newer standard-library and typing behaviour is available without a later upgrade.
- Some third-party wheels, mypy plugin combinations or Docker tags may lag 3.14. Phase 1 must verify install and test on 3.14 before locking dependencies.
- Documentation that said 3.12 is updated through the PLAN.md change-control record.

## Follow-up

During Phase 1, confirm that FastAPI, Pydantic, SQLAlchemy, pytest, Ruff and mypy install and run on Python 3.14. If a required package has no viable 3.14 build, stop and propose a documented rollback rather than silently switching versions.
