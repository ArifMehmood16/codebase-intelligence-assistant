# AI-Assisted Development Log

This document records how AI tools contributed to the project. It is an engineering evidence log, not a claim that AI independently designed, implemented or verified the system.

The developer remains accountable for requirements, architecture, source review, security decisions, test validity and the published result.

## Logging principles

- Record meaningful AI-assisted work when it happens; do not reconstruct a flattering history at the end.
- Base entries on actual prompts, diffs, reviews and command results.
- State what the AI proposed, what the developer decided and how the outcome was checked.
- Include rejected or materially changed suggestions.
- Never claim a test, scan, review, command or metric unless it was observed.
- Do not paste secrets, credentials, private source code, personal data, full provider responses or unnecessary prompt contents.
- Use short prompt summaries where full prompts would expose sensitive or irrelevant material.
- AI-generated code receives the same review and quality gates as any other code.
- Use `TBD` for evidence not yet available.

## Development controls

For each agent-assisted implementation task:

- [ ] The agent read `AGENTS.md` and the relevant `PLAN.md` task.
- [ ] The requested scope was bounded.
- [ ] Proposed tests and files were reviewed before editing.
- [ ] The intended test was observed failing for the correct reason.
- [ ] The complete diff was inspected.
- [ ] Focused tests and relevant quality checks were run.
- [ ] Security/dependency implications were reviewed.
- [ ] Claims in documentation match observed behaviour.
- [ ] The human approved the final change and log entry.

## Tool register

Add exact tools and versions when known.

| Tool/model | Purpose | Data shared | Human control |
|---|---|---|---|
| ChatGPT/Codex | Initial product analysis, architecture, delivery-plan and governance-document drafting | High-level product requirements | Developer selected the scope, constrained it and reviews documents before use |
| Cursor (Grok 4.6) | Governance, implementation, tests, PLAN/README updates, git commit/push | Local repository files, git status and observed command output | Developer approves architecture/runtime decisions and reviews diffs |

## Entry 001 — Initial architecture and project planning

**Date:** 2026-09-04  
**Phase/task:** Pre-implementation planning  
**Tool/model:** ChatGPT/Codex  
**Status:** Draft documents created; no application code implemented

### Objective

Choose a bounded product that can demonstrate senior engineering judgement while remaining small and reliable, then prepare repository documents that allow the project to be implemented incrementally with coding agents.

### How AI assisted

- Compared possible product directions against simplicity, differentiation and engineering evidence.
- Recommended a code documentation assistant.
- Proposed a modular-monolith architecture and a limited MVP.
- Drafted `README.md`, `AGENTS.md`, `PLAN.md` and this development log.
- Proposed a TDD sequence, quality gates, OWASP/LLM security concerns, documentation checkpoints and commit boundaries.

### Human decisions and direction

- Required a simple solution that demonstrates senior-to-architect-level thinking.
- Required SOLID, OWASP, Sonar-style quality and TDD practices.
- Selected a document-first workflow: repository setup, README, execution plan, agent rules and AI log before implementation.
- Required the plan to be directly usable for agent-led incremental delivery and regular commits.
- Rejected an earlier answer because it was explanatory guidance rather than downloadable repository documents.

### Suggestions accepted in this draft

- Modular monolith rather than microservices.
- FastAPI backend, React/TypeScript frontend and PostgreSQL/pgvector.
- Direct, narrow provider ports rather than a large LLM orchestration framework.
- Python AST-aware chunking with a line-based fallback.
- Deterministic fake providers for the default automated suite.
- Secure ZIP ingestion and server-side citation validation as core trust controls.
- ADRs, threat model, evaluation evidence and a maintained AI development log.

### Suggestions deliberately excluded or deferred

- GitHub OAuth and remote cloning, because they expand the security and integration scope.
- Autonomous code modification and multi-agent application behaviour.
- Microservices, Kubernetes and dedicated vector infrastructure.
- Universal language parsing, knowledge graphs, reranking and hybrid retrieval before evaluation demonstrates a need.
- Authentication for the initial MVP; documented as mandatory production work.

### Verification performed

- Draft documents were later placed in the supplied repository (see Entry 002).
- No application tests, builds, scans or runtime verification have occurred.
- All technical choices remain subject to reconciliation with the supplied repository baseline in Phase 0.

### Evidence

- `README.md`
- `AGENTS.md`
- `PLAN.md`
- This entry
- Commit: see Entry 002

### Residual questions/risks

- Existing repository stack and instructions have not yet been inspected.
- Concrete LLM and embedding model selection is intentionally deferred until implementation.
- Dependency versions and exact commands must be validated against the actual repository.

## Entry 002 — Install governance documents in the supplied repository

**Date:** 2026-09-04  
**Phase/task:** PLAN.md 0.2  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed for document installation; Phase 0 exit gate remains open

### Objective

Install the drafted root governance documents in the starter repository, record that work in this log, and publish the first project commit.

### Context provided to AI

The working tree already contained the human-started document set: a replaced `README.md` plus untracked `AGENTS.md`, `PLAN.md` and `AI_DEVELOPMENT_LOG.md`. The supplied repository previously had source-specific starter material and a starter README. The developer asked to commit these changes, push them, and update this log. Later feature work is intended to land on dedicated branches.

### Prompt summary

Review current git changes, commit them with a conventional title and message, push to origin, and update the AI development log with what has been done so far.

### AI contribution

- Confirmed the diff is documentation only: product README, agent rules, TDD delivery plan and this log.
- Marked PLAN.md task 0.2 complete after the four root documents were present.
- Added this log entry and the Cursor tool-register row.
- Prepared the requested conventional commit and push of these documents to `origin/main`.

### Human decisions and changes

- Developer chose the code documentation assistant direction and the product name Codebase Intelligence Assistant.
- Developer started setup by placing the four governance documents before any application code.
- Developer requested a single baseline commit on `main`, with later work committed on feature branches.
- No application implementation was requested or added.

### Suggestions rejected or deferred

- Phase 0.1 repository inspection, engineering journal, directory skeleton and ADRs were not started in this change.
- Application scaffolding remains deferred to Phase 1.

### TDD evidence

- Not applicable: no behaviour or application tests exist yet.

### Verification performed

- `git status`, `git diff` and `git log` were run; the only pending files were the four governance documents.
- `git diff --check` was not required beyond reviewing the documentation diff.
- No `make`, test, lint or security commands were run because those targets do not exist yet.
- Source-specific starter material was left unchanged at that stage.

### Files changed

- `README.md` — replaced the starter welcome page with the planned product, architecture and limitations
- `AGENTS.md` — added agent working rules
- `PLAN.md` — added the TDD delivery plan; marked 0.2 complete
- `AI_DEVELOPMENT_LOG.md` — recorded planning (Entry 001) and this installation (Entry 002)

### Security, quality and limitations

- No secrets, credentials or application code were added.
- A source-specific private URL remained in the starter material at that stage; it was removed before public release.
- Phase 0 is not complete: baseline inspection, docs skeleton and ADRs are still outstanding.

### Evidence

- Tests: none
- Plan item: 0.2
- Commit: TBD until created

### Follow-up

- PLAN.md 0.1 inspect the supplied repository and record the baseline.
- PLAN.md 0.3 add only the directories needed for Phase 1.
- PLAN.md 0.4 record the first ADRs.

## Entry 003 — Phase 0 baseline, skeleton and ADRs

**Date:** 2026-09-04
**Phase/task:** PLAN.md 0.1, 0.3, 0.4
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Finish Phase 0 after a read-only inspection: record the repository baseline, add only `docs/` and `.gitignore`, write the first ADRs, and document the approved Python 3.14 runtime.

### Context provided to AI

The inspection found a documentation-only repository (five root markdown files, no application tooling). The developer then approved writing `docs/engineering-journal.md`, adding `docs/` plus `.gitignore` without empty backend/frontend packages, recording ADRs 001 and 002, and using the newest Python on the machine instead of 3.12.

### Prompt summary

First: inspect without modifying and report structure, tooling, tests, constraints, baseline results and conflicts. Second: use host Python 3.14, write the engineering journal, confirm 0.3 as docs + `.gitignore`, and confirm 0.4 ADRs.

### AI contribution

- Ran the Phase 0 inspection commands and documented exact missing-tooling failures.
- Drafted the engineering journal from observed output.
- Added `.gitignore` and ADRs 001–003.
- Updated README/PLAN Python 3.12 references and the change-control record.

### Human decisions and changes

- Approved the inspection findings before any write.
- Chose Python 3.14 (observed host `python3` 3.14.4) over the planned 3.12 pin.
- Restricted the skeleton to `docs/` and `.gitignore`; no empty application packages.
- Confirmed modular monolith and PostgreSQL/pgvector ADRs.
- Required this Phase 0 work on its own readable branch, and standing instructions that branch and commit wording stay understandable.

### Suggestions rejected or deferred

- Empty `backend/` and `frontend/` directories — deferred until Phase 1 populates them.
- `docs/threat-model.md` and `docs/evaluation.md` — deferred until they have content.
- Starting Phase 1 application code — not requested.

### TDD evidence

- Not applicable: Phase 0 is documentation and baseline recording.

### Verification performed

- Inspection commands and README/make/npm/pytest/compose outcomes were recorded in the previous read-only pass (see `docs/engineering-journal.md`).
- This change adds documentation and `.gitignore` only; `make verify` still does not exist.
- No application files were added.

### Files changed

- `docs/engineering-journal.md` — Phase 0 baseline
- `.gitignore` — secrets, Python/Node artefacts, OS files
- `docs/adr/001-modular-monolith.md`
- `docs/adr/002-postgres-pgvector.md`
- `docs/adr/003-python-runtime.md`
- `AGENTS.md` — branch and commit wording rules
- `README.md` — Python 3.14, `.gitignore` in the target tree, ADR pointer, readable-branch standard
- `PLAN.md` — 0.1/0.3/0.4 and exit gate checked; change-control row; readable branch/commit policy
- `AGENTS.md` — branch and commit wording rules
- `AI_DEVELOPMENT_LOG.md` — this entry

### Security, quality and limitations

- `.gitignore` excludes `.env` while keeping `.env.example`.
- Python 3.14 package compatibility is unverified until Phase 1 installs dependencies.
- ZIP-only ingest remains an intentional scope cut versus GitHub cloning or arbitrary local-file access.

### Evidence

- Tests: none
- Plan items: 0.1, 0.3, 0.4
- Commit: TBD until created

### Follow-up

- Phase 1.1 after human approval: minimal FastAPI app and first API test, on Python 3.14.

## Phase 0 AI usage summary

### AI-supported activities

- Compared product directions and drafted governance documents (Entry 001).
- Installed those documents in git (Entry 002).
- Inspected the supplied repository and recorded baseline command results (Entry 003).
- Drafted the engineering journal, `.gitignore` and ADRs 001–003 (Entry 003).

### Most useful contribution

- A bounded Phase 0 inspection that separated missing tooling from application failures, and kept empty package scaffolding out of the tree.

### Material output rejected or corrected

- Original Python 3.12 pin — replaced by the developer with Python 3.14.
- Empty `backend/` and `frontend/` roots — not added.

### Human-owned decisions

- Codebase Intelligence Assistant product direction.
- Modular monolith, PostgreSQL/pgvector, ZIP-only ingest.
- Python 3.14 runtime.
- Document-first workflow, dedicated readable branches, and plain-English commit subjects.

### Verification evidence

- Observed git history, file listing and failing README/make/npm/pytest/compose commands as recorded in `docs/engineering-journal.md`.
- No application tests exist yet.

### Learning carried forward

- Pin Python 3.14 in Phase 1 project metadata and containers.
- Treat README commands as invalid until Phase 1 implements them.
- Retain the original starter material during private development; remove it before public release.

## Entry 004 — Minimal FastAPI liveness endpoint

**Date:** 2026-09-04
**Phase/task:** PLAN.md 1.1
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Create a Python 3.14 backend project with a FastAPI application factory, a liveness endpoint, dependency locking, and one API test written first.

### Context provided to AI

Phase 0 was merged. The developer approved Phase 1.1 with pip/`pyproject.toml` locking, `GET /api/health/live` returning `{"status":"ok"}`, branch `feat/minimal-fastapi-liveness-endpoint`, and Python 3.14.

### Prompt summary

Proceed with Phase 1.1 from the approved defaults.

### AI contribution

- Wrote `test_liveness_returns_ok_status` before the application package existed.
- Added `backend/` with hatchling, FastAPI factory, liveness schema, and `requirements.lock`.
- Did not add empty domain/application packages, frontend, Compose or Make.

### Human decisions and changes

- Approved 1.1 before implementation.
- Chose pip + lockfile over uv/poetry (those tools are not on the machine).
- Chose the liveness path and body.

### Suggestions rejected or deferred

