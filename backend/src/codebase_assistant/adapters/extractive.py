"""Completer that quotes retrieved excerpts instead of calling a hosted LLM."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

_SOURCE_BLOCK = re.compile(
    r"### Source \d+\nfile_path: (?P<path>[^\n]+)\nstart_line: (?P<start>\d+)\n"
    r"end_line: (?P<end>\d+)\nexcerpt:\n(?P<excerpt>.*?)(?=\n### |\Z)",
    re.DOTALL,
)
_TERMS = re.compile(r"[a-z0-9_]+")
_STOPWORDS = frozenset(
    {
        "about",
        "after",
        "assistant",
        "codebase",
        "default",
        "defined",
        "does",
        "from",
        "handled",
        "implement",
        "implemented",
        "instruct",
        "override",
        "project",
        "prompt",
        "repository",
        "require",
        "required",
        "service",
        "system",
        "that",
        "this",
        "what",
        "where",
        "which",
        "work",
        "works",
    }
)
_WEAK_ALONE = frozenset(
    {
        "architecture",
        "assistant",
        "document",
        "fixture",
        "sample",
        "service",
        "system",
    }
)


@dataclass(frozen=True, slots=True)
class _Source:
    file_path: str
    start_line: int
    end_line: int
    excerpt: str


class ExtractiveCompleter:
    def complete(self, prompt: str) -> str:
        question = prompt.split("### Question", 1)[-1].strip()
        sources = tuple(
            _Source(
                file_path=match.group("path").strip(),
                start_line=int(match.group("start")),
                end_line=int(match.group("end")),
                excerpt=match.group("excerpt").strip(),
            )
            for match in _SOURCE_BLOCK.finditer(prompt.split("### Question", 1)[0])
        )
        chosen = _best_source(question, sources)
        if chosen is None:
            return json.dumps(
                {
                    "text": (
                        "The indexed repository does not contain enough "
                        "evidence to answer that question."
                    ),
                    "citations": [],
                    "insufficient_evidence": True,
                }
            )
        snippet = chosen.excerpt.splitlines()[0] if chosen.excerpt else chosen.file_path
        return json.dumps(
            {
                "text": (
                    f"In `{chosen.file_path}` lines "
                    f"{chosen.start_line}-{chosen.end_line}: {snippet}"
                ),
                "citations": [
                    {
                        "file_path": chosen.file_path,
                        "start_line": chosen.start_line,
                        "end_line": chosen.end_line,
                    }
                ],
                "insufficient_evidence": False,
            }
        )


def _content_terms(question: str) -> tuple[str, ...]:
    return tuple(
        token
        for token in _TERMS.findall(question.lower())
        if len(token) > 4 and token not in _STOPWORDS
    )


def _best_source(question: str, sources: tuple[_Source, ...]) -> _Source | None:
    terms = _content_terms(question)
    if not terms:
        return sources[0] if sources else None
    ranked: list[tuple[int, int, int, int, _Source]] = []
    route_question = bool(re.search(r"\bendpoints?\b", question.lower()))
    for index, source in enumerate(sources):
        haystack = f"{source.file_path}\n{source.excerpt}".lower()
        matched = tuple(term for term in terms if _whole_word(term, haystack))
        route_bonus = (
            2
            if route_question
            and re.search(r"\b(get|post|put|patch|delete)\s+/", haystack)
            else 0
        )
        if not matched and not route_bonus:
            continue
        definition_bonus = sum(
            1
            for term in matched
            if re.search(rf"\b(?:def|class)\s+{re.escape(term)}\b", haystack)
        )
        if (
            not definition_bonus
            and not route_bonus
            and matched
            and set(matched) <= _WEAK_ALONE
        ):
            continue
        ranked.append((definition_bonus + route_bonus, len(matched), -index, 0, source))
    if not ranked:
        return None
    ranked.sort(reverse=True)
    return ranked[0][4]


def _whole_word(term: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(term)}\b", text) is not None
