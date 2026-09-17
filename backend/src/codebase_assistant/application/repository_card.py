"""Build a bounded extractive repository card from accepted source files."""

from __future__ import annotations

import json
import tomllib
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath

from codebase_assistant.application.extractors import (
    DeclaredDependency,
    ExtractedEndpoint,
    extract_endpoints_from_members,
    line_span_for_token,
)
from codebase_assistant.chunking.ids import language_for_path

_README_NAMES = frozenset({"readme.md", "readme.txt", "readme"})
_MANIFEST_RANK = {
    "package.json": 0,
    "pyproject.toml": 1,
    "requirements.txt": 2,
}


@dataclass(frozen=True, slots=True)
class RepositoryCardLimits:
    max_readme_chars: int = 2_000
    max_outline_entries: int = 80
    max_outline_depth: int = 4
    max_dependencies: int = 40
    max_endpoints: int = 40

    def __post_init__(self) -> None:
        if self.max_readme_chars < 1:
            raise ValueError("max_readme_chars must be at least 1")
        if self.max_outline_entries < 1:
            raise ValueError("max_outline_entries must be at least 1")
        if self.max_outline_depth < 1:
            raise ValueError("max_outline_depth must be at least 1")
        if self.max_dependencies < 1:
            raise ValueError("max_dependencies must be at least 1")
        if self.max_endpoints < 1:
            raise ValueError("max_endpoints must be at least 1")


@dataclass(frozen=True, slots=True)
class RepositoryCard:
    display_name: str
    readme_path: str | None = None
    readme_excerpt: str = ""
    manifest_name: str | None = None
    manifest_description: str | None = None
    dependencies: tuple[str, ...] = ()
    languages: tuple[tuple[str, int], ...] = ()
    outline_paths: tuple[str, ...] = ()
    outline_truncated: bool = False
    declared_dependencies: tuple[DeclaredDependency, ...] = ()
    endpoints: tuple[ExtractedEndpoint, ...] = ()


def format_outline_tree(paths: Sequence[str]) -> str:
    """Turn bounded outline paths into a README-style nested directory tree."""
    root: dict[str, object] = {}
    for path in paths:
        if not path or path == "/":
            continue
        is_dir = path.endswith("/")
        parts = [part for part in path.replace("\\", "/").strip("/").split("/") if part]
        if not parts:
            continue
        node: dict[str, object] = root
        for index, part in enumerate(parts):
            last = index == len(parts) - 1
            if last:
                existing = node.get(part)
                if is_dir:
                    if not isinstance(existing, dict):
                        node[part] = {}
                elif part not in node:
                    node[part] = None
                break
            child = node.get(part)
            if not isinstance(child, dict):
                child = {}
                node[part] = child
            node = child
    rendered = _render_outline_tree(root, "")
    return "\n".join(rendered) if rendered else "(empty)"


def _render_outline_tree(node: dict[str, object], indent: str) -> list[str]:
    lines: list[str] = []
    for name in sorted(node, key=str.lower):
        child = node[name]
        if isinstance(child, dict):
            lines.append(f"{indent}{name}/")
            lines.extend(_render_outline_tree(child, f"{indent}  "))
        else:
            lines.append(f"{indent}{name}")
    return lines


def build_repository_card(
    members: Sequence[tuple[str, str]],
    *,
    source_filename: str | None = None,
    limits: RepositoryCardLimits | None = None,
) -> RepositoryCard:
    policy = limits or RepositoryCardLimits()
    paths = tuple(path for path, _text in members)
    by_path = {path: text for path, text in members}

    readme_path, readme_excerpt = _readme(by_path, policy.max_readme_chars)
    manifest_name, manifest_description, declared = _manifests(
        by_path, policy.max_dependencies
    )
    outline_paths, outline_truncated = _outline(
        paths, policy.max_outline_depth, policy.max_outline_entries
    )
    return RepositoryCard(
        display_name=_display_name(source_filename, manifest_name, paths),
        readme_path=readme_path,
        readme_excerpt=readme_excerpt,
        manifest_name=manifest_name,
        manifest_description=manifest_description,
        dependencies=tuple(item.name for item in declared),
        languages=_languages(paths),
        outline_paths=outline_paths,
        outline_truncated=outline_truncated,
        declared_dependencies=declared,
        endpoints=extract_endpoints_from_members(members, limit=policy.max_endpoints),
    )


