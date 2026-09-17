"""Retrieve repository-scoped evidence and validate model citations."""

from __future__ import annotations

import re
from collections.abc import Sequence

from codebase_assistant.application.completion import parse_completion
from codebase_assistant.application.contracts import (
    AskQuestionRequest,
    AskQuestionResult,
    CitedExcerpt,
)
from codebase_assistant.application.intent import (
    QuestionIntent,
    classify_question_intent,
)
from codebase_assistant.application.limits import AnswerLimits
from codebase_assistant.application.ports import (
    CompleteAnswer,
    EmbedTexts,
    SearchChunks,
)
from codebase_assistant.application.prompt import (
    build_answer_prompt,
    select_context_chunks,
)
from codebase_assistant.application.repository_card import (
    RepositoryCard,
    format_outline_tree,
)
from codebase_assistant.domain import (
    Citation,
    InvalidQuestionError,
    SourceChunk,
    grounded_answer,
    insufficient_evidence_answer,
)

_INSUFFICIENT = (
    "The indexed repository does not contain enough evidence to answer that question."
)

_PIN_INTENTS = frozenset(
    {
        "overview",
        "structure",
        "dependencies",
        "endpoints",
        "architecture_flow",
        "code_unit_details",
    }
)
_MANIFEST_BASENAMES = frozenset({"package.json", "pyproject.toml", "requirements.txt"})
_ENDPOINT_MARKERS = ("handler", "route", "router", "controller", "endpoint", "/api/")
_MAX_STRUCTURE_FILES = 15
_MAX_ARCHITECTURE_FILES = 32
_ARCHITECTURE_SOURCE_SUFFIXES = (
    ".java",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".cs",
    ".go",
    ".rb",
    ".php",
    ".kt",
)


def ask_question(
    request: AskQuestionRequest,
    *,
    embed: EmbedTexts,
    search: SearchChunks,
    complete: CompleteAnswer,
    retrieval_limit: int = 5,
    answer_limits: AnswerLimits | None = None,
) -> AskQuestionResult:
    limits = answer_limits or AnswerLimits()
    question = request.question.strip()
    if len(question) > limits.max_question_chars:
        raise InvalidQuestionError("question exceeds configured length")

    intent = classify_question_intent(question)
    card, pinned = _pinned_context(search, request.repository_id, intent, question)

    hits: list[SourceChunk] = []
    if intent in _PIN_INTENTS:
        if _lacks_required_evidence(intent, card) or not pinned:
            return _insufficient()
        hits.extend(pinned)
    else:
        query_vectors = embed.embed([question])
        if not query_vectors:
            return _insufficient()
        hits.extend(
            search.search(request.repository_id, query_vectors[0], retrieval_limit)
        )
        if intent == "locate":
            hits = _with_locate_symbol_hits(
                search, request.repository_id, question, tuple(hits)
            )
    if not hits:
        return _insufficient()

    selected = select_context_chunks(hits, limits)
    if not selected:
        return _insufficient()
    if intent == "structure" and card is not None:
        return _structure_answer(card, selected)
    if intent == "endpoints" and card is not None:
        return _endpoints_answer(card, selected)

    raw = complete.complete(
        build_answer_prompt(
            question,
            selected,
            limits=limits,
            card=card if intent in _PIN_INTENTS else None,
            intent=intent,
            evidence_complete=(
                _context_is_complete(pinned, selected, limits)
                if intent == "code_unit_details"
                else None
            ),
        )
    )
    parsed = parse_completion(raw)
    if parsed is None:
        return _insufficient()
    if parsed.insufficient_evidence:
        return AskQuestionResult(
            answer=insufficient_evidence_answer(parsed.text or _INSUFFICIENT)
        )
    if intent == "code_unit_details" and not _has_code_unit_detail_shape(parsed.text):
        return _insufficient()

    retrieved = [chunk.as_citation() for chunk in selected]
    retrieved_set = set(retrieved)
    valid = [citation for citation in parsed.citations if citation in retrieved_set]
    if not valid:
        return _insufficient()
    excerpts = tuple(_excerpt_for(citation, selected) for citation in valid)
    answer_text = parsed.text
    if intent == "architecture_flow":
        answer_text = _format_architecture_answer(parsed.text, pinned)
    return AskQuestionResult(
        answer=grounded_answer(answer_text, valid, retrieved),
        excerpts=excerpts,
    )


def _insufficient() -> AskQuestionResult:
    return AskQuestionResult(answer=insufficient_evidence_answer(_INSUFFICIENT))


