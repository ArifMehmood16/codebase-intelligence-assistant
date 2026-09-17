import pytest

from codebase_assistant.domain import (
    Citation,
    DomainError,
    GroundedAnswer,
    UnverifiedCitationError,
    grounded_answer,
    insufficient_evidence_answer,
)


def _citation() -> Citation:
    return Citation(file_path="app.py", start_line=1, end_line=2)


def test_grounded_answer_rejects_citation_not_in_retrieved_set() -> None:
    retrieved = (_citation(),)
    invented = Citation(file_path="secret.py", start_line=1, end_line=1)
    with pytest.raises(UnverifiedCitationError):
        grounded_answer("uses secret", (invented,), retrieved)


def test_grounded_answer_keeps_verified_citations() -> None:
    citation = _citation()
    answer = grounded_answer("the handler runs", (citation,), (citation,))
    assert answer.insufficient_evidence is False
    assert answer.citations == (citation,)


def test_insufficient_evidence_answer_has_no_citations() -> None:
    answer = insufficient_evidence_answer("The indexed code does not support this.")
    assert answer.insufficient_evidence is True
    assert answer.citations == ()


def test_grounded_answer_requires_at_least_one_citation() -> None:
    with pytest.raises(DomainError):
        GroundedAnswer(text="it works", citations=(), insufficient_evidence=False)


def test_insufficient_evidence_cannot_carry_citations() -> None:
    with pytest.raises(DomainError):
        GroundedAnswer(
            text="not enough evidence",
            citations=(_citation(),),
            insufficient_evidence=True,
        )