- `httpx2` as a test extra — extra transitive packages; Starlette still warns via FastAPI's TestClient. Deferred to quality tooling if it becomes a gate.
- Makefile, CI, frontend, PostgreSQL — later Phase 1 tasks.

### TDD evidence

- Failing test/command and expected reason: `python3 -m pytest backend/tests/api/test_health.py -q` → `ModuleNotFoundError: No module named 'codebase_assistant'`.
- Passing focused test/command: `backend/.venv/bin/pytest backend/tests/api/test_health.py` → `1 passed`.
- Refactoring performed after green: none beyond documenting the httpx2 warning.

### Verification performed

- `pip install -e ".[dev]"` on Python 3.14.4 succeeded, including a `pydantic_core` cp314 wheel.
- Focused pytest passed with two unfiltered deprecation warnings.
- `make verify` still does not exist.

### Files changed

- `backend/tests/api/test_health.py` — liveness contract
- `backend/src/codebase_assistant/main.py` — factory and liveness
- `backend/pyproject.toml`, `backend/requirements.lock`, `backend/.python-version`
- `README.md`, `PLAN.md`, `docs/engineering-journal.md`, `AI_DEVELOPMENT_LOG.md`

### Security, quality and limitations

- Liveness does not check the database or model providers.
- No secrets added.
- README Make commands are explicitly marked unimplemented.

### Evidence

- Tests: `backend/.venv/bin/pytest backend/tests/api/test_health.py` → 1 passed
- Plan item: 1.1
- Commit: TBD until created

### Follow-up

- Phase 1.2 after approval: minimal React/Vite shell and one component test.

## Entry 005 — Local Ollama for private repository analysis

**Date:** 2026-09-04
**Phase/task:** Provider decision (applies to PLAN.md 5.3 and 6.2)
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed as documentation; adapter not implemented

### Objective

Record the approved choice of a local LLM via Ollama, justified by privacy when analysing private repositories.

### Context provided to AI

Phase 1.1 was merged. The developer stated that a local LLM is required, that Ollama is the preferred solution, and that the justification is privacy: an internal deployment would pass private repositories for analysis.

### Prompt summary

Remember to use a local LLM; prefer Ollama; justify with privacy for private-repository analysis inside an organisation.

### AI contribution

- Drafted ADR 004 (Ollama as first real embed/complete adapter; ports unchanged; tests stay fake).
- Started `docs/threat-model.md` with the hosted-API vs in-network inference boundary.
- Updated README, PLAN, AGENTS and the engineering journal. Did not implement an Ollama client.

### Human decisions and changes

- Required local inference rather than a hosted LLM API as the default.
- Chose Ollama over other local runtimes for this project.
- Privacy for private source code is the stated reason.

### Suggestions rejected or deferred

- Hosted OpenAI/Anthropic as the default path.
- Wiring the adapter in this change — deferred to Phases 5.3 and 6.2.
- Picking concrete Ollama model tags — deferred until those phases run.

### TDD evidence

- Not applicable: documentation only.

### Verification performed

- No Ollama process was started and no model was pulled.
- No application tests were added or re-run for this change.

### Files changed

- `docs/adr/004-ollama-local-inference.md`
- `docs/threat-model.md`
- `README.md`, `PLAN.md`, `AGENTS.md`, `docs/engineering-journal.md`, `AI_DEVELOPMENT_LOG.md`

### Security, quality and limitations

- This records policy. Enforcement in code does not exist until the adapter lands.
- Model-weight download from Ollama’s library is called out as supply-chain, not as repo upload.

### Evidence

- Tests: none
- ADR: 004
- Commit: `a6e96be`
- Pull request: merged `#3`

### Follow-up

- Phases 5.3 and 6.2 implement the Ollama adapters.

## Entry 006 — Minimal React application shell

**Date:** 2026-09-04
**Phase/task:** PLAN.md 1.2
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Create a Vite + React + strict TypeScript frontend with a minimal application shell and one component test written first.

### Context provided to AI

Phase 1.1 and the Ollama ADR (PR `#3`, Entry 005) were merged. The developer asked to open a PR for the 1.2 frontend work.

### Prompt summary

Continue with the next phase of work, then create a PR for task 1.2 after PR 3 merged.

### AI contribution

- Wrote `tests/app/App.test.tsx` before `package.json` existed.
- Added a Vite/React shell with an `h1` inside `<main>`.
- Rebased the uncommitted 1.2 work onto `main` after the Ollama merge.
- Did not add upload/chat features, ESLint, or empty `features/` packages.

### Human decisions and changes

- Approved continuing Phase 1 after 1.1.
- Frontend stack (React, Vite, strict TypeScript) was already fixed in PLAN.md.

### Suggestions rejected or deferred

- ESLint, coverage XML and CI — Phase 1.4/1.5.
- Upload/chat UI — Phase 8.
- Pinning Node in Docker — later Phase 1 container work.

### TDD evidence

- Failing test/command and expected reason: `npm --prefix frontend test` → `ENOENT` `frontend/package.json`.
- Passing focused test/command: `cd frontend && npm test` → 1 passed.
- Typecheck: `npx tsc -b --noEmit` succeeded.

### Verification performed

- `npm install` in `frontend/` (160 packages, 0 npm audit vulnerabilities reported).
- Focused Vitest run passed in 372ms.
- `make verify` still does not exist.

### Files changed

- `frontend/tests/app/App.test.tsx`, `frontend/tests/setup.ts`
- `frontend/src/app/App.tsx`, `frontend/src/main.tsx`
- `frontend/package.json`, `frontend/package-lock.json`, Vite/TS config, `index.html`
- `README.md`, `PLAN.md`, `docs/engineering-journal.md`, `AI_DEVELOPMENT_LOG.md`

### Security, quality and limitations

- No API calls; heading text is static.
- Shell has no upload of repository content.
- Transitive deprecation warning for `whatwg-encoding` was recorded, not suppressed.

### Evidence

- Tests: `cd frontend && npm test` → 1 passed
- Plan item: 1.2
- Commit: TBD until created

### Follow-up

- Phase 1.3 after approval: PostgreSQL/pgvector and an Alembic migration test.

## Entry 007 — Local stack, pgvector and quality gates

**Date:** 2026-09-04
**Phase/task:** PLAN.md 1.3, 1.4, 1.5, 1.6
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed for the implemented gates; security Docker scans not observed locally

### Objective

Build a significant Phase 1 increment: Postgres/pgvector, quality tooling, Make/CI and accurate local setup so the stack runs.

### Context provided to AI

PR 4 (React shell) was merged. The developer asked to move on with a significant chunk of feature work rather than another tiny endpoint.

### Prompt summary

PR merged; build a significant chunk of feature.

### AI contribution

- Wrote the pgvector integration test first (failed: missing SQLAlchemy).
- Added Compose Postgres 16 + pgvector, Alembic migration `CREATE EXTENSION vector`, settings, Dockerfiles, Makefile and GitHub Actions.
- Added Ruff, mypy, pytest-cov, ESLint and Vitest coverage.
- Mapped the database to host port 5433 after 5432 was occupied by another Postgres.

### Human decisions and changes

- Asked for a larger increment than 1.1/1.2, then asked to slow down for TDD and commit regularly.
- One pull request for this local-stack feature; merge only when the feature is complete.
- Prior Ollama privacy decision remains: default tests do not call a hosted LLM.

### Suggestions rejected or deferred

- Starting Phase 2/3 ingestion in this branch — Phase 1 exit still needed a runnable stack first.
- Four separate PRs for 1.3–1.6 — one branch/PR, regular commits instead.
- Gitleaks/Trivy local execution — commands exist; not observed in this session.

### TDD evidence

- Failing: pytest integration file → `No module named 'sqlalchemy'`.
- Passing unit: `cd backend && .venv/bin/pytest` → 4 passed, 100% package coverage.
- Passing integration: `pytest -m integration` after migrate → vector extension present.

### Verification performed

- `docker compose config` succeeded.
- `docker compose up -d --build`: live `{"status":"ok"}`, frontend HTTP 200.
- Bandit clean; pip-audit no known vulns; npm audit 0.
- `make security` gitleaks/trivy not run here.

### Files changed

- `compose.yaml`, `Makefile`, `.env.example`, `.github/workflows/ci.yml`
- `backend` Alembic, adapters/postgres, config, Docker, lockfile, quality config
- `frontend` ESLint, coverage, Dockerfile
- README, PLAN, journal, AI log

### Security, quality and limitations

- Dev Compose images run as root; Phase 11 hardens that.
- Coverage XML is produced locally and gitignored.
- No application secrets in `.env.example`.

### Evidence

- Tests: backend unit 4 passed; integration 1 passed; frontend coverage 100% App.tsx
- Plan items: 1.3–1.6
- Commits on `build/phase-1-local-stack-and-quality-gates`: `08cfebf`, `017715e`, `e7a1338`. PR not opened yet.

### Follow-up

- Observe gitleaks/trivy before treating the Phase 1 security exit gate as closed.
- Do not start Phase 2 until that gate is closed and the developer approves the next TDD task.

## Entry 008 — Keep GitHub Actions minimal

**Date:** 2026-09-04
**Phase/task:** PLAN.md 1.5 (narrow CI)
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Keep a GitHub Actions workflow to show CI experience, but strip it to the minimum.

### Prompt summary

Leave the GitHub workflow; keep it very basic and minimal.

### AI contribution

- Removed the Postgres service, integration-test step and `make security` from `.github/workflows/ci.yml`.
- Left one job: `make setup`, `make lint`, `make test`, with read-only permissions and pip/npm caches.

### Human decisions and changes

- Keep CI as a skill signal, not as a second copy of the full local verify path.
- Integration tests and Gitleaks/Trivy stay on `make` locally.

### Suggestions rejected or deferred

- Removing GitHub Actions entirely — rejected; the workflow stays as a basic check.

### Verification performed

- Workflow file reviewed; no CI run observed in this step.

### Files changed

- `.github/workflows/ci.yml`
- README, PLAN, journal, this log

### Evidence

- Plan item: 1.5
- Pull request: historical private link removed during public-repository sanitization.

### Follow-up

- Confirm the simplified workflow is green on the pull request.

## Entry 009 — Combined config and three run paths

**Date:** 2026-09-04
**Phase/task:** PLAN.md 1.6
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

First-time run should not require a pre-existing database. Add combined config, backend/frontend settings including LLM fields, Compose with Ollama, and three documented run paths.

### Prompt summary

DB should be part of the project; Makefile should start it. Config for backend, frontend, LLM settings, a combined file Make can use, Docker Compose for Ollama/backend/frontend/database, three ways to run, README.

### AI contribution

- Red: `test_load_settings_reads_llm_runtime` (`Settings` had no `ollama_host`); frontend test failed to import `src/app/config`.
- Combined `config/app.env.example`; backend Settings; frontend `loadFrontendConfig`.
- Compose Ollama service; `make run-docker` vs `make run` (host apps, Compose db+ollama).
- YAML combined config was not used; env files work with Make and Compose without extra tools.

### Human decisions and changes

- Keep GitHub Actions minimal (unchanged in this entry).
- LLM fields are configuration only; no Ollama adapter yet.

### Verification performed

- Focused unit/component tests after implementation (recorded in the commit).
- `docker compose config` with `--env-file config/app.env`.

### Files changed

- `config/app.env.example`, `compose.yaml`, `Makefile`, backend Settings, frontend config, README, PLAN, journal, this log

### Evidence

- Plan item: 1.6
- Pull request: historical private link removed during public-repository sanitization.

### Follow-up

- Pull Ollama models only when the adapter is implemented.
- Phase 1 security scans still unobserved.

## Entry 010 — Ollama vs hosted/HF and Make-free first run

**Date:** 2026-09-04
**Phase/task:** PLAN.md 1.6 / ADR 004
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed (documentation)

### Objective

Explain why Ollama is the runtime, how Hugging Face fits, and what a from-scratch clone must install (Make is optional).

### Prompt summary

Is Ollama or OpenAI right; can we use Hugging Face? First-time users may not have Make or sh; consider all dependencies.

### AI contribution

- Kept Ollama as the local runtime. Documented Hugging Face Inference API as hosted (same privacy issue as OpenAI) and in-process Transformers as a heavier local alternative.
- Documented Docker Desktop as the only required tool for the first-run path; Make is optional.

### Human decisions and changes

- Did not add a Hugging Face adapter or change ADR 004 status.

### Verification performed

- Documentation review only; no new tests.

### Files changed

- `README.md`, `docs/adr/004-ollama-local-inference.md`, journal, this log

### Evidence

- ADR 004
- Pull request: historical private link removed during public-repository sanitization.

## Entry 011 — Close Phase 1 security exit gate

**Date:** 2026-09-04
**Phase/task:** PLAN.md Phase 1 exit
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Observe `make security` and close the Phase 1 exit gate.

### Verification performed

