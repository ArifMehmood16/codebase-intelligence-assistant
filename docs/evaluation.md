# Evaluation evidence

This document records retrieval/answer evaluation datasets, metrics and observed results. Do not invent thresholds or outcomes.

## Fixture repository (PLAN 9.1)

Controlled sample tree: [`sample-data/fixture-repository/`](../sample-data/fixture-repository/).

| Area | Path | Role |
|---|---|---|
| README | `README.md` | Product overview for overview/structure pins |
| Manifest | `pyproject.toml` | PEP 621 dependency `pydantic` |
| Handlers | `src/api/handlers.py` | `list_items`, `create_item`, `GET /items`, `POST /items` |
| Controller | `src/api/ItemController.py` | Layered controller → in-memory service (no database) |
| Service | `src/services/inventory.py` | `find_by_name` and inventory calls |
| Model | `src/models/item.py` | `InventoryItem` |
| Config | `config/settings.toml` | Indexed settings |
| Distractor docs | `docs/architecture.md` | Irrelevant narrative plus injection bait |
| Noise script | `scripts/seed_demo_data.py` | Offline seed helper |
| Ignored secret | `config/credentials.json` | Must not be indexed |
| Ignored vendor | `vendor/leftpad.js` | Excluded directory |

The tree is original fixture code only. Placeholder token: `FIXTURE_NOT_A_SECRET`.

Layout and ingest behaviour are locked by `backend/tests/unit/test_fixture_repository.py`.

## Dataset (PLAN 9.2 / 13.9)

Path: [`sample-data/evaluation/dataset.json`](../sample-data/evaluation/dataset.json).

Schema:

- `version` — dataset format version (`1`)
- `fixture_repository` — relative path to the controlled tree
- `cases[]`:
  - `id` — stable case id
  - `question` — reviewer/eval question text
  - `expect.kind` — `grounded` or `insufficient_evidence`
  - for `grounded`: `expected_files`, `expected_symbols`
  - optional `tags` / `injection_source_files`

Current cases (14):

| id | kind | Notes |
|---|---|---|
| `list-items-location` | grounded | `list_items` in `src/api/handlers.py` |
| `create-item-validation` | grounded | `create_item` validation |
| `inventory-service-find` | grounded | `find_by_name` in `src/services/inventory.py` |
| `inventory-item-model` | grounded | `InventoryItem` |
| `settings-page-size` | grounded | `default_page_size` in settings |
| `repo-overview` | grounded | README purpose |
| `directory-structure` | grounded | Outline plus a real cited file |
| `api-endpoints` | grounded | `GET /items` and `POST /items` citing `src/api/handlers.py` |
| `declared-dependencies` | grounded | `pydantic` in `pyproject.toml` |
| `controller-database-flow` | grounded | `ItemController`; absent DB hop must not be invented |
| `inventory-service-methods` | grounded, tag `code_unit_details` | Method table; extractive cannot synthesise it |
| `oauth-unsupported` | insufficient_evidence | No auth code in fixture |
| `payment-unsupported` | insufficient_evidence | No payments code |
| `prompt-injection-policy-override` | insufficient_evidence | Bait in `docs/architecture.md` |

Injection bait text was added to `docs/architecture.md` for evaluation only; answers must not treat it as system policy.

## Runner and metrics (PLAN 9.3 / 13.9)

Package: `codebase_assistant.evaluation`.

Commands:

```bash
make test-evaluation
# or
cd backend && .venv/bin/python -m codebase_assistant.evaluation
```

Hermetic configuration recorded with every report:

| Field | Baseline value |
|---|---|
| `embedding_provider` | `lexical` |
| `completion_provider` | `extractive` |
| `retrieval_k` | `5` |
| Dataset | `sample-data/evaluation/dataset.json` |
| Fixture | `sample-data/fixture-repository` |

Metrics:

| Metric | Meaning |
|---|---|
| `grounded_source_hit_rate` | Share of grounded cases where an expected file appears in vector hits **or** cited files |
| `grounded_answer_file_hit_rate` | Share of grounded cases (excluding `code_unit_details`) whose citations include an expected file |
| `citation_validity_rate` | Share of cases whose citations match ask-path excerpts |
| `insufficient_evidence_correct_rate` | Share of IE-expected cases that return `insufficient_evidence` |
| `outcome_pass_rate` | Grounded: cited expected file **and** expected symbols in answer/excerpts; tagged `code_unit_details` counts as OK when extractive returns IE; IE-expected: insufficient-evidence flag |
| `latency_ms` | Per-case wall time for retrieve + answer |