def card_to_payload(card: RepositoryCard) -> dict[str, object]:
    return {
        "display_name": card.display_name,
        "readme_path": card.readme_path,
        "readme_excerpt": card.readme_excerpt,
        "manifest_name": card.manifest_name,
        "manifest_description": card.manifest_description,
        "dependencies": list(card.dependencies),
        "languages": [
            {"language": name, "count": count} for name, count in card.languages
        ],
        "outline_paths": list(card.outline_paths),
        "outline_truncated": card.outline_truncated,
        "declared_dependencies": [
            {
                "name": item.name,
                "file_path": item.file_path,
                "start_line": item.start_line,
                "end_line": item.end_line,
            }
            for item in card.declared_dependencies
        ],
        "endpoints": [
            {
                "method": item.method,
                "path": item.path,
                "file_path": item.file_path,
                "start_line": item.start_line,
                "end_line": item.end_line,
            }
            for item in card.endpoints
        ],
    }


def card_from_payload(payload: object) -> RepositoryCard | None:
    if not isinstance(payload, dict) or not payload:
        return None
    display = payload.get("display_name")
    display_name = (
        display.strip()
        if isinstance(display, str) and display.strip()
        else "Untitled repository"
    )
    readme_path = payload.get("readme_path")
    excerpt = payload.get("readme_excerpt")
    manifest_name = payload.get("manifest_name")
    manifest_description = payload.get("manifest_description")
    raw_deps = payload.get("dependencies")
    dependencies = (
        tuple(item for item in raw_deps if isinstance(item, str))
        if isinstance(raw_deps, list)
        else ()
    )
    languages: list[tuple[str, int]] = []
    raw_langs = payload.get("languages")
    if isinstance(raw_langs, list):
        for item in raw_langs:
            if not isinstance(item, dict):
                continue
            language = item.get("language")
            count = item.get("count")
            if isinstance(language, str) and isinstance(count, int):
                languages.append((language, count))
    raw_paths = payload.get("outline_paths")
    outline_paths = (
        tuple(item for item in raw_paths if isinstance(item, str))
        if isinstance(raw_paths, list)
        else ()
    )
    truncated = payload.get("outline_truncated")
    return RepositoryCard(
        display_name=display_name,
        readme_path=readme_path if isinstance(readme_path, str) else None,
        readme_excerpt=excerpt if isinstance(excerpt, str) else "",
        manifest_name=manifest_name if isinstance(manifest_name, str) else None,
        manifest_description=(
            manifest_description if isinstance(manifest_description, str) else None
        ),
        dependencies=dependencies,
        languages=tuple(languages),
        outline_paths=outline_paths,
        outline_truncated=truncated is True,
        declared_dependencies=_declared_from_payload(payload),
        endpoints=_endpoints_from_payload(payload),
    )


def _declared_from_payload(
    payload: dict[str, object],
) -> tuple[DeclaredDependency, ...]:
    raw = payload.get("declared_dependencies")
    if not isinstance(raw, list):
        return ()
    found: list[DeclaredDependency] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        file_path = item.get("file_path")
        start = item.get("start_line")
        end = item.get("end_line")
        if (
            isinstance(name, str)
            and name.strip()
            and isinstance(file_path, str)
            and isinstance(start, int)
            and isinstance(end, int)
        ):
            found.append(
                DeclaredDependency(
                    name=name,
                    file_path=file_path,
                    start_line=start,
                    end_line=end,
                )
            )
    return tuple(found)


def _endpoints_from_payload(
    payload: dict[str, object],
) -> tuple[ExtractedEndpoint, ...]:
    raw = payload.get("endpoints")
    if not isinstance(raw, list):
        return ()
    found: list[ExtractedEndpoint] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        method = item.get("method")
        path = item.get("path")
        file_path = item.get("file_path")
        start = item.get("start_line")
        end = item.get("end_line")
        if (
            isinstance(method, str)
            and isinstance(path, str)
            and isinstance(file_path, str)
            and isinstance(start, int)
            and isinstance(end, int)
        ):
            found.append(
                ExtractedEndpoint(
                    method=method,
                    path=path,
                    file_path=file_path,
                    start_line=start,
                    end_line=end,
                )
            )
    return tuple(found)


def _display_name(
    source_filename: str | None,
    manifest_name: str | None,
    paths: Sequence[str],
) -> str:
    if source_filename and source_filename.strip():
        name = source_filename.strip()
        if name.lower().endswith(".zip"):
            name = name[:-4].strip()
        if name:
            return name
    if manifest_name:
        return manifest_name
    roots = [path.split("/", 1)[0] for path in paths if path.split("/", 1)[0]]
    if roots and all(root == roots[0] for root in roots):
        return roots[0]
    return "Untitled repository"


def _readme(by_path: dict[str, str], max_chars: int) -> tuple[str | None, str]:
    candidates = [
        path for path in by_path if PurePosixPath(path).name.lower() in _README_NAMES
    ]
    if not candidates:
        return None, ""
    candidates.sort(key=lambda path: (len(PurePosixPath(path).parts), path))
    path = candidates[0]
    return path, by_path[path][:max_chars]