- Bandit: no issues (`backend/src`, 46 lines).
- pip-audit: no known vulnerabilities.
- npm audit --omit=dev: 0 vulnerabilities.
- Gitleaks: scanned ~168.48 KB, no leaks found.
- Trivy fs HIGH,CRITICAL: 0 on `frontend/package-lock.json` (exit 0).

### Evidence

- Plan: Phase 1 exit gate security checkbox
- Pull request: historical private link removed during public-repository sanitization.

### Follow-up

- Phase 2.1 domain types with a failing citation test first.

## Entry 012 — Phase 2 domain types, ports and use-case contracts

**Date:** 2026-09-04
**Phase/task:** PLAN.md 2.1, 2.2, 2.3
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Close Phase 1, then define domain invariants, provider ports and ingest/Q&A request types without infrastructure.

### TDD evidence

- Failing: missing `codebase_assistant.domain` / `application` / `contracts` modules.
- Passing: `cd backend && .venv/bin/pytest` → 27 passed, 100% package coverage.

### Human decisions and changes

- Continue TDD with regular commits and pushes.
- Phase 2 lives on `feat/domain-and-provider-contracts` (not mixed into further Phase 1-only work after the security close).

### Files changed

- `backend/src/codebase_assistant/domain/`
- `backend/src/codebase_assistant/application/`
- unit tests under `backend/tests/unit/domain` and `application`
- PLAN, README, journal, this log

### Evidence

- Plan items: 2.1–2.3
- Branch: `feat/domain-and-provider-contracts`

### Follow-up

- Phase 3: secure ZIP ingestion.

## Entry 013 — Phase 3 ZIP admission and named phase branches

**Date:** 2026-09-04
**Phase/task:** PLAN.md 3.1, 3.2
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed for 3.1–3.2

### Objective

Rename branches to include the phase number. Start Phase 3 with TDD: reject non-ZIP, oversized, malformed, and non-.zip names.

### TDD evidence

- Failing: `No module named 'codebase_assistant.ingestion'`
- Passing: admission tests plus existing unit suite (observed after implementation).

### Human decisions and changes

- Branch names include the phase number (`feat/phase-2-...`, `feat/phase-3-...`).
- Phase 2 PR 7 had already merged from the old name; Phase 3 starts from `main`.

### Files changed

- `backend/src/codebase_assistant/ingestion/`
- `backend/tests/unit/ingestion/test_admission.py`
- `docs/threat-model.md`, PLAN, AGENTS, README, this log

### Follow-up

- Phase 3.3: ZIP slip, symlinks, size/ratio/count limits.

## Entry 014 — Phase 3.3 safe archive members

**Date:** 2026-09-04
**Phase/task:** PLAN.md 3.3
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Reject ZIP slip, absolute paths, symlinks and resource-exhaustion members without extracting to disk.

### TDD evidence

- Failing: `No module named 'codebase_assistant.ingestion.members'`
- Passing: member tests plus full backend pytest after implementation.

### Follow-up

- Phase 3.4: extension allowlist, secret files, binaries.

## Entry 015 — Phase 3.4 source-file policy

**Date:** 2026-09-04
**Phase/task:** PLAN.md 3.4
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Classify ZIP member bytes as indexable source or ignored, without returning secret or binary contents.

### TDD evidence

- Failing: `pytest tests/unit/ingestion/test_source_policy.py` → `No module named 'codebase_assistant.ingestion.source_policy'`
- Passing: `make test` — backend 49 passed, 1 deselected; frontend 3 passed.

### Human decisions and changes

- Secret names are checked before the extension allowlist so `credentials.json` is never treated as source.
- Ignored decisions always set `text` to `None`.
- Directory exclusion looks at parent path parts, not the filename.

### Suggestions rejected or deferred

- Extracting members to disk before classification — rejected; 3.4 classifies in-memory bytes.
- Exhaustive secret-content scanning — deferred; name/suffix policy only.

### Files changed

- `backend/src/codebase_assistant/ingestion/source_policy.py`
- `backend/tests/unit/ingestion/test_source_policy.py`
- `docs/threat-model.md`, PLAN, README, journal, this log

### Follow-up

- Phase 3.5: ingestion summary, deterministic order, temp cleanup.

## Entry 016 — Phase 3.5 ingestion summary

**Date:** 2026-09-07
**Phase/task:** PLAN.md 3.5
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Produce a deterministic ingestion summary from an admitted ZIP without returning secret contents, and always remove the temporary ZIP copy.

### TDD evidence

- Failing: `pytest tests/unit/ingestion/test_summary.py` → `No module named 'codebase_assistant.ingestion.summary'`
- Passing: `make test` — backend 56 passed, 1 deselected; frontend 3 passed.

### Human decisions and changes

- Summary lives in the ingestion module, not an HTTP use case (Phase 5 orchestration).
- Members are read as bytes from the ZIP; they are not extracted as files.
- Ignored members have path and reason only (no `text` field).
- A `TemporaryDirectory` holds `upload.zip` and is removed on success and failure.

### Suggestions rejected or deferred

- Extracting accepted files to disk for later chunking — deferred to Phase 4; summary keeps accepted text in memory.
- Adding `tests/integration/ingestion` — not required; this path does not use PostgreSQL.

### Files changed

- `backend/src/codebase_assistant/ingestion/summary.py`
- `backend/tests/unit/ingestion/test_summary.py`
- PLAN 3.5 and Phase 3 exit gate, threat model, README, journal, this log

### Follow-up

- Phase 4: code-aware chunking.

## Entry 017 — Short demo: upload to cited answer

**Date:** 2026-09-07
**Phase/task:** PLAN.md 4.1–4.3 plus a vertical slice of 5.4/6.3/7/8 for a short demo
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed for the demo journey; Phase 5 pgvector and Phase 6 Ollama remain

### Objective

Reach a reviewer-demoable upload → indexed summary → cited answer → excerpt inspector path as quickly as TDD commits allow.

### TDD evidence

- Chunking: missing `codebase_assistant.chunking`; AST test failed with `symbols == [None]`.
- Use cases: missing `adapters.extractive`.
- API: `create_app() got an unexpected keyword argument 'workspace'`.
- Passing: `make test` — backend 69 passed, 1 deselected; frontend 9 passed.

### Human decisions and changes

- Demo uses an in-process lexical index and extractive completer so it runs without pulling Ollama models.
- PostgreSQL/pgvector remains the persistence target; chunks are not stored there in this slice.
- Secret file bodies never appear in ingest results; excerpts render as React text.

### Suggestions rejected or deferred

- Wiring Ollama for the first demo — deferred; ADR 004 still applies for real inference.
- Extracting ZIP members to disk — still avoided; summary reads bytes.

### Follow-up

- Phase 5: persist chunks in pgvector.
- Phase 6.2: Ollama completion adapter.

## Entry 018 — Phase 5.3–5.4 embeddings and ingest persistence

**Date:** 2026-09-07
**Phase/task:** PLAN.md 5.3 and 5.4
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Add an Ollama embedding adapter with mocked unit tests, then persist ingest through pgvector with an honest failed status.

### TDD evidence

- Red: `No module named 'codebase_assistant.adapters.ollama'`.
- Red: ingest raised `EmbeddingError` and did not store `status=failed`.
- Green: `cd backend && .venv/bin/pytest` — 79 passed, 4 deselected, coverage 85.37%.
- Green: `pytest -m integration` — 4 passed against local Postgres.

### Human decisions and changes

- Real embeddings use Ollama `POST /api/embed` and `nomic-embed-text` (768).
- Default `EMBEDDING_PROVIDER=lexical` so tests and the demo do not call Ollama.
- `httpx` moved to runtime dependencies because stdlib `urllib` would hide timeouts and JSON errors behind more code, and httpx was already locked.
- Failed indexing returns `status=failed` and 409 on questions; it does not save `completed`.
- Database URL can be `DATABASE_URL` or `DATABASE_USER`/`DATABASE_NAME` parts.

### Suggestions rejected or deferred

- Defaulting the running app to Ollama embeddings — rejected; reviewers would need a pulled model for the demo.
- Calling Ollama from the default pytest suite — forbidden by ADR 004.

### Files changed

- `backend/src/codebase_assistant/adapters/ollama.py`, `application/errors.py`, `application/ingest.py`, `main.py`, `config.py`
- Tests under `backend/tests/unit` and `backend/tests/api`
- PLAN, README, ADR 004, threat model, journal, this log

### Follow-up

- Phase 6: grounded answering with an Ollama completion adapter.

## Entry 019 — Host-run CORS and Ollama model pull

**Date:** 2026-09-07
**Phase/task:** Host `make run` (after PLAN.md 5.4)
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Fix upload CORS preflight on 127.0.0.1, and pull `nomic-embed-text` during `make run` when it is missing.

### TDD evidence

- Red: OPTIONS from `http://127.0.0.1:3000` returned 400; `No module named 'codebase_assistant.ops'`.
- Green: CORS test passed; `test_ollama_models.py` — 3 passed without calling Ollama.

### Human decisions and changes

- CORS allowlist includes the localhost/127.0.0.1 twin of the configured origin.
- `make run` no longer passes an empty Vite `--port`.
- When `EMBEDDING_PROVIDER=ollama`, `make run` calls Ollama HTTP `/api/tags` and `/api/pull` if the embed model is absent. `make run-docker` uses `compose exec ollama`.
- Default pytest still does not pull or call Ollama.

### Follow-up

- Phase 6.2: Ollama completion adapter.

## Entry 020 — Align PLAN, README and this log with implemented work

**Date:** 2026-09-07
**Phase/task:** Documentation after PLAN.md checkbox review (phases 6–8 partial)
**Tool/model:** Cursor (Grok 4.6)
**Status:** completed

### Objective

Mark PLAN.md tasks that already exist on `main`, then keep README and this log from claiming unfinished work.

### Context provided to AI

`PLAN.md` still showed phases 6–8 unchecked after the 4–8 demo, Phase 5 persistence, and PR #16 (CORS and Ollama embed pull) had merged. The developer asked to check completed work, then update README and this log.

### Prompt summary

Mark completed PLAN.md parts; update README and the AI development log.

### Human decisions and changes

- Checked 6.1, 6.3, 7.1–7.3, 8.1–8.4 and the exit items already covered by existing tests.
- Left 6.2, 6.4, 7.4, correlation IDs in 7.5, 8.5 and phases 9–12 open.
- README status, delivery table, MVP, observability and limitations now match that split. Extractive answers and missing readiness are stated as current, not future tense.

### Suggestions rejected or deferred

- Marking Phase 6 or 7 complete — rejected; Ollama chat, readiness and correlation IDs are still missing.
- Rewriting the proposed repository tree as if `api/` and `features/` packages existed — rejected; noted actual layout instead.

### TDD evidence

- Not applicable. This change is documentation only. No new tests were run for this entry.

### Files changed

- `PLAN.md` — checkboxes and remaining-work notes for phases 6–8
- `README.md` — status, delivery progress, MVP, observability, limitations
- `AI_DEVELOPMENT_LOG.md` — this entry; Cursor tool-register row

### Follow-up

- Phase 6.2: Ollama completion adapter.

## Entry 021 — Bounded archive integrity validation

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 3.6  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Reject ZIP bombs using metadata limits and bounded member reads, without `ZipFile.testzip()` decompressing every member first.

### Context provided to AI

Security review: `summarise_archive()` admitted first; admission called `testzip()`, which inflates every member before size/ratio limits. Stronger option approved: admit type/size only, metadata limits, then capped reads.

### Prompt summary

Start PLAN 3.6 after the proposal was approved.

### AI contribution

- Red test: high-ratio archive on the summary path while `ZipFile.testzip` and `ZipFile.read` raise if called.
- Removed `testzip()` from admission; parse the central directory only.
- Added `read_member_bounded` and wired it into summary after `validate_members`.

### Human decisions and changes

- Approved the stronger control (bounded reads), not metadata-reorder plus `testzip()`.
- `ZipInfo` sizes remain a first pass; actual inflation is capped at per-file and remaining extracted budgets.

### Suggestions rejected or deferred

- Reordering to metadata-then-`testzip()` — rejected; `testzip()` still inflates members that pass declared sizes.

### TDD evidence

- Failing: `pytest tests/unit/ingestion/test_summary.py::test_high_ratio_member_is_rejected_without_decompressing --no-cov` → `AssertionError: members must not be decompressed before size limits` from `admit_archive` → `testzip()`.
- Passing focused: same test after removing `testzip()`. Bounded-read tests: `read_member_bounded` missing, then 200-byte member rejected at a 50-byte cap.
- Passing: `cd backend && .venv/bin/pytest` — 87 passed, 4 deselected, coverage 81.86%. Frontend: 9 passed.

### Verification performed

