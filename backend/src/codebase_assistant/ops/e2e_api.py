"""Deterministic API process for Playwright e2e (fake providers only)."""

from __future__ import annotations

import argparse

import uvicorn

from codebase_assistant.adapters.extractive import ExtractiveCompleter
from codebase_assistant.adapters.lexical import LexicalEmbedder
from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.main import create_app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8010)
    args = parser.parse_args(argv)
    app = create_app(
        workspace=InMemoryWorkspace(),
        embed=LexicalEmbedder(),
        complete=ExtractiveCompleter(),
    )
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
