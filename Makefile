.PHONY: help setup format lint test test-integration test-evaluation test-e2e security verify config run run-docker down ensure-ollama-models

PYTHON ?= python3
BACKEND_VENV = backend/.venv
BACKEND_BIN = $(BACKEND_VENV)/bin
FRONTEND_NPM = npm --prefix frontend
ENV_FILE ?= config/app.env
COMPOSE = docker compose --env-file $(ENV_FILE)
LOAD_ENV = set -a && . ./$(ENV_FILE) && if [ -f .env ]; then . ./.env; fi && set +a

.DEFAULT_GOAL := help

help:
	@echo "Codebase Assistant"
	@echo ""
	@echo "Run"
	@echo "  make setup              Copy config/app.env if missing; install Python and Node deps"
	@echo "  make run                Host API + Vite (local Postgres; does not start Docker)"
	@echo "  make run-docker         Compose Postgres, Ollama, API, web; pull required models"
	@echo "  make down               Stop Compose services"
	@echo ""
	@echo "Check"
	@echo "  make lint               Ruff, mypy, TypeScript, ESLint"
	@echo "  make test               Hermetic backend and frontend tests"
	@echo "  make test-integration   Postgres/pgvector tests (needs a running database)"
	@echo "  make test-evaluation    Fixture retrieval/answer baseline"
	@echo "  make test-e2e           Playwright upload-to-citation (needs zip + Chromium)"
	@echo "  make security           Bandit, pip-audit, npm audit, Gitleaks, Trivy"
	@echo "  make verify             lint + test + security"
	@echo ""
	@echo "Also"
	@echo "  make format             Auto-fix Ruff format and lint"
	@echo "  make config             Ensure config/app.env exists"
	@echo ""
	@echo "Settings: $(ENV_FILE) (copy from config/app.env.example). Optional root .env overlays host runs."

config:
	test -f $(ENV_FILE) || cp config/app.env.example $(ENV_FILE)

setup: config
	$(PYTHON) -m venv $(BACKEND_VENV)
	$(BACKEND_BIN)/pip install -U pip
	$(BACKEND_BIN)/pip install -r backend/requirements.lock
	$(BACKEND_BIN)/pip install --no-deps -e ./backend
	$(FRONTEND_NPM) ci

format:
	$(BACKEND_BIN)/ruff format backend/src backend/tests backend/migrations
	$(BACKEND_BIN)/ruff check --fix backend/src backend/tests backend/migrations

lint:
	$(BACKEND_BIN)/ruff check backend/src backend/tests backend/migrations
	$(BACKEND_BIN)/ruff format --check backend/src backend/tests backend/migrations
	cd backend && .venv/bin/mypy
	$(FRONTEND_NPM) run typecheck
	$(FRONTEND_NPM) run lint

test:
	cd backend && .venv/bin/pytest
	$(FRONTEND_NPM) run test:coverage

test-integration:
	# Integration is a narrow Postgres suite; do not apply the default 80% coverage gate.
	cd backend && .venv/bin/pytest -m integration -q --no-cov

test-evaluation:
	# Hermetic lexical+extractive baseline against sample-data/evaluation/dataset.json.
	cd backend && .venv/bin/python -m codebase_assistant.evaluation
	cd backend && .venv/bin/pytest tests/evaluation -q --no-cov

test-e2e:
	# Playwright upload→ask→citation against in-memory API (fake providers).
	@command -v zip >/dev/null || (echo "test-e2e requires the zip CLI on PATH." && exit 1)
	@test -x $(BACKEND_BIN)/python || (echo "Run make setup first." && exit 1)
	npm --prefix e2e ci
	npm --prefix e2e exec -- playwright install chromium
	npm --prefix e2e test

security:
	$(BACKEND_BIN)/bandit -r backend/src
	$(BACKEND_BIN)/pip-audit -r backend/requirements.lock
	$(FRONTEND_NPM) audit --omit=dev
	docker run --rm -v "$(CURDIR):/src" -w /src ghcr.io/gitleaks/gitleaks:latest detect --source /src --no-git --verbose --config /src/.gitleaks.toml
	docker run --rm -v "$(CURDIR):/src" aquasec/trivy:latest fs --skip-dirs /src/frontend/node_modules --skip-dirs /src/backend/.venv --severity HIGH,CRITICAL --exit-code 1 /src

verify: lint test security

run-docker: config
	@test -x $(BACKEND_BIN)/python || (echo "Run make setup first." && exit 1)
	$(LOAD_ENV) && \
	$(COMPOSE) up -d --build && \
	$(MAKE) ensure-ollama-models && \
	echo "Web http://localhost:$$FRONTEND_PORT  API http://localhost:$$API_PORT"

# Host API + Vite. Uses local Postgres and Ollama from config/app.env / .env.
# Does not start Docker. For Compose services use make run-docker.
run: config
	@test -x $(BACKEND_BIN)/uvicorn || (echo "Run make setup first." && exit 1)
	$(LOAD_ENV) && \
	if [ -z "$$DATABASE_URL" ] && { [ -z "$$DATABASE_USER" ] || [ -z "$$DATABASE_NAME" ]; }; then \
		echo "Set DATABASE_URL or DATABASE_USER and DATABASE_NAME for local Postgres (config/app.env or .env)."; \
		exit 1; \
	fi && \
	cd backend && .venv/bin/alembic upgrade head && cd .. && \
	$(MAKE) ensure-ollama-models && \
	echo "Web http://localhost:$$FRONTEND_PORT  API http://localhost:$$API_PORT" && \
	trap 'kill 0' EXIT && \
	$(BACKEND_BIN)/uvicorn codebase_assistant.main:app --reload --host "$$API_HOST" --port "$$API_PORT" & \
	$(FRONTEND_NPM) run dev

# Pull models required by EMBEDDING_PROVIDER / COMPLETION_PROVIDER when missing.
ensure-ollama-models: config
	@test -x $(BACKEND_BIN)/python || (echo "Run make setup first." && exit 1)
	$(LOAD_ENV) && \
	$(BACKEND_BIN)/python -m codebase_assistant.ops.ollama_models \
		--host "$${OLLAMA_HOST:-http://127.0.0.1:11434}" \
		--embedding-provider "$${EMBEDDING_PROVIDER:-lexical}" \
		--completion-provider "$${COMPLETION_PROVIDER:-extractive}" \
		--embed-model "$${OLLAMA_EMBED_MODEL:-nomic-embed-text}" \
		--chat-model "$${OLLAMA_CHAT_MODEL:-llama3.2}"

down: config
	$(COMPOSE) down
