"""Decide which unpacked paths may become indexed source text."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        "dist",
        "build",
        "coverage",
        "htmlcov",
        "target",
        "vendor",
        ".next",
        "site-packages",
    }
)
_EXCLUDED_DIRECTORY_NAMES = frozenset(name.lower() for name in _EXCLUDED_DIRECTORIES)

_SECRET_BASENAMES = frozenset(
    {
        ".env",
        ".envrc",
        ".netrc",
        ".npmrc",
        ".pypirc",
        ".pgpass",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "credentials.json",
        "credentials.yml",
        "credentials.yaml",
        "secrets.yml",
        "secrets.yaml",
    }
)

_SECRET_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"})

_GENERATED_LOCKFILE_BASENAMES = frozenset(
    {
        "package-lock.json",
        "npm-shrinkwrap.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "cargo.lock",
        "poetry.lock",
        "composer.lock",
        "go.sum",
        "pipfile.lock",
    }
)

_MINIFIED_SUFFIXES = (".min.js", ".min.css")

_ALLOWED_SUFFIXES = frozenset(
    {
        ".py",
        ".pyi",
        ".md",
        ".txt",
        ".toml",
        ".json",
        ".yml",
        ".yaml",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".java",
        ".c",
        ".h",
        ".cpp",
        ".hpp",
        ".cs",
        ".rb",
        ".sh",
        ".sql",
        ".css",
        ".html",
        ".xml",
        ".ini",
    }
)


@dataclass(frozen=True, slots=True)
class SourceFileDecision:
    relative_path: str
    accepted: bool
    reason: str
    text: str | None


def classify_source_file(relative_path: str, data: bytes) -> SourceFileDecision:
    path = PurePosixPath(relative_path.replace("\\", "/"))
    if any(part.lower() in _EXCLUDED_DIRECTORY_NAMES for part in path.parts[:-1]):
        return _ignored(relative_path, "excluded_directory")

    basename = path.name
    if _is_secret_name(basename):
        return _ignored(relative_path, "secret_file")

    lower_name = basename.lower()
    if lower_name in _GENERATED_LOCKFILE_BASENAMES:
        return _ignored(relative_path, "generated_lockfile")
    if lower_name.endswith(_MINIFIED_SUFFIXES):
        return _ignored(relative_path, "generated_bundle")

    suffix = path.suffix.lower()
    if suffix not in _ALLOWED_SUFFIXES:
        return _ignored(relative_path, "extension")

    if b"\x00" in data[:8192]:
        return _ignored(relative_path, "binary")

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return _ignored(relative_path, "encoding")

    return SourceFileDecision(
        relative_path=relative_path,
        accepted=True,
        reason="accepted",
        text=text,
    )


def _is_secret_name(basename: str) -> bool:
    lower = basename.lower()
    if lower in _SECRET_BASENAMES or lower.startswith(".env"):
        return True
    return PurePosixPath(lower).suffix in _SECRET_SUFFIXES


def _ignored(relative_path: str, reason: str) -> SourceFileDecision:
    return SourceFileDecision(
        relative_path=relative_path,
        accepted=False,
        reason=reason,
        text=None,
    )
