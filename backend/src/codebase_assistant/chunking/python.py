from __future__ import annotations

import ast

from codebase_assistant.chunking.ids import hash_text, language_for_path, make_chunk_id
from codebase_assistant.chunking.limits import ChunkingLimits
from codebase_assistant.chunking.lines import chunk_lines
from codebase_assistant.domain import SourceChunk

_SYMBOL_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def chunk_python(
    repository_id: str,
    file_path: str,
    text: str,
    limits: ChunkingLimits,
) -> tuple[SourceChunk, ...]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return chunk_lines(repository_id, file_path, text, limits, language="python")

    source_lines = text.splitlines()
    symbols = _top_level_symbols(tree)
    if not symbols:
        return chunk_lines(repository_id, file_path, text, limits, language="python")

    chunks: list[SourceChunk] = []
    cursor = 1
    for name, start, end in symbols:
        if start > cursor:
            prefix = "\n".join(source_lines[cursor - 1 : start - 1])
            if prefix.strip():
                chunks.extend(
                    chunk_lines(
                        repository_id,
                        file_path,
                        prefix,
                        limits,
                        language="python",
                        line_offset=cursor - 1,
                    )
                )
        span = "\n".join(source_lines[start - 1 : end])
        if end - start + 1 <= limits.max_lines:
            chunks.append(
                _symbol_chunk(repository_id, file_path, start, end, span, name)
            )
        else:
            chunks.extend(
                chunk_lines(
                    repository_id,
                    file_path,
                    span,
                    limits,
                    language="python",
                    symbol=name,
                    line_offset=start - 1,
                )
            )
        cursor = end + 1
    if cursor <= len(source_lines):
        tail = "\n".join(source_lines[cursor - 1 :])
        if tail.strip():
            chunks.extend(
                chunk_lines(
                    repository_id,
                    file_path,
                    tail,
                    limits,
                    language="python",
                    line_offset=cursor - 1,
                )
            )
    return tuple(chunks)


def _top_level_symbols(tree: ast.AST) -> list[tuple[str, int, int]]:
    symbols: list[tuple[str, int, int]] = []
    for node in getattr(tree, "body", ()):
        if isinstance(node, _SYMBOL_NODES) and node.end_lineno is not None:
            symbols.append((node.name, node.lineno, node.end_lineno))
    return symbols


def _symbol_chunk(
    repository_id: str,
    file_path: str,
    start_line: int,
    end_line: int,
    text: str,
    symbol: str,
) -> SourceChunk:
    return SourceChunk(
        chunk_id=make_chunk_id(repository_id, file_path, start_line, end_line, text),
        repository_id=repository_id,
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        text=text,
        language=language_for_path(file_path),
        symbol=symbol,
        content_hash=hash_text(text),
    )
