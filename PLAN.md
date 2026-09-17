# TDD Delivery Plan

This is the operational source of truth for building the project with coding agents. Execute phases in order, except where **Remaining work for a portfolio-ready release** reorders leftover tasks. A phase is complete only when its tests, documentation and exit gate are satisfied.

The next implementation task is **Phase 7.1** (explicit Pydantic response models), then the rest of essential Phase 7 / light Phase 10. Phase 13.9–13.10 evaluation and documentation are recorded. Observability and productionisation stay **light**. Residual **8.1** timeouts remain optional.

## How to use this plan

At the start of each agent session, use:

```text
Read AGENTS.md, README.md, PLAN.md and AI_DEVELOPMENT_LOG.md.
Identify the first incomplete task using the remaining-work sequence in PLAN.md
(currently essential Phase 7/10, then light Phase 11, then Phase 12.5
read-only review; residual 8.1 optional).
Do not modify files yet.

Report:
1. the selected task and acceptance criteria;
2. relevant existing code/tests;
3. tests to write first and why they should fail;
4. expected production files to change;
5. security or architectural considerations;
6. assumptions or decisions requiring approval.

Wait for approval before implementation.
```

After approving the proposal, use:

```text
Proceed only with the approved PLAN.md task and follow AGENTS.md.
Demonstrate red-green-refactor. Run focused verification, inspect the diff,
update the required documentation, and draft a factual AI_DEVELOPMENT_LOG.md
entry. Stop at the task checkpoint and provide the required task report.
Do not commit or start the next task until I approve.
```

The human reviews the diff, runs or confirms verification, approves the AI log entry and then commits.

## Fixed technical direction

These choices are approved for the initial implementation. A change requires an ADR and human approval.

| Area | Decision | Reason | Deferred alternative |
|---|---|---|---|
| Shape | Modular monolith | Clear boundaries without operational overhead | Microservices |
| Backend | Python 3.14, FastAPI, Pydantic | Typed API and mature AI ecosystem; 3.14 is the host runtime approved on 2026-09-04 | Node/NestJS |
| Frontend | React, Vite, strict TypeScript | Small production-capable frontend | Next.js |
| Store | PostgreSQL 16 with pgvector | Metadata and vectors in one datastore | Dedicated vector database |
| ORM/migrations | SQLAlchemy 2 and Alembic | Explicit persistence and repeatable schema changes | Raw SQL-only data layer |
| Model integration | Narrow internal ports; first real adapter is local Ollama | Visible control flow; private repo text stays in-network | Hosted OpenAI/Anthropic APIs; LangChain/LlamaIndex |
| Chunking | Python AST plus bounded line fallback | Useful code awareness with limited scope | Universal parser/Tree-sitter |
| Backend tests | pytest | Established Python testing ecosystem | — |
| Frontend tests | Vitest and React Testing Library | Fast component-level behaviour tests | Jest |
| E2E | Playwright | Reliable browser automation | Cypress |
| Local operation | Docker Compose and Make | Reproducible, simple command surface | Kubernetes |

The exact chat and embedding **model tags** must be configuration values. The approved runtime is local **Ollama** ([ADR 004](docs/adr/004-ollama-local-inference.md)): private repository text must not be sent to a hosted LLM API. Select cost-effective Ollama models when Phase 5/6 implement the adapter and record them in the ADR follow-up and README. Tests must remain provider-independent.

## Global definition of done

A task is done only when:

- acceptance criteria are satisfied;
- the test was observed failing for the intended reason before implementation, where applicable;
- focused and related tests pass;
- formatting, linting and type checks for changed code pass;
- security implications were reviewed;
- no unrelated changes are present;
- relevant documentation is accurate;
- the AI development log contains only verifiable facts;
- a small, coherent commit is ready.

The project release is done only when `make verify`, the clean setup path, container checks and the manual review checklist pass.

## Remaining work for a portfolio-ready release

The architecture is retained. The product is roughly three-quarters complete; the remaining quarter is disproportionately important for a public portfolio release: it has to prove accuracy, light observability, reproducible setup, security judgement, and a README a new contributor can actually follow.

Observability (**Phase 10**) and productionisation (**Phase 11**) stay **light**: correlation IDs, a few structured operation events, redaction tests, non-root images, Compose health, and a clean-room README walkthrough. No vendor APM, dashboards, Kubernetes or extra services.

Checked tasks that still had unfinished criteria have been reopened or split into unchecked follow-ups. Do not treat a checkbox as done when a later follow-up item exists.

Follow this sequence rather than the lowest unchecked number in a later phase:

1. Close essential API and operational gaps from **Phases 7 and 10**: response contracts (**7.1**), reject oversized uploads before buffering (**7.2**), readiness (**7.4**), correlation IDs (**7.5**), light structured logs and redaction tests (**10.1**–**10.3**). **10.4** stays a short “production telemetry” note, not an implementation.
2. Light container and clean-room verification (**Phase 11**).
3. Remaining **Phase 12** evidence: read-only final review (**12.5**). README (**12.1**), AI-account examples (**12.2**), eval/journal (**12.3**) and screenshots (**12.4**) are recorded; keep README honest as behaviour changes.
4. Optional **8.1** request timeouts/cancellation if time remains.

Phase 6, Phase 9, Phase 13.1–13.10, and Phase 8 demo polish (**8.2**–**8.6**) are complete. Vector-only retrieval remains for `locate` / `explain` except a capped identifier pin when top-k misses a long name. Overview / structure / dependencies / endpoints pin declaring files and return insufficient evidence when required card evidence is missing (**13.7**). Structure and endpoint answers can be assembled from the card without a completer.

Open leftover counts (do not use these as execution order): Phase **7** four tasks; **8.1**; Phase **10** four tasks (keep light); Phase **11** four tasks (keep light); Phase **12.5** read-only review.

Observed product failure this phase exists to fix: `"what does this repo do?"` retrieved `package-lock.json` and the completer summarised npm metadata as the product. Root cause is index pollution plus nearest-neighbour-only context, not the chat model wording.

---

## Phase 0 — Repository baseline and governance

### Outcome

A known baseline, agreed repository structure and documented working process exist before feature code.

### Tasks

- [x] **0.1 Inspect the supplied repository**
  - Record existing files, branches, instructions, tooling and entry points.
  - Run all existing tests/checks without changing code.
  - Record pre-existing failures separately; do not conceal or fix them incidentally.
  - Add the factual baseline to `docs/engineering-journal.md`.

- [x] **0.2 Install the project governance documents**
  - Add `README.md`, `AGENTS.md`, `PLAN.md` and `AI_DEVELOPMENT_LOG.md` at repository root.
  - Reconcile these documents with any existing repository instructions.
  - Replace generic project naming only after the final project name is chosen.

- [x] **0.3 Establish directory skeleton**
  - Add only root directories/configuration needed for Phase 1.
  - Do not add empty deep packages solely to resemble the proposed tree.
  - Add `docs/engineering-journal.md`, `docs/threat-model.md`, `docs/evaluation.md` and `docs/adr/` when first populated.

- [x] **0.4 Record the first decisions**
  - Add `docs/adr/001-modular-monolith.md`.
  - Add `docs/adr/002-postgres-pgvector.md`.
  - Record the decision, context, alternatives, consequences and status.
  - Additional accepted change: `docs/adr/003-python-runtime.md` (Python 3.12 → 3.14).

### Tests/checks

```bash
git status
git branch --show-current
git log --oneline -10
find . -maxdepth 3 -type f | sort
```

