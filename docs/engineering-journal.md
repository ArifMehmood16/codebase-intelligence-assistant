# Engineering journal

Observed commands, baselines and checkpoint outcomes. Entries are factual; unobserved results are not recorded.

## Phase 0 — Repository baseline (2026-09-04)

### Scope

Inspect the supplied starter repository without changing it, then record the baseline. Governance documents (`README.md`, `AGENTS.md`, `PLAN.md`, `AI_DEVELOPMENT_LOG.md`) were already present from task 0.2.

### Git

Commands:

```bash
git status
git branch --show-current
git log --oneline -10
```

Observed:

- Branch: `main`, tracking `origin/main`, working tree clean.
- Original remote: removed during public-repository sanitization.
- History:
  - `2a12606` `docs: establish project architecture and delivery plan` (2026-09-04)
  - Earlier starter commits: source identity and brief details removed during public-repository sanitization.

`2a12606` replaced the starter README and added the four governance files.

### Tracked files at inspection

Command: `find . -maxdepth 3 -type f ! -path './.git/*' | sort`

Observed:

```text
./AGENTS.md
./AI_DEVELOPMENT_LOG.md
./PLAN.md
./README.md
```

Absent at inspection: `backend/`, `frontend/`, `docs/`, `e2e/`, `sample-data/`, `.github/`, `Makefile`, `compose.yaml`, `.env.example`, `.gitignore`, lockfiles, Dockerfiles and CI.

The original starter material was removed during public-repository sanitization because it contained source-specific instructions and a private URL.

### Repository-provided checks

There is no project Makefile, `package.json`, `pyproject.toml` or Compose file. Documented README commands and common fallbacks were run as written:

| Command | Exit | Observed |
|---|---|---|
| `cp .env.example .env` | 1 | `cp: .env.example: No such file or directory` |
| `make setup` | 2 | `No rule to make target 'setup'` |
| `make test` | 2 | `No rule to make target 'test'` |
| `make run` | 2 | `No rule to make target 'run'` |
| `make -n` | 2 | `No targets specified and no makefile found` |
| `npm test` | 254 | `ENOENT` opening `package.json` |
| `pytest` | 5 | Host pytest 9.1.1 collected 0 items; `no tests ran` |
| `docker compose config` | 1 | `no configuration file provided: not found` |

These are missing-tooling outcomes, not application defects. They must not be mixed with later Phase 1 failures.

### Host toolchain (not part of the repository)

Observed on the implementation machine during inspection:

| Tool | Version |
|---|---|
| `python3` | 3.14.4 (`python` not found) |
| Node.js | v24.14.1 |
| npm | 11.11.0 |
| Docker | 29.7.2 |
| Docker Compose | v5.4.0 |
| GNU Make | 3.81 |
| Git | 2.50.1 (Apple Git-155) |
| ruff | 0.16.5 |
| mypy | 2.3.1 |
| uv / poetry | not found |
| pytest (global) | 9.1.1 |

### Initial product constraints

The initial brief did not prescribe a language, framework, database or model. The planned MVP uses ZIP upload only and treats GitHub cloning/OAuth as an explicit non-goal. That is a scope cut, not a stack conflict.

The project prioritises a solid, well-engineered basic solution over unnecessary complexity and keeps a human README voice.

### Conflicts with the original plan

- No existing application stack to reconcile; FastAPI / React / PostgreSQL+pgvector are unconstrained by prior code.
- README quick-start commands are aspirational until Phase 1.
- Planned backend runtime was Python 3.12; the host interpreter is 3.14.4. The developer approved using the newest Python on this machine. See the change-control record and `docs/adr/003-python-runtime.md`.
- Task 0.2 was completed before this inspection.

### Phase 0 artefacts after approval

Developer approval on 2026-09-04:

- Write this journal (task 0.1).
- Add `docs/` and `.gitignore` only; do not add empty `backend/` or `frontend/` packages (task 0.3).
- Record ADRs 001 and 002 (task 0.4).
- Use Python 3.14 as the project runtime.

`docs/threat-model.md` and `docs/evaluation.md` are still omitted until those documents have content.

### Residual risks

- Some third-party wheels or type checkers may lag Python 3.14; Phase 1 must pin versions that actually install and run.
- Container images and CI must use Python 3.14 rather than inheriting an unpinned host.
- Node.js is unpinned (host v24.14.1); a container/LTS pin remains a Phase 1 choice.
- The inspection `pytest` run created a local `.pytest_cache/` directory; it is excluded by `.gitignore` and is not part of the repository.

## Phase 1.1 — Minimal FastAPI liveness (2026-09-04)

### Scope

Python 3.14 backend project, application factory, `GET /api/health/live`, one API test first. No frontend, database, Makefile or CI.

### TDD

Red (repo root, host pytest 9.1.1):

```bash
python3 -m pytest backend/tests/api/test_health.py -q
```

Observed: collection error `ModuleNotFoundError: No module named 'codebase_assistant'` (exit 2). FastAPI was already present on the host; the failure was the missing application package.

