# Fixture Inventory Service

Synthetic sample repository for evaluation and demos of the Codebase Intelligence Assistant.

It is intentionally small and contains **no proprietary code**. Strings that look like secrets are placeholders only (`FIXTURE_NOT_A_SECRET`).

## What lives where

- `src/api/handlers.py` — HTTP-style request handlers (`list_items`, `create_item`).
- `src/api/ItemController.py` — controller that calls `InventoryService`.
- `src/services/inventory.py` — service calls used by those handlers.
- `src/models/item.py` — `InventoryItem` model.
- `pyproject.toml` — declared fixture dependency (`pydantic`).
- `config/settings.toml` — runtime configuration knobs.
- `docs/architecture.md` — narrative that is mostly irrelevant to coding questions.
- `scripts/seed_demo_data.py` — one-off noise script.
- `config/credentials.json` and `vendor/` — deliberately ignored by ingestion policy.

## Reviewer tip

Ask: `Where is list_items defined?` or `How does create_item validate names?`
