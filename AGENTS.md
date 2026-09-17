# Instructions for Coding Agents

This file applies to the entire repository. Human instructions always take precedence. `PLAN.md` is the authoritative execution order; `README.md` describes the intended product and architecture.

## Mission

Build the project incrementally as a simple, production-minded modular monolith. Demonstrate senior engineering judgement through explicit trade-offs, secure boundaries, reliable tests and clear documentation—not through additional frameworks or services.

## Mandatory working protocol

For every task:

1. Read `README.md`, `PLAN.md`, `AGENTS.md` and the latest relevant entries in `AI_DEVELOPMENT_LOG.md`.
2. Locate the current phase and task in `PLAN.md`.
3. Inspect relevant code and tests before proposing edits.
4. Restate the selected task, acceptance criteria and expected files.
5. Identify assumptions or conflicts. Ask before making a material architectural choice not already approved.
6. Write or update the smallest failing test first.
7. Run it and confirm that it fails for the expected behavioural reason.
8. Add the minimum implementation required to pass.
9. Run the focused test again.
10. Refactor only while the tests remain green.
11. Run the phase quality checks.
12. Inspect the complete diff for unrelated changes, security issues and unnecessary complexity.
13. Update documentation required by the phase.
14. Draft a factual AI log entry based only on work actually performed.
15. Stop at the phase checkpoint and report results. Do not automatically begin the next phase.

If the environment cannot demonstrate the red test because the feature already exists, explain why and add a regression test that would fail if the relevant behaviour were removed.

## Task boundaries

- Work on one unchecked `PLAN.md` task or explicitly assigned group of tasks at a time.
- Do not start a later phase while an earlier exit gate is incomplete.
- Do not change architecture, provider, database or public API without documenting the decision and receiving approval.
- Do not modify unrelated files or reformat the entire repository.
- Do not create speculative abstractions or unused extension points.
- Do not add dependencies without stating why the standard library or an existing dependency is insufficient.
- Do not silently change scope to make a test pass.
- Do not weaken, delete, skip or mark tests as expected failures merely to obtain green CI.
- Do not suppress lint, type or security findings without a narrow documented justification.
- Do not claim a command passed unless it was run and its result was observed.
- Do not claim compliance, security or production readiness as an absolute.

## Branch and commit wording

Branches and commit messages must be readable by someone who was not in the chat.

### Branches

- Use lowercase words separated by hyphens. A `docs/`, `feat/`, `fix/`, `test/`, `build/` or `ci/` prefix is allowed when it helps.
- Name the phase or feature and the outcome, not a nickname, ticket-only slug or `wip`.
- One concern per branch. Do not reuse a Phase 0 docs branch for later application work.
- Prefer `docs/phase-0-repository-baseline-and-decisions` or `feat/phase-3-secure-zip-ingestion` over `p0`, `tmp`, `updates` or `quick-fix`. Include the phase number in the branch name.

### Commits

- Conventional prefixes (`docs:`, `feat(ingestion):`) are fine when the rest is still plain English.
- The subject must be an imperative sentence that states the change, not a file list.
- Add a short body when the why is not obvious from the subject.
- Avoid `wip`, `misc`, `update files`, `address comments` or commit-message-only hashes.

Good: `docs: record repository baseline and initial architecture decisions`
Poor: `update`, `phase0`, `asdf`

When asked to commit, create or use a dedicated readable branch unless the developer explicitly asks for `main`.

## TDD standard

Use red-green-refactor at behaviour boundaries:

- **Red:** add one focused test expressing an acceptance criterion; confirm the failure is expected.
- **Green:** implement the smallest correct behaviour.
- **Refactor:** improve names/structure and remove duplication with all related tests green.

Tests should describe observable behaviour. Prefer fakes at provider boundaries and real collaborators inside the domain/application. Mock framework edges only when a fake is impractical.

Every production defect fixed must receive a regression test first.

### Test layers

- Unit: domain policies, filtering, chunking, prompt construction and use cases.
- API: validation, status codes, response contracts and safe error mapping.
- Integration: PostgreSQL/pgvector, migrations and concrete adapters.
- Component: frontend interactions, accessibility and error/loading states.
- End-to-end: one critical upload-to-cited-answer journey using deterministic model providers.
- Evaluation: retrieval and citation behaviour against a controlled fixture repository.
- Manual smoke: explicitly enabled real embedding/LLM provider only.

Default tests must be deterministic, repeatable and independent of paid APIs or public network access.

## Architecture rules

