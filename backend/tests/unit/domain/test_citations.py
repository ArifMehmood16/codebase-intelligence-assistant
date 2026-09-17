"""Citation line ranges must be valid 1-based inclusive spans."""

import pytest

from codebase_assistant.domain import Citation, InvalidLineRangeError, SourceChunk


def test_citation_rejects_start_line_below_one() -> None:
    with pytest.raises(InvalidLineRangeError):
        Citation(file_path="app.py", start_line=0, end_line=1)


def test_citation_rejects_end_line_before_start_line() -> None:
    with pytest.raises(InvalidLineRangeError):
        Citation(file_path="app.py", start_line=4, end_line=2)


def test_citation_accepts_single_line() -> None:
    citation = Citation(file_path="app.py", start_line=3, end_line=3)
    assert citation.start_line == 3
    assert citation.end_line == 3


def test_chunk_rejects_invalid_line_range() -> None:
    with pytest.raises(InvalidLineRangeError):
        SourceChunk(
            chunk_id="c1",
            repository_id="r1",
            file_path="app.py",
            start_line=0,
            end_line=2,
            text="x",
        )


def test_chunk_as_citation_matches_span() -> None:
    chunk = SourceChunk(
        chunk_id="c1",
        repository_id="r1",
        file_path="app.py",
        start_line=2,
        end_line=4,
        text="def f():\n    return 1\n",
    )
    assert chunk.as_citation() == Citation(file_path="app.py", start_line=2, end_line=4)
