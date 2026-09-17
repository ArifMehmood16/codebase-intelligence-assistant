"""Bounded extractors for HTTP routes and declaring-file spans."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

_METHOD_PATH = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+"
    r"(/(?:[A-Za-z0-9._~!$&'()*+,;=:@%/\-]*))"
)
_CALL_ROUTE = re.compile(
    r"(?:app|router|api|blueprint)\.(get|post|put|patch|delete|head|options)"
    r"\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
_SPRING_MAPPING = re.compile(
    r"@(Get|Post|Put|Patch|Delete)Mapping\(\s*(?:path\s*=\s*|value\s*=\s*)?"
    r"[\"']([^\"']+)[\"']"
)
_REQUEST_MAPPING = re.compile(
    r"@RequestMapping\(\s*(?:path\s*=\s*|value\s*=\s*)?[\"']([^\"']+)[\"']"
)


@dataclass(frozen=True, slots=True)
class ExtractedEndpoint:
    method: str
    path: str
    file_path: str
    start_line: int
    end_line: int


@dataclass(frozen=True, slots=True)
class DeclaredDependency:
    name: str
    file_path: str
    start_line: int
    end_line: int


_SOURCE_SUFFIXES = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rb",
    ".php",
    ".cs",
    ".kt",
)


def extract_endpoints(
    file_path: str, text: str, *, limit: int = 40
) -> tuple[ExtractedEndpoint, ...]:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    lower = file_path.lower()
    if not lower.endswith(_SOURCE_SUFFIXES):
        return ()
    found: list[ExtractedEndpoint] = []
    seen: set[tuple[str, str, str]] = set()
    for line_no, line in enumerate(text.splitlines(), start=1):
        for method, path in _routes_on_line(line):
            key = (method, path, file_path)
            if key in seen:
                continue
            seen.add(key)
            found.append(
                ExtractedEndpoint(
                    method=method,
                    path=path,
                    file_path=file_path,
                    start_line=line_no,
                    end_line=line_no,
                )
            )
            if len(found) >= limit:
                return tuple(found)
    return tuple(found)


def extract_endpoints_from_members(
    members: Sequence[tuple[str, str]], *, limit: int = 40
) -> tuple[ExtractedEndpoint, ...]:
    found: list[ExtractedEndpoint] = []
    remaining = limit
    for path, text in members:
        if remaining < 1:
            break
        found.extend(extract_endpoints(path, text, limit=remaining))
        remaining = limit - len(found)
    return tuple(found)


def line_span_for_token(text: str, token: str) -> tuple[int, int]:
    if not token:
        return 1, 1
    for index, line in enumerate(text.splitlines() or [text], start=1):
        if token in line:
            return index, index
    return 1, 1


def _routes_on_line(line: str) -> tuple[tuple[str, str], ...]:
    found: list[tuple[str, str]] = []
    for match in _METHOD_PATH.finditer(line):
        path = _clean_path(match.group(2))
        if path:
            found.append((match.group(1).upper(), path))
    for match in _CALL_ROUTE.finditer(line):
        path = _clean_path(match.group(2))
        if path:
            found.append((match.group(1).upper(), path))
    for match in _SPRING_MAPPING.finditer(line):
        path = _clean_path(match.group(2))
        if path:
            found.append((match.group(1).upper(), path))
    for match in _REQUEST_MAPPING.finditer(line):
        path = _clean_path(match.group(1))
        if path:
            found.append(("GET", path))
    return tuple(found)


def _clean_path(raw: str) -> str | None:
    path = raw.strip().rstrip(".,;:'\")")
    if not path.startswith("/"):
        return None
    return path or None
