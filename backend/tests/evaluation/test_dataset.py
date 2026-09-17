"""Evaluation dataset schema and fixture alignment (PLAN 9.2)."""

from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DATASET_PATH = _REPO_ROOT / "sample-data" / "evaluation" / "dataset.json"
_FIXTURE_ROOT = _REPO_ROOT / "sample-data" / "fixture-repository"

_REQUIRED_CASE_KEYS = frozenset({"id", "question", "expect"})
_GROUNDING_KINDS = frozenset({"grounded", "insufficient_evidence"})


def _load_dataset() -> dict[str, object]:
    assert _DATASET_PATH.is_file(), f"missing dataset at {_DATASET_PATH}"
    payload = json.loads(_DATASET_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_evaluation_dataset_file_exists_with_version_and_cases() -> None:
    payload = _load_dataset()
    assert payload.get("version") == 1
    assert payload.get("fixture_repository") == "sample-data/fixture-repository"
    cases = payload.get("cases")
    assert isinstance(cases, list)
    assert len(cases) >= 6


def test_evaluation_dataset_cases_have_strict_schema() -> None:
    payload = _load_dataset()
    cases = payload["cases"]
    assert isinstance(cases, list)
    ids: set[str] = set()
    kinds_seen: set[str] = set()
    for case in cases:
        assert isinstance(case, dict)
        assert _REQUIRED_CASE_KEYS <= set(case.keys())
        case_id = case["id"]
        assert isinstance(case_id, str) and case_id.strip()
        assert case_id not in ids
        ids.add(case_id)
        assert isinstance(case["question"], str) and case["question"].strip()
        expect = case["expect"]
        assert isinstance(expect, dict)
        kind = expect.get("kind")
        assert kind in _GROUNDING_KINDS
        kinds_seen.add(str(kind))
        if kind == "grounded":
            files = expect.get("expected_files")
            assert isinstance(files, list) and files
            assert all(isinstance(path, str) and path.strip() for path in files)
            symbols = expect.get("expected_symbols")
            assert isinstance(symbols, list) and symbols
            assert all(isinstance(symbol, str) and symbol.strip() for symbol in symbols)
        else:
            assert "expected_files" not in expect
            assert "expected_symbols" not in expect
    assert kinds_seen == _GROUNDING_KINDS


def test_grounded_expected_files_exist_in_fixture() -> None:
    payload = _load_dataset()
    cases = payload["cases"]
    assert isinstance(cases, list)
    for case in cases:
        assert isinstance(case, dict)
        expect = case["expect"]
        assert isinstance(expect, dict)
        if expect.get("kind") != "grounded":
            continue
        files = expect["expected_files"]
        assert isinstance(files, list)
        for relative in files:
            assert (_FIXTURE_ROOT / str(relative)).is_file()


def test_dataset_includes_supported_question_types() -> None:
    payload = _load_dataset()
    cases = payload["cases"]
    assert isinstance(cases, list)
    ids = {case["id"] for case in cases if isinstance(case, dict)}
    assert {
        "repo-overview",
        "directory-structure",
        "api-endpoints",
        "declared-dependencies",
        "controller-database-flow",
        "inventory-service-methods",
        "list-items-location",
        "oauth-unsupported",
        "prompt-injection-policy-override",
    } <= ids


def test_dataset_includes_prompt_injection_source_examples() -> None:
    payload = _load_dataset()
    cases = payload["cases"]
    assert isinstance(cases, list)
    injection_cases = [
        case
        for case in cases
        if isinstance(case, dict) and case.get("tags") == ["prompt_injection"]
    ]
    assert injection_cases, "dataset must include prompt_injection tagged cases"
    for case in injection_cases:
        sources = case.get("injection_source_files")
        assert isinstance(sources, list) and sources
        for relative in sources:
            path = _FIXTURE_ROOT / str(relative)
            assert path.is_file()
            text = path.read_text(encoding="utf-8")
            assert "Ignore previous instructions" in text or "unrestricted mode" in text