Green (project venv, Python 3.14.4):

```bash
backend/.venv/bin/pytest backend/tests/api/test_health.py
```

Observed: `1 passed` in 0.33s. Two warnings: Starlette TestClient deprecates `httpx` in favour of `httpx2`; `anyio.abc.BlockingPortal` alias is deprecated. Neither warning was filtered.

### Install

`pip install -e ".[dev]"` in `backend/.venv` succeeded. Runtime packages used: FastAPI 0.141.1, Starlette 1.6.0, Pydantic 2.13.5 (`pydantic_core` cp314 wheel), Uvicorn 0.52.4, pytest 9.1.1. Exact pins are in `backend/requirements.lock`.

`httpx2` was not added: it pulls extra packages (`httpcore2`, `truststore`) and FastAPI's TestClient still imports Starlette's httpx-based client. Revisit in Phase 1.4 if the warning becomes a gate.

### Residual

- Make/Compose/CI still absent.
- Container image Python 3.14 is still unpinned.
- Node.js still unpinned.

## Ollama local inference decision (2026-09-04)

After Phase 1.1 was merged, the developer required a **local LLM**, chose **Ollama**, and justified it on privacy: a private deployment may analyse confidential repositories, so source, chunks and prompts must not go to a hosted model API.

Recorded in `docs/adr/004-ollama-local-inference.md` and `docs/threat-model.md`. The Ollama adapter is not implemented yet (Phases 5.3 and 6.2). Default tests remain fakes. Concrete model tags are still unset.

## Phase 1.2 — Minimal React application shell (2026-09-04)

### Scope

Vite, React, strict TypeScript, one component test first. No upload/chat UI, ESLint, coverage gates, Makefile or CI.

### TDD

Red:

```bash
npm --prefix frontend test
```

Observed: exit 254, `ENOENT` opening `frontend/package.json`.

Green:

```bash
cd frontend && npm test
```

Observed: Vitest 3.2.7, `tests/app/App.test.tsx` 1 passed. `npx tsc -b --noEmit` succeeded.

Installed versions included React 19.2.8, Vite 7.3.6, TypeScript 5.9.3 on host Node.js v24.14.1. npm reported a deprecated `whatwg-encoding` transitive dependency; it was not patched in this task.

### Residual

- Make/Compose/CI still absent.
- Frontend ESLint and coverage gates belong to Phase 1.4.
- Node.js is still unpinned in containers.

## Phase 1.3–1.6 — Local stack and quality gates (2026-09-04)

### Scope

PostgreSQL/pgvector, Alembic `vector` extension, Ruff/mypy/coverage, ESLint/Vitest coverage, Makefile, Compose, GitHub Actions, `.env.example`.

### TDD

Red: `pytest backend/tests/integration/test_pgvector_extension.py` failed with `ModuleNotFoundError: No module named 'sqlalchemy'`.

Green:

- `cd backend && .venv/bin/pytest` → 4 passed, 1 integration deselected, 100% coverage of application package.
- After `docker compose up -d db` and `alembic upgrade head` on host port 5433: `pytest -m integration` passed (vector extension present).
- `docker compose up -d --build`: `GET /api/health/live` → `{"status":"ok"}`; frontend HTTP 200 on port 3000.

Host port 5432 already had a Postgres without role `codebase`; Compose publishes 5433 instead.

### Quality

- Bandit: no issues on `backend/src`.
- pip-audit: no known vulnerabilities (local package skipped).
- npm audit --omit=dev: 0 vulnerabilities.
- Gitleaks and Trivy were not executed in this session (Docker targets exist in `make security`).
- GitHub Actions was reduced to one job: `make setup`, `make lint`, `make test`. No Postgres service or scanner images.

### Residual

- GitHub Actions was reduced to one job: `make setup`, `make lint`, `make test`. No Postgres service or scanner images.
- Phase 1 security exit gate is open until Gitleaks/Trivy are observed locally.
- No ingestion or answering yet.

## Combined config and run paths (2026-09-04)

### Scope

`config/app.env` as the combined file; backend Settings and frontend `src/app/config.ts`; Compose Ollama; `make run-docker` and `make run`.

### TDD

Red: `Settings` had no `ollama_host`; Vitest could not import `src/app/config`.

Green: backend LLM settings test and frontend API-base-URL tests (observed after implementation).

### Residual

- Ollama image tag is `latest`; models are not pulled automatically.
- Application still does not call Ollama.
- Phase 1 security exit gate remains open.

## Prerequisites and LLM choice (2026-09-04)

Documented Docker-only first run (no Make) and recorded Hugging Face hosted vs local Transformers against ADR 004. No adapter change.

## Phase 1 closed — security scans (2026-09-04)

Command: `make security`

| Check | Observed |
|---|---|
| Bandit | No issues |
| pip-audit | No known vulnerabilities |
| npm audit --omit=dev | 0 vulnerabilities |
| Gitleaks | No leaks (~168.48 KB) |
| Trivy fs HIGH,CRITICAL | 0 on `frontend/package-lock.json` |