- `cd backend && .venv/bin/pytest tests/unit/ingestion --no-cov` — 33 passed.
- Backend ruff, ruff format --check, mypy on ingestion — clean.
- `make lint` — failed on pre-existing `frontend/vite.config.ts` `process` typing (PLAN 5.5). Backend ruff/mypy in that run were clean.
- Bandit on `src/codebase_assistant/ingestion` — no issues.
- `make security` not run (Docker image pulls). No Docker verification.

### Files changed

- `backend/src/codebase_assistant/ingestion/admission.py`
- `backend/src/codebase_assistant/ingestion/members.py`
- `backend/src/codebase_assistant/ingestion/summary.py`
- `backend/tests/unit/ingestion/test_admission.py`
- `backend/tests/unit/ingestion/test_members.py`
- `backend/tests/unit/ingestion/test_summary.py`
- `docs/threat-model.md`, `PLAN.md`, `README.md`, `docs/engineering-journal.md`, this log

### Security, quality and limitations

- Metadata limits run before inflate. Bounded reads stop actual expansion. CRC is checked by `zipfile` only when a member is fully consumed within budget.
- Residual: configuration limits, not a guarantee against a local attacker with huge RAM.

### Evidence

- Tests: ingestion unit tests listed above
- Plan item: 3.6
- Pull request/commit: TBD until created

### Follow-up

- Phase 5.5: hermetic `make lint` / `make test` and Compose env parity.

## Entry 022 — Restore deterministic reviewer baseline

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 5.5  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Make `make lint` and `make test` green and environment-independent, and pass embedding/archive settings into the Compose backend.

### Context provided to AI

Project review: local `.env` with `EMBEDDING_PROVIDER=ollama` made API tests construct OllamaEmbedder; `vite.config.ts` used `process` without Node typings; Compose omitted provider and archive limits.

### Prompt summary

Work on the next plan item (5.5) and commit in TDD manner.

### AI contribution

- Red/green: hermetic `create_app` under pytest (lexical + in-memory defaults).
- Green: `@types/node` and `tsconfig.node.json` `types: ["node"]`.
- Red/green: Compose parity unit tests and `compose.yaml` environment keys.

### Human decisions and changes

- Used `pytest in sys.modules` as the hermetic switch so uvicorn runtime still honours `.env`.
- Stacked the 5.5 branch on the unmerged 3.6 branch.

### Suggestions rejected or deferred

- Forcing every API test to inject `LexicalEmbedder` only — insufficient alone; `create_app()` without inject still constructed Ollama.
- Running `make security` / Docker Compose up — deferred; Docker Engine not required for this task.

### TDD evidence

- Failing: hermetic API test → `AssertionError: OllamaEmbedder must not be constructed in default tests`.
- Failing: Compose parity assertions for `EMBEDDING_PROVIDER` and `MAX_ARCHIVE_*`.
- Passing: same tests after fixes; `make lint` green; `make test` — 90 backend + 9 frontend.

### Verification performed

- `make lint` — passed.
- `make test` — 90 passed, 4 deselected, coverage 81.15%; frontend 9 passed.
- Docker container execution not re-verified.

### Files changed

- `backend/src/codebase_assistant/main.py`
- `backend/tests/api/test_hermetic_app.py`
- `backend/tests/unit/test_compose_parity.py`
- `compose.yaml`
- `frontend/package.json`, `package-lock.json`, `tsconfig.node.json`
- `PLAN.md`, `README.md`, `docs/engineering-journal.md`, this log

### Follow-up

- Phase 6.2: Ollama completion adapter.

## Entry 023 — Ollama completion adapter

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 6.2  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Implement the first real LLM completion adapter against local Ollama, wire it behind `COMPLETION_PROVIDER`, and keep default tests and offline demos on `ExtractiveCompleter`.

### Context provided to AI

- PLAN 6.2 acceptance criteria and ADR 004.
- Existing `OllamaEmbedder`, `CompleteAnswer` port, `ask_question` JSON parse path, hermetic pytest defaults from Phase 5.5.

### Prompt summary

Continue Phase 6.2 after red/green adapter commits: finish composition-root wiring, config/Compose parity, hermetic guards, documentation, and checkpoint report.

### AI contribution

- Unit tests with mocked `httpx` for chat success, retries, timeout, invalid JSON and missing schema keys.
- `OllamaCompleter` (`POST /api/chat`, non-streaming, `format: json`, temperature/`num_predict`, bounded retries).
- `CompletionError`; composition root selects Ollama when `COMPLETION_PROVIDER=ollama`; pytest stays extractive; safe HTTP 503 on completion failure.
- Config/`app.env.example`/Compose for `COMPLETION_PROVIDER` and `LLM_MAX_RETRIES`.
- PLAN/README/ADR 004/threat-model/journal/log updates.

### Human decisions and changes

- Default completion provider remains `extractive` so reviewer demos stay offline.
- Chat model tag recorded as `llama3.2` via configuration.
- Do not auto-start Phase 6.1 or claim conversational RAG as the default demo.

### Suggestions rejected or deferred

- Making Ollama chat the default running-app provider — would break offline/no-model demos.
- Auto-pulling `llama3.2` on `make run` — deferred; only embed pull exists today.
- Treating 6.1/6.3/6.4/6.5 as done — adapter-only scope for 6.2.

### TDD evidence

- Failing: unit tests for `OllamaCompleter` before the class existed (`ModuleNotFoundError` / missing symbol).
- Passing: `backend/tests/unit/test_ollama_completer.py`; hermetic app test blocks `OllamaCompleter` under pytest; API 503 mapping test; `make lint` / `make test`.

### Verification performed

- `make lint` — passed.
- `make test` — backend 97 passed, 4 deselected, coverage 80.52%; frontend 9 passed.
- No live Ollama chat smoke in this task (**6.4** remains open).

### Files changed

- `backend/src/codebase_assistant/adapters/ollama.py` — `OllamaCompleter`
- `backend/src/codebase_assistant/application/errors.py` — `CompletionError`
- `backend/src/codebase_assistant/main.py` — completer injection and 503 mapping
- `backend/src/codebase_assistant/config.py`, `compose.yaml`, `config/app.env.example`
- `backend/tests/unit/test_ollama_completer.py` and related wiring/parity tests
- `PLAN.md`, `README.md`, `docs/adr/004-ollama-local-inference.md`, `docs/threat-model.md`, `docs/engineering-journal.md`, this log

### Security, quality and limitations

- Completions stay on local Ollama only when selected; hosted APIs not wired.
- Adapter rejects non-JSON and incomplete answer schemas before returning content.
- Default path remains extractive; real conversational quality depends on the local chat model and later answer-boundary work.

### Evidence

- Tests: unit completer + hermetic + API 503 + config/Compose parity
- ADR/plan item: ADR 004 follow-up; PLAN 6.2 checked
- Pull request/commit: TBD until created

### Follow-up

- Phase 6.1: enforce question and total-context limits.
- Then 6.3 / 6.5; optional 6.4 local Ollama smoke; consider chat-model pull on `make run`.

## Entry 024 — Question and context budget enforcement

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 6.1  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Specify and enforce prompt/context policy: untrusted delimited sources, question length rejection, total-context truncation, and configurable budgets.

### AI contribution

- Red tests for prompt delimiters, oversized questions, context truncation and citation verification against budgeted chunks.
- `AnswerLimits`, `select_context_chunks`, ask-path enforcement, Settings/Compose env keys.
- Makefile `--no-cov` for `test-integration` (coverage gate false positive on narrow suite).

### Human decisions and changes

- Oversized questions are rejected; over-budget context is truncated in retrieval order rather than hard-failing after search.
- Continue Phase 6 on the existing feature branch; PR after the whole phase.

### TDD evidence

- Failing: `ModuleNotFoundError` for `AnswerLimits`.
- Passing: `tests/unit/application/test_answer_limits.py`; `make lint` / `make test` (102 backend + 9 frontend).

### Follow-up

- Phase 6.3: strict completion parsing at the use-case boundary.
- Phase 6.5: injection/forgery regression tests; optional 6.4 smoke.

## Entry 025 — Strict completion schema validation

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 6.3  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Replace best-effort completion parsing with strict schema validation and keep citation verification against retrieved metadata.

### AI contribution

- Unit tests for non-JSON, missing keys, wrong types, malformed citations, fabricated/expanded ranges, and empty-retrieval short-circuit.
- `parse_completion` + `ask_question` wiring; invalid schema → insufficient evidence.

### TDD evidence

- Failing: `ModuleNotFoundError` for `application.completion`.
- Passing: `test_strict_completion.py`; `make lint` / `make test` (111 backend + 9 frontend).

### Follow-up

- Phase 6.5 regression suite; optional 6.4 Ollama smoke.

## Entry 026 — Provider-selected Ollama model pulls on make run

**Date:** 2026-09-08  
**Phase/task:** Ops follow-up (supports PLAN 6.2 chat path)  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

`make run` and `make run-docker` should pull every Ollama model required by the selected embedding/completion providers.

### AI contribution

- `required_ollama_models` + Makefile `ensure-ollama-models` using provider/env tags.
- Tests for provider selection and Makefile wiring; README/ADR updates.

### Follow-up

- Phase 6.5; optional 6.4 smoke.

## Entry 027 — Answer-boundary regression suite

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 6.5  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Add Phase 6.5 regression tests for question/context budgets, malformed completions, citation forgery, and prompt injection in retrieved source.

### AI contribution

- `test_answer_boundary.py` (8 cases). No production code changes; behaviour already present from 6.1/6.3.

### TDD evidence

- Feature already green; suite would fail if budgets, strict parse, or citation verification were removed.
- `make test` — 122 passed, coverage 81.13%.

### Follow-up

- Optional 6.4 Ollama smoke; then Phase 9.

## Entry 028 — Optional real Ollama smoke tests

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 6.4  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Add opt-in local Ollama embed/chat smoke tests outside the default suite.

### AI contribution

- `tests/smoke/test_real_provider.py`; `smoke` marker; pyproject excludes smoke by default.
- Verified live: `RUN_LLM_SMOKE=1 pytest -m smoke` — 2 passed.

### Follow-up

- Phase 9. Phase 6 complete; open PR when ready.

## Entry 029 — Controlled fixture repository

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 9.1  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Add a small original fixture repository for evaluation/demos with handlers, services, config, distractors and deliberately ignored noise.

### AI contribution

- `sample-data/fixture-repository/` inventory-service tree.
- `test_fixture_repository.py` layout + ingest ignore checks.
- `docs/evaluation.md` started with fixture inventory.

### Follow-up

- Phase 9.2 evaluation dataset.

## Entry 030 — Evaluation dataset

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 9.2  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Create a known-answer / insufficient-evidence / prompt-injection evaluation dataset tied to the fixture repository.

### AI contribution

- `sample-data/evaluation/dataset.json` (8 cases).
- Injection bait in fixture `docs/architecture.md`.
- `backend/tests/evaluation/test_dataset.py` schema and fixture-path checks.

### Follow-up

- Phase 9.3 retrieval evaluation runner.

## Entry 031 — Retrieval evaluation runner

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 9.3  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Add a hermetic retrieval/answer evaluation runner against the fixture dataset and record evidence-based gates.

### AI contribution

- `codebase_assistant.evaluation` (dataset load, runner, CLI JSON report).
- `make test-evaluation`; tests under `backend/tests/evaluation/`.
- Observed lexical+extractive metrics recorded in `docs/evaluation.md` (hit-at-k 0.8; IE rate 0.0; citation validity 1.0).

### Human-owned decisions

- Gate on citation validity + grounded hit-at-k only; do not invent answer-file or IE thresholds for extractive baseline.

### Follow-up

- Phase 9.4 Playwright E2E.

## Entry 032 — Deterministic browser E2E

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 9.4  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Prove upload → indexed summary → question → cited excerpt with fake providers.

### AI contribution

- `e2e/` Playwright suite; `ops.e2e_api` in-memory API; `make test-e2e`.
- Fixed CORS by setting `CORS_ALLOW_ORIGIN` to the Playwright web origin (`:3010`).

### Verification performed

- `npm --prefix e2e test` — 1 passed after Chromium install.

### Follow-up

- Phase 9.5 adversarial matrix.

## Entry 033 — Adversarial matrix

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 9.5  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Consolidate defensive regressions for hostile ZIP, secrets, injection, forgery, oversized input, provider failure, re-upload and escaped rendering.

### AI contribution

- `backend/tests/adversarial/test_matrix.py`.
- Threat-model and evaluation docs updated; Phase 9 exit gate marked complete in PLAN.

### Follow-up

