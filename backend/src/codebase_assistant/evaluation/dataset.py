"""Load the Phase 9 evaluation dataset from disk."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ExpectKind = Literal["grounded", "insufficient_evidence"]

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_DATASET = _REPO_ROOT / "sample-data" / "evaluation" / "dataset.json"


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    case_id: str
    question: str
    kind: ExpectKind
    expected_files: tuple[str, ...] = ()
    expected_symbols: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    injection_source_files: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EvaluationDataset:
    version: int
    fixture_repository: str
    cases: tuple[EvaluationCase, ...]


def default_dataset_path() -> Path:
    return _DEFAULT_DATASET


def load_evaluation_dataset(path: Path | None = None) -> EvaluationDataset:
    dataset_path = path or _DEFAULT_DATASET
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evaluation dataset must be a JSON object")
    version = payload.get("version")
    fixture = payload.get("fixture_repository")
    raw_cases = payload.get("cases")
    if not isinstance(version, int):
        raise ValueError("evaluation dataset version must be an int")
    if not isinstance(fixture, str) or not fixture.strip():
        raise ValueError("evaluation dataset fixture_repository is required")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("evaluation dataset cases must be a non-empty list")
    cases = tuple(_parse_case(item) for item in raw_cases)
    return EvaluationDataset(
        version=version,
        fixture_repository=fixture.strip(),
        cases=cases,
    )


def _parse_case(item: object) -> EvaluationCase:
    if not isinstance(item, dict):
        raise ValueError("evaluation case must be an object")
    case_id = item.get("id")
    question = item.get("question")
    expect = item.get("expect")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("evaluation case id is required")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("evaluation case question is required")
    if not isinstance(expect, dict):
        raise ValueError("evaluation case expect is required")
    kind = expect.get("kind")
    if kind not in ("grounded", "insufficient_evidence"):
        raise ValueError(f"unsupported expect.kind: {kind!r}")
    expected_files = _string_tuple(expect.get("expected_files"), "expected_files")
    expected_symbols = _string_tuple(expect.get("expected_symbols"), "expected_symbols")
    if kind == "grounded" and not expected_files:
        raise ValueError(f"grounded case {case_id!r} requires expected_files")
    tags = _string_tuple(item.get("tags"), "tags")
    injection = _string_tuple(
        item.get("injection_source_files"), "injection_source_files"
    )
    return EvaluationCase(
        case_id=case_id.strip(),
        question=question.strip(),
        kind=kind,
        expected_files=expected_files,
        expected_symbols=expected_symbols,
        tags=tags,
        injection_source_files=injection,
    )


def _string_tuple(value: object, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list of strings")
    items: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"{field} entries must be non-empty strings")
        items.append(entry.strip())
    return tuple(items)