Run any repository-provided test, lint and build commands and record exact outcomes.

### Exit gate

- [x] Baseline is recorded.
- [x] Existing failures are distinguished from new failures.
- [x] Root documents agree on scope and structure.
- [x] No application implementation has been added.

### Commit

Already on `main`: `docs: establish project architecture and delivery plan` (`2a12606`). Remaining Phase 0 documentation:

```text
Branch: docs/phase-0-repository-baseline-and-decisions
Commit: docs: record repository baseline and initial architecture decisions
```

---

## Phase 1 — Reproducible project and quality foundation

### Outcome

Backend, frontend and database start locally; quality checks run through stable commands; CI proves the baseline.

### Tasks

- [x] **1.1 Create minimal backend application**
  - Configure Python project and dependency locking.
  - Add one FastAPI application factory and liveness endpoint.
  - Add one API test first.

- [x] **1.2 Create minimal frontend application**
  - Configure Vite, React and strict TypeScript.
  - Render a minimal application shell.
  - Add one component test first.

- [x] **1.3 Add PostgreSQL/pgvector and migrations**
  - Configure Docker Compose service and application settings.
  - Enable the vector extension through an Alembic migration.
  - Add an integration test that proves the extension is available.

- [x] **1.4 Establish quality tooling**
  - Backend: Ruff, mypy, pytest and branch coverage.
  - Frontend: ESLint, TypeScript check and Vitest coverage.
  - Security: Bandit, dependency audit, Gitleaks and Trivy commands.
  - Produce XML coverage compatible with SonarQube/SonarCloud.
  - Use realistic initial coverage gates; target at least 80% line and 75% branch coverage for new code.

- [x] **1.5 Add command surface and CI**
  - Implement `make setup`, `format`, `lint`, `test`, `security`, `verify`, `run` and `down` as they become valid.
  - Add one GitHub Actions job with least-privilege permissions and dependency caches.
  - The workflow file stays in the repo; it is not triggered on push or pull request. Local `make lint` and `make test` are the default checks.
  - Default tests must not require API credentials.

- [x] **1.6 Document local setup**
  - Make README quick start accurate.
  - Combined settings in `config/app.env.example`; backend Settings and frontend `src/app/config.ts`.
  - Three run paths: Docker Compose, Make (host apps + Compose Postgres/Ollama), and manual with a local database.
  - Record tool choices and any skipped standards.

### TDD examples

- Liveness returns `200` and a stable schema.
- Application shell has an accessible main heading.
- Database migration enables the required extension.

### Verification

```bash
make setup
make lint
make test
docker compose config
docker compose up -d --build
docker compose ps
make test-integration
make security
```

### Exit gate

- [x] Fresh setup is documented and repeatable.
- [x] Backend, frontend and database are healthy.
- [x] A GitHub Actions workflow file exists; lint and test are run locally, not on every push.
- [x] Coverage reports are produced.
- [x] No unresolved high/critical security finding exists without documented acceptance.

### Suggested commits

```text
build: initialise backend and frontend applications
build: add postgres vector development environment
ci: establish quality and security gates
```

---

## Phase 2 — Domain model and application contracts

### Outcome

Core behaviour is expressed independently of HTTP, database and model SDKs.

### Tasks

- [x] **2.1 Define domain types and invariants**
  - Add source file, chunk, repository, citation and grounded-answer types only as required by tests.
  - Validate line ranges, IDs and insufficient-evidence rules.

- [x] **2.2 Define external ports**
  - Add narrow interfaces for repository reading, embeddings, vector persistence and LLM completion.
  - Keep interfaces use-case specific.

- [x] **2.3 Define application use-case contracts**
  - Add ingestion and question-answering request/result types.
  - Do not implement infrastructure behaviour yet.

### Tests first

- Invalid citation line ranges are rejected.
- A grounded answer cannot expose an unverified citation.
- An insufficient-evidence answer can contain no factual citation claim.
- Invalid/empty questions are rejected at the correct boundary.
- Provider fakes can satisfy the intended narrow contracts.

### Verification

```bash
pytest backend/tests/unit/domain backend/tests/unit/application -q
make lint
make test
```

### Exit gate

- [x] Domain/application do not import FastAPI, SQLAlchemy or provider SDKs.
- [x] No speculative abstractions or unused classes exist.
- [x] Invariants are protected by tests.

### Commit

```text
feat(core): define domain and provider contracts
```

---

## Phase 3 — Secure repository ingestion

### Outcome

Untrusted ZIP input is validated and read under explicit safety and resource limits without executing its contents.

### Tasks

- [x] **3.1 Write the ingestion threat model**
  - Define trust boundaries, attack paths, controls and residual risks.
  - Map relevant controls to OWASP categories without claiming certification.

- [x] **3.2 Implement archive admission policy**
  - Validate ZIP type/signature and configured upload size.
  - Reject malformed archives.

- [x] **3.3 Implement safe member validation**
  - Reject absolute paths, parent traversal and members escaping the extraction root.
  - Reject/ignore symlinks consistently.
  - Enforce extracted-size, compression-ratio, file-count and per-file limits.

- [x] **3.4 Implement source-file policy**
  - Allowlist extensions.
  - Exclude VCS, dependency, cache, coverage and build directories.
  - Exclude `.env*`, private keys, credentials and common secret files at any depth.
  - Detect/ignore binary content and handle supported encodings safely.

- [x] **3.5 Implement ingestion summary**
  - Return counts and reason categories without returning sensitive contents.
  - Ensure deterministic ordering.
  - Ensure temporary resources are cleaned after success/failure.

- [x] **3.6 Bounded archive integrity validation**
  - Enforce extracted-size, compression-ratio, file-count and per-file limits from archive metadata before any full-member decompression.
  - Do not call `ZipFile.testzip()` (or equivalent full-member CRC/decompression) before those bounds are applied.
  - Reject bombs with a controlled error and without unbounded CPU or memory use.
  - Replace `testzip()` with a bounded per-member read that stops at the configured file and extracted-size budget.
  - Regression: a high-ratio member is rejected on the summary path without `testzip()` or `ZipFile.read()`.

### Tests first

- Valid small archive succeeds.
- Non-ZIP and malformed ZIP fail safely.
- `../`, nested traversal and absolute paths fail.
- Symlinks never expose external content.
- Excessive expansion ratio, size and file count fail **before** full-member decompression.
- A high-ratio member is rejected without `testzip()` expanding it first.
- Nested `.env`, key and credentials files never reach output.
- Dependencies, builds and binaries are ignored.
- Invalid text encoding does not crash the process.
- Repository files are never imported or executed.
- Temporary files are cleaned when processing raises.

### Verification

```bash
pytest backend/tests/unit/ingestion -q
pytest backend/tests/integration/ingestion -q
make lint
make security
make test
```

### Exit gate

- [x] All hostile archive fixtures are generated safely within tests.
- [x] Content cannot escape the working directory.
- [x] Limits are configuration values with safe defaults.
- [x] Integrity validation is bounded: size, ratio, count and per-file limits run before full-member decompression (**3.6**).
- [x] Threat model and README match the implemented ZIP-bomb control.

### Suggested commits

```text
test(ingestion): define hostile archive behaviour
feat(ingestion): add secure repository reader
```

---

## Phase 4 — Code-aware chunking

### Outcome

Accepted source files become bounded, deterministic and citation-ready chunks.

### Tasks

