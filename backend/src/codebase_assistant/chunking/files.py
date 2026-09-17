from codebase_assistant.chunking.ids import language_for_path
from codebase_assistant.chunking.limits import ChunkingLimits
from codebase_assistant.chunking.lines import chunk_lines
from codebase_assistant.chunking.python import chunk_python
from codebase_assistant.domain import SourceChunk, SourceFile


def chunk_source_file(
    repository_id: str,
    source: SourceFile,
    limits: ChunkingLimits,
) -> tuple[SourceChunk, ...]:
    if not source.content.strip():
        return ()
    language = language_for_path(source.path)
    if language == "python":
        return chunk_python(repository_id, source.path, source.content, limits)
    return chunk_lines(
        repository_id,
        source.path,
        source.content,
        limits,
        language=language,
    )
