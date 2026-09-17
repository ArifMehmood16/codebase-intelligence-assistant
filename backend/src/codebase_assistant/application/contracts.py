from dataclasses import dataclass

from codebase_assistant.application.repository_card import RepositoryCard
from codebase_assistant.domain import GroundedAnswer, InvalidQuestionError, Repository
from codebase_assistant.domain.models import require_non_empty

__all__ = [
    "AskQuestionRequest",
    "AskQuestionResult",
    "CitedExcerpt",
    "IngestArchiveRequest",
    "IngestArchiveResult",
    "InvalidQuestionError",
    "RepositoryCard",
]


@dataclass(frozen=True, slots=True)
class IngestArchiveRequest:
    filename: str
    content: bytes

    def __post_init__(self) -> None:
        require_non_empty(self.filename, "filename")


@dataclass(frozen=True, slots=True)
class IngestArchiveResult:
    repository: Repository
    indexed_file_count: int
    ignored_file_count: int
    ignored_reason_counts: tuple[tuple[str, int], ...] = ()
    indexed_paths: tuple[str, ...] = ()
    status: str = "completed"
    failure_code: str | None = None
    source_filename: str | None = None
    card: RepositoryCard | None = None


@dataclass(frozen=True, slots=True)
class AskQuestionRequest:
    repository_id: str
    question: str

    def __post_init__(self) -> None:
        require_non_empty(self.repository_id, "repository_id")
        if not self.question.strip():
            raise InvalidQuestionError("question is required")


@dataclass(frozen=True, slots=True)
class CitedExcerpt:
    file_path: str
    start_line: int
    end_line: int
    excerpt: str


@dataclass(frozen=True, slots=True)
class AskQuestionResult:
    answer: GroundedAnswer
    excerpts: tuple[CitedExcerpt, ...] = ()