- [x] **4.1 Implement line-based chunking**
  - Preserve path and exact start/end lines.
  - Bound size and overlap through configuration.

- [x] **4.2 Implement Python AST-aware chunking**
  - Prefer complete class/function boundaries within configured limits.
  - Preserve module-level source.
  - Fall back to the line chunker on invalid syntax or oversized symbols.

- [x] **4.3 Add stable metadata and IDs**
  - Include repository ID, relative path, language, symbol, content hash and line range.
  - Generate deterministic chunk IDs.

### Tests first

- No accepted source line is silently lost.
- Citation excerpts match the original line range.
- Reasonably sized functions/classes remain intact.
- Large symbols are subdivided within limits.
- Invalid Python uses safe fallback.
- Empty files create no chunks.
- Repeated chunking produces identical IDs/order.
- Secret/ignored files never enter the chunker.

### Verification

```bash
pytest backend/tests/unit/chunking -q
make lint
make test
```

### Exit gate

- [x] Chunk boundaries are deterministic and bounded.
- [x] Citation line accuracy is tested.
- [x] No universal parsing framework has been introduced.

### Commit

```text
feat(chunking): add deterministic code-aware source chunks
```

---

## Phase 5 — Persistence, embeddings and retrieval

### Outcome

Chunks can be indexed idempotently and retrieved only within their repository.

### Tasks

- [x] **5.1 Create persistence schema and migrations**
  - Store repository metadata, ingestion status and chunks/vectors.
  - Define ownership and deletion relationships explicitly.

- [x] **5.2 Implement vector repository adapter**
  - Batch insert/update.
  - Replace a repository index atomically or through an explicit safe state transition.
  - Filter every search by repository ID.

- [x] **5.3 Implement embedding adapter**
  - First real adapter: Ollama local HTTP API ([ADR 004](docs/adr/004-ollama-local-inference.md)).
  - Batch requests and configure model, timeout and batch size.
  - Map provider failures to application errors.
  - Never log keys or source contents.
  - Unit tests use fakes; do not call Ollama in the default suite.

- [x] **5.4 Add ingestion orchestration**
  - Secure read → chunk → embed → persist → update status.
  - Represent failed state honestly; do not expose partial results as complete.

- [x] **5.5 Restore the deterministic reviewer baseline**
  - `make lint` and `make test` pass with a developer `.env` that selects Ollama.
  - Under pytest, `create_app()` defaults to `LexicalEmbedder` and `InMemoryWorkspace` so local env cannot select a real provider.
  - Frontend Node typings cover `process` in `vite.config.ts`.
  - Compose backend environment passes `EMBEDDING_PROVIDER`, Ollama timeout/batch, and archive limits from `config/app.env` interpolation.
  - Observed 2026-09-08: `make lint` green; `make test` — 90 backend passed (4 deselected), 9 frontend passed, coverage 81.15%.

### Tests first

- Unit tests use deterministic fake embeddings and no network.
- Metadata survives persistence correctly.
- Repository A cannot retrieve Repository B chunks.
- Re-ingestion does not duplicate chunks.
- Failed indexing cannot leave a false completed status.
- Top-k and empty results work correctly.
- Timeout and malformed provider responses map to controlled errors.
- Default `make test` stays fake when a local `.env` sets `EMBEDDING_PROVIDER=ollama`.
- Compose config (or a documented `docker compose config` assertion) includes `EMBEDDING_PROVIDER` and archive limits on the backend service.

### Verification

```bash
pytest backend/tests/unit/indexing backend/tests/unit/retrieval -q
make test-integration
make lint
make test
```

### Exit gate

- [x] Default `make test` makes zero real provider calls regardless of a local `.env` (**5.5**).
- [x] Real pgvector integration is tested.
- [x] Repository isolation and re-ingestion are proven.
- [x] Model and archive settings in `config/app.env` configure both host and Compose backend (**5.5**).
- [x] `make lint` is green without local workarounds (**5.5**).

### Suggested commits

```text
feat(storage): add repository and vector persistence
feat(indexing): add provider-independent embedding workflow
```

---

## Phase 6 — Grounded answering and citation validation

### Outcome

Answers use retrieved evidence, resist instructions contained in source files and expose only server-verified citations.

Default answers remain extractive unless `COMPLETION_PROVIDER=ollama`. Next priority is **Phase 9**.

### Tasks

- [x] **6.1 Specify prompt and context policy**
  - Treat repository text as untrusted data.
  - Delimit retrieved sources.
  - Define and **enforce** question, total-context and output limits at the use-case boundary (`MAX_QUESTION_CHARS`, `MAX_CONTEXT_CHARS`, `MAX_EXCERPT_CHARS`; output via `LLM_MAX_OUTPUT_TOKENS` on the Ollama adapter).
  - Require structured output and insufficient-evidence behaviour.

- [x] **6.2 Implement LLM adapter**
  - First real adapter: Ollama local HTTP API ([ADR 004](docs/adr/004-ollama-local-inference.md)).
  - Configure model, temperature, timeout and bounded retry policy.
  - Parse provider response into an internal result; reject loose or non-schema completions.
  - Do not send source, chunks or prompts to a hosted LLM API.
  - Composition root defaults to `ExtractiveCompleter`; set `COMPLETION_PROVIDER=ollama` for `OllamaCompleter` (`POST /api/chat`, `OLLAMA_CHAT_MODEL`).

- [x] **6.3 Implement answer use case**
  - Retrieve repository-scoped chunks.
  - Construct bounded context that respects the total-context budget.
  - Validate response schema strictly (not a best-effort parse) via `parse_completion`.
  - Match every citation to retrieved server-side metadata.
  - Reject or safely degrade fabricated citations.

- [x] **6.4 Add optional real-provider smoke test**
  - Skip unless explicitly enabled with a local Ollama process (`RUN_LLM_SMOKE=1`).
  - Keep it outside default CI (`pytest -m "not smoke"`). Do not require a hosted LLM API key.
  - `backend/tests/smoke/test_real_provider.py` covers embed + chat against local Ollama.

- [x] **6.5 Add answer-boundary regression tests**
  - Oversized questions and over-budget retrieved context are rejected or truncated at the application boundary.
  - Malformed or non-JSON completion output fails safely.
  - Instructions in comments, README or source strings cannot modify system policy.
  - Unknown chunk IDs, altered file paths and expanded line ranges are rejected.
  - Covered by `backend/tests/unit/application/test_answer_boundary.py`.

### Tests first

- Prompt clearly separates system instructions from source data.
- Instructions in comments/README cannot modify system policy.
- No retrieved evidence returns insufficient evidence without an LLM call where appropriate.
- Valid citations are accepted.
- Unknown chunk IDs, altered file paths or expanded line ranges are rejected.
- Malformed structured output fails safely.
- Timeout/retry exhaustion produces a controlled application error.
- Context selection respects its budget.

### Verification

```bash
pytest backend/tests/unit/answering -q
make test
make lint
```

Optional, explicitly enabled:

```bash
RUN_LLM_SMOKE=1 pytest backend/tests/smoke/test_real_provider.py -q
```

### Exit gate

- [x] Every normal answer has server-verified citations.
- [x] Unsupported answers are not fabricated.
- [x] Prompt-injection and citation-forgery regression tests pass (**6.5**).
- [x] Question and total-context limits are enforced (**6.1**).
- [x] Default answering unit tests remain network-free.

### Commit

```text
feat(answering): add grounded answers with verified citations
```

---

## Phase 7 — FastAPI contract

### Outcome