def _structure_answer(
    card: RepositoryCard, selected: Sequence[SourceChunk]
) -> AskQuestionResult:
    source = _citation_chunk(selected, card)
    citation = source.as_citation()
    intro = (
        f"Bounded directory outline of {card.display_name}, derived from indexed files."
    )
    if card.outline_truncated:
        intro += " Deeper or additional paths are truncated."
    tree = format_outline_tree(card.outline_paths)
    parts = [intro, f"### Directory structure\n\n```tree\n{tree}\n```"]
    context = _readme_context(card.readme_excerpt)
    if context:
        parts.append(f"{context} [1]")
    else:
        parts.append(f"Cited indexed file: `{citation.file_path}`. [1]")
    return AskQuestionResult(
        answer=grounded_answer("\n\n".join(parts), (citation,), (citation,)),
        excerpts=(_excerpt_for(citation, selected),),
    )


def _endpoints_answer(
    card: RepositoryCard, selected: Sequence[SourceChunk]
) -> AskQuestionResult:
    if not card.endpoints:
        return _insufficient()
    cited_chunks: list[SourceChunk] = []
    seen: set[tuple[str, int, int]] = set()
    for item in card.endpoints:
        chunk = _chunk_overlapping(
            selected, item.file_path, item.start_line, item.end_line
        )
        if chunk is None:
            continue
        key = (chunk.file_path, chunk.start_line, chunk.end_line)
        if key in seen:
            continue
        seen.add(key)
        cited_chunks.append(chunk)
    if not cited_chunks:
        cited_chunks.append(selected[0])
    citations = tuple(chunk.as_citation() for chunk in cited_chunks)
    markers = " ".join(f"[{index}]" for index in range(1, len(citations) + 1))
    rows = [
        f"| `{_cell(item.method)} {_cell(item.path)}` | `{_cell(item.file_path)}` |"
        for item in card.endpoints
    ]
    text = (
        "HTTP routes extracted from indexed source comments or framework "
        f"declarations. Unsupported or runtime-only routes are omitted. {markers}\n\n"
        "### API endpoints\n\n"
        "| Route | Declaring file |\n"
        "| --- | --- |\n" + "\n".join(rows)
    )
    return AskQuestionResult(
        answer=grounded_answer(text, citations, citations),
        excerpts=tuple(_excerpt_for(citation, selected) for citation in citations),
    )


def _chunk_overlapping(
    selected: Sequence[SourceChunk],
    file_path: str,
    start_line: int,
    end_line: int,
) -> SourceChunk | None:
    for chunk in selected:
        if (
            chunk.file_path == file_path
            and chunk.start_line <= end_line
            and chunk.end_line >= start_line
        ):
            return chunk
    for chunk in selected:
        if chunk.file_path == file_path:
            return chunk
    return None