Phase 1 exit gate is closed. Next: Phase 2 domain contracts.

## Phase 2 — Domain and application contracts (2026-09-04)

### TDD

Red: `from codebase_assistant.domain.models import Citation` → `No module named 'codebase_assistant.domain'`.
Red: `from codebase_assistant.application.ports import EmbedTexts` → `No module named 'codebase_assistant.application'`.
Red: `from codebase_assistant.application.contracts import AskQuestionRequest` → `No module named 'codebase_assistant.application.contracts'`.

Green: `cd backend && .venv/bin/pytest` → 27 passed, 100% coverage of the application package.

### Residual

- No ingestion, retrieval or answering use-case implementation yet.
- Ollama is configured but not called.

## Phase 3.1–3.2 — ZIP admission (2026-09-04)

Branch: `feat/phase-3-secure-zip-ingestion`

Red: pytest collection failed with `No module named 'codebase_assistant.ingestion'`.

Green: admission tests reject non-ZIP, oversized uploads, non-`.zip` names and truncated ZIP; a small in-memory ZIP is admitted. Hostile fixtures are built in memory, not written to disk.

## Phase 3.3 — Safe archive members (2026-09-04)

Branch: `feat/phase-3-safe-archive-members`

Red: missing `codebase_assistant.ingestion.members`.

Green: traversal, absolute paths, Unix symlink members, file-count, per-file size, extracted size and high compression ratio are rejected. Members are inspected via `ZipInfo` only.

## Phase 3.4 — Source-file policy (2026-09-04)

Branch: `feat/phase-3-source-file-policy`

Red: `pytest tests/unit/ingestion/test_source_policy.py` → `No module named 'codebase_assistant.ingestion.source_policy'`.

Green: allowlisted `.py` is accepted as UTF-8 text; nested `.env*`, `id_rsa`, `.pem` and `credentials.json` are ignored with `text is None`; `node_modules`, `.git`, `dist` and `__pycache__` are excluded; `.docx`, NUL bytes and invalid UTF-8 are ignored without crashing.

`make lint` passed. `make test`: backend 49 passed (1 deselected), coverage 95.97%; frontend Vitest 3 passed, 100% coverage. Bandit: no issues on `backend/src`.

## Phase 3.5 — Ingestion summary (2026-09-07)

Branch: `feat/phase-3-ingestion-summary`

Red: `pytest tests/unit/ingestion/test_summary.py` → `No module named 'codebase_assistant.ingestion.summary'`.

Green: `summarise_archive` returns sorted accepted paths, ignored paths and reason counts; secret file bodies are absent from the summary; directory ZIP entries are skipped; Python members are not executed; invalid UTF-8 is ignored; the temp ZIP copy is removed on success, admission failure and classify failure.

`make lint` passed. `make test`: backend 56 passed (1 deselected), coverage 97.21%; frontend Vitest 3 passed, 100% coverage. Bandit: no issues on `backend/src`.

Phase 3 exit gate is closed. Next: Phase 4 chunking.

## Demo slice — upload to cited answer (2026-09-07)

Branch: `feat/phase-4-8-demo-upload-to-cited-answer`

Red: missing `codebase_assistant.chunking`; Python AST test saw one untagged chunk; missing extractive/memory adapters; `create_app()` rejected `workspace=`.

Green: line and AST chunking; ingest/ask use cases; ZIP upload and question API; React ingest/chat/inspector.

`make lint` passed. `make test`: backend 69 passed (1 deselected), coverage 90.63%; frontend 9 passed. Bandit: no issues on `backend/src`.

Not done: Ollama adapters, wiring ingest to pgvector, readiness, evaluation/e2e.

## Phase 5.1 persistence schema (2026-09-07)

Branch: `feat/phase-5-postgres-chunk-persistence`

Red: `No module named 'codebase_assistant.adapters.persistence'`.

Green: unit schema test; `alembic upgrade head` created `repositories` and `chunks`; integration tests passed (vector extension + `vector(768)` + FK `ON DELETE CASCADE`).

Embedding size is 768 for `nomic-embed-text` (ADR 002). Uploads still use the in-memory index until 5.2/5.4.

## Phase 5.2 pgvector workspace (2026-09-07)

Branch: `feat/phase-5-postgres-chunk-persistence`

Red: `as_vector_literal` was missing; two test files named `test_postgres_workspace.py` blocked collection.

Green: `cd backend && .venv/bin/pytest` → 72 passed, 4 deselected, coverage 86.11%. Integration (`pytest -m integration`) → 4 passed against local Postgres.

Search always includes `WHERE repository_id`. Re-ingest deletes then inserts chunks in one transaction.

## Phase 5.3 Ollama embedding adapter (2026-09-07)

Branch: `feat/phase-5-postgres-chunk-persistence`