Thin API adapters expose the implemented use cases with safe validation and errors.

### Initial endpoints

```text
POST /api/repositories
GET  /api/repositories/{repository_id}
POST /api/repositories/{repository_id}/questions
GET  /api/health/live
GET  /api/health/ready
```

### Tasks

- [ ] **7.1 Define request, response and error contracts**
  - Use explicit Pydantic response models for upload, status and question handlers (currently they return `dict`).
  - Use stable machine-readable error codes and safe messages.
  - OpenAPI must describe those models.

- [ ] **7.2 Implement repository upload/status adapters**
  - Enforce HTTP content type and configured upload size **before** the entire request body is buffered.
  - Wrong content type returns `415`; excessive body returns `413` without retaining the full oversized payload.

- [x] **7.3 Implement question adapter**
  - Validate request and map application result without adding business rules.

- [ ] **7.4 Implement correct health semantics**
  - Liveness tests process health only.
  - Readiness reports required dependencies/configuration.
  - Remaining: `GET /api/health/ready` is not implemented.

- [ ] **7.5 Apply boundary controls**
  - Configured CORS allowlist.
  - Correlation ID.
  - Safe exception mapping.
  - Document rate limiting as a production requirement or add a small justified implementation.
  - Done: CORS allowlist (localhost/127.0.0.1 twin) with API tests. Remaining: correlation IDs. Rate limiting is listed as production follow-up in README.

### Tests first

- Valid upload returns the documented schema/status.
- Wrong content type returns `415`; excessive body returns `413` before the body is fully retained.
- Invalid data returns `422`; missing repository returns `404`.
- Valid question returns answer and citation contract.
- Known infrastructure failure returns safe `5xx` without internal details.
- CORS allows only configured origins.
- Liveness remains live during a dependency failure; readiness does not.

### Verification

```bash
pytest backend/tests/api -q
make lint
make test
```

### Exit gate

- [ ] OpenAPI accurately describes the API (response models, not `dict`).
- [x] Routes contain translation/orchestration only.
- [ ] Upload size is rejected before the entire body is buffered.
- [ ] Error responses leak no stack, prompt, key or provider payload.
- [x] API tests use fakes and remain deterministic.

### Commit

```text
feat(api): expose secure repository question API
```

---

## Phase 8 — React user interface

### Outcome

The complete workflow is understandable, accessible and demo-ready.

Keep UI creativity small: visible indexing/answering states, starter-question chips, a stronger evidence/source panel, honest failed-ingestion handling, and a controlled sample repository. Do not expand into unused product surface.

### Tasks

- [ ] **8.1 Add typed API client**
  - Keep transport and UI state separate.
  - Handle request timeouts, cancellation and mapped errors (timeouts and cancellation are not implemented; errors are mapped).

- [x] **8.2 Build repository upload/status flow**
  - Accessible file selection, progress, indexed/ignored summary and recoverable errors.
  - Failed indexing must be visually distinct from a successful summary and from a transport error.

- [x] **8.3 Build question/answer flow**
  - Starter-question chips after a successful index.
  - Visible loading/answering feedback (not only a disabled submit control).
  - Answer and insufficient-evidence states.
  - Follow-up: chips are still the fixture `list_items` list; **13.8** makes them repository-specific.

- [x] **8.4 Build source inspector**
  - Show cited path, line range and escaped excerpt.
  - Do not label similarity as model confidence.

- [x] **8.5 Complete accessibility and responsive review**
  - Keyboard operation, focus management, semantic labels, contrast and usable small-screen layout.

- [x] **8.6 Reviewer-demo polish**
  - Stronger evidence/source panel as the primary cited-answer surface.
  - Controlled sample repository (or a documented pointer to the Phase 9 fixture) so a reviewer does not invent a ZIP.
  - Track screenshots of upload, indexing, cited answer, source inspector and insufficient-evidence (Phase 12.4 records the files).
  - Keep the visual design small and product-like; the current `App.tsx` shell is functional but basic.

### Tests first

- Invalid file selection is explained.
- Submit controls disable correctly during work.
- Ingestion summary renders from API data.
- Empty questions cannot be submitted.
- Citation activation opens the matching excerpt.
- Insufficient evidence is visually distinct from a failure.
- API failure can be retried.
- Source containing HTML/script text is rendered harmlessly.
- Critical workflow is keyboard accessible.

### Verification

```bash
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test:coverage
make test
```

### Exit gate

- [x] Core workflow requires no reviewer explanation (**8.6**).
- [x] All asynchronous states have visible feedback (**8.1–8.3**, **8.6**). Note: **8.1** timeouts/cancellation still open.
- [x] Citations are easy to inspect.
- [x] Accessibility/component tests pass (**8.5**).

### Suggested commits

```text
feat(web): add repository upload workflow
feat(web): add grounded chat and source inspection
```

---

## Phase 9 — Evaluation, end-to-end and adversarial verification

### Outcome

The integrated system has repeatable evidence for functional, retrieval and defensive behaviour.

Do this after answer-boundary work (**6.1** / **6.3** / **6.5**) and before finishing UI polish (**8.5** / **8.6**), so evaluation and E2E prove the conversational RAG journey rather than extractive fallback.

### Tasks

- [x] **9.1 Create controlled fixture repository**
  - Include representative endpoints, service calls, configuration and deliberate irrelevant areas.
  - Ensure it contains no copied proprietary code or secrets.
  - Tree: `sample-data/fixture-repository/` (see `docs/evaluation.md`).

- [x] **9.2 Create evaluation dataset**
  - Known-answer questions with expected source files/symbols.
  - Unsupported questions expected to produce insufficient evidence.
  - Prompt-injection source examples.
  - Dataset: `sample-data/evaluation/dataset.json` (schema locked by `backend/tests/evaluation/test_dataset.py`).

- [x] **9.3 Add retrieval evaluation runner**
  - Measure source hit rate at `k`, citation validity, insufficient-evidence outcome and latency.
  - Record model/embedding/configuration versions.
  - Establish an initial evidence-based threshold; never invent a target result.
  - Package: `codebase_assistant.evaluation`; gate via `make test-evaluation`.

- [x] **9.4 Add deterministic browser E2E**
  - Upload → index → question → cited source.
  - Run against fake model providers.
  - Playwright suite under `e2e/`; gate via `make test-e2e`.

- [x] **9.5 Execute adversarial matrix**
  - Hostile ZIPs, nested secrets, prompt injection, citation forgery, oversized input, unavailable database/provider, repeated upload and escaped source rendering.
  - Consolidated regressions: `backend/tests/adversarial/test_matrix.py` (+ existing frontend XSS excerpt test).

### Verification

```bash
make test-evaluation
make test-e2e
make verify
```

### Exit gate

- [x] Critical workflow passes end-to-end.
- [x] Evaluation results are repeatable and recorded in `docs/evaluation.md`.
- [x] Failed/unsupported cases are visible and honest.
- [x] Residual risks are documented.

### Commit

```text
test: add retrieval evaluation and adversarial journeys
```

---

## Phase 10 — Observability and operational readiness

Do not start this phase until **Phase 13** exit criteria are met (or the developer explicitly reorders).

### Outcome

Important behaviour can be diagnosed without leaking code, prompts or secrets.

Add only the minimum that demonstrates production judgement: correlation IDs, a few structured operation events, and redaction tests. Do not introduce an observability vendor, dashboards or a metrics platform for this project stage.

### Tasks