def _cell(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def _citation_chunk(
    selected: Sequence[SourceChunk], card: RepositoryCard
) -> SourceChunk:
    if card.readme_path:
        for chunk in selected:
            if chunk.file_path == card.readme_path:
                return chunk
    return selected[0]


def _readme_context(excerpt: str) -> str:
    pieces: list[str] = []
    for line in excerpt.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        if stripped:
            pieces.append(stripped)
        elif pieces:
            break
    summary = " ".join(pieces).strip()
    if not summary:
        return ""
    if len(summary) > 400:
        summary = summary[:400].rsplit(" ", 1)[0] + "…"
    return f"README context: {summary}"


def _excerpt_for(citation: Citation, hits: Sequence[SourceChunk]) -> CitedExcerpt:
    for chunk in hits:
        if chunk.as_citation() == citation:
            return CitedExcerpt(
                file_path=citation.file_path,
                start_line=citation.start_line,
                end_line=citation.end_line,
                excerpt=chunk.text,
            )
    return CitedExcerpt(
        file_path=citation.file_path,
        start_line=citation.start_line,
        end_line=citation.end_line,
        excerpt="",
    )


def _with_locate_symbol_hits(
    search: SearchChunks,
    repository_id: str,
    question: str,
    hits: tuple[SourceChunk, ...],
) -> list[SourceChunk]:
    """If vector search missed a long identifier, pin chunks that contain it."""
    ident = _locate_identifier(question)
    if not ident:
        return list(hits)
    pattern = re.compile(rf"\b{re.escape(ident)}\b", re.IGNORECASE)
    if any(pattern.search(chunk.text) for chunk in hits):
        return list(hits)
    chunks_for_paths = getattr(search, "chunks_for_paths", None)
    get_summary = getattr(search, "get_summary", None)
    if not callable(chunks_for_paths) or not callable(get_summary):
        return list(hits)
    summary = get_summary(repository_id)
    paths = tuple((summary.indexed_paths if summary is not None else ())[:40])
    extra = [
        chunk
        for chunk in chunks_for_paths(repository_id, paths)
        if pattern.search(chunk.text)
    ]
    ordered: list[SourceChunk] = []
    seen: set[tuple[str, int, int]] = set()
    for chunk in (*extra, *hits):
        key = (chunk.file_path, chunk.start_line, chunk.end_line)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(chunk)
    return ordered


def _locate_identifier(question: str) -> str:
    tokens = [
        token
        for token in re.findall(r"[a-z0-9_]+", question.lower())
        if len(token) >= 8
    ]
    return max(tokens, key=len) if tokens else ""


def _pinned_context(
    search: SearchChunks,
    repository_id: str,
    intent: QuestionIntent,
    question: str = "",
) -> tuple[RepositoryCard | None, tuple[SourceChunk, ...]]:
    if intent not in _PIN_INTENTS:
        return None, ()
    get_summary = getattr(search, "get_summary", None)
    chunks_for_paths = getattr(search, "chunks_for_paths", None)
    if not callable(get_summary) or not callable(chunks_for_paths):
        return None, ()
    summary = get_summary(repository_id)
    card = summary.card if summary is not None else None
    indexed_paths = summary.indexed_paths if summary is not None else ()
    paths = _pinned_paths(intent, card, indexed_paths, question)
    if not paths:
        return card, ()
    pinned = tuple(chunks_for_paths(repository_id, paths))
    if intent == "architecture_flow":
        pinned = _spread_architecture_chunks(pinned, paths)
    elif intent == "code_unit_details":
        pinned = tuple(
            sorted(
                pinned,
                key=lambda chunk: (
                    paths.index(chunk.file_path),
                    chunk.start_line,
                    chunk.end_line,
                ),
            )
        )
    return card, _prefer_overlapping(intent, card, pinned)


def _pinned_paths(
    intent: QuestionIntent,
    card: RepositoryCard | None,
    indexed_paths: Sequence[str] = (),
    question: str = "",
) -> tuple[str, ...]:
    if intent == "architecture_flow":
        return _architecture_paths(indexed_paths)
    if intent == "code_unit_details":
        return _code_unit_paths(indexed_paths, question)
    if card is None:
        return ()
    paths: list[str] = []
    if intent in {"overview", "structure"} and card.readme_path:
        paths.append(card.readme_path)
    if intent in {"overview", "dependencies"}:
        if card.declared_dependencies:
            paths.extend(item.file_path for item in card.declared_dependencies)
        else:
            paths.extend(_manifest_paths(card))
    if intent == "structure":
        for path in card.outline_paths:
            if path.endswith("/"):
                continue
            paths.append(path)
            if len(_unique(paths)) >= _MAX_STRUCTURE_FILES:
                break
    if intent == "endpoints":
        if card.endpoints:
            paths.extend(item.file_path for item in card.endpoints)
        else:
            paths.extend(_endpoint_paths(card))
    return _unique(paths)


def _lacks_required_evidence(
    intent: QuestionIntent, card: RepositoryCard | None
) -> bool:
    if intent == "architecture_flow":
        return False
    if intent == "code_unit_details":
        return False
    if card is None:
        return True
    if intent == "overview":
        return (
            not card.readme_path
            and not card.declared_dependencies
            and not _manifest_paths(card)
        )
    if intent == "structure":
        has_file = any(not path.endswith("/") for path in card.outline_paths)
        return not has_file and not card.readme_path
    if intent == "dependencies":
        return not card.declared_dependencies and not _manifest_paths(card)
    if intent == "endpoints":
        return not card.endpoints
    return False


def _manifest_paths(card: RepositoryCard) -> tuple[str, ...]:
    found: list[str] = []
    for path in card.outline_paths:
        name = path.rsplit("/", 1)[-1].lower()
        if name in _MANIFEST_BASENAMES:
            found.append(path)
    return tuple(found)


def _endpoint_paths(card: RepositoryCard) -> tuple[str, ...]:
    found: list[str] = []
    for path in card.outline_paths:
        lower = path.lower()
        if any(marker in lower for marker in _ENDPOINT_MARKERS):
            found.append(path)
    return tuple(found)


def _architecture_paths(indexed_paths: Sequence[str]) -> tuple[str, ...]:
    files = tuple(path for path in indexed_paths if path and not path.endswith("/"))
    controllers = tuple(path for path in files if _is_controller_path(path))
    if not controllers:
        return ()
    controller_parents = {path.rsplit("/", 1)[0] for path in controllers if "/" in path}
    services = tuple(path for path in files if _has_role(path, ("service", "usecase")))
    repositories = tuple(
        path
        for path in files
        if _has_role(path, ("repository", "repositories", "dao", "persistence"))
    )
    models = tuple(
        path
        for path in files
        if _has_role(path, ("entity", "entities", "model", "models", "domain"))
    )
    peers = tuple(
        path
        for path in files
        if path.lower().endswith(_ARCHITECTURE_SOURCE_SUFFIXES)
        and "/" in path
        and path.rsplit("/", 1)[0] in controller_parents
    )
    database = tuple(path for path in files if _is_database_path(path))
    ordered = _unique(
        (*controllers, *services, *repositories, *models, *peers, *database)
    )
    return ordered[:_MAX_ARCHITECTURE_FILES]


def _code_unit_paths(indexed_paths: Sequence[str], question: str) -> tuple[str, ...]:
    compact_question = _compact_identifier(question)
    matches: list[tuple[int, str]] = []
    for path in indexed_paths:
        if not path or path.endswith("/"):
            continue
        filename = path.rsplit("/", 1)[-1]
        stem = filename.rsplit(".", 1)[0]
        compact_stem = _compact_identifier(stem)
        if len(compact_stem) >= 4 and compact_stem in compact_question:
            matches.append((len(compact_stem), path))
    if not matches:
        return ()
    longest = max(length for length, _path in matches)
    return _unique(tuple(path for length, path in matches if length == longest))


def _compact_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _context_is_complete(
    pinned: Sequence[SourceChunk],
    selected: Sequence[SourceChunk],
    limits: AnswerLimits,
) -> bool:
    return (
        len(selected) == len(pinned)
        and all(len(chunk.text) <= limits.max_excerpt_chars for chunk in selected)
        and sum(len(chunk.text) for chunk in selected) <= limits.max_context_chars
    )


def _has_code_unit_detail_shape(text: str) -> bool:
    lines = text.splitlines()
    expected_header = (
        "method",
        "route / trigger",
        "purpose",
        "collaborators / entities",
    )
    for index, line in enumerate(lines[:-1]):
        if _markdown_table_cells(line) != expected_header:
            continue
        delimiter = _markdown_table_cells(lines[index + 1])
        if (
            delimiter is None
            or len(delimiter) != len(expected_header)
            or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in delimiter)
        ):
            continue
        summary = " ".join(lines[:index]).strip()
        count = re.search(
            r"\b(\d+)\b.{0,40}\b(?:methods?|functions?|callables?)\b",
            summary,
            re.IGNORECASE,
        )
        rows = 0
        for row_line in lines[index + 2 :]:
            row = _markdown_table_cells(row_line)
            if row is None:
                break
            if len(row) != len(expected_header) or not all(row):
                return False
            rows += 1
        return len(summary) >= 20 and count is not None and int(count.group(1)) == rows
    return False


