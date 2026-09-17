from pathlib import Path

import pytest

from codebase_assistant.application.contracts import (
    AskQuestionRequest,
    AskQuestionResult,
    IngestArchiveRequest,
    IngestArchiveResult,
    InvalidQuestionError,
)
from codebase_assistant.domain import (
    Citation,
    DomainError,
    Repository,
    grounded_answer,
)


def test_ask_question_rejects_empty_question() -> None:
    with pytest.raises(InvalidQuestionError):
        AskQuestionRequest(repository_id="repo-1", question="   ")


def test_ask_question_accepts_non_empty_question() -> None:
    request = AskQuestionRequest(repository_id="repo-1", question="Where is main?")
    assert request.question == "Where is main?"


def test_ingest_archive_requires_filename() -> None:
    with pytest.raises(DomainError):
        IngestArchiveRequest(filename="  ", content=b"unused")


def test_ingest_and_ask_results_carry_domain_types() -> None:
    repository = Repository(repository_id="repo-1")
    ingest = IngestArchiveResult(
        repository=repository,
        indexed_file_count=2,
        ignored_file_count=1,
    )
    citation = Citation(file_path="app.py", start_line=1, end_line=1)
    answer = grounded_answer("entry is app.py", (citation,), (citation,))
    result = AskQuestionResult(answer=answer)
    assert ingest.indexed_file_count == 2
    assert result.answer.citations == (citation,)


def test_domain_and_application_do_not_import_frameworks() -> None:
    root = Path(__file__).resolve().parents[3] / "src" / "codebase_assistant"
    forbidden = ("fastapi", "sqlalchemy", "openai", "ollama")
    for package in ("domain", "application"):
        for path in (root / package).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for name in forbidden:
                assert f"import {name}" not in text
                assert f"from {name}" not in text