- Reviewer-demo polish (**8.5**/**8.6**) or Phase 10 observability.

## Entry 034 — Reviewer UI polish

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 8.5 / 8.6 (also closes demo-facing 8.2 / 8.3)  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Make the upload-to-cited-answer UI demo-ready: visible busy states, starter questions, distinct failed indexing, stronger evidence panel, a11y/responsive polish, and a fixture path pointer.

### AI contribution

- Extended `frontend/tests/app/App.test.tsx` (indexing/answering status, chips, failed-index, Evidence focus, fixture hint).
- Reworked `App.tsx` / `App.css`; mapped ingest `status` / `failureCode` in the API client.
- Avoided adding `@testing-library/user-event`; used existing fireEvent patterns.

### Verification performed

- `npm --prefix frontend run test` — 14 passed (observed during implementation).
- Focused lint/typecheck/coverage and e2e to be recorded in the task report.

### Follow-up

- Phase 10 observability; residual **8.1** timeouts/cancellation.

## Entry 035 — Bootstrap UI and repository list API

**Date:** 2026-09-08  
**Phase/task:** Phase 8 follow-up (UI + GET repositories)  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Improve the demo UI (spinner, scrollable indexed files, stable columns, Bootstrap) and expose a repository list/select API so reviewers can switch between indexed uploads.

### AI contribution

- `GET /api/repositories`, `list_summaries` on memory/Postgres stores, `source_filename` + Alembic 003.
- Frontend: `bootstrap` + `react-bootstrap`, repositories panel, spinner states, scrollable indexed-file list.

### Verification performed

- Backend pytest green (coverage ~82%).
- Frontend lint/typecheck/tests (16) and `make test-e2e` (1 passed).

### Follow-up

- Phase 10; optional **8.1** timeouts.

## Entry 036 — App-shell chat UI refactor

**Date:** 2026-09-08  
**Phase/task:** Phase 8 follow-up (frontend-only shell + chat)  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Replace the stacked Bootstrap card form with a full-viewport app shell: sidebar + chat thread, ingest modal, file drawer, per-repo chat history, and citations inside assistant messages — without changing API contracts.

### AI contribution

- Split UI into `AppShell`, `RepoSidebar`, `RepoListItem`, `IngestModal`, `FileDrawer`, `ChatThread`, `ChatMessage`, `CitationCard`, `Composer`.
- Typed `api.ts` + `useChat` (sessionStorage threads, AbortController stop).
- Design tokens / light-dark via `prefers-color-scheme` + `data-bs-theme`.
- Updated frontend unit tests and Playwright e2e selectors for the new chat/citation chrome.

### Verification performed

- `npm --prefix frontend run typecheck` — pass
- `npm --prefix frontend run lint` — pass
- `npm --prefix frontend run test` — 14 passed
- `make test-e2e` — not re-run in this turn (selector updated; needs live stack)

### Follow-up

- Optional icon-rail sidebar between `md` and `lg` (current: full sidebar ≥lg, Offcanvas below).
- Re-run `make test-e2e` with API + UI up.

## Entry 037 — Richer grounded answer prompt

**Date:** 2026-09-08  
**Phase/task:** Answer quality (prompt / completion settings)  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Stop one-line “file list” answers; ask the local model for multi-paragraph grounded explanations while keeping citation verification.

### AI contribution

- Expanded `build_answer_prompt` with explicit detail and inline `[n]` citation guidance.
- Raised local `LLM_TEMPERATURE` to `0.2` and `LLM_MAX_OUTPUT_TOKENS` to `2048`.
- Chat UI splits double-newline paragraphs for readability.

### Verification performed

- `pytest tests/unit/application/test_answer_limits.py tests/unit/application/test_answer_boundary.py --no-cov` — pass
- `npm --prefix frontend run test` — 14 passed

### Follow-up

- Restart API / re-ask questions to see new answers (old sessionStorage threads stay short until new turns).

## Entry 038 — Repository delete and name-unique replace

**Date:** 2026-09-08  
**Phase/task:** Repository lifecycle  
**Tool/model:** Cursor (Composer)  
**Status:** completed

### Objective

Add real repository delete and stop duplicate indexes for the same repository name.

### AI contribution

- `DELETE /api/repositories/{id}` plus `IngestionStore.delete_repository`.
- Ingest removes any existing repo with the same ZIP basename (case-insensitive) before indexing the new one.
- UI Delete calls the API (no more session-only hide).

### Verification performed

- Backend focused pytest for ingest replace + delete API — pass
- Frontend test/typecheck — 16 passed

### Follow-up

- Restart API to pick up delete/replace behaviour.

## Entry 039 — Plan Phase 13 repository-aware Q&A

**Date:** 2026-09-08  
**Phase/task:** Planning only (Phase 13)  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** plan and docs updated; no application behaviour changed

### Objective

Record the design needed so ingested repositories can answer core product questions (overview, how it works, where functionality lives, API endpoints, dependencies, directory structure/hierarchy), after a live failure where `"what does this repo do?"` was answered from `package-lock.json`.

### How AI assisted

- Diagnosed the failure as nearest-neighbour retrieval plus lockfile index pollution, not completer wording.
- Drafted Phase 13 tasks, approved design table, remaining-work reorder, and documentation pointers.

### Human decisions and direction

- Update the plan first; do not implement in this step.
- Keep the modular monolith, Postgres/pgvector, and local Ollama ports.
- Prefer extractive repository card + deterministic intent routing over ingest-time LLM summaries, hybrid BM25, Tree-sitter or an extra datastore.
- Phase 13 before Phases 10–12.

### Suggestions accepted

- Ignore lockfiles/minified bundles at source-policy time.
- Persist a bounded extractive card on the repository summary.
- Route overview/structure/dependencies/endpoints away from vector-only context; keep vector search for locate/explain.
- Build directory hierarchy from `indexed_paths`.
- Regex extractors for routes and manifests.
- Repo-aware starter chips (**13.8**).

### Suggestions rejected or deferred

- Ingest-time Ollama architecture summary.
- Hybrid lexical/vector retrieval (unless evaluation after Phase 13 requires it).
- Synthetic uploaded `INDEX.md` as a fake source file.
- New ADR (intent routing + JSONB card is reversible; change-control row recorded instead).

### TDD evidence

- Not applicable (documentation only).

### Verification performed

- Files edited by inspection. No tests run (no production code changed).

### Files changed

- `PLAN.md` — remaining-work sequence, Phase 13, change-control, Phase 8.3 follow-up, Phase 10 wait note
- `README.md` — next-work pointers, delivery table, retrieval/limitations/future-work notes
- `docs/engineering-journal.md` — next pointer and plan-update note
- `AI_DEVELOPMENT_LOG.md` — this entry

### Follow-up

- Implement **13.1** after developer approval (failing source-policy test for lockfiles first).

## Entry 040 — Ignore generated lockfiles and minified bundles

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.1  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Stop indexing lockfiles and minified bundles so generic questions cannot retrieve `package-lock.json` as repository purpose.

### How AI assisted

- Added failing source-policy tests, then basename/suffix ignore rules.

### Human decisions and direction

- Developer approved starting Phase 13 implementation.
- Reasons: `generated_lockfile` and `generated_bundle`. Keep `package.json` / `pyproject.toml` / `requirements.txt` / README.

### Suggestions accepted

- Case-insensitive basename list for lockfiles; `*.min.js` / `*.min.css` suffix check before the extension allowlist so `yarn.lock` is not classified only as `extension`.

### Suggestions rejected or deferred

- Ignoring all `.json` files.
- Re-writing already-ingested PostgreSQL chunks (operators must re-upload).

### TDD evidence

- Red: `test_generated_lockfiles_are_ignored_without_returning_contents` — `frontend/package-lock.json` was accepted.
- Green: `pytest backend/tests/unit/ingestion/test_source_policy.py -q --no-cov` — 10 passed.

### Verification performed

- `pytest backend/tests/unit/ingestion -q --no-cov` — 36 passed (before ruff fix on the new test).
- Focused source-policy tests re-run after line-length fix.

### Files changed

- `backend/src/codebase_assistant/ingestion/source_policy.py`
- `backend/tests/unit/ingestion/test_source_policy.py`
- `docs/threat-model.md`, `README.md`, `PLAN.md`, `docs/engineering-journal.md`, this log

### Follow-up

- **13.2** extractive repository card. Re-ingest existing ZIPs to drop old lockfile chunks.

## Entry 041 — Extractive repository card builder

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.2  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Build a bounded, extractive repository card from accepted files (README excerpt, manifest name/description/dependencies, language histogram, directory outline) without an LLM call or persistence.

### How AI assisted

- Added failing unit tests, then `build_repository_card` using stdlib `json` and `tomllib`.

### Human decisions and direction

- Continue Phase 13 after 13.1. Card is a pure function of accepted (path, text) pairs; ingest/API wiring is **13.3**.

### Suggestions accepted

- Dedicated `RepositoryCardLimits` (readme chars, outline depth/entries, dependency cap) rather than reading environment variables.
- Prefer root README; union declared deps from `package.json` / `pyproject.toml` / `requirements.txt`; skip malformed manifests.

### Suggestions rejected or deferred

- Persisting the card or returning it from ingest (13.3).
- Endpoint extraction (13.6).
- Ingest-time LLM summary.

### TDD evidence

- Red: collecting `test_repository_card.py` raised `ModuleNotFoundError: repository_card`.
- Green: `pytest backend/tests/unit/application/test_repository_card.py -q --no-cov` — 5 passed.

### Verification performed

- ruff check/format and mypy on the new module — passed.
- Focused tests re-run after format — 5 passed.

### Files changed

- `backend/src/codebase_assistant/application/repository_card.py`
- `backend/tests/unit/application/test_repository_card.py`
- `PLAN.md`, `docs/engineering-journal.md`, this log

### Follow-up

- **13.3** persist the card on the repository summary.

## Entry 042 — Persist extractive repository card

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.3  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Persist the extractive repository card on ingest summaries and expose a compact `repository_card` object on upload/list/get.

### How AI assisted

- Failing ingest/API tests, then contract field, ingest wiring, JSONB migration, memory/Postgres adapters, and frontend mapping.

### Human decisions and direction

- Continue 13.3. Nested `repository_card` JSON (outline, languages, manifest, README excerpt). No ingest-time LLM.

### Suggestions accepted

- JSONB column default `{}` so older rows map to `card=None`.
- Same-name re-ingest replaces the card with the new archive.
- Fixture test: ignored credential-file prose must not appear in the summary repr; README may still mention the documented placeholder.

### Suggestions rejected or deferred

- Using the card at ask time (**13.4**/**13.5**).
- Custom `repr` hiding README excerpts.

### TDD evidence

- Red: `test_ingest_attaches_extractive_repository_card` — `AttributeError: card`.
- Green: ingest, replace, API upload/get/list, payload round-trip tests passed.

### Verification performed

- `pytest backend/tests/unit backend/tests/api -q --no-cov` — passed (after fixture assertion update).
- ruff + mypy on changed Python — passed.
- `npm --prefix frontend run typecheck` — passed.
- Frontend focused tests — 14 passed.
- Postgres integration test updated but not executed in this session (`-m integration`).

### Files changed

- contracts, ingest, repository_card payload helpers, memory/postgres/persistence, main payload
- `backend/migrations/versions/004_repository_card.py`
- API/unit/integration tests; frontend `types.ts` + tests
- PLAN/README/threat-model/journal/this log

### Follow-up

- **13.4** classify question intent. Run `alembic upgrade head` on existing Postgres.

## Entry 043 — Deterministic question intent

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.4  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Classify questions into overview, structure, dependencies, endpoints, locate, or explain without a model call.

### How AI assisted

- Parametrized failing tests, then regex first-match rules.

### Human decisions and direction

- Continue 13.4 only. Do not change `ask_question` yet (**13.5**).
- Endpoints/dependencies/structure/overview match before locate so “where are the API endpoints?” is `endpoints`.

### Suggestions accepted

- Default `explain` for unrecognised text (including “how does…”).
- Phrase lists from PLAN 13.4 plus close variants (folder structure, pyproject.toml, which file).

### Suggestions rejected or deferred

- LLM router.
- Wiring into retrieval (**13.5**).

### TDD evidence

- Red: `ModuleNotFoundError: codebase_assistant.application.intent`
- Green: `pytest backend/tests/unit/application/test_intent.py -q --no-cov` — 20 passed

### Verification performed

- ruff check/format and mypy on `intent.py` — passed

### Files changed

- `backend/src/codebase_assistant/application/intent.py`
- `backend/tests/unit/application/test_intent.py`
- PLAN/README/journal/this log

### Follow-up

- **13.5** assemble intent-routed context in `ask_question`.

## Entry 044 — Intent-routed ask context

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.5  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Pin README, manifests and related files for overview/structure/dependency/endpoint questions so “what does this repo do?” is not answered from noisy JSON or lockfile-like chunks.

### How AI assisted

- Strengthened the overview test until lexical retrieval preferred the noisy JSON, then implemented pin-path loading and a derived repository index in the prompt.

### Human decisions and direction