def _manifests(
    by_path: dict[str, str], max_dependencies: int
) -> tuple[str | None, str | None, tuple[DeclaredDependency, ...]]:
    parsed: list[
        tuple[int, int, str, str | None, str | None, tuple[DeclaredDependency, ...]]
    ] = []
    for path, text in by_path.items():
        name = PurePosixPath(path).name.lower()
        if name not in _MANIFEST_RANK:
            continue
        extracted = _parse_manifest(path, name, text)
        if extracted is None:
            continue
        manifest_name, description, deps = extracted
        depth = len(PurePosixPath(path).parts)
        parsed.append(
            (_MANIFEST_RANK[name], depth, path, manifest_name, description, deps)
        )
    if not parsed:
        return None, None, ()
    parsed.sort(key=lambda row: (row[1], row[0], row[2]))
    primary = next((row for row in parsed if row[3] or row[4]), parsed[0])
    seen: list[DeclaredDependency] = []
    names: set[str] = set()
    for _rank, _depth, _path, _name, _description, deps in parsed:
        for dep in deps:
            if dep.name in names:
                continue
            names.add(dep.name)
            seen.append(dep)
            if len(seen) >= max_dependencies:
                return primary[3], primary[4], tuple(seen)
    return primary[3], primary[4], tuple(seen)


def _parse_manifest(
    path: str, basename: str, text: str
) -> tuple[str | None, str | None, tuple[DeclaredDependency, ...]] | None:
    if basename == "package.json":
        return _parse_package_json(path, text)
    if basename == "pyproject.toml":
        return _parse_pyproject(path, text)
    if basename == "requirements.txt":
        return None, None, _parse_requirements(path, text)
    return None


def _parse_package_json(
    path: str,
    text: str,
) -> tuple[str | None, str | None, tuple[DeclaredDependency, ...]] | None:
    try:
        payload: object = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    name = payload.get("name")
    description = payload.get("description")
    deps: list[DeclaredDependency] = []
    for key in ("dependencies", "optionalDependencies", "devDependencies"):
        block = payload.get(key)
        if isinstance(block, dict):
            for item in block:
                if not isinstance(item, str) or not item.strip():
                    continue
                start, end = line_span_for_token(text, f'"{item}"')
                deps.append(
                    DeclaredDependency(
                        name=item,
                        file_path=path,
                        start_line=start,
                        end_line=end,
                    )
                )
    return (
        name if isinstance(name, str) and name.strip() else None,
        description if isinstance(description, str) else None,
        tuple(deps),
    )


def _parse_pyproject(
    path: str,
    text: str,
) -> tuple[str | None, str | None, tuple[DeclaredDependency, ...]] | None:
    try:
        payload = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return None
    project = payload.get("project")
    if not isinstance(project, dict):
        return None, None, ()
    name = project.get("name")
    description = project.get("description")
    raw_deps = project.get("dependencies")
    deps: list[DeclaredDependency] = []
    if isinstance(raw_deps, list):
        for item in raw_deps:
            if not isinstance(item, str):
                continue
            extracted = _requirement_name(item)
            if not extracted:
                continue
            start, end = line_span_for_token(text, extracted)
            deps.append(
                DeclaredDependency(
                    name=extracted,
                    file_path=path,
                    start_line=start,
                    end_line=end,
                )
            )
    return (
        name if isinstance(name, str) and name.strip() else None,
        description if isinstance(description, str) else None,
        tuple(deps),
    )


def _parse_requirements(path: str, text: str) -> tuple[DeclaredDependency, ...]:
    names: list[DeclaredDependency] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        extracted = _requirement_name(line)
        if extracted:
            names.append(
                DeclaredDependency(
                    name=extracted,
                    file_path=path,
                    start_line=line_no,
                    end_line=line_no,
                )
            )
    return tuple(names)


def _requirement_name(spec: str) -> str | None:
    token = spec.strip()
    if not token or token.startswith(("#", "-", ".")):
        return None
    for separator in ("[", ";", " ", "<", ">", "=", "!", "~"):
        if separator in token:
            token = token.split(separator, 1)[0]
    token = token.strip()
    return token or None


def _outline(
    paths: Sequence[str], max_depth: int, max_entries: int
) -> tuple[tuple[str, ...], bool]:
    derived: list[str] = []
    depth_truncated = False
    for path in paths:
        parts = PurePosixPath(path.replace("\\", "/")).parts
        if not parts:
            continue
        if len(parts) <= max_depth:
            derived.append("/".join(parts))
            continue
        depth_truncated = True
        derived.append("/".join(parts[:max_depth]) + "/")
    unique = tuple(sorted(dict.fromkeys(derived)))
    if len(unique) <= max_entries:
        return unique, depth_truncated
    return unique[:max_entries], True


def _languages(paths: Sequence[str]) -> tuple[tuple[str, int], ...]:
    counts = Counter(language_for_path(path) for path in paths)
    return tuple(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
