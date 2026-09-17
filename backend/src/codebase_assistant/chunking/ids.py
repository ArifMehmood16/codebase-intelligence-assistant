from hashlib import sha256


def language_for_path(path: str) -> str:
    suffix = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {
        "py": "python",
        "pyi": "python",
        "md": "markdown",
        "txt": "text",
        "js": "javascript",
        "jsx": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "go": "go",
        "rs": "rust",
        "java": "java",
        "json": "json",
        "yml": "yaml",
        "yaml": "yaml",
        "toml": "toml",
        "sh": "shell",
        "sql": "sql",
        "css": "css",
        "html": "html",
        "xml": "xml",
    }.get(suffix, "text")


def hash_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def make_chunk_id(
    repository_id: str,
    file_path: str,
    start_line: int,
    end_line: int,
    text: str,
) -> str:
    payload = f"{repository_id}\n{file_path}\n{start_line}\n{end_line}\n{text}"
    return sha256(payload.encode("utf-8")).hexdigest()
