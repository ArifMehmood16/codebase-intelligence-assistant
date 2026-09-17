"""Strict parsing of structured completion JSON at the use-case boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass

from codebase_assistant.domain import Citation

_REQUIRED_KEYS = frozenset({"text", "citations", "insufficient_evidence"})


@dataclass(frozen=True, slots=True)
class ParsedCompletion:
    text: str
    citations: tuple[Citation, ...]
    insufficient_evidence: bool


def parse_completion(raw: str) -> ParsedCompletion | None:
    """Return a typed completion, or None when the schema is invalid."""
    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if set(payload.keys()) != _REQUIRED_KEYS:
        return None

    text = payload["text"]
    citations_raw = payload["citations"]
    insufficient = payload["insufficient_evidence"]
    if not isinstance(text, str):
        return None
    if not isinstance(citations_raw, list):
        return None
    if not isinstance(insufficient, bool):
        return None

    citations: list[Citation] = []
    for item in citations_raw:
        citation = _parse_citation(item)
        if citation is None:
            return None
        citations.append(citation)

    cleaned = text.strip()
    if insufficient and citations:
        return None
    if not insufficient and not cleaned:
        return None

    return ParsedCompletion(
        text=cleaned,
        citations=tuple(citations),
        insufficient_evidence=insufficient,
    )


def _parse_citation(item: object) -> Citation | None:
    if not isinstance(item, dict):
        return None
    if set(item.keys()) != {"file_path", "start_line", "end_line"}:
        return None
    file_path = item["file_path"]
    start_line = item["start_line"]
    end_line = item["end_line"]
    if not isinstance(file_path, str) or not file_path.strip():
        return None
    if type(start_line) is not int or type(end_line) is not int:
        return None
    if start_line < 1 or end_line < start_line:
        return None
    return Citation(
        file_path=file_path.strip(),
        start_line=start_line,
        end_line=end_line,
    )