- Continue 13.5 only. Do not add endpoint regex extractors (**13.6**) or per-intent prompt policy (**13.7**).
- When pins exist for pin intents, skip vector search; fall back to vector if pins are empty. Search-only fakes without `get_summary` / `chunks_for_paths` stay vector-only.

### Suggestions accepted

- Duck-type `get_summary` and `chunks_for_paths` on the search collaborator so HTTP can pass the workspace store.
- Derived index is application metadata, not a citation source, and counts toward `MAX_CONTEXT_CHARS`.

### Suggestions rejected or deferred

- Hybrid BM25 / extra datastore.
- Endpoint and dependency regex extractors (**13.6**).
- Insufficient-evidence when README/manifests are absent (**13.7**).

### TDD evidence

- Red: overview question cited `meta/packages.json` instead of `README.md`
- Green: `pytest backend/tests/unit/application/test_intent_context.py -q --no-cov` — 2 passed; locate still cites `src/app.py`

### Verification performed

- `pytest backend/tests/unit/application -q --no-cov` — 67 passed
- `pytest` focused set including evaluation and `test_repositories` — 35 passed
- ruff check/format and mypy on changed Python modules — passed

### Files changed

- `backend/src/codebase_assistant/application/ask.py`
- `backend/src/codebase_assistant/application/prompt.py`
- `backend/src/codebase_assistant/application/ports.py`
- `backend/src/codebase_assistant/adapters/memory.py`
- `backend/src/codebase_assistant/adapters/postgres.py`
- `backend/tests/unit/application/test_intent_context.py`
- `backend/tests/unit/application/test_answer_limits.py`
- PLAN/README/journal/this log

### Follow-up

- **13.6** extract endpoints and declared dependencies without new parsers.

## Entry 045 — Phase 13 plan corrections

**Date:** 2026-09-08  
**Phase/task:** PLAN 13 (governance)  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Record human review of Phase 13 before implementing extractors: trust boundary, exact lookup, citations, task order, evaluation correctness, supported formats.

### How AI assisted

- Rewrote the Phase 13 section and change-control rows from the review points.

### Human decisions and direction

- Card schema/counts/outline structure are application-derived; README/manifest/dep/endpoint/symbol strings stay untrusted.
- Keep directory-structure Q&A; outline is first-class derived evidence; do not add an uncited `GroundedAnswer` exception.
- Do not renumber 13.1–13.5. Remaining 13.6 is endpoints + declaring-file provenance, not a second dependency-name parser.
- 13.9 must require the correct cited file and IE behaviour; Playwright must assert `src/api/handlers.py` and `list_items`.
- Outcome is supported repositories and declared formats, not arbitrary ZIP.

### Suggestions accepted

- Derived-evidence outline rather than dropping structure Q&A.
- Additive JSONB fields, no new Alembic revision.

### Suggestions rejected or deferred

- General uncited-answer exception.
- Rebuilding 13.2 manifest name extraction.
- Cargo.toml / go.mod (unsupported, document in 13.10).

### Follow-up

- **13.6** implemented in the same session (entry 046).

## Entry 046 — Endpoint extractors and provenance

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.6  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Extract HTTP routes at ingest with declaring file and line range; attach the same provenance to existing 13.2 dependency names; pin those files at ask time.

### How AI assisted

- Failing extractor tests, then regex extractors, card payload fields, and pin-list switch in `ask_question`.

### Human decisions and direction

- Do not re-parse dependency names. Extend them with file path and line span.
- Skip route extraction on non-source suffixes so JSON noise cannot become a “route.”
- Keep filename heuristics only when stored endpoint records are empty (old cards).

### Suggestions accepted

- Bounded METHOD `/path`, `app.get`/`router.`, Spring `@GetMapping` / `@RequestMapping`.
- Prefer chunks overlapping stored line ranges.

### Suggestions rejected or deferred

- Per-intent insufficient-evidence policy (**13.7**).
- Raising eval answer-file gates (**13.9**).

### TDD evidence

- Red: `ModuleNotFoundError: codebase_assistant.application.extractors`
- Green: `pytest backend/tests/unit/application/test_extractors.py` plus `test_endpoints_question_cites_handler_not_noisy_json`

### Verification performed

- `pytest backend/tests/unit/application -q --no-cov` — 71 passed
- `npm --prefix frontend run typecheck` — passed
- `npm --prefix frontend run test` — 16 passed
- ruff check/format and mypy on changed Python modules — passed

### Files changed

- `PLAN.md`, `README.md`, `docs/threat-model.md`, `docs/engineering-journal.md`, this log
- `backend/src/codebase_assistant/application/extractors.py`
- `backend/src/codebase_assistant/application/repository_card.py`
- `backend/src/codebase_assistant/application/ask.py`
- `backend/src/codebase_assistant/application/prompt.py`
- `backend/tests/unit/application/test_extractors.py`
- `backend/tests/unit/application/test_intent_context.py`
- `frontend/src/app/types.ts`

### Follow-up

- **13.7** prompt policy per intent (card strings untrusted; no uncited exception).

## Entry 047 — Per-intent prompt policy

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.7  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Stop overview/endpoint/dependency answers from being invented from random chunks, and give the completer intent-specific instructions without weakening citation verification.

### How AI assisted

- Failing prompt and BoomCompleter tests, then intent policy lines and ask-path evidence checks.

### Human decisions and direction

- Pin intents return insufficient evidence when required card evidence is missing; they do not fall back to vector search.
- Locate/explain keep the existing grounded-explanation prompt.
- No `GroundedAnswer` empty-citation exception.

### Suggestions accepted

- Overview requires README or a declaring manifest; endpoints require extracted routes; dependencies require a declaring manifest.

### Suggestions rejected or deferred

- Repo-aware starter chips (**13.8**).
- Eval/e2e correct-file gates (**13.9**).

### TDD evidence

- Red: completer ran for “what does this repo do?” on `src/app.py` only; prompt lacked “README and manifest” / “Do not invent directories” / “List only extracted”
- Green: those asks return insufficient evidence without calling complete; prompt tests pass

### Verification performed

- `pytest backend/tests/unit/application -q --no-cov` — 77 passed
- `pytest backend/tests/unit/application backend/tests/adversarial backend/tests/evaluation -q --no-cov` — 90 passed
- ruff check/format and mypy on `ask.py`, `prompt.py` — passed

### Files changed

- `backend/src/codebase_assistant/application/ask.py`
- `backend/src/codebase_assistant/application/prompt.py`
- `backend/tests/unit/application/test_answer_limits.py`
- `backend/tests/unit/application/test_intent_context.py`
- PLAN/README/threat-model/journal/this log

### Follow-up

- **13.8** repo-aware starter chips.

## Entry 048 — Repo-aware starter chips

**Date:** 2026-09-08  
**Phase/task:** PLAN 13.8  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Replace hardcoded fixture starter questions with chips derived from the selected repository card and indexed paths.

### How AI assisted

- Failing unit and App tests, then a small `starterQuestions` helper wired into `ChatThread`.

### Human decisions and direction

- Always offer overview and structure.
- Offer endpoints/dependencies only when the card has extracted items.
- Keep “Where is list_items defined?” only when `handlers.py` is indexed.
- Otherwise locate from a real indexed source path. Cap at four chips.

### Suggestions accepted

- Pure helper for chip selection so behaviour is unit-tested without mounting the full shell for every case.

### Suggestions rejected or deferred

- LLM-generated suggestions.
- Evaluation/e2e cited-file gates (**13.9**).

### TDD evidence

- Red: missing `starterQuestions` module; App still rendered `list_items` for `src/app.py`
- Green: `npm --prefix frontend run test` — 20 passed

### Verification performed

- `npm --prefix frontend run test` — 20 passed
- `npm --prefix frontend run typecheck` — passed
- `npm --prefix frontend run lint` — passed
- Browser end-to-end click-through: not run (no browser tools)

### Files changed

- `frontend/src/app/starterQuestions.ts`
- `frontend/src/app/components/ChatThread.tsx`
- `frontend/tests/app/starterQuestions.test.ts`
- `frontend/tests/app/App.test.tsx`
- PLAN/README/journal/this log

### Follow-up

- **13.9** evaluation and answer correctness (correct cited files and IE behaviour).

## Entry 049 — Revive leftover pending chat searches

**Date:** 2026-09-08  
**Phase/task:** User-reported UI bug (not a PLAN checkbox)  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Stop a repository chat from remaining on “Searching N files…” after the page is reopened.

### How AI assisted

- Diagnosed leftover `pending` assistant messages in `sessionStorage` (`cia.chatByRepo.v1`): reload restores the spinner with `isAsking` false and no in-flight fetch.
- Added `reviveStoredMessages` so pending rows become a retryable interrupted-search error on load and when saving.

### Human decisions and direction

- Keep the user question. Do not auto-retry on hydrate.
- Do not persist a live spinner across reloads.

### Suggestions rejected or deferred

- Client request timeout (residual PLAN **8.1**).
- Auto-retry of the interrupted question on load.

### TDD evidence

- Red: `tests/app/chatStore.test.ts` failed to resolve `../../src/app/chatStore`
- Green: `npx vitest run tests/app/chatStore.test.ts tests/app/App.test.tsx` — 11 passed
- Typecheck: `npx tsc -b --noEmit` — passed
- Lint: `npx eslint src/app/chatStore.ts src/app/useChat.ts tests/app/chatStore.test.ts tests/app/App.test.tsx` — passed

### Files changed

- `frontend/src/app/chatStore.ts` — hydrate/save revival of pending messages
- `frontend/src/app/useChat.ts` — use shared store helpers
- `frontend/tests/app/chatStore.test.ts`
- `frontend/tests/app/App.test.tsx`

### Follow-up

- **13.9** remains next PLAN task. Residual **8.1** timeouts if a live Ollama ask hangs with Stop visible.

## Entry 050 — Structure tree and overview wording

**Date:** 2026-09-08  
**Phase/task:** User-requested Q&A behaviour (13.7 refinement; not 13.9)  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Directory-structure questions should show a nested file tree with README context. Overview questions should mix business and technical language.

### How AI assisted

- Nested `format_outline_tree` from card `outline_paths`.
- Structure answers composed in `ask_question` from the derived tree (no completer).
- Overview prompt asks for 2–4 paragraphs mixing product purpose and technical shape.

### Human decisions and direction

- Show a README-style tree, not a flat path list.
- Keep citing a real indexed file. Do not add an uncited-answer exception.

### Suggestions rejected or deferred

- Asking Ollama to invent the tree (unreliable vs application-derived outline).
- Phase **13.9** evaluation gates.

### TDD evidence

- Red: missing `format_outline_tree`; “structure of this repo” classified as `explain`; structure ask invoked completer; overview prompt lacked business/technical wording
- Green: `cd backend && .venv/bin/pytest` — 197 passed, 6 deselected, coverage 81.62%
- `ruff check` / `ruff format --check` on changed Python files — passed
- `mypy` on changed application modules — passed

### Files changed

- `backend/src/codebase_assistant/application/repository_card.py`
- `backend/src/codebase_assistant/application/ask.py`
- `backend/src/codebase_assistant/application/prompt.py`
- `backend/src/codebase_assistant/application/intent.py`
- related unit tests
- `README.md`

### Follow-up

- Re-ingest repositories ingested before the card existed.
- **13.9** remains next PLAN task.

## Entry 051 — Architecture flows, code-unit inventories and Markdown cards

**Date:** 2026-09-08
**Phase/task:** PLAN 13.8a–13.8c
**Tool/model:** Codex (GPT-5 family; exact build not exposed)
**Status:** completed

### Objective

Improve observed Spring Petclinic answers so architecture questions cover every controller and explain controller → service → repository/DAO → entity/model → database paths. Make named code-unit inventories retrieve the full matched file, explain each callable and honour requested tables. Render directory outlines and structured answers as safe Markdown-style UI rather than raw text.

### Context provided to AI

The product criteria, repository governance, existing Phase 13 code/tests and the user-observed question/answer. No credentials or uploaded source contents were copied into this log.

### Prompt summary

Implement the requested Q&A/UI improvements, keep the project production-minded and simple, avoid making “controller” a universal product abstraction, and add every change to pending/new `PLAN.md` work before editing implementation files.

### AI contribution

- Added focused red tests, deterministic intent routing, bounded exact-path architecture context and per-intent prompt instructions.
- Added conservative post-processing for flat valid architecture responses so each indexed controller has a Markdown section and missing method evidence stays explicit.
- Added a constrained React Markdown renderer, directory-tree card styling and hostile-HTML/citation interaction tests.
- Reviewed the browser output, found that prompt instructions alone did not guarantee structure, and added the formatter regression rather than assuming model compliance.
- Diagnosed the controller-method example as partial-file retrieval. Added a generic named code-unit intent/resolver, completeness-aware prompt policy and response-shape validation; a flat partial inventory now degrades to insufficient evidence.
- Added semantic Markdown-table rendering with hostile cell text and citation-marker regressions.