- [ ] **10.1 Add structured event logging**
  - Correlation ID, operation name, duration, counts, status and safe error category.

- [ ] **10.2 Add operational measurements**
  - Ingestion, chunking, embedding, retrieval, model and total durations.
  - Token usage when safely available.

- [ ] **10.3 Prove log redaction**
  - Test that credentials, source content, prompts and model response bodies are absent.

- [ ] **10.4 Document production telemetry**
  - OpenTelemetry traces/metrics/logs, dashboards and alerts as production follow-up.

### Tests first

- Correlation ID is returned/propagated.
- Required safe fields appear in captured structured logs.
- Sentinel secret/source strings never appear in logs.
- Provider error is categorised without leaking its raw payload.

### Verification

```bash
pytest backend/tests/unit/observability backend/tests/api -q
make verify
```

### Exit gate

- [ ] A failed request can be traced by ID.
- [ ] Timing/count events are available.
- [ ] Sensitive log tests pass.
- [ ] No observability vendor is required for local use.

### Commit

```text
feat(observability): add privacy-conscious operational telemetry
```

---

## Phase 11 — Container hardening and clean-room setup

### Outcome

A reviewer can run the application from a fresh checkout using the documented path.

Compose setting parity with `config/app.env` is **5.5**, not this phase. Here, add only non-root images, health checks, `.dockerignore`, and a clean-room README walkthrough. Do not expand into Kubernetes or extra services.

### Tasks

- [ ] **11.1 Harden container builds**
  - Multi-stage builds, non-root users, minimal runtime contents and health checks.
  - Locked dependencies and effective `.dockerignore` files.

- [ ] **11.2 Validate Compose lifecycle**
  - Start, health, migration, stop and volume behaviour.

- [ ] **11.3 Perform clean-room setup**
  - Clone/copy to a fresh temporary location.
  - Follow README without relying on undeclared machine state.
  - Correct documentation rather than using undocumented workarounds.

- [ ] **11.4 Run final security scans**
  - Source, secrets, dependencies and built images.
  - Triage findings; remediate or document risk acceptance accurately.

### Verification

```bash
docker compose config
docker compose build --no-cache
docker compose up -d
docker compose ps
docker compose exec backend id
make verify
make security
docker compose down
```

### Exit gate

- [ ] Clean setup succeeds from README alone.
- [ ] Runtime containers do not run as root.
- [ ] Images contain no copied `.env`, Git history or development secrets.
- [ ] No unresolved critical finding exists.

### Suggested commits

```text
build: add reproducible non-root containers
docs: verify clean local setup
```

---

## Phase 12 — Public documentation and evidence

### Outcome

The repository documents every project requirement with evidence and authentic reasoning.

Prefer a shorter, human-centred README over repeating the full plan. Distil the AI log into two or three specific accepted/changed/rejected examples. Screenshots are required evidence; none are tracked yet.

### Tasks

- [x] **12.1 Reconcile README with implementation**
  - Setup, architecture, RAG decisions, guardrails, quality, observability, productionisation, standards followed/skipped, limitations and future work.
  - Remove planned claims that were not implemented.
  - Rewrite the opening as a short narrative a new reader can scan: what it does, how to run it, what is still extractive vs conversational, and what was deferred on purpose.
  - 2026-09-08: README rewritten with architecture + request-flow diagrams, a `make help` command list, and the remaining-work order. Re-check this box if later phases contradict the README.

- [x] **12.2 Complete AI-assisted development account**
  - Summarise actual tools and uses from `AI_DEVELOPMENT_LOG.md`.
  - Give two or three specific examples of AI suggestions accepted, changed or rejected, with the verification used.
  - Explain human control. Do not describe this file as fully human-written if an AI helped draft it.

- [x] **12.3 Complete decision/evaluation evidence**
  - ADRs and threat model were already current from **13.10**.
  - `docs/evaluation.md` and `docs/engineering-journal.md` record observed hermetic eval (13.9) and host Playwright (2026-09-08).

- [x] **12.4 Capture media**
  - Live tic-tac-toe screenshots: [`docs/screenshots/01-upload.png`](docs/screenshots/01-upload.png), [`02-ingestion-summary.png`](docs/screenshots/02-ingestion-summary.png), [`03-cited-answer.png`](docs/screenshots/03-cited-answer.png), [`04-source-inspector.png`](docs/screenshots/04-source-inspector.png), [`05-directory-structure.png`](docs/screenshots/05-directory-structure.png).
  - Insufficient-evidence remains in Playwright (`make test-e2e`), not in the README gallery.
  - Optional video: not created.

- [ ] **12.5 Perform read-only agent review**
  - Ask the agent to classify findings as blocking, important or optional.
  - Review project coverage, correctness, SOLID, OWASP, LLM threats, tests, Sonar-style maintainability, setup and unsupported README claims.
  - Approve fixes individually; do not allow uncontrolled final rewrites.

- [x] **12.6 Give the project a standalone public identity**
  - Use **Codebase Intelligence Assistant** as the README heading.
  - Describe the product without relying on external brief terminology.

### Final review prompt

```text
Perform a read-only final release review. Do not edit files.

Assess:
1. every project requirement against concrete repository evidence;
2. correctness and usability;
3. modularity, SOLID and unnecessary abstraction;
4. OWASP web and LLM-specific risks;
5. test behaviour and missing failure paths, not coverage alone;
6. Sonar-style reliability, maintainability, duplication and security concerns;
7. container, dependency and CI risks;
8. README claims versus implemented behaviour;
9. clean setup reproducibility;
10. unnecessary complexity that should be removed.

Classify each finding as blocking, important or optional. Cite exact files.
Recommend the smallest appropriate correction. State when no evidence supports
a conclusion. Do not make changes.
```

### Final verification

```bash
git status
git diff --check
git log --oneline --decorate -20
make verify
make test-integration
make test-evaluation
make test-e2e
make security
docker compose build --no-cache
docker compose up -d
docker compose ps
```

Manual scenarios:

- [ ] Valid repository indexes successfully.
- [ ] Invalid/hostile ZIP fails safely.
- [ ] Known question cites expected code.
- [ ] Unsupported question reports insufficient evidence.
- [ ] Prompt injection in source does not override policy.
- [ ] Re-ingestion does not duplicate results.
- [ ] Provider/database failure is safe and diagnosable.
- [ ] Source inspector renders hostile markup as text.

### Exit gate

- [ ] CI is green at the submitted commit.
- [ ] Worktree contains no unintended files or secrets.
- [ ] README commands were tested from a clean checkout.
- [ ] Project requirements are traceable to evidence.
- [x] Screenshots exist; optional video is linked if created.
- [ ] Limitations and skipped standards are explicit.
- [ ] AI log contains no invented activities.

### Suggested final commit

```text
docs: complete release evidence and productionisation notes
```

---

## Phase 13 — Repository-aware Q&A for core question types

### Outcome

A user can ingest a **supported** repository ZIP (the fixture, plus other archives that use the declared manifest and route formats below) and get grounded answers to the core product questions:

- what this repository does (overview);
- how a behaviour works;
- where functionality is implemented;
- which API endpoints exist (declared formats only);
- what dependencies the project declares (declared manifests only);
- what the directory structure / hierarchy is (bounded outline from indexed paths).

This is **not** a promise that every ecosystem ZIP will yield complete endpoint or dependency tables. Unsupported formats must be documented (README / 13.10) rather than implied by “arbitrary ZIP.”

