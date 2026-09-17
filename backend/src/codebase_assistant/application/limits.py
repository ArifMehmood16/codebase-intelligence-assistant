"""Configurable budgets for questions, retrieved context and excerpts."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnswerLimits:
    max_question_chars: int = 2_000
    max_context_chars: int = 12_000
    max_excerpt_chars: int = 2_000

    def __post_init__(self) -> None:
        if self.max_question_chars < 1:
            raise ValueError("max_question_chars must be at least 1")
        if self.max_context_chars < 1:
            raise ValueError("max_context_chars must be at least 1")
        if self.max_excerpt_chars < 1:
            raise ValueError("max_excerpt_chars must be at least 1")
