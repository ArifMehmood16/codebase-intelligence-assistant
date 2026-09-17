"""Extractive repository card from accepted members only (PLAN 13.2)."""

from pathlib import Path

from codebase_assistant.application.repository_card import (
    RepositoryCardLimits,
    build_repository_card,
    card_from_payload,
    card_to_payload,
    format_outline_tree,
)

_REPO_ROOT = Path(__file__).resolve().parents[4]
_FIXTURE_ROOT = _REPO_ROOT / "sample-data" / "fixture-repository"


def _members(*pairs: tuple[str, str]) -> tuple[tuple[str, str], ...]:
    return pairs


def test_fixture_card_uses_readme_and_real_paths() -> None:
    members = tuple(
        (path.relative_to(_FIXTURE_ROOT).as_posix(), path.read_text(encoding="utf-8"))
        for path in sorted(_FIXTURE_ROOT.rglob("*"))
        if path.is_file()
        and "credentials" not in path.name
        and "vendor" not in path.parts
    )
    card = build_repository_card(members, source_filename="fixture-repository.zip")

    assert card.display_name == "fixture-repository"
    assert card.readme_path == "README.md"
    assert "inventory" in card.readme_excerpt.lower()
    assert "src/api/handlers.py" in card.outline_paths
    assert "vendor/leftpad.js" not in card.outline_paths
    assert "node_modules" not in " ".join(card.outline_paths)
    languages = dict(card.languages)
    assert languages["python"] >= 1
    assert languages["markdown"] >= 1


def test_package_json_name_description_and_dependencies() -> None:
    card = build_repository_card(
        _members(
            (
                "frontend/package.json",
                '{"name":"school-crm","description":"School portal","dependencies":'
                '{"react":"18.2.0","axios":"1.6.0"},"devDependencies":{"vite":"5.0.0"}}',
            ),
            ("frontend/src/App.tsx", "export function App() { return null }\n"),
        ),
        source_filename="unused.zip",
    )
    assert card.manifest_name == "school-crm"
    assert card.manifest_description == "School portal"
    assert "react" in card.dependencies
    assert "axios" in card.dependencies
    assert card.display_name == "unused"


def test_pyproject_and_requirements_contribute_declared_dependencies() -> None:
    card = build_repository_card(
        _members(
            (
                "pyproject.toml",
                '[project]\nname = "inventory"\ndescription = "Stock API"\n'
                'dependencies = ["fastapi>=0.141", "pydantic>=2"]\n',
            ),
            ("requirements.txt", "httpx==0.28.1\n# comment\n-r other.txt\n"),
        )
    )
    assert card.manifest_name == "inventory"
    assert card.manifest_description == "Stock API"
    assert "fastapi" in card.dependencies
    assert "pydantic" in card.dependencies
    assert "httpx" in card.dependencies
    assert "-r" not in card.dependencies


def test_outline_is_bounded_by_depth_and_entry_count() -> None:
    deep = tuple((f"src/layer{index}/file.py", "x = 1\n") for index in range(40))
    extra = (("a/b/c/d/e/f/too-deep.py", "y = 2\n"),)
    card = build_repository_card(
        deep + extra,
        limits=RepositoryCardLimits(max_outline_entries=10, max_outline_depth=3),
    )
    assert len(card.outline_paths) <= 10
    assert card.outline_truncated is True
    assert all(path.count("/") < 3 or path.endswith("/") for path in card.outline_paths)
    assert "a/b/c/d/e/f/too-deep.py" not in card.outline_paths
    assert any(path.startswith("a/b/c") for path in card.outline_paths)


def test_outline_tree_nests_directories_like_a_readme() -> None:
    tree = format_outline_tree(
        (
            "README.md",
            "src/app.py",
            "src/api/handlers.py",
            "src/api/",
        )
    )
    assert tree == "\n".join(
        [
            "README.md",
            "src/",
            "  api/",
            "    handlers.py",
            "  app.py",
        ]
    )


def test_outline_tree_empty_paths_are_omitted() -> None:
    assert format_outline_tree(("", "/")) == "(empty)"


def test_readme_excerpt_is_capped_and_malformed_manifests_are_skipped() -> None:
    card = build_repository_card(
        _members(
            ("README.md", "A" * 80),
            ("package.json", "{not-json"),
        ),
        limits=RepositoryCardLimits(max_readme_chars=20),
    )
    assert card.readme_excerpt == "A" * 20
    assert card.manifest_name is None
    assert card.dependencies == ()


def test_card_payload_roundtrip_preserves_fields() -> None:
    original = build_repository_card(
        _members(
            ("README.md", "# Hello\n"),
            ("src/app.py", "x = 1\n"),
        ),
        source_filename="hello.zip",
    )
    restored = card_from_payload(card_to_payload(original))
    assert restored == original
    assert card_from_payload({}) is None
    assert card_from_payload(None) is None