The ask path stops treating every question as “embed the question, take top-k chunks, answer only from those excerpts.” Overview, structure, dependency and endpoint questions need **pinned excerpts plus card fields**. Vector search remains the default for locate/explain questions.

Do not add a second datastore, an ingest-time LLM summary, hybrid BM25, Tree-sitter, call graphs or an agent that walks the tree. Those stay deferred unless evaluation after this phase proves they are necessary.

### Trust boundary (card)

Treat the card’s **schema and provenance** as trusted application work: which fields exist, that `outline_paths` is a bounded list of already-indexed relative paths, language **counts**, truncation flags, and that extractors ran at ingest.

Treat **every repository-derived string** as untrusted data, including after extraction: `readme_excerpt`, manifest name and description, dependency names, endpoint method/path strings, symbols, and copied source snippets. They must not override system prompt policy (existing **6.5**). Delimit them in the prompt the same way as retrieved excerpts: data, not instructions.

Do **not** describe the whole card or “derived repository index” as trusted application data.

### Supported extractors (declared formats)

| Kind | Supported | Unsupported (document, do not silently invent) |
|---|---|---|
| Dependencies | `package.json` (`dependencies` / `optionalDependencies` / `devDependencies`), PEP 621 `pyproject.toml` `[project]`, `requirements.txt` lines | Lockfile graphs, `Cargo.toml`, `go.mod`, Poetry-only / setup.py-only, undocumented package managers |
| Endpoints | Comment/docstring `METHOD /path` (fixture `GET /items`, `POST /items`); FastAPI/Flask/Starlette `@app.get` / `APIRouter`; Express `app.get`/`router.`; Spring `@GetMapping` / `@RequestMapping` | Other frameworks, generated OpenAPI only, routes that exist only at runtime |

### Approved design (do not reopen per task)

| Decision | Choice | Why | Rejected alternative |
|---|---|---|---|
| Generated artefacts | Ignore lockfiles and minified bundles at source-policy time | `package-lock.json` currently dominates retrieval for generic questions | Prompt-only “ignore lockfiles” (fails when lockfile is the only hit) |
| Repo understanding | Extractive **repository card** at ingest from README, manifests, indexed paths, and bounded extractors | Stable overview/structure/route/dep evidence without a second model call | Ingest-time Ollama architecture summary (latency, injection, cost) |
| Persistence | JSON card on the existing repository summary (Alembic JSONB + in-memory store) | One datastore; ADR 002 unchanged | Separate outline table or vector of a fake `INDEX.md` |
| Routing | Deterministic **question intent** (rules, not an LLM classifier) | Tests stay hermetic; no extra provider | Always vector; or LLM-as-router |
| Exact lookup | Repository-scoped **get chunks by path** (`chunks_for_paths`), then prefer chunks overlapping stored line ranges | Search port was vector-only; pinning README/handlers needs exact retrieval to keep citation verification | Filename heuristics only; ask-time full-tree rescan |
| Structure answers | Outline is a **first-class derived-evidence field** on the card (`outline_paths`). Chat answers still cite at least one **real indexed file** from pinned outline/README chunks | `GroundedAnswer` requires verified citations; a general uncited-answer exception would weaken that control | Empty-citation exception; synthetic `.codebase-assistant/index.md`; dropping structure Q&A from the current scope |
| Endpoints / deps | Bounded extractors over accepted files; store **declaring file + 1-based line range** (and thus chunk/citation metadata) | The system must be able to cite the declaring file, not only know that a route/dep exists | Universal AST / language servers; names-only with no provenance |
| Starters | Frontend chips from the card + intent templates | Hardcoded `list_items` chips are fixture-only | Per-question LLM suggestions |
| ADR | No new ADR unless this phase later adds hybrid search or ingest-time LLM | Intent routing and JSONB on `repositories` are reversible | Rewriting ADR 002 |

### Intended task order vs what already shipped

Ideal order: **card + extractors → persist → intent → exact lookup / context → prompt policy → starters → evaluation**.

Shipped: **13.1** lockfiles; **13.2** card including **dependency names**; **13.3** persist; **13.4** intent; **13.5** `chunks_for_paths` plus heuristic pins. Remaining **13.6** adds endpoint extractors and declaring-file/line provenance (do not rebuild 13.2 name parsing), then switches pin lists to those records. Do not renumber completed tasks.

### Question types and evidence

| Intent | Example questions | Context to assemble | Completer role |
|---|---|---|---|
| `overview` | “What does this repo do?” | Pin README + declaring manifest files via `chunks_for_paths`; card strings in the prompt as untrusted data | Summarise purpose from those files only; never lockfiles |
| `structure` | “What is the directory structure?”, “What is the hierarchy?” | Card `outline_paths` (derived evidence) **and** pin real outline/README chunks so citations exist | Present the bounded tree; do not invent folders; still emit verified file citations |
| `dependencies` | “What dependencies does this use?” | Pin declaring manifest files from stored provenance (`package.json` / `pyproject.toml` / `requirements.txt`) | List extracted names; cite the declaring file |
| `endpoints` | “What API endpoints exist?” | Pin declaring handler files from stored route records (method, path, file, line range) | List only extracted routes; cite the declaring file |
| `locate` | “Where is X implemented?” | Existing vector top-k (lockfiles already gone) | File/symbol + citation of the expected file |
| `explain` | “How does Y work?” | Vector top-k, optionally pin README/entry files when ranked low | Explain from excerpts; insufficient evidence if missing |

Unrecognised questions default to `explain` (current vector path). Ambiguous questions may attach card fields **in addition to** vector hits, still inside `MAX_CONTEXT_CHARS`.

If extractors found no endpoints/deps, do not invent them; fall back to vector or (from **13.7**) `insufficient_evidence`.

### Tasks

- [x] **13.1 Exclude generated lockfiles and minified bundles**
  - Extend `classify_source_file` so these are ignored with a stable reason (e.g. `generated_lockfile` / `generated_bundle`): `package-lock.json`, `npm-shrinkwrap.json`, `yarn.lock`, `pnpm-lock.yaml`, `Cargo.lock`, `poetry.lock`, `composer.lock`, `go.sum`, `Pipfile.lock`, `*.min.js`, `*.min.css`.
  - Keep `package.json`, `pyproject.toml`, `requirements.txt` and README files.
  - README already claims generated files are excluded; make the policy match.
  - Expected files: `backend/src/codebase_assistant/ingestion/source_policy.py`, `backend/tests/unit/ingestion/test_source_policy.py`.

- [x] **13.2 Build an extractive repository card at ingest**
  - From accepted members only, collect bounded fields: display name, README excerpt (`MAX_EXCERPT_CHARS` or a dedicated cap), manifest `name`/`description`/dependency names, language histogram, bounded directory outline from relative paths.
  - Trust: schema/counts/outline structure are application-derived; README/manifest/dependency **strings** remain untrusted.
  - No LLM call. Truncate the tree (depth and entry count) so a 500-file ZIP cannot blow the prompt.
  - Dependency **names** from the three supported manifests landed here. **13.6** must not duplicate that parser; it adds provenance and endpoints.
  - Expected files: `backend/src/codebase_assistant/application/repository_card.py` and unit tests.

- [x] **13.3 Persist the card on the repository summary**
  - Add the card to `IngestArchiveResult` / list-get API if the UI starters need it (keep the public schema small: outline paths, languages, manifest name, readme excerpt optional).
  - Alembic revision on `repositories` (JSONB). Additive JSON fields later (**13.6**) do not need a new migration. Update memory and Postgres adapters.
  - Re-ingest of the same display name must replace the card with the new archive.
  - Expected files: contracts, `adapters/memory.py`, `adapters/postgres.py`, new migration, API mapping tests.