### Human decisions and changes

- The developer required all-controller layer traces and Markdown-style directory presentation.
- The developer challenged repo-specific wording. The implementation was corrected from a controller-specific detail intent to generic named code-unit lookup; Petclinic remains a regression fixture rather than a product assumption.
- The implementation remains a modular-monolith heuristic over indexed files; no parser framework, call-graph service, new dependency or hosted model was introduced.
- Full answer-quality evaluation remains a separate human-visible gate in **13.9**.

### Suggestions rejected or deferred

- Compiler/static-analysis call graph — disproportionate complexity for the current scope and unsupported across all indexed languages.
- Full Markdown/HTML library — unnecessary surface and dependency for the requested headings/lists/code/tree/table subset.
- Treating model formatting instructions as sufficient — rejected after the observed flat response; a bounded regression-tested normaliser was added.

### TDD evidence

- Failing tests: architecture questions classified as `explain`; prompt/context lacked layer files; structure answer lacked fenced Markdown; component tests found no semantic heading/tree card; flat model output lacked per-controller sections; a separately packaged domain entity was omitted; method inventory questions embedded/searched instead of exact-loading the named file; lower chunks, table semantics and flat-response refusal were absent.
- Passing focused tests: `backend/.venv/bin/pytest backend/tests/unit/application -q --no-cov`; frontend component tests included in the full Vitest run.
- Refactoring: extracted `MarkdownAnswer`; kept architecture helpers inside the ask use case until another consumer exists.

### Verification performed

- `make lint && make test && make test-evaluation` — passed. Backend: 211 passed, 6 deselected, 82.26% coverage. Frontend: 33 passed, 81.13% line and 79.16% branch coverage. Evaluation tests passed with the existing weak baseline retained honestly.
- Browser: Spring Petclinic structure answer rendered with a semantic heading and labelled tree card. Live Ollama completion was unavailable and returned the safe provider error.
- Playwright: `npm --prefix e2e test` failed on the existing ambiguous “New repository” locator; repair remains explicitly pending in **13.9**.
- Complete working-tree diff inspected; no dependency, migration, public API or raw-HTML rendering was added.

### Files changed

- `PLAN.md` — added/completed 13.8a–13.8c and extended pending 13.9 evaluation/e2e evidence.
- backend intent/ask/prompt modules and focused unit tests — architecture routing, evidence selection, response shape and deterministic structure Markdown.
- frontend chat renderer, styles and component tests — constrained Markdown, tree cards and semantic tables.
- `README.md`, `docs/threat-model.md`, `docs/engineering-journal.md` — behaviour, limitations, security boundary and observed checks.

### Security, quality and limitations

- Exact loads remain repository-scoped and context-limited; citations still pass server verification.
- React escapes all repository/model text; raw HTML is not parsed.
- Architecture discovery relies on conventional paths/names, caps candidates at 32 and cannot prove a runtime call graph. Local Ollama availability/latency remains operational work.
- Named code-unit lookup resolves filenames, not arbitrary symbols declared in differently named files; oversized matches are explicitly partial. Its output validator requires the numeric count to equal the Markdown row count. The default extractive completer cannot synthesize this shape and therefore returns insufficient evidence for these questions; local Ollama is required for the rich answer.

### Evidence

- Tests: commands and outcomes above.
- ADR/plan item: `PLAN.md` 13.8a–13.8c.
- Pull request/commit: TBD.

### Follow-up

- PLAN **13.9** correct-file/insufficient-evidence evaluation and Playwright repair.

## Entry 052 — Persistent indexed file tree panel

**Date:** 2026-09-08  
**Phase/task:** Developer-requested UI follow-up (not PLAN 13.9)  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Show indexed files in a persistent right-hand card as a directory tree, with filename-plus-extension as the primary label and the full path available on hover.

### Context provided to AI

`AGENTS.md`, `README.md`, `PLAN.md`, the existing `FileDrawer` offcanvas, `AppShell`, repository `indexedPaths`, and the running local UI. No credentials were copied into this log.

### Prompt summary

The indexed file list was not visible in the main layout. Add a tall rectangular card on the right of the screen, list indexed files, prefer filename with extension, show the full path on hover, and use directory hierarchy where possible.

### AI contribution

- Added `buildFileTree` tests, then the path-to-tree helper.
- Added `IndexedFilePanel` / `FileTree` component tests for hierarchy, hover titles, extension visibility, filtering and hostile path rendering.
- Wired a desktop-only right-hand card into `AppShell` and kept the existing drawer for small screens and ignored-file counts.

### Human decisions and changes

- This was an explicit product UI request, not the next PLAN item (13.9).
- No public API, persistence or provider change: the panel reads `indexedPaths` already returned by the repository summary.

### Suggestions rejected or deferred

- Paginated flat path list in the new card — rejected in favour of a scrollable tree so directory structure stays visible.
- New backend file-list endpoint — unnecessary; summaries already include indexed paths.

### TDD evidence

- Failing test/command and expected reason: `npm --prefix frontend test -- tests/app/fileTree.test.ts` failed to resolve `../../src/app/fileTree`; `IndexedFilePanel.test.tsx` failed to resolve the panel module.
- Passing focused test/command: the same file-tree and panel files, plus `tests/app/App.test.tsx` (16 tests in that focused set; later 9 tests in the tree/panel files after filter/sort cases).
- Refactoring performed after green: `FileTreeView` memoises the tree; the drawer reuses the same tree for the indexed tab.

### Verification performed

- `npm --prefix frontend run typecheck` — passed.
- `npm --prefix frontend run lint` — passed.
- `npm --prefix frontend run test:coverage` — 41 tests passed; coverage 82% lines / 79.9% branches (thresholds 80 / 75).
- Playwright screenshot of `http://127.0.0.1:3000` against the running `make run` UI showed the right-hand **Indexed files** card with nested folders and filenames including extensions for `tic-tac-toe-react-app-main`. Hover and filter were covered by component tests, not that screenshot.
- Diff inspected for this change set; no new dependencies.

### Files changed

- `frontend/src/app/fileTree.ts` — path tree builder and filename helpers.
- `frontend/src/app/components/FileTree.tsx` — nested directory/file renderer.
- `frontend/src/app/components/IndexedFilePanel.tsx` — right-hand card chrome and filter.
- `frontend/src/app/components/AppShell.tsx`, `App.tsx`, `App.css` — desktop files column and styles.
- `frontend/src/app/components/FileDrawer.tsx` — tree in the indexed tab; mobile/drawer still available.
- frontend tests for the tree, panel and app shell.
- `README.md`, `docs/threat-model.md` — UI journey and untrusted-path rendering.

### Security, quality and limitations

- Indexed paths are untrusted ZIP-derived strings and are rendered as React text.
- The panel lists accepted indexed paths only, not ignored secrets or lockfiles.
- Large indexes scroll in the browser. Desktop shows the card; viewports below 992px use the **Files** control / drawer.

### Evidence

- Tests: commands and outcomes above.
- ADR/plan item: none (not PLAN 13.9).
- Pull request/commit: TBD.

### Follow-up

- PLAN **13.9** evaluation and Playwright repair remain next in the remaining-work sequence.

## Entry 053 — Visible repository delete button

**Date:** 2026-09-08  
**Phase/task:** Developer-requested UI follow-up (not PLAN 13.9)  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Make repository delete visible without opening the top-bar kebab menu.

### Prompt summary

Make the delete button more visible for repo delete.

### AI contribution

- Added a failing app-shell test for a top-bar **Delete repository** button.
- Moved delete out of the kebab menu onto a labelled outline-danger control; kept re-index and indexed-files in the menu.

### TDD evidence

- Failing test: `shows a visible delete control for the selected repository without opening a menu` — no button named "Delete repository" (only the kebab).
- Passing focused test: `npm --prefix frontend test -- tests/app/App.test.tsx` — 10 passed.

### Verification performed

- Focused App tests passed. The local Vite server was not running, so a live screenshot was not captured.

### Files changed

- `frontend/src/app/App.tsx`, `App.css` — visible Delete control.
- `frontend/tests/app/App.test.tsx` — visibility regression.
- `README.md` — top-bar delete wording.

### Follow-up

- PLAN **13.9** remains next.

## Entry 054 — Public README, flow diagram and light remaining-work order

**Date:** 2026-09-08  
**Phase/task:** PLAN 12.1 / 12.2; remaining-work reorder (not 13.9)  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Replace the long README with a reader-friendly guide: run instructions, architecture and request-flow diagrams, honest limitations. Keep observability/productionisation light. Record the remaining-work order: 13.9–13.10, then essential 7/10, light 11, remaining 12 evidence, optional 8.1.

### Prompt summary

Keep observability and productionisation light. Need a clean README, clean script instructions, a logic/flow diagram beside an updated architecture diagram, and removal of redundant README content. Remaining-work review supplied by the developer.

### AI contribution

- Rewrote `README.md`: Docker vs Make, `make help`, architecture mermaid, ingest/ask flow mermaid, RAG table, light observability, productionisation table, three AI-use examples.
- Added `make help` as the default Make target.
- Updated `PLAN.md` remaining-work sequence and marked 12.1 / 12.2 checked with a re-check note.

### Human decisions and changes

- Developer set the completion order and required light Phase 10/11.
- 13.9 was not started in this pass.

### Suggestions rejected or deferred

- Implementing Phase 10/11 now — deferred; README describes the light remaining scope only.
- Checking 13.10 complete — evaluation.md numbers and journal checkpoint still outstanding.

### TDD evidence

- Documentation and Make help text; no production behaviour change. `make help` was run and listed the documented targets.

### Verification performed

- `make help` — printed Run / Check / Also targets as written in the Makefile.
- README project sections present: setup, architecture, productionisation, RAG, decisions, standards, AI use, more time.

### Files changed

- `README.md` — rewritten.
- `Makefile` — `help` and `.DEFAULT_GOAL`.
- `PLAN.md` — remaining-work order; 12.1 / 12.2 checked.
- `AI_DEVELOPMENT_LOG.md` — this entry.

### Follow-up

- PLAN **13.9** answer-correctness evaluation, then **13.10**.

## Entry 055 — Answer-correctness evaluation and retrieval docs

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 13.9 then 13.10  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** partial (hermetic eval green; Playwright not observed in sandbox)

### Objective

Close evaluation as answer correctness, not retrieval-only: expected files/symbols, IE cases, locate `list_items` / `find_by_name`, endpoints listing `GET /items` and `POST /items` from `src/api/handlers.py`. Document observed numbers.

### Context provided to AI

Developer remaining-work order: 13.9 then 13.10, then essential Phase 7/10. Prior extractive ranking and a locate helper call were in progress; `_with_locate_symbol_hits` had to be defined. PLAN forbids marking 13.9 done while locate cites the wrong file or IE cases answer confidently.

### Prompt summary

Continue remaining PLAN work starting at 13.9.

### AI contribution

- Implemented locate identifier pin (`chunks_for_paths`, cap 40).
- Deterministic endpoint answers from the card (no completer).
- Dataset cases for overview/structure/endpoints/deps/architecture/code-unit; eval runner answer-file and IE gates.
- Empty-state **Ingest a ZIP**; Playwright citation path `src/api/handlers.py`.
- `docs/evaluation.md`, README, threat model, PLAN checkboxes, journal.

### Human decisions and changes

- Endpoint listing from extracted card records rather than quoting one controller docstring.
- `code_unit_details` extractive IE counted as outcome_ok for that tagged case only; excluded from answer-file hit rate.
- Playwright host re-run left to the developer (sandbox Chromium arch mismatch).

### Suggestions rejected or deferred

- Raising the CLI gate to 100% `grounded_source_hit_rate` — the tagged method-inventory case still misses lexical top-k.
- Treating extractive method tables as in-scope for the hermetic gate.

### TDD evidence

- Failing: `test_endpoints_question_lists_extracted_routes_from_card` (completer invoked); eval `api-endpoints` `outcome_ok` false; ChatThread **Ingest a ZIP** missing.
- Passing: those tests plus `make test-evaluation` after the card listing and locate pin.

### Verification performed

- `cd backend && .venv/bin/python -m codebase_assistant.evaluation` — exit 0; rates recorded in `docs/evaluation.md`.
- `make test-evaluation` — CLI JSON plus 7 pytest passed.
- `pytest tests/unit/application -q --no-cov` — passed.
- `pytest tests/adversarial/test_matrix.py tests/evaluation -q --no-cov` — passed (part of earlier combined run).
- Frontend ChatThread + App tests — 14 passed.
- `ruff`/`mypy` on `ask.py`, `extractive.py`, evaluation package — passed after format.
- `npm --prefix e2e test` — failed: Playwright looked for `chrome-headless-shell-mac-x64` in the sandbox cache; host has `chrome-headless-shell-mac-arm64`. Not claimed passed.

