"""Python AST chunking keeps small symbols intact and falls back safely."""

from codebase_assistant.chunking import ChunkingLimits, chunk_source_file
from codebase_assistant.domain import SourceFile

_TWO_FUNCTIONS = """\
def alpha():
    return 1

def beta():
    return 2
"""

_OVERSIZED = """\
def bulky():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    return a
"""


def test_small_python_functions_stay_intact() -> None:
    source = SourceFile(path="src/app.py", content=_TWO_FUNCTIONS)
    chunks = chunk_source_file(
        "repo-1",
        source,
        ChunkingLimits(max_lines=40, overlap_lines=0),
    )
    symbols = [chunk.symbol for chunk in chunks]
    assert symbols == ["alpha", "beta"]
    assert chunks[0].text.startswith("def alpha")
    assert chunks[1].text.startswith("def beta")
    assert chunks[0].end_line >= chunks[0].start_line
    assert "return 1" in chunks[0].text
    assert "return 2" in chunks[1].text


def test_oversized_python_symbol_is_subdivided() -> None:
    source = SourceFile(path="src/big.py", content=_OVERSIZED)
    chunks = chunk_source_file(
        "repo-1",
        source,
        ChunkingLimits(max_lines=3, overlap_lines=0),
    )
    assert len(chunks) > 1
    assert all(chunk.end_line - chunk.start_line + 1 <= 3 for chunk in chunks)
    covered: set[int] = set()
    for chunk in chunks:
        covered.update(range(chunk.start_line, chunk.end_line + 1))
    assert covered == set(range(1, len(_OVERSIZED.splitlines()) + 1))


def test_invalid_python_falls_back_to_line_chunks() -> None:
    source = SourceFile(path="src/broken.py", content="def nope(\n")
    chunks = chunk_source_file(
        "repo-1",
        source,
        ChunkingLimits(max_lines=8, overlap_lines=0),
    )
    assert len(chunks) == 1
    assert chunks[0].symbol is None
    assert "def nope(" in chunks[0].text
