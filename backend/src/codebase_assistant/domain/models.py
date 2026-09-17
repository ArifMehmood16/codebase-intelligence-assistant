from collections.abc import Collection, Sequence
from dataclasses import dataclass

from codebase_assistant.domain.errors import (
    DomainError,
    InvalidLineRangeError,
    UnverifiedCitationError,
)


def require_line_range(start_line: int, end_line: int) -> None:
    if start_line < 1 or end_line < start_line:
        raise InvalidLineRangeError(
            f"line range {start_line}-{end_line} is not a valid 1-based inclusive span"
        )


def require_non_empty(value: str, field: str) -> None:
    if not value.strip():
        raise DomainError(f"{field} is required")


@dataclass(frozen=True, slots=True)
class Repository:
    repository_id: str

    def __post_init__(self) -> None:
        require_non_empty(self.repository_id, "repository_id")


@dataclass(frozen=True, slots=True)
class SourceFile:
    path: str
    content: str

    def __post_init__(self) -> None:
        require_non_empty(self.path, "path")


@dataclass(frozen=True, slots=True)
class Citation:
    file_path: str
    start_line: int
    end_line: int

    def __post_init__(self) -> None:
        require_non_empty(self.file_path, "file_path")
        require_line_range(self.start_line, self.end_line)


@dataclass(frozen=True, slots=True)
class SourceChunk:
    chunk_id: str
    repository_id: str
    file_path: str
    start_line: int
    end_line: int
    text: str
    language: str = "unknown"
    symbol: str | None = None
    content_hash: str = ""

    def __post_init__(self) -> None:
        require_non_empty(self.chunk_id, "chunk_id")
        require_non_empty(self.repository_id, "repository_id")
        require_non_empty(self.file_path, "file_path")
        require_line_range(self.start_line, self.end_line)

    def as_citation(self) -> Citation:
        return Citation(
            file_path=self.file_path,
            start_line=self.start_line,
            end_line=self.end_line,
        )


@dataclass(frozen=True, slots=True)
class GroundedAnswer:
    text: str
    citations: tuple[Citation, ...]
    insufficient_evidence: bool

    def __post_init__(self) -> None:
        require_non_empty(self.text, "text")
        if self.insufficient_evidence and self.citations:
            raise DomainError("insufficient-evidence answers cannot include citations")
        if not self.insufficient_evidence and not self.citations:
            raise DomainError("grounded answers must include at least one citation")


def grounded_answer(
    text: str,
    citations: Sequence[Citation],
    retrieved: Collection[Citation],
) -> GroundedAnswer:
    retrieved_set = frozenset(retrieved)
    for citation in citations:
        if citation not in retrieved_set:
            raise UnverifiedCitationError(
                "citation "
                f"{citation.file_path}:{citation.start_line}-{citation.end_line} "
                "was not retrieved"
            )
    return GroundedAnswer(
        text=text,
        citations=tuple(citations),
        insufficient_evidence=False,
    )


def insufficient_evidence_answer(text: str) -> GroundedAnswer:
    return GroundedAnswer(text=text, citations=(), insufficient_evidence=True)
