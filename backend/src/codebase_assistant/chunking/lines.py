from collections.abc import Iterator

from codebase_assistant.chunking.ids import hash_text, language_for_path, make_chunk_id
from codebase_assistant.chunking.limits import ChunkingLimits
from codebase_assistant.domain import SourceChunk


def line_windows(
    line_count: int, max_lines: int, overlap_lines: int
) -> Iterator[tuple[int, int]]:
    if line_count < 1:
        return
    step = max(max_lines - overlap_lines, 1)
    start = 1
    while start <= line_count:
        end = min(start + max_lines - 1, line_count)
        yield start, end
        if end == line_count:
            return
        start += step


def chunk_lines(
    repository_id: str,
    file_path: str,
    text: str,
    limits: ChunkingLimits,
    *,
    language: str | None = None,
    symbol: str | None = None,
    line_offset: int = 0,
) -> tuple[SourceChunk, ...]:
    source_lines = text.splitlines()
    if not source_lines:
        return ()
    resolved_language = language or language_for_path(file_path)
    chunks: list[SourceChunk] = []
    for start, end in line_windows(
        len(source_lines), limits.max_lines, limits.overlap_lines
    ):
        excerpt = "\n".join(source_lines[start - 1 : end])
        start_line = start + line_offset
        end_line = end + line_offset
        chunks.append(
            SourceChunk(
                chunk_id=make_chunk_id(
                    repository_id, file_path, start_line, end_line, excerpt
                ),
                repository_id=repository_id,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                text=excerpt,
                language=resolved_language,
                symbol=symbol,
                content_hash=hash_text(excerpt),
            )
        )
    return tuple(chunks)
