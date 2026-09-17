"""Ensure Ollama models required by selected providers. Pulls when missing."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable, Sequence

import httpx


def model_is_present(tags: object, name: str) -> bool:
    if not isinstance(tags, dict):
        return False
    models = tags.get("models")
    if not isinstance(models, list):
        return False
    wanted = {name}
    if ":" not in name:
        wanted.add(f"{name}:latest")
    else:
        wanted.add(name.split(":", 1)[0])
    for item in models:
        if isinstance(item, dict) and str(item.get("name") or "") in wanted:
            return True
    return False


def required_ollama_models(
    *,
    embedding_provider: str,
    completion_provider: str,
    embed_model: str,
    chat_model: str,
) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    if embedding_provider.strip().lower() == "ollama":
        name = embed_model.strip()
        if name and name not in seen:
            ordered.append(name)
            seen.add(name)
    if completion_provider.strip().lower() == "ollama":
        name = chat_model.strip()
        if name and name not in seen:
            ordered.append(name)
            seen.add(name)
    return tuple(ordered)


def ensure_model(
    name: str,
    *,
    list_tags: Callable[[], object],
    pull_model: Callable[[str], None],
) -> None:
    if model_is_present(list_tags(), name):
        return
    pull_model(name)


def ensure_models(
    names: Sequence[str],
    *,
    list_tags: Callable[[], object],
    pull_model: Callable[[str], None],
) -> None:
    for name in names:
        ensure_model(name, list_tags=list_tags, pull_model=pull_model)


def http_list_tags(host: str, timeout: float = 5.0) -> object:
    with httpx.Client(base_url=_http_host(host), timeout=timeout) as client:
        response = client.get("/api/tags")
        response.raise_for_status()
        payload: object = response.json()
        return payload


def http_pull_model(host: str, name: str, timeout: float = 600.0) -> None:
    with httpx.Client(base_url=_http_host(host), timeout=timeout) as client:
        response = client.post("/api/pull", json={"name": name, "stream": False})
        response.raise_for_status()


def _http_host(host: str) -> str:
    base = host.rstrip("/")
    if not base.startswith(("http://", "https://")):
        raise ValueError("Ollama host must be an http(s) URL")
    return base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Pull Ollama models selected by embedding/completion providers "
            "when they are not already present."
        )
    )
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--embedding-provider", default="lexical")
    parser.add_argument("--completion-provider", default="extractive")
    parser.add_argument("--embed-model", default="nomic-embed-text")
    parser.add_argument("--chat-model", default="llama3.2")
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        default=None,
        help="Explicit model tag to ensure (repeatable). Overrides provider selection.",
    )
    args = parser.parse_args(argv)
    names = (
        tuple(args.models)
        if args.models
        else required_ollama_models(
            embedding_provider=args.embedding_provider,
            completion_provider=args.completion_provider,
            embed_model=args.embed_model,
            chat_model=args.chat_model,
        )
    )
    if not names:
        return 0
    try:
        _wait_for_tags(args.host)

        def pull(name: str) -> None:
            print(f"Pulling Ollama model {name} ...", flush=True)
            http_pull_model(args.host, name)

        ensure_models(
            names,
            list_tags=lambda: http_list_tags(args.host),
            pull_model=pull,
        )
    except (httpx.HTTPError, TimeoutError, OSError, ValueError) as exc:
        joined = ", ".join(names)
        print(f"Could not ensure Ollama model(s) {joined!r}: {exc}", file=sys.stderr)
        return 1
    return 0


def _wait_for_tags(host: str) -> object:
    last_error: Exception | None = None
    for _ in range(30):
        try:
            return http_list_tags(host)
        except (httpx.HTTPError, TimeoutError, OSError) as exc:
            last_error = exc
            time.sleep(1)
    raise last_error or RuntimeError(f"Ollama is not reachable at {host}")


if __name__ == "__main__":
    raise SystemExit(main())