Red: `No module named 'codebase_assistant.adapters.ollama'` after `EmbeddingError` existed.

Green: `pytest tests/unit/test_ollama_embedder.py` — 4 passed with `httpx.MockTransport` (no network). Timeout and malformed JSON map to `EmbeddingError`. Source text is absent from logs.

Default model `nomic-embed-text`, 768 dimensions. `httpx` is a runtime dependency for the adapter. Default `EMBEDDING_PROVIDER=lexical`.

## Phase 5.4 ingest orchestration (2026-09-07)

Branch: `feat/phase-5-postgres-chunk-persistence`

Red: `test_failed_embedding_does_not_mark_ingest_completed` raised `EmbeddingError` and never stored `status=failed`.

Green: `cd backend && .venv/bin/pytest` → 79 passed, 4 deselected, coverage 85.37%. Integration → 4 passed.

`create_app` uses `PostgresWorkspace` when a database URL can be resolved (`DATABASE_URL` or `DATABASE_USER`/`DATABASE_NAME`). Failed embedding marks the repository failed, clears chunks, and questions return 409. Answers remain extractive.

## Host-run CORS and Ollama embed pull (2026-09-07)

Branch: `fix/host-run-cors-and-ensure-ollama-embed-model`

Red: OPTIONS from `http://127.0.0.1:3000` returned 400; `No module named 'codebase_assistant.ops'`.

Green: CORS preflight accepts the loopback alias; `pytest tests/unit/test_ollama_models.py` — 3 passed. `make run` pulls `nomic-embed-text` via Ollama HTTP when `EMBEDDING_PROVIDER=ollama` and the model is missing. No prompts.

## Phase 3.6 — Bounded archive integrity (2026-09-08)

Branch: `fix/phase-3-bounded-archive-integrity-validation`

Red: `test_high_ratio_member_is_rejected_without_decompressing` raised `AssertionError: members must not be decompressed before size limits` because `admit_archive` called `ZipFile.testzip()`.

Green: admission parses the ZIP directory only. `validate_members` still applies declared count/size/ratio limits. `read_member_bounded` inflates at most `max_file_bytes` / remaining extracted bytes. High-ratio summary path does not call `testzip` or `ZipFile.read`.

`cd backend && .venv/bin/pytest` — 87 passed, 4 deselected, coverage 81.86%. Frontend Vitest 9 passed. Bandit on `ingestion/` — no issues. `make lint` still fails on `frontend/vite.config.ts` `process` (PLAN 5.5).

Phase 3 ZIP-bomb order gap is closed. Next: PLAN 5.5.

## Phase 5.5 — Deterministic reviewer baseline (2026-09-08)

Branch: `fix/phase-5-restore-deterministic-reviewer-baseline` (stacked on 3.6)

Red: `test_create_app_does_not_construct_ollama_when_env_selects_ollama` raised when `EMBEDDING_PROVIDER=ollama`; Compose parity tests missed `EMBEDDING_PROVIDER` and archive limits; `make lint` failed on `process` in `vite.config.ts`.

Green: under pytest, `create_app` defaults to lexical embeddings and in-memory store; `@types/node` for Vite config; Compose backend receives embedding and archive settings from `config/app.env` interpolation.

`make lint` passed. `make test` — backend 90 passed (4 deselected), coverage 81.15%; frontend 9 passed.

Next: PLAN 6.2 Ollama completion adapter.

## Host make run without Docker (2026-09-08)

`make run` no longer starts Compose `db`/`ollama`. It migrates the configured local Postgres, ensures the Ollama embed model when `EMBEDDING_PROVIDER=ollama`, then starts uvicorn and Vite. Docker remains `make run-docker` / `make down`.

## Phase 6.2 — Ollama completion adapter (2026-09-08)

Branch: `feat/phase-6-ollama-completion-adapter`

Red: `test_ollama_completer_posts_chat_and_returns_json_content` raised `ModuleNotFoundError` / missing `OllamaCompleter` before the adapter existed.

Green: `OllamaCompleter` calls `POST /api/chat` with `format: json`, temperature/`num_predict`, bounded retries; validates JSON keys `text` / `citations` / `insufficient_evidence`; raises `CompletionError` on timeout/HTTP/schema failure. `create_app` selects it when `COMPLETION_PROVIDER=ollama`; pytest defaults stay extractive. Completion failures map to safe HTTP 503.

`make lint` passed. `make test` — backend 97 passed, 4 deselected, coverage 80.52%; frontend 9 passed.

Next: PLAN 6.1 (enforce question/context limits), then 6.3 / 6.5 / optional 6.4.

## Phase 6.1 — Prompt and context budgets (2026-09-08)

Branch: `feat/phase-6-ollama-completion-adapter`

Red: `test_answer_limits.py` raised `ModuleNotFoundError: AnswerLimits` before `application/limits.py` existed.