### Files changed

- `backend/src/codebase_assistant/application/ask.py` — locate pin; deterministic endpoints answer
- `backend/src/codebase_assistant/adapters/extractive.py` — ranking / IE whole-word terms
- `backend/src/codebase_assistant/evaluation/` — runner metrics and CLI gates
- `sample-data/evaluation/dataset.json` — supported question types
- `sample-data/fixture-repository/` — controller, pyproject, README as needed
- `frontend/src/app/components/ChatThread.tsx` — Ingest a ZIP
- `e2e/tests/upload-ask.spec.ts` — handlers.py citation
- `docs/evaluation.md`, `docs/threat-model.md`, `docs/engineering-journal.md`, `README.md`, `PLAN.md`

### Security, quality and limitations

- Card route/path strings stay untrusted; table cells strip `|` and newlines.
- Locate scan is repository-scoped and capped.
- Extractive method inventories remain insufficient evidence.

### Evidence

- Tests: evaluation suite, intent_context endpoints/locate, ChatThread
- Plan items: 13.9, 13.10
- Pull request/commit: TBD until created

### Follow-up

- Host `make test-e2e`
- PLAN **7.1** Pydantic response models

## Entry 056 — Host Playwright, screenshots, and E2E evidence

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 12.3, 12.4, residual 13.9 host e2e  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed (CI dispatch pending until the branch is on GitHub)

### Objective

Close the leftover host Playwright run, capture the five required product screenshots, and replace the stale “suite not completed” E2E note in the docs.

### Context provided to AI

Minimum path to release evidence: fix and rerun E2E, capture/commit screenshots, correct E2E documentation, trigger existing CI if possible. Do not expand into Phase 7/10/11.

### Prompt summary

Make the changes direct; do not create extra mess.

### AI contribution

- Disambiguated Playwright locators: **Ingest** `exact: true`; wait for the ingest dialog to close; assert `list_items` in the citation excerpt.
- Extended the same spec to assert **Insufficient evidence** for the OAuth question and to write `docs/screenshots/01`–`05`.
- Updated evaluation, journal, PLAN, README.

### Human decisions and changes

- Screenshots are produced by the existing e2e journey rather than a second capture tool.
- Optional video was not created.

### Suggestions rejected or deferred

- Phase 7/10/11 implementation.
- **12.5** read-only review.

### TDD evidence

- First host run failed: `getByRole('button', { name: 'Ingest' })` matched **Ingest a ZIP** and **Ingest**.
- Next failure: `getByText('fixture-repository')` matched two strings still in the open modal.
- Next failure: `getByText(/list_items/)` matched four visible nodes (strict mode).
- Passing: `make test-e2e` — 1 passed (3.0s).

### Verification performed

- `unset PLAYWRIGHT_BROWSERS_PATH; npm --prefix e2e test` — 1 passed.
- `unset PLAYWRIGHT_BROWSERS_PATH; make test-e2e` — 1 passed (3.0s).
- Screenshots written under `docs/screenshots/`.

### Files changed

- `e2e/tests/upload-ask.spec.ts` — locators, IE assertion, screenshot capture
- `docs/screenshots/*.png` — upload, ingest summary, cited answer, inspector, IE
- `docs/evaluation.md`, `docs/engineering-journal.md`, `PLAN.md`, `README.md`, `AI_DEVELOPMENT_LOG.md`

### Security, quality and limitations

- E2E still uses fake providers only.
- `PLAYWRIGHT_BROWSERS_PATH` pointing at an x64 sandbox cache still breaks Chromium on this arm64 host; the passing run unset that variable.

### Evidence

- Tests: Playwright `upload-ask.spec.ts`
- Plan items: 12.3, 12.4, 13.9 host e2e
- Pull request/commit: TBD until created

### Follow-up

- PLAN **12.5** read-only review
- Trigger `.github/workflows/ci.yml` (`workflow_dispatch`)

## Entry 057 — Recapture live tic-tac-toe screenshots

**Date:** 2026-09-08  
**Phase/task:** PLAN.md 12.4  
**Tool/model:** Cursor (Grok 4.6)  
**Status:** completed

### Objective

Replace the hermetic-fixture screenshots. They were hard to read and the gallery ended on insufficient evidence.

### Prompt summary

Screenshots are not clear; they hit insufficient evidence. Use the attached tic-tac-toe ZIP in `tmp/`.

### AI contribution

- Recaptured five live shots against `make run` + Ollama using `tic-tac-toe-react-app-main.zip`.
- Questions: overview, `checkWinnerFrom` locate with inspector, directory structure. Upload cropped to `.modal-content`.
- Stopped Playwright from writing into `docs/screenshots/` so `make test-e2e` cannot overwrite the demo images.
- Ignored `tmp/`.

### Human decisions and changes

- Keep insufficient evidence in the e2e assertion, not in the README gallery.

### Verification performed

- Capture script against `http://localhost:3000` completed without the insufficient-evidence callout on the three demo questions.
- Images written under `docs/screenshots/01`–`05-directory-structure.png`.

### Follow-up

- PLAN **12.5**

## Entry 058 — Clarify the initial product identity

**Date:** 2026-09-09
**Phase/task:** PLAN.md 12.6
**Tool/model:** Codex
**Status:** completed

### Objective

Make the selected product direction explicit at the top of the README using the original internal wording. This was later replaced with a standalone public identity.

### AI contribution

- Updated the README heading and opening sentence.
- Added and completed PLAN task 12.6 to record the product clarification.

### Human decisions and changes

- The developer required a specific internal title at that stage; it was replaced before public release.

### Verification performed

- Confirmed the README heading and opening sentence used the selected internal title at that stage.
- Inspected the diff; no product code changed.

### Follow-up

- PLAN **12.5** remains pending.

## Entry 059 — Sanitize the repository for public portfolio use

**Date:** 2026-09-17
**Phase/task:** User-requested public repository sanitization
**Tool/model:** Codex
**Status:** completed for the working tree; clean-history publication pending

### Objective

Remove source-organisation, private-link, origin-specific framing and personal-data references from the public working tree while preserving the product and its engineering evidence.

### Context provided to AI

The repository is intended to become a public portfolio project. The developer asked to remove references to its original source and improve how a new reader understands the work.

### AI contribution

- Deleted the original brief containing a private URL.
- Reframed the README and plan around the standalone **Codebase Intelligence Assistant** product.
- Sanitized historical documentation, ADRs, test names and comments while preserving technical decisions and observed outcomes.
- Removed the obsolete source-organisation Git remote from the local repository.
- Audited tracked text, image strings, ignored environment files and Git history for likely public-release concerns.

### Human decisions and changes

- The developer requested the public sanitization and retains authority over any Git-history rewrite, force-push, repository rename and licence choice.

### Suggestions rejected or deferred

- Rewriting and force-pushing Git history — deferred because it is destructive and needs explicit approval.
- Adding an open-source licence — deferred because the licence is a legal/product choice for the developer.

### TDD evidence

- Failing test/command and expected reason: not applicable for the documentation-only sanitization. The first focused test command did not start because the ignored virtual environment retained a stale absolute interpreter path from an earlier checkout.
- Passing focused test/command: `python3 -m pytest backend/tests/unit/application/test_intent.py backend/tests/evaluation/test_dataset.py -q --no-cov` — 32 passed.
- Refactoring performed after green: none.

### Verification performed

- `python3 -m ruff check ...` — passed for the three touched Python files.
- `python3 -m ruff format --check ...` — three files already formatted.
- `npm --prefix frontend run typecheck` — passed.
- `npm --prefix frontend run lint` — passed.
- `git diff --check` — passed.
- Targeted tracked-file and sensitive-phrase searches found no source-organisation URL/name, origin-specific framing, personal email, personal name or absolute user path in the current tree.
- Docker-based Gitleaks did not run because the Docker daemon was unavailable. The full scan remains outstanding.

### Files changed

- `README.md` — standalone public product identity and neutral project wording.
- `PLAN.md`, `AGENTS.md` — public-release language and neutral examples.
- `docs/` ADRs, threat model, evaluation and journal — sanitized source-specific wording and links.
- `AI_DEVELOPMENT_LOG.md` — sanitized historical references and this factual entry.
- `backend/src/.../intent.py` and related tests — neutral comment and test names; no behavior change.
- Original source brief — removed because it contained a private URL and source-specific material.

### Security, quality and limitations

- Local `.env` and `config/app.env` are ignored and have no tracked history.
- Current tracked files contain intentional fake secret strings used by security tests and the controlled fixture.
- The private source repository history still contains the removed brief, original remote identity and author emails, so it must remain private. Public release must start from a clean sanitized snapshot rather than pushing that history.

### Evidence

- Tests: focused intent and evaluation dataset tests; Python and frontend static checks.
- Plan item: user-assigned task outside the feature sequence.
- Pull request/commit: TBD until created.

### Follow-up

- Choose either a new public repository with a clean single-root history or an approved history rewrite before publishing.
- Run `make security` with Docker available.
- Choose a licence and optionally rename the GitHub repository to match the product.

## Entry 060 — Publish a clean-history public repository

**Date:** 2026-09-17
**Phase/task:** User-requested public repository publication
**Tool/model:** Codex
**Status:** completed

### Objective

Publish the sanitized project as a new public GitHub repository without exposing the private source repository's earlier history.

### AI contribution

- Confirmed the source repository remained private and the target repository name was available.
- Exported the reviewed sanitization commit as a tracked-file snapshot with no inherited `.git` data.
- Initialized a new `main` history and used the developer's GitHub no-reply author address.
- Created and pushed the public `codebase-intelligence-assistant` repository.
- Added accurate technology topics for discoverability.

### Verification performed

- The public repository reports `PUBLIC` visibility and `main` as its default branch.
- The initial public history contains one root commit, `bf14e39`, with 185 tracked files.
- The pushed `main` ref matched local commit `bf14e3902c3ce98732afbcba61aecc393ea323a8` before this publication-log follow-up.
- The published tree contains neither the removed source brief nor local `.env` files.
- The root commit author uses `59412791+ArifMehmood16@users.noreply.github.com`.

### Security, quality and limitations

- The original repository and its historical sensitive references remain private and were not connected to the public remote.
- The public repository contains only the sanitized snapshot and subsequent public-safe commits.
- A full Docker-based Gitleaks scan remains outstanding because Docker Desktop was unavailable.
- No open-source licence was added; that decision remains with the developer.

### Evidence

- Repository: `https://github.com/ArifMehmood16/codebase-intelligence-assistant`
- Initial public root commit: `bf14e39`
- Publication-log commit: the commit containing this entry.

### Follow-up

- Run `make security` when Docker is available.
- Choose and add a licence if reuse permissions should be granted.

## Entry template

Copy this section for each meaningful AI-assisted task.

```markdown
## Entry NNN — Short task name

**Date:** YYYY-MM-DD  
**Phase/task:** PLAN.md X.Y  
**Tool/model:** tool and model/version if known  
**Status:** completed | partial | blocked

### Objective

What outcome was requested?

### Context provided to AI

Summarise the relevant files, requirements and constraints. Do not include secrets.

### Prompt summary

Summarise what the AI was asked to analyse, implement or review. Link to a
checked-in prompt only if preserving it adds real evidence.

### AI contribution

- Tests, code, review findings, alternatives or documentation it proposed.

### Human decisions and changes

- What was approved?
- What was changed manually or constrained?
- Which decision remained the developer's and why?

### Suggestions rejected or deferred

- Proposal — reason it was not used.

### TDD evidence

- Failing test/command and expected reason:
- Passing focused test/command:
- Refactoring performed after green:

### Verification performed

- Exact commands run and observed summary.
- Diff/code/security review performed.
- Never claim unobserved checks.

### Files changed

- `path` — purpose

### Security, quality and limitations

- Risks considered, controls applied and residual limitations.

### Evidence

- Tests:
- ADR/plan item:
- Pull request/commit: TBD until created

### Follow-up

- Remaining task or `None`.
```

## Phase summary template

Complete this at each phase boundary.

```markdown
## Phase N AI usage summary

### AI-supported activities

-

### Most useful contribution

-

### Material output rejected or corrected

-

### Human-owned decisions

-

### Verification evidence

-

### Learning carried forward

-
```

## Final README summary template

Use the completed log to write the README section near release. Do not fill this with planned work.

```markdown
## How AI tools were used

AI coding tools supported [actual activities]. I retained responsibility for
[actual human-owned decisions]. I reviewed [actual review method] and verified
changes through [actual test and quality evidence].

Examples include:

- [specific example with accepted/changed/rejected proposal and verification]
- [specific example]
- [specific example]

AI was not given secrets or production data. Its output was treated as
untrusted until reviewed and tested. The detailed development record is in
AI_DEVELOPMENT_LOG.md.
```