- [x] **13.4 Classify question intent deterministically**
  - Pure function: question text → `overview` | `structure` | `dependencies` | `endpoints` | `locate` | `explain`.
  - Rule-based (phrases such as “what does this repo/project/codebase do”, “directory structure”, “hierarchy”, “dependencies”, “package.json”, “API endpoints”, “routes”, “where is”, “how does”).
  - Tests for each supported question type plus a default `explain` case.
  - Expected files: `backend/src/codebase_assistant/application/intent.py` (or equivalent) and unit tests.

- [x] **13.5 Assemble intent-routed context in `ask_question`**
  - Search/store port: **exact repository-scoped lookup** `chunks_for_paths(repository_id, paths)` in addition to vector `search`. HTTP already passes the workspace store.
  - `overview` / `structure` / `dependencies` / `endpoints`: pin matching files; skip vector when pins exist; otherwise fall back to vector.
  - `locate` / `explain`: keep current embed → search → `select_context_chunks`.
  - Still enforce `AnswerLimits`. Card text in the prompt counts toward the context budget and remains untrusted data.
  - A test that indexes README + noisy JSON and asks “what does this repo do?” must retrieve README, not dependency noise.
  - Endpoint pins in this task used filename heuristics (`handler`, `route`, …). **13.6** replaces that with stored declaring files.
  - Expected files: `application/ask.py`, `application/prompt.py`, `application/ports.py`, memory/Postgres adapters, `test_intent_context.py`.

- [x] **13.6 Extract endpoints; attach declaring-file provenance (do not rebuild 13.2 dep names)**
  - Bounded regex over accepted member text: HTTP method + path including fixture docstrings `GET /items`, `POST /items`; declared framework patterns in the supported table.
  - Store capped `endpoints` on the card: `method`, `path`, `file_path`, `start_line`, `end_line`.
  - Keep 13.2 dependency **name** extraction. Extend each name with declaring `file_path` and line range so ask-time can pin and cite the manifest chunk.
  - Switch endpoint/dependency pin lists in `ask_question` to those records. Prefer chunks that overlap the stored line range when a path has several chunks.
  - Old JSON cards without the new fields load as empty endpoints / names-only deps until re-ingest. No new Alembic revision.
  - Expected files: extractor module (or `repository_card.py`), card payload round-trip, `ask.py` pin lists, unit tests (Python handler, `package.json`, `pyproject.toml`).

- [x] **13.7 Prompt policy per intent**
  - Overview: answer purpose from README/manifest excerpts; if those files are absent, `insufficient_evidence` rather than narrating tooling from a random chunk.
  - Structure: reproduce the bounded `outline_paths`; do not invent directories; still require at least one verified citation of a pinned indexed file. **Do not** add a `GroundedAnswer` empty-citation exception.
  - Endpoints / dependencies: list only extracted items; cite the declaring file.
  - Explain/locate: keep the existing grounded-explanation instructions.
  - Lockfiles and vendor lists must not be treated as product description.
  - Card strings in the prompt stay untrusted (same delimiter rules as excerpts).
  - Expected files: `application/prompt.py`, `test_answer_limits.py` / prompt tests. No domain exception test.

- [x] **13.8 Repo-aware starter chips**
  - Replace hardcoded fixture questions in `ChatThread.tsx`.
  - Build 3–4 chips from the selected repository card / indexed paths (overview, structure, endpoints or dependencies when the card has extracted items, otherwise a locate-style question from a real indexed filename).
  - Fixture still supports “Where is list_items defined?” **when that path/symbol exists**.
  - Expected files: `frontend/src/app/components/ChatThread.tsx` (or a small helper), `frontend/tests/app/App.test.tsx` and a unit test for chip selection.

- [x] **13.8a Ground controller-to-database architecture-flow answers**
  - Add a deterministic `architecture_flow` question intent for requests such as “controller to database” and “end-to-end logic path for all controllers”.
  - Pin bounded, repository-scoped controller, service, repository/DAO, entity/model and persistence-configuration files found in the indexed outline; do not add a call-graph framework or ingest-time LLM.
  - Prompt for one traceable section per evidenced controller: entry method/route → service (when present) → repository/DAO → entity/model → database boundary. Explicitly say when a layer is bypassed or unsupported rather than inventing it.
  - Begin with a short plain-language summary of the overall request/persistence design before the per-controller detail; a bare arrow list is not a sufficient answer.
  - Normalise a flat but otherwise valid model response into one Markdown section per indexed controller, preserving the model text and making omitted method-level detail explicit.
  - Preserve verified citations and `MAX_CONTEXT_CHARS`; return insufficient evidence when no controller source is indexed.
  - Expected files: `application/intent.py`, `application/ask.py`, `application/prompt.py`, focused unit tests.

- [x] **13.8b Render safe Markdown-style answer cards**
  - Return deterministic structure answers as a Markdown heading plus fenced tree block.
  - Render headings, paragraphs, simple lists, inline code and fenced blocks as escaped React elements; never render repository/model HTML with `dangerouslySetInnerHTML`.
  - Show fenced directory trees in a labelled, responsive card while preserving whitespace and citation-marker activation.
  - Add component tests for semantic headings/tree blocks, citation markers and hostile HTML remaining inert. Restore the configured frontend coverage gate.
  - Expected files: `application/ask.py`, `frontend/src/app/components/ChatMessage.tsx` (or a small renderer), `frontend/src/app/App.css`, backend/frontend tests.

- [x] **13.8c Ground named code-unit method inventories**
  - Classify method/function inventory questions separately from generic `explain` retrieval. “What does VisitController do?” is the regression example, not a universal controller abstraction.
  - Resolve the requested class/module/file name against repository-scoped indexed paths (including spaced/case/underscore variants) and pin all of the matched file's available chunks in line order. The same mechanism must support names such as `InventoryService` or `user_repository.py` without new intent types.
  - Do not claim a complete count when context limits truncate the file; return insufficient evidence when the requested code unit is absent.
  - Require a short plain-language code-unit summary, an explicit evidenced method/function count and a Markdown table with one row per evidenced callable (name, route/trigger, purpose, collaborators/entities). Do not count fields, constructors or nested-class methods as top-level actions.
  - Validate that the completion actually contains the summary, count and renderable table; degrade to insufficient evidence instead of presenting a confident partial inventory as complete.
  - Render this constrained table as escaped semantic React table elements inside a responsive card; raw HTML remains inert and citation markers remain interactive.
  - Add backend prompt/context regressions for a method below the first chunk and frontend component tests for table semantics and hostile cell text.
  - Expected files: `application/intent.py`, `application/ask.py`, `application/prompt.py`, `frontend/src/app/components/MarkdownAnswer.tsx`, `frontend/src/app/App.css`, focused backend/frontend tests.