Green: `AnswerLimits` + `select_context_chunks`; oversized questions raise `InvalidQuestionError`; prompt keeps untrusted-source delimiters; citations verified only against budgeted chunks. Settings/Compose expose `MAX_QUESTION_CHARS`, `MAX_CONTEXT_CHARS`, `MAX_EXCERPT_CHARS`.

Also: `make test-integration` uses `--no-cov` so the default 80% gate is not applied to the narrow Postgres suite.

`make lint` passed. `make test` — backend 102 passed, 4 deselected, coverage 80.26%; frontend 9 passed.

Next: PLAN 6.3 (strict completion parsing), then 6.5 / optional 6.4.

## Phase 6.3 — Strict completion parsing (2026-09-08)

Branch: `feat/phase-6-ollama-completion-adapter`

Red: `test_strict_completion.py` raised `ModuleNotFoundError` for `application.completion` before `parse_completion` existed.

Green: `parse_completion` requires exact keys and types; malformed citation entries invalidate the whole payload; ask verifies citations against budgeted retrieved chunks and drops fabrications; empty retrieval skips the completer.

`make lint` passed. `make test` — backend 111 passed, 4 deselected, coverage 81.34%; frontend 9 passed.

Next: PLAN 6.5 (injection/forgery regression tests), optional 6.4 smoke.

## Ensure Ollama models from providers (2026-09-08)

`make run` and `make run-docker` call `ensure-ollama-models`, which pulls `OLLAMA_EMBED_MODEL` when `EMBEDDING_PROVIDER=ollama` and `OLLAMA_CHAT_MODEL` when `COMPLETION_PROVIDER=ollama`. No pull when both providers stay lexical/extractive.

## Phase 6.5 — Answer-boundary regressions (2026-09-08)

Branch: `feat/phase-6-ollama-completion-adapter`

Added `test_answer_boundary.py` covering oversized questions, context truncation, malformed completions, altered/expanded citations, and prompt-injection in source/README text. Behaviour already existed from **6.1**/**6.3**; tests lock it. All eight cases passed without production code changes.

`make lint` passed. `make test` — backend 122 passed, 4 deselected, coverage 81.13%; frontend 9 passed.

Next: optional PLAN 6.4 smoke, then Phase 9.

## Phase 6.4 — Optional Ollama smoke (2026-09-08)

Branch: `feat/phase-6-ollama-completion-adapter`

Added `tests/smoke/test_real_provider.py` (embed + chat) marked `smoke`, excluded from default pytest via `not integration and not smoke`. Requires `RUN_LLM_SMOKE=1` and a reachable local Ollama with the configured models.

Observed with local Ollama: `RUN_LLM_SMOKE=1 pytest -m smoke -q --no-cov` — 2 passed. Default `make test` — 123 passed, 6 deselected.

Next: Phase 9.

## Phase 9.1 — Controlled fixture repository (2026-09-08)

Branch: `feat/phase-9-controlled-fixture-repository`

Red: `test_fixture_repository_contains_required_layout` failed before `sample-data/fixture-repository/` existed.

Green: synthetic inventory-service tree with handlers, service, model, config, distractors; `credentials.json` and `vendor/` ignored on ingest. Documented in `docs/evaluation.md`.

`pytest tests/unit/test_fixture_repository.py` — 3 passed.

Next: PLAN 9.2 evaluation dataset.

## Phase 9.2 — Evaluation dataset (2026-09-08)

Branch: `feat/phase-9-controlled-fixture-repository`

Red: `test_evaluation_dataset_file_exists_with_version_and_cases` failed before `sample-data/evaluation/dataset.json` existed.

Green: eight cases (5 grounded, 2 unsupported, 1 prompt-injection). Injection bait added to fixture `docs/architecture.md`. Schema tests pass.

Next: PLAN 9.3 retrieval evaluation runner.

## Phase 9.3–9.5 — Evaluation runner, E2E, adversarial matrix (2026-09-08)

Branch: `feat/phase-9-controlled-fixture-repository`

### 9.3

Red: runner/tests absent before package existed.

Green: `codebase_assistant.evaluation` ingest fixture ZIP with lexical+extractive, report metrics, CLI gate.

Observed (`make test-evaluation` / `python -m codebase_assistant.evaluation`):

- `citation_validity_rate=1.0`
- `grounded_source_hit_rate=0.8`
- `grounded_answer_file_hit_rate=0.0`
- `insufficient_evidence_correct_rate=0.0`
- Gate: citation validity 1.0 and grounded hit-at-k ≥ 0.75

### 9.4

Playwright `e2e/` against `ops.e2e_api` (InMemory + Lexical + Extractive). CORS set to `http://127.0.0.1:3010`.

`make test-e2e` — 1 passed (upload fixture → ask → open citation).

### 9.5

`backend/tests/adversarial/test_matrix.py` consolidates hostile ZIP, secrets, injection, forgery, oversized question, provider 503, repeated upload. Excerpt escape remains in frontend App tests.

`make test` — backend + frontend green after entrypoint smoke tests restored coverage.

Documented in `docs/evaluation.md` and `docs/threat-model.md`.

Next: PLAN **8.5**/**8.6** demo polish, then Phase 10.