def _markdown_table_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return tuple(cell.strip().casefold() for cell in stripped[1:-1].split("|"))


def _is_controller_path(path: str) -> bool:
    lower = path.lower()
    name = lower.rsplit("/", 1)[-1]
    return lower.endswith(_ARCHITECTURE_SOURCE_SUFFIXES) and (
        "controller" in name or "/controllers/" in lower
    )


def _has_role(path: str, markers: Sequence[str]) -> bool:
    lower = f"/{path.lower()}"
    name = lower.rsplit("/", 1)[-1]
    return lower.endswith(_ARCHITECTURE_SOURCE_SUFFIXES) and any(
        marker in name or f"/{marker}/" in lower for marker in markers
    )


def _is_database_path(path: str) -> bool:
    lower = f"/{path.lower()}"
    name = lower.rsplit("/", 1)[-1]
    return (
        name in {"schema.sql", "data.sql", "application.yml", "application.yaml"}
        or "/migration" in lower
        or "/migrations/" in lower
    )


def _spread_architecture_chunks(
    chunks: tuple[SourceChunk, ...], paths: Sequence[str]
) -> tuple[SourceChunk, ...]:
    grouped: dict[str, list[SourceChunk]] = {path: [] for path in paths}
    for chunk in chunks:
        grouped.setdefault(chunk.file_path, []).append(chunk)
    for path_chunks in grouped.values():
        path_chunks.sort(
            key=lambda chunk: (-_architecture_chunk_score(chunk), chunk.start_line)
        )
    spread: list[SourceChunk] = []
    offset = 0
    while True:
        added = False
        for path in paths:
            current_chunks = grouped.get(path)
            if current_chunks is not None and offset < len(current_chunks):
                spread.append(current_chunks[offset])
                added = True
        if not added:
            break
        offset += 1
    return tuple(spread)