- [x] **13.9 Evaluation and answer correctness (not retrieval-only)**
  - Hermetic eval currently records `outcome_pass_rate` `0.5`, `grounded_answer_file_hit_rate` `0.0`, `insufficient_evidence_correct_rate` `0.0` (lexical + extractive, 2026-09-08). Citation validity `1.0` and source hit-at-k `0.8` are **not** sufficient to close this task.
  - Extend `sample-data/evaluation/dataset.json` with grounded cases: overview (README), how `create_item` works (already present), where `find_by_name` lives (already present), endpoints (`GET /items`, `POST /items` in `src/api/handlers.py`), dependencies (add a small `pyproject.toml` to the fixture if none exists), directory structure (outline + at least one real cited file).
  - Add a small layered-code fixture or equivalent hermetic case for controller-to-database flow; require every fixture controller to appear and require absent service/method hops to be reported rather than invented.
  - Add a multi-chunk named code-unit case that requires a summary, accurate evidenced callable count and one table row per fixture callable.
  - Keep existing IE / injection cases.
  - **Required behaviour:** grounded cases must cite an expected file (and symbol in text or excerpt where the dataset names one). IE-expected cases must return `insufficient_evidence`. Record observed rates; raise numeric gates only with a new observed baseline — but **do not mark 13.9 done** while locate still cites the wrong file or IE cases still return confident answers.
  - Playwright `e2e/tests/upload-ask.spec.ts`: after “Where is list_items defined?”, assert the visible citation path includes `src/api/handlers.py` and the excerpt or answer contains `list_items`. Opening “some” citation is not enough.
  - Disambiguate the Playwright “New repository” locator; the current shell exposes desktop and empty-state buttons with the same accessible name.
  - Update `test_fixture_repository.py` / `docs/evaluation.md` / dataset schema tests.
  - Re-run `make test-evaluation` and `make test-e2e`.
  - 2026-09-08: hermetic eval observed `outcome_pass_rate` 1.0, `grounded_answer_file_hit_rate` 1.0, `insufficient_evidence_correct_rate` 1.0, `list-items-location` cites `src/api/handlers.py`. Empty-state control is **Ingest a ZIP**. Host `make test-e2e` — 1 passed (arm64 Chromium).

- [x] **13.10 Documentation**
  - README retrieval: intent routing, extractive card, **supported vs unsupported** formats, limitations if a ZIP has no README/manifest/declared routes. (README 2026-09-08 covers this; keep it aligned after 13.9 numbers land.)
  - `docs/threat-model.md`: card schema/provenance trusted; repository-derived strings untrusted; exact path lookup is repository-scoped.
  - `docs/evaluation.md`: new cases and observed results (`TBD` until run).
  - Engineering journal checkpoint after the phase exit gate.

### Tests first (illustrative red cases)

- `package-lock.json` and `yarn.lock` are ignored; `package.json` is accepted.
- Ingesting the fixture produces a card whose README excerpt mentions the inventory service and whose outline includes `src/api/handlers.py`.
- “What does this repo do?” selects README (and card), not a lockfile or `vendor/`.
- “What is the directory structure?” lists `src/api/handlers.py`, does not invent `node_modules`, and still has a verified source citation.
- “What API endpoints exist?” includes `GET /items` and `POST /items` from the fixture handlers and cites `src/api/handlers.py`.
- “What dependencies does this project declare?” cites `pyproject.toml` / `package.json`, never a lockfile.
- “Where is list_items defined?” cites `src/api/handlers.py` and mentions `list_items` (eval + e2e, not only “a citation opened”).
- Unsupported questions (`oauth-unsupported`, `payment-unsupported`) return `insufficient_evidence`.
- Starter chips for a repo whose indexed paths are `src/app.py` do **not** show `list_items`.
- Prompt-injection in README still cannot override system policy.

### Verification

```bash
pytest backend/tests/unit/ingestion/test_source_policy.py -q
pytest backend/tests/unit/application -q
pytest backend/tests/evaluation -q
npm --prefix frontend run test
make lint
make test
make test-evaluation
make test-e2e
```

### Exit gate

- [x] Generated lockfiles are not indexed.
- [x] Overview answers for the fixture cite README, not generated manifests.
- [x] Structure, endpoints and dependency questions have hermetic tests against the fixture (or added fixture manifests). Structure answers keep verified citations.
- [x] Locate answers for `list_items` cite `src/api/handlers.py` (unit/eval 2026-09-08; host `make test-e2e` 1 passed 2026-09-08).
- [x] IE-expected eval cases return insufficient evidence (or 13.9 records a new honest baseline **and** tests that lock the intended behaviour).
- [x] Starter chips are repository-specific.
- [x] Threat model and README match the implemented retrieval policy and supported formats.
- [x] No ingest-time LLM, no extra datastore, no uncited `GroundedAnswer` exception.

### Suggested commits

```text
fix(ingestion): ignore lockfiles and minified bundles
feat(ingest): store extractive repository card
feat(ask): route overview structure dependency and endpoint questions
feat(ingest): extract endpoints with declaring-file provenance
feat(web): suggest questions from the repository card
test: require correct cited files in evaluation and e2e
```

Suggested branch: `feat/phase-13-repository-aware-question-routing`

---

## Commit and review policy

Commit after a coherent task is green, not after every generated file and not as one final bulk commit.

Put the work on a dedicated branch whose name a reviewer can understand without the chat history. Do not commit Phase work to `main` unless the developer asks for that.

Branch names use lowercase hyphenated words, optionally prefixed with `docs/`, `feat/`, `fix/`, `test/`, `build/` or `ci/`. They name the phase or feature and the outcome.

Examples:

```text
docs/phase-0-repository-baseline-and-decisions
feat/phase-2-domain-and-provider-contracts
feat/phase-3-secure-zip-ingestion
fix/reject-parent-path-archive-members
```

Avoid `wip`, `tmp`, `p0`, `updates` and personal nicknames.

Before committing:

```bash
git status
git diff --check
git diff
```

Run the focused tests plus checks affected by the change. At each phase end, run `make verify`.

Commit format:

```text
type(optional-scope): imperative summary
```

The summary must be readable English. Preferred types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `refactor`, `test`.

Good: `docs: record repository baseline and initial architecture decisions`
Poor: `wip`, `misc`, `update files`

Do not rewrite or fabricate history to make TDD appear to have happened. The engineering journal and observed commands provide the detailed evidence; commits remain small and meaningful.

## Change-control record

Add entries when an approved fixed decision changes:

| Date | Decision changed | Reason | ADR | Approved by |
|---|---|---|---|---|
| 2026-09-04 | Backend runtime Python 3.12 → 3.14 | Newest interpreter on the implementation machine (observed `python3` 3.14.4) | [003](docs/adr/003-python-runtime.md) | Developer |
| 2026-09-04 | LLM/embedding runtime: local Ollama | Private repository text must not leave the organisation during analysis | [004](docs/adr/004-ollama-local-inference.md) | Developer |
| 2026-09-08 | Ask path is vector-only for every question | Overview/structure/dependency/endpoint questions failed (e.g. `package-lock.json` as “what this repo does”). Phase 13 adds extractive repo card + intent-routed context; vector search stays for locate/explain. No new ADR. | — | Developer |
| 2026-09-08 | Whole derived card described as trusted application data | Schema/provenance and counts are application-derived; README/manifest/dep/endpoint/symbol strings stay untrusted | — | Developer |
| 2026-09-08 | Structure answers may omit citations | Would weaken `GroundedAnswer`; outline is first-class derived evidence and chat answers still cite indexed files | — | Developer |
| 2026-09-08 | Phase 13 outcome for an arbitrary ZIP | Extractors cover declared manifests and route patterns only; document unsupported ecosystems | — | Developer |
| 2026-09-08 | 13.6 duplicate dependency-name extraction after 13.5 | Intended order is extractors before context; 13.2 already stores names; remaining 13.6 is endpoints + declaring-file/line provenance | — | Developer |