## Phase 8.5–8.6 — Reviewer UI polish (2026-09-08)

Branch: `feat/phase-8-reviewer-demo-polish`

Red: App tests for indexing/answering status, starter chips, failed-index panel, Evidence focus, fixture pointer.

Green: polished shell with live regions, starter questions from the fixture dataset, distinct failed-index UX, Evidence panel as primary answer surface, focus management, responsive layout.

`npm --prefix frontend run test` — 14 passed.

Next: Phase 10 observability (residual **8.1** timeouts optional).

## Phase 8 UI follow-up — Bootstrap shell and repository list (2026-09-08)

Branch: `feat/phase-8-reviewer-demo-polish`

Backend:

- `GET /api/repositories` lists stored summaries (newest first).
- Summaries include `source_filename`; migration `003_repository_source_filename`.

Frontend:

- Bootstrap 5 + react-bootstrap layout: repositories column, upload column, ask column.
- Indexing/answering use Bootstrap spinners; indexed paths in a scrollable region so long paths do not crush the ask column.
- Selecting a listed repository loads it via `GET /api/repositories/{id}` and clears the prior answer.

`npm --prefix frontend run test` — 16 passed; `make test-e2e` — 1 passed.

## Phase 8 UI follow-up — App shell, chat, delete, name-unique ingest (2026-09-08)

Branch: `feat/phase-8-reviewer-demo-polish`

Backend:

- `DELETE /api/repositories/{id}` removes summary + chunks.
- Ingest replaces any existing repository with the same display name (ZIP basename, case-insensitive).
- Answer prompt asks for multi-paragraph grounded answers with inline `[n]` citations.
- Example completion settings: `LLM_TEMPERATURE=0.2`, `LLM_MAX_OUTPUT_TOKENS=2048`.

Frontend:

- Full-viewport app shell: repository sidebar, chat thread with sessionStorage history, ingest modal, indexed-files drawer.
- Citations live inside assistant messages; Delete calls the API.

Verification:

- Backend focused pytest (ingest replace + delete API) — pass
- `npm --prefix frontend run typecheck` / `lint` / `test` — 16 passed
- `make test-e2e` — selector updated; re-run with stack up if not already green on this branch

Next: Phase 13 repository-aware Q&A (PLAN 13.1 lockfile exclusion first), then Phase 10 observability (residual **8.1** timeouts optional).

## Plan update — Phase 13 repository-aware Q&A (2026-09-08)

No implementation in this checkpoint. `PLAN.md` remaining-work now starts at **Phase 13** so overview, structure, endpoint, dependency, locate and how-it-works questions are designed before observability. Observed failure: `"what does this repo do?"` answered from `package-lock.json`.

## Phase 13.1 — Ignore generated lockfiles and minified bundles (2026-09-08)

Red: `test_generated_lockfiles_are_ignored_without_returning_contents` failed because `frontend/package-lock.json` was `accepted`.

Green: basename lockfile list + `*.min.js`/`*.min.css` return `generated_lockfile` / `generated_bundle` with no text. Manifests and README stay indexed.

`pytest backend/tests/unit/ingestion/test_source_policy.py -q --no-cov` — 10 passed.

Next: **13.2** extractive repository card.

## Phase 13.2 — Extractive repository card (2026-09-08)

Red: `test_repository_card.py` collection failed (`ModuleNotFoundError: repository_card`).

Green: `build_repository_card` from accepted (path, text) pairs. Fixture README excerpt mentions inventory; outline includes `src/api/handlers.py`; manifests yield name/description/deps; outline depth/entry caps apply; malformed JSON is skipped.

`pytest backend/tests/unit/application/test_repository_card.py -q --no-cov` — 5 passed.

The card is not persisted or returned from ingest yet (**13.3**).

Next: **13.3** persist the card on the repository summary.

## Phase 13.3 — Persist repository card (2026-09-08)

Red: `test_ingest_attaches_extractive_repository_card` — `IngestArchiveResult` had no `card`.

Green: ingest builds and stores the card; memory + list/get API expose `repository_card`; same-name re-ingest replaces outline; Alembic `004_repository_card` JSONB column; frontend maps the field. Fixture ingest test now checks ignored credential file text is absent from the summary, not the README placeholder.

`pytest backend/tests/unit backend/tests/api -q --no-cov` — passed.
`npm --prefix frontend run typecheck` — passed.
Frontend focused tests — 14 passed.

Postgres round-trip is asserted in `test_postgres_workspace.py` (integration marker; not run in default `make test`). Apply `alembic upgrade head` on existing databases.

Next: **13.4** classify question intent.

## Phase 13.4 — Question intent classifier (2026-09-08)

Red: collecting `test_intent.py` raised `ModuleNotFoundError: intent`.