def _architecture_chunk_score(chunk: SourceChunk) -> int:
    text = chunk.text.lower()
    cues = (
        "controller",
        "service",
        "repository",
        "@entity",
        "@getmapping",
        "@postmapping",
        ".save(",
        ".find",
        "select ",
        "insert ",
        "create table",
    )
    return sum(cue in text for cue in cues)


def _format_architecture_answer(text: str, chunks: Sequence[SourceChunk]) -> str:
    controllers = _unique(
        tuple(
            chunk.file_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            for chunk in chunks
            if _is_controller_path(chunk.file_path)
        )
    )
    if not controllers:
        return text

    fallback_summary = (
        f"This repository exposes {len(controllers)} controller"
        f"{'s' if len(controllers) != 1 else ''} in the indexed source. "
        "The sections below explain the evidence-backed request-to-persistence "
        "paths and call out layers or method details that could not be confirmed."
    )
    first_heading = re.search(r"(?m)^#{1,4}\s+`?([A-Za-z0-9_]*Controller)\b", text)
    headed = {
        match.group(1).casefold()
        for match in re.finditer(r"(?m)^#{1,4}\s+`?([A-Za-z0-9_]*Controller)\b", text)
    }
    if headed:
        missing = [name for name in controllers if name.casefold() not in headed]
        if not missing:
            return (
                text
                if first_heading is not None and text[: first_heading.start()].strip()
                else f"{fallback_summary}\n\n{text}"
            )
        additions = [_missing_controller_section(name) for name in missing]
        formatted = "\n\n".join((text, *additions))
        return (
            formatted
            if first_heading is not None and text[: first_heading.start()].strip()
            else f"{fallback_summary}\n\n{formatted}"
        )

    name_pattern = "|".join(
        re.escape(name) for name in sorted(controllers, key=len, reverse=True)
    )
    matches: list[tuple[int, str]] = []
    seen: set[str] = set()
    for match in re.finditer(rf"\b({name_pattern})\b", text, re.IGNORECASE):
        canonical = next(
            name for name in controllers if name.casefold() == match.group(1).casefold()
        )
        if canonical in seen:
            continue
        seen.add(canonical)
        matches.append((match.start(), canonical))

    intro = text[: matches[0][0]].strip() if matches else ""
    sections: list[str] = []
    for index, (start, name) in enumerate(matches):
        end = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        flow = text[start:end].strip()
        section = f"### {name}\n\n**Flow:** {flow}"
        if not re.search(rf"\b{re.escape(name)}\s*\.", flow, re.IGNORECASE):
            section += "\n\n**Method-level detail:** Not evidenced."
        sections.append(section)
    sections.extend(
        _missing_controller_section(name) for name in controllers if name not in seen
    )
    if not sections:
        return text
    return "\n\n".join((intro or fallback_summary, *sections))


def _missing_controller_section(name: str) -> str:
    return (
        f"### {name}\n\n"
        "**Flow:** Not evidenced in the generated answer.\n\n"
        "**Method-level detail:** Not evidenced."
    )


def _prefer_overlapping(
    intent: QuestionIntent,
    card: RepositoryCard | None,
    chunks: tuple[SourceChunk, ...],
) -> tuple[SourceChunk, ...]:
    if card is None or not chunks:
        return chunks
    spans: tuple[tuple[str, int, int], ...] = ()
    if intent == "endpoints" and card.endpoints:
        spans = tuple(
            (item.file_path, item.start_line, item.end_line) for item in card.endpoints
        )
    elif intent == "dependencies" and card.declared_dependencies:
        spans = tuple(
            (item.file_path, item.start_line, item.end_line)
            for item in card.declared_dependencies
        )
    if not spans:
        return chunks
    overlapping: list[SourceChunk] = []
    rest: list[SourceChunk] = []
    for chunk in chunks:
        if any(
            chunk.file_path == path
            and chunk.start_line <= end
            and chunk.end_line >= start
            for path, start, end in spans
        ):
            overlapping.append(chunk)
        else:
            rest.append(chunk)
    if not overlapping:
        return chunks
    return tuple(overlapping + rest)


def _unique(paths: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        if path and path not in seen:
            seen.add(path)
            ordered.append(path)
    return tuple(ordered)