- Keep the backend a modular monolith.
- Domain and application modules must not import FastAPI, SQLAlchemy or provider SDKs.
- HTTP routes translate requests/responses and invoke use cases; they contain no business logic.
- Use interfaces/protocols only at external or meaningfully variable boundaries.
- Provider implementations belong in adapters.
- Configuration is injected; domain code must not read environment variables.
- Persistence models must not become domain models by convenience.
- Keep the frontend feature-oriented and avoid global state unless actual shared state requires it.
- Prefer explicit Python/TypeScript over metaprogramming and opaque framework magic.

## SOLID interpretation

- **Single responsibility:** modules have one reason to change; do not split trivial cohesive code across excessive classes.
- **Open/closed:** provider adapters can be replaced through stable ports; do not predict every future variation.
- **Liskov substitution:** test provider fakes against the same behavioural contract where useful.
- **Interface segregation:** keep ports small and use-case specific.
- **Dependency inversion:** application logic depends on ports, never concrete SDK clients.

SOLID is a design aid, not a target class count.

## Security rules

Treat uploads, archive members, repository text, user questions, retrieved chunks and model output as untrusted.

Mandatory controls:

- Never execute, import, compile or evaluate uploaded repository content.
- Defend against ZIP slip, absolute paths, symlinks, decompression bombs and resource exhaustion.
- Enforce configurable archive, extracted-size, file-count, per-file, question, context and output limits.
- Use allowlists for accepted extensions and safe path handling.
- Exclude secrets, binaries, dependency trees, VCS metadata and build output.
- Repository content cannot issue instructions to the application or override the system prompt.
- Validate model output and verify citations against retrieved server-side metadata.
- Escape source excerpts in the browser; never inject them as raw HTML.
- Use parameterised database access and repository-scoped queries.
- Return safe external errors; never expose stack traces, prompts, secrets or provider payloads.
- Do not send repository text, retrieved chunks or prompts to a hosted LLM API. Real inference uses local Ollama ([ADR 004](docs/adr/004-ollama-local-inference.md)).
- Do not log source code, raw uploads, embeddings, full prompts, credentials or model responses.
- Keep secrets in environment variables locally and secret management in production.
- Use least-privilege CI permissions and pin automation actions to stable versions/SHAs where practical.

Update `docs/threat-model.md` when a trust boundary or control changes.

## Code quality rules

- Python must be typed at public boundaries and pass the configured Ruff and mypy checks.
- TypeScript must use strict mode and avoid unjustified `any`.
- Prefer small functions, cohesive modules and descriptive names.
- Avoid boolean parameters when they obscure behaviour.
- Avoid broad exception handling; translate known infrastructure failures at boundaries.
- Preserve exception causes internally without exposing them externally.
- Comments explain why, constraints or risk—not what obvious code does.
- Remove dead code. Do not commit commented-out implementations.
- Coverage supports confidence but does not replace meaningful assertions.
- New/changed code should meet the configured coverage gate; do not test trivial implementation details solely to increase percentage.

## Documentation rules

Documentation is part of the change:

- Keep `README.md` commands and current limitations accurate.
- Update `PLAN.md` checkboxes only after exit criteria are proven.
- Add or amend an ADR for consequential, difficult-to-reverse choices.
- Update `docs/engineering-journal.md` at phase checkpoints with commands and observed outcomes.
- Update `docs/threat-model.md` for security boundary changes.
- Update `docs/evaluation.md` for datasets, metrics, thresholds or results.
- Add a factual entry to `AI_DEVELOPMENT_LOG.md` for agent-assisted work.

Never invent command output, test results, commit hashes, dates, metrics or review actions. Use `TBD` until evidence exists.

## AI-assisted development rules

- AI suggestions are proposals, not authority.
- Explain material options and trade-offs before implementing an unrecorded decision.
- Do not send secrets, credentials, personal data or proprietary external code to an AI service.
- Inspect all AI-generated diffs.
- Verify suggested APIs and security claims against installed versions or official documentation when necessary.
- Record rejected or materially changed suggestions, not only successful output.
- Identify the human-owned decision and validation for each significant entry.
- Prepare the log draft; the human reviews and approves it.

## Required task report

At each checkpoint, report:

```text
Plan task:
Status: completed | blocked | partial

Changed:
- files and purpose

TDD evidence:
- failing test and expected failure
- passing focused test

Verification:
- exact commands run
- observed result summary

Security/quality review:
- findings and mitigations

Documentation:
- files updated

Residual risks or decisions needed:
- items, or "none"

Suggested branch:
- readable hyphenated name of the phase or feature and its outcome

Suggested commit:
- readable conventional subject, for example `docs: record repository baseline and initial architecture decisions`
```

Stop and ask when credentials, external writes, destructive actions, scope expansion or a material product/architecture choice requires human authority.