Green: `classify_question_intent` maps supported questions to `overview` / `structure` / `dependencies` / `endpoints` / `locate` / `explain` with first-match regex rules. Unrecognised questions default to `explain`. Not wired into `ask_question` yet (**13.5**).

`pytest backend/tests/unit/application/test_intent.py -q --no-cov` — 20 passed.

Next: **13.5** assemble intent-routed context.

## Phase 13.5 — Intent-routed ask context (2026-09-08)

Red: `test_overview_question_cites_readme_not_noisy_json` cited `meta/packages.json` under lexical top-k when that file repeated the question text.

Green: overview/structure/dependencies/endpoints load the stored card and pin matching chunks (`chunks_for_paths`). Vector search is skipped when pins exist, otherwise it remains the fallback. `locate` / `explain` stay vector-only. The prompt may include a derived repository index; that text counts toward `MAX_CONTEXT_CHARS` and is not a citation source.

`pytest backend/tests/unit/application/test_intent_context.py backend/tests/unit/application/test_ingest_and_ask.py backend/tests/unit/application/test_answer_limits.py backend/tests/unit/application/test_answer_boundary.py backend/tests/api/test_repositories.py backend/tests/evaluation -q --no-cov` — 35 passed.

`pytest backend/tests/unit/application -q --no-cov` — 67 passed.

ruff check/format and mypy on `ask.py`, `prompt.py`, `ports.py`, `memory.py`, `postgres.py` — passed.

Next: **13.6** extract endpoints and declared dependencies.

## Phase 13 plan correction (2026-09-08)

PLAN Phase 13 rewritten before **13.6**: card schema/provenance trusted, copied strings untrusted; exact `chunks_for_paths` required; no uncited `GroundedAnswer` exception (outline is derived evidence plus real file citations); extractors before remaining prompt/eval work; 13.2 already has dependency names so 13.6 is endpoints + provenance; 13.9 must require correct cited files and IE behaviour; outcome is supported formats, not arbitrary ZIP.

## Phase 13.6 — Endpoint extraction and declaring-file provenance (2026-09-08)

Red: collecting `test_extractors.py` raised `ModuleNotFoundError: extractors`.

Green: ingest-time regex extracts `GET /items` / `POST /items` from fixture handlers and FastAPI-style `@app.get`; card stores endpoints and declared dependencies with file path and line range; ask pins those declaring files (filename heuristics only if records are empty). JSON/manifest files are not scanned for routes.

`pytest backend/tests/unit/application -q --no-cov` — 71 passed.
`npm --prefix frontend run typecheck` — passed.
`npm --prefix frontend run test` — 16 passed.

ruff check/format and mypy on `extractors.py`, `repository_card.py`, `ask.py`, `prompt.py` — passed.

Next: **13.7** per-intent prompt policy.

## Phase 13.7 — Per-intent prompt policy (2026-09-08)

Red: overview/endpoint questions against a repo with only `src/app.py` still invoked the completer (vector fallback). Prompt tests lacked intent-specific instructions.

Green: pin intents no longer fall back to vector search. Overview without README/manifest, endpoints with no extracted routes, and dependencies with no declaring manifest return insufficient evidence before completion. Prompts tell overview/structure/deps/endpoints what to list or refuse; locate/explain keep the grounded-explanation instructions. Card index strings remain untrusted. `GroundedAnswer` still requires citations; no domain exception.

`pytest backend/tests/unit/application -q --no-cov` — 77 passed.
`pytest backend/tests/unit/application backend/tests/adversarial backend/tests/evaluation -q --no-cov` — 90 passed.

ruff check/format and mypy on `ask.py`, `prompt.py` — passed.

Next: **13.8** repo-aware starter chips.

## Phase 13.8 — Repo-aware starter chips (2026-09-08)

Red: `App.test.tsx` still showed “Where is list_items defined?” for a repo whose only indexed path was `src/app.py`; `starterQuestions` did not exist.

Green: chips are overview + structure, then endpoints/dependencies when the card has extracted items, plus a locate question from a real indexed file. `list_items` is included only when `handlers.py` is indexed. Paths are rendered as button text (not HTML).

`npm --prefix frontend run test` — 20 passed.
`npm --prefix frontend run typecheck` — passed.
`npm --prefix frontend run lint` — passed.

Browser click-through was not run in this session (no browser tools); Vitest/RTL covered empty-state chips for `src/app.py` and a handlers-bearing card.

Next: **13.9** evaluation and answer correctness.

## Phase 13.8a–13.8c — Architecture flows and safe Markdown cards (2026-09-08)

User direction: improve “controller to database” answers so they show controller, service, repository/DAO, entity/model and database hops for every controller; show directory trees as Markdown-style content inside a card. A follow-up example showed that a `VisitController` method inventory retrieved one chunk, called two visible methods the complete count, omitted their purposes and ignored the requested table.

Red evidence:

