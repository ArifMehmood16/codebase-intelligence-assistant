import json

from codebase_assistant.adapters.extractive import ExtractiveCompleter

_PROMPT = """You are a codebase Q&A assistant.

### Source 1
file_path: README.md
start_line: 1
end_line: 8
excerpt:
Handlers live in src/api/handlers.py (`list_items`, `create_item`).

### Source 2
file_path: src/api/handlers.py
start_line: 9
end_line: 12
excerpt:
def list_items(service: InventoryService, *, limit: int = 20) -> list:
    return service.list_items(limit=limit)

### Question
{question}
"""


def _parse(raw: str) -> dict[str, object]:
    payload = json.loads(raw)
    assert isinstance(payload, dict)
    return payload


def test_extractive_cites_defining_file_not_the_first_retrieved_mention() -> None:
    result = _parse(
        ExtractiveCompleter().complete(
            _PROMPT.format(question="Where is list_items defined?")
        )
    )
    assert result["insufficient_evidence"] is False
    citations = result["citations"]
    assert isinstance(citations, list) and citations
    assert citations[0]["file_path"] == "src/api/handlers.py"


def test_extractive_returns_insufficient_evidence_for_absent_features() -> None:
    result = _parse(
        ExtractiveCompleter().complete(
            _PROMPT.format(question="How does OAuth login work in this service?")
        )
    )
    assert result["insufficient_evidence"] is True
    assert result["citations"] == []
