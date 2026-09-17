"""Endpoint extractors and declaring-file provenance (PLAN 13.6)."""

from pathlib import Path

from codebase_assistant.application.extractors import extract_endpoints
from codebase_assistant.application.repository_card import build_repository_card

_REPO_ROOT = Path(__file__).resolve().parents[4]
_HANDLERS = (
    _REPO_ROOT / "sample-data/fixture-repository/src/api/handlers.py"
).read_text(encoding="utf-8")


def test_fixture_handlers_extract_get_and_post_items() -> None:
    found = extract_endpoints("src/api/handlers.py", _HANDLERS)
    routes = {(item.method, item.path) for item in found}
    assert ("GET", "/items") in routes
    assert ("POST", "/items") in routes
    for item in found:
        if item.path == "/items":
            assert item.file_path == "src/api/handlers.py"
            assert item.start_line >= 1
            assert item.end_line >= item.start_line


def test_fastapi_decorator_is_extracted() -> None:
    text = '@app.get("/health")\nasync def health():\n    return {"ok": True}\n'
    found = extract_endpoints("src/main.py", text)
    assert (found[0].method, found[0].path, found[0].file_path) == (
        "GET",
        "/health",
        "src/main.py",
    )
    assert found[0].start_line == 1


def test_card_stores_endpoints_and_dependency_provenance() -> None:
    card = build_repository_card(
        (
            (
                "src/api/handlers.py",
                'def list_items():\n    """GET /items"""\n    return []\n',
            ),
            (
                "package.json",
                '{"name":"web","dependencies":{"react":"18.2.0"}}\n',
            ),
        )
    )
    routes = {(item.method, item.path, item.file_path) for item in card.endpoints}
    assert ("GET", "/items", "src/api/handlers.py") in routes
    assert "react" in card.dependencies
    react_deps = [item for item in card.declared_dependencies if item.name == "react"]
    assert react_deps
    assert react_deps[0].file_path == "package.json"
    assert react_deps[0].start_line >= 1