- Architecture wording classified as generic `explain`; prompts had no per-controller flow contract and exact context did not include deep layered Java paths.
- Structure answers were plain outline text, and assistant messages had no semantic Markdown/tree-card rendering.
- A flat model response remained one paragraph; an entity in a separate `domain/` directory was absent from the prompt.
- Named code-unit inventory wording used generic vector retrieval, so methods below the first chunk were absent. The prompt had no summary/count/table contract and the frontend had no table block.

Green implementation:

- `architecture_flow` uses the full repository-scoped indexed path list to pin a bounded conventional set of controllers, services/use cases, repositories/DAOs, entities/models/domain files and database evidence. Chunk ordering spreads evidence across files and favours architecture cues.
- Prompts request an explicit repeated controller-flow shape and forbid invented hops. A flat valid response is normalised into one Markdown section per indexed controller; missing method detail remains visibly “Not evidenced”. This is a bounded heuristic, not a static call graph.
- `code_unit_details` is generic rather than controller-specific: it resolves spaced/case/underscore filename variants, pins the complete matched file when it fits the context budget, requires a summary/count/callable table and rejects a flat partial inventory. The same regression path covers `VisitController.java` and `inventory_service.py`.
- Structure answers emit a deterministic fenced `tree` block. The frontend renders a constrained Markdown subset as escaped React nodes and presents fenced trees and semantic tables in bounded cards.

Verification:

- `backend/.venv/bin/pytest backend/tests/unit/application -q --no-cov` — passed.
- `make lint && make test && make test-evaluation` — lint/type checks passed; backend 211 passed, 6 deselected, 82.26% coverage; frontend 33 passed, 81.13% line / 79.16% branch coverage; evaluation tests passed and retained the documented weak lexical/extractive baseline (`0.5` outcome pass, `0.0` answer-file hit, `0.0` insufficient-evidence correctness).
- In-app browser against the persisted Spring Petclinic repository showed a semantic “Directory structure” heading and labelled tree card. A new live Ollama answer could not be completed because local Ollama was unavailable; the UI returned the safe “completion provider unavailable” error.
- `npm --prefix e2e test` reached Playwright but failed on the pre-existing ambiguous “New repository” locator (two accessible matches). Its repair and stronger cited-file assertion remain in pending **13.9**.

Next: **13.9** answer-correctness evaluation; do not infer production call-graph completeness from filename heuristics.

## Phase 13.9 — Answer-correctness evaluation (2026-09-08)

Red: `test_endpoints_question_lists_extracted_routes_from_card` called the completer (AssertionError: endpoint answers must list extracted card routes). `test_evaluation_runner_reports_observed_metrics` failed because `api-endpoints` cited `src/api/ItemController.py` only (`outcome_ok` false). ChatThread empty-state test failed looking for **Ingest a ZIP**.

Green: endpoint intent lists extracted card routes and cites overlapping declaring-file chunks without a completer. Locate prepends identifier-matching chunks when vector hits omit them (capped 40 paths, same repository). Extractive ranking still prefers defining files / route-bearing excerpts for locate/explain. Eval gates: citation validity 1.0, IE correctness 1.0, grounded answer-file hit ≥ 0.8, `list-items-location` and `api-endpoints` cite `src/api/handlers.py`. Empty-state button is **Ingest a ZIP**; Playwright asserts that citation path.

Observed `make test-evaluation` / `python -m codebase_assistant.evaluation`:

- `outcome_pass_rate` 1.0
- `grounded_source_hit_rate` 0.9090909090909091
- `grounded_answer_file_hit_rate` 1.0
- `citation_validity_rate` 1.0
- `insufficient_evidence_correct_rate` 1.0

`inventory-service-methods` remains extractive insufficient evidence (tagged outcome_ok). Playwright was not completed in the agent sandbox (x64 headless-shell path vs host arm64 cache).

`pytest backend/tests/unit/application -q --no-cov` — 99 passed.
`pytest backend/tests/evaluation -q --no-cov` — 7 passed.
`npm --prefix frontend run test -- --run tests/app/ChatThread.test.tsx tests/app/App.test.tsx` — 14 passed.

## Phase 13.10 — Retrieval and evaluation documentation (2026-09-08)

README, threat model, `docs/evaluation.md` and this journal updated from the observed 13.9 numbers. No invented metrics. Residual: host `make test-e2e`.

Next: **7.1** Pydantic response models.

## Phase 12.4 / residual 13.9 — Host Playwright and screenshots (2026-09-08)

`Ingest` without `exact: true` matched both **Ingest a ZIP** and the modal submit. `getByText("fixture-repository")` also matched text still in the open modal. Locators now wait for the dialog to close, assert `src/api/handlers.py` plus excerpt `list_items`, then assert **Insufficient evidence** for the OAuth question.

`make test-e2e` — 1 passed (3.0s). Live README screenshots recaptured from `tmp/tic-tac-toe-react-app-main.zip` with Ollama: upload modal, indexed-file tree, overview, `checkWinnerFrom` inspector, directory structure. Insufficient evidence stays in Playwright only.

Next: **12.5** read-only review, then essential Phase **7** / **10**.