### Evidence-based gate (lexical + extractive)

Observed on 2026-09-08 after intent routing, extractive ranking, locate identifier pin, and deterministic endpoint listing. Locked by `backend/tests/evaluation/test_runner.py` and CLI exit code:

- `citation_validity_rate` must be `1.0`
- `insufficient_evidence_correct_rate` must be `1.0`
- `grounded_source_hit_rate` must be `>= 0.75` (observed `0.909`)
- `grounded_answer_file_hit_rate` must be `>= 0.8` (observed `1.0`)
- `list-items-location` must cite `src/api/handlers.py`
- `api-endpoints` must cite `src/api/handlers.py` and include `GET /items` and `POST /items`

`inventory-service-methods` is excluded from `grounded_answer_file_hit_rate`. Extractive completion cannot emit the required summary/count/table; the ask path returns insufficient evidence. That is counted as `outcome_ok` for the tagged case only. Conversational inventories need `COMPLETION_PROVIDER=ollama` and are out of this hermetic gate.

## Observed results

Date: 2026-09-08. Providers: lexical + extractive. `k=5`.

Command: `cd backend && .venv/bin/python -m codebase_assistant.evaluation` (also `make test-evaluation`).

| Metric | Value |
|---|---|
| `outcome_pass_rate` | `1.0` |
| `grounded_source_hit_rate` | `0.9090909090909091` |
| `grounded_answer_file_hit_rate` | `1.0` |
| `citation_validity_rate` | `1.0` |
| `insufficient_evidence_correct_rate` | `1.0` |
| Per-case latency | ~0.7–2.0 ms |

Honest notes on this baseline:

- `inventory-service-find` cites `src/services/inventory.py` even when that file is absent from lexical top-5; locate prepends identifier-matching chunks from a capped repository-scoped path scan.
- `api-endpoints` lists extracted routes from the card (no completer). Citations can include `src/api/ItemController.py` as well as `src/api/handlers.py` because both declare `GET /items`.
- `inventory-service-methods` is extractive insufficient evidence (`source_hit_at_k` false); tagged outcome is still OK as above.
- `grounded_source_hit_rate` is not 1.0 because that tagged code-unit case still contributes to the retrieval-hit denominator.

Re-run with `COMPLETION_PROVIDER=ollama` is out of scope for the hermetic gate; document any future Ollama eval separately with model name and host.

## Browser E2E (PLAN 9.4 / 13.9)

```bash
make test-e2e
```

Playwright (`e2e/`) starts an in-memory API (`codebase_assistant.ops.e2e_api`, lexical + extractive) on `:8010` and Vite on `:3010`, uploads the fixture ZIP via the empty-state **Ingest a ZIP** control (modal submit is the exact name **Ingest**; sidebar remains **New repository**), asks “Where is list_items defined?”, and requires a citation whose path title is `src/api/handlers.py` plus `list_items` in the opened excerpt. It then asks “How does OAuth login work in this service?” and requires the **Insufficient evidence** callout.

Product screenshots in [`docs/screenshots/`](screenshots/) are a separate live Ollama demo of `tmp/tic-tac-toe-react-app-main.zip`, not produced by this hermetic suite.

Observed 2026-09-08 on the developer machine (arm64 Chromium, `PLAYWRIGHT_BROWSERS_PATH` unset):

```text
make test-e2e
# 1 passed (3.0s) — tests/upload-ask.spec.ts
```

## Adversarial matrix (PLAN 9.5)

| Case | Coverage |
|---|---|
| Hostile ZIP slip | `tests/adversarial/test_matrix.py` |
| Nested secrets ignored | same |
| Prompt-injection citation coercion | same (+ Phase 6.5) |
| Citation forgery (expanded range) | same |
| Oversized question | same |
| Unavailable completion provider → safe 503 | same |
| Repeated upload → distinct repository IDs | same |
| Escaped source rendering | `frontend/tests/app/App.test.tsx` |

Unavailable database is covered by hermetic in-memory defaults when no usable `DATABASE_URL` is configured; Postgres isolation remains in integration tests.

## Residual risks

- Lexical retrieval is not semantic; Ollama embeddings will change hit rates and must be measured before raising gates.
- Extractive answers are not conversational. Named method inventories remain insufficient evidence on this baseline.
- Locate identifier pin scans at most 40 indexed paths in the current repository; it is not a global symbol index.
- E2E uses fake providers only; it does not prove Ollama latency or quality.
