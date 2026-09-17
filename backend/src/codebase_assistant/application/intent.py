"""Classify ask-path intent from question text without a model call."""

from __future__ import annotations

import re
from typing import Literal

QuestionIntent = Literal[
    "overview",
    "structure",
    "dependencies",
    "endpoints",
    "architecture_flow",
    "code_unit_details",
    "locate",
    "explain",
]

_WHITESPACE = re.compile(r"\s+")

# Specific product intents before locate/explain. First match wins.
_RULES: tuple[tuple[QuestionIntent, re.Pattern[str]], ...] = (
    (
        "architecture_flow",
        re.compile(
            r"\b(end[- ]to[- ]end (?:logic |request )?(?:path|flow)"
            r"|controller(?:s)?\s+(?:to|through)\s+(?:the\s+)?(?:database|service)"
            r"|request flow from controller(?:s)?"
            r"|controller(?:s)?.{0,30}(?:service|repository|dao).{0,30}database)\b"
        ),
    ),
    (
        "code_unit_details",
        re.compile(
            r"^(?=.*\b(?:methods?|functions?|callables?)\b)"
            r"(?=.*\b(?:what does|purpose|how many|table|list|each)\b)"
        ),
    ),
    (
        "endpoints",
        re.compile(r"\b(api\s+endpoints?|endpoints?|routes?)\b"),
    ),
    (
        "dependencies",
        re.compile(
            r"\b(dependencies|dependency|package\.json|pyproject\.toml|"
            r"requirements\.txt|libraries)\b"
        ),
    ),
    (
        "structure",
        re.compile(
            r"\b(directory structure|folder structure|file tree|hierarchy|"
            r"directory layout|folder layout|project structure|"
            r"structure of (?:the |this )?(?:repo|project|codebase|repository)|"
            r"(?:repo|project|codebase|repository) structure)\b"
        ),
    ),
    (
        "overview",
        re.compile(
            r"(what does this (?:repo|project|codebase|repository)\s+do"
            r"|purpose of this (?:repo|project|codebase|repository)"
            r"|summar[iy]se this (?:repo|project|codebase|repository)"
            r"|what is this (?:repo|project|codebase|repository)\b"
            r"|overview of this (?:repo|project|codebase|repository))"
        ),
    ),
    (
        "locate",
        re.compile(r"\b(where is|where are|which file|which files|where does)\b"),
    ),
)


def classify_question_intent(question: str) -> QuestionIntent:
    text = _WHITESPACE.sub(" ", question.strip().lower())
    if not text:
        return "explain"
    for intent, pattern in _RULES:
        if pattern.search(text):
            return intent
    return "explain"
