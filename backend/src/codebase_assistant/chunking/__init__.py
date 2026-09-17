"""Bounded, deterministic chunking of accepted source files."""

from codebase_assistant.chunking.files import chunk_source_file
from codebase_assistant.chunking.limits import ChunkingLimits

__all__ = ["ChunkingLimits", "chunk_source_file"]
