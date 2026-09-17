"""Ollama completion adapter must stay offline in unit tests via mocked HTTP."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable

import httpx
import pytest


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    )


def test_ollama_completer_posts_chat_and_returns_json_content() -> None:
    from codebase_assistant.adapters.ollama import OllamaCompleter

    answer = {
        "text": "greet is defined in app.py",
        "citations": [
            {"file_path": "src/app.py", "start_line": 1, "end_line": 2},
        ],
        "insufficient_evidence": False,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.read().decode())
        assert request.url.path == "/api/chat"
        assert data["model"] == "llama3.2"
        assert data["stream"] is False
        assert data["format"] == "json"
        assert data["options"]["temperature"] == 0.0
        assert data["options"]["num_predict"] == 1024
        assert data["messages"][0]["role"] == "user"
        assert "Answer using only" in data["messages"][0]["content"]
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": json.dumps(answer)}},
        )

    completer = OllamaCompleter(
        host="http://ollama.test",
        model="llama3.2",
        temperature=0.0,
        max_output_tokens=1024,
        client=_client(handler),
    )
    raw = completer.complete(
        "Answer using only the retrieved source excerpts.\n### Question\nWhere?"
    )
    assert json.loads(raw) == answer


def test_ollama_completer_retries_then_succeeds() -> None:
    from codebase_assistant.adapters.ollama import OllamaCompleter

    attempts = {"count": 0}
    answer = {
        "text": "ok",
        "citations": [],
        "insufficient_evidence": True,
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise httpx.TimeoutException("timed out")
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": json.dumps(answer)}},
        )

    completer = OllamaCompleter(
        host="http://ollama.test",
        model="llama3.2",
        max_retries=2,
        client=_client(handler),
    )
    raw = completer.complete("prompt")
    assert json.loads(raw)["text"] == "ok"
    assert attempts["count"] == 2


def test_ollama_completer_maps_timeout_exhaustion_to_completion_error() -> None:
    from codebase_assistant.adapters.ollama import OllamaCompleter
    from codebase_assistant.application.errors import CompletionError

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    completer = OllamaCompleter(
        host="http://ollama.test",
        model="llama3.2",
        max_retries=1,
        client=_client(handler),
    )
    with pytest.raises(CompletionError, match="timed out"):
        completer.complete("prompt")


def test_ollama_completer_rejects_non_json_message_content() -> None:
    from codebase_assistant.adapters.ollama import OllamaCompleter
    from codebase_assistant.application.errors import CompletionError

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "not json at all"}},
        )

    completer = OllamaCompleter(
        host="http://ollama.test",
        model="llama3.2",
        client=_client(handler),
    )
    with pytest.raises(CompletionError, match="invalid"):
        completer.complete("prompt")


def test_ollama_completer_rejects_schema_missing_keys() -> None:
    from codebase_assistant.adapters.ollama import OllamaCompleter
    from codebase_assistant.application.errors import CompletionError

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": json.dumps({"text": "only"}),
                }
            },
        )

    completer = OllamaCompleter(
        host="http://ollama.test",
        model="llama3.2",
        client=_client(handler),
    )
    with pytest.raises(CompletionError, match="invalid"):
        completer.complete("prompt")


def test_ollama_completer_does_not_log_prompt(
    caplog: pytest.LogCaptureFixture,
) -> None:
    from codebase_assistant.adapters.ollama import OllamaCompleter

    secret = "SUPER_SECRET_PROMPT_BODY"
    answer = {
        "text": "ok",
        "citations": [],
        "insufficient_evidence": True,
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": json.dumps(answer)}},
        )

    completer = OllamaCompleter(
        host="http://ollama.test",
        model="llama3.2",
        client=_client(handler),
    )
    with caplog.at_level(logging.DEBUG):
        completer.complete(secret)
    assert secret not in caplog.text
