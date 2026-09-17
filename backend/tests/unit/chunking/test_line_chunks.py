"""Line-based chunks keep exact line ranges and do not drop source."""

from codebase_assistant.chunking import ChunkingLimits, chunk_source_file
from codebase_assistant.domain import SourceFile


def test_line_chunks_cover_every_source_line_and_match_excerpts() -> None:
    lines = [f"line-{index}" for index in range(1, 11)]
    source = SourceFile(path="notes.md", content="\n".join(lines))

    chunks = chunk_source_file(
        "repo-1",
        source,
        ChunkingLimits(max_lines=4, overlap_lines=1),
    )

    covered: set[int] = set()
    source_lines = source.content.splitlines()
    for chunk in chunks:
        covered.update(range(chunk.start_line, chunk.end_line + 1))
        assert chunk.text == "\n".join(
            source_lines[chunk.start_line - 1 : chunk.end_line]
        )
        assert chunk.repository_id == "repo-1"
        assert chunk.file_path == "notes.md"
        assert chunk.language == "markdown"

    assert covered == set(range(1, 11))


def test_empty_file_creates_no_chunks() -> None:
    chunks = chunk_source_file(
        "repo-1",
        SourceFile(path="empty.txt", content="  \n"),
        ChunkingLimits(max_lines=8, overlap_lines=2),
    )
    assert chunks == ()


def test_repeated_chunking_is_deterministic() -> None:
    source = SourceFile(path="readme.md", content="a\nb\nc\nd\ne\n")
    limits = ChunkingLimits(max_lines=2, overlap_lines=0)
    first = chunk_source_file("repo-1", source, limits)
    second = chunk_source_file("repo-1", source, limits)
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert [chunk.content_hash for chunk in first] == [
        chunk.content_hash for chunk in second
    ]
