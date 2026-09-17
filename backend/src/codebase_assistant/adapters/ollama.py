"""Ollama embedding and completion adapters. Tests inject mock HTTP clients."""

from __future__ import annotations

import json
from collections.abc import Sequence

import httpx

from codebase_assistant.adapters.persistence import EMBEDDING_DIMENSIONS
from codebase_assistant.application.errors import CompletionError, EmbeddingError

_EMBED_PATH = "/api/embed"
_CHAT_PATH = "/api/chat"
_REQUIRED_ANSWER_KEYS = frozenset({"text", "citations", "insufficient_evidence"})


class OllamaEmbedder:
    def __init__(
        self,
        host: str,
        model: str,
        *,
        timeout_seconds: float = 30.0,
        batch_size: int = 16,
        client: httpx.Client | None = None,
    ) -> None:
        self._model = model
        self._batch_size = max(1, batch_size)
        self._client = client or httpx.Client(
            base_url=host.rstrip("/"),
            timeout=timeout_seconds,
        )

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        if not texts:
            return ()
        vectors: list[Sequence[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = list(texts[start : start + self._batch_size])
            vectors.extend(self._embed_batch(batch))
        if len(vectors) != len(texts):
            raise EmbeddingError("embedding provider returned an invalid response")
        return tuple(vectors)

    def _embed_batch(self, texts: list[str]) -> list[Sequence[float]]:
        try:
            response = self._client.post(
                _EMBED_PATH,
                json={"model": self._model, "input": texts},
            )
            response.raise_for_status()
            payload: object = response.json()
        except httpx.TimeoutException as exc:
            raise EmbeddingError("embedding provider timed out") from exc
        except httpx.HTTPError as exc:
            raise EmbeddingError("embedding provider request failed") from exc
        except ValueError as exc:
            raise EmbeddingError(
                "embedding provider returned an invalid response"
            ) from exc
        parsed = _parse_embeddings(payload)
        if len(parsed) != len(texts):
            raise EmbeddingError("embedding provider returned an invalid response")
        return parsed


class OllamaCompleter:
    def __init__(
        self,
        host: str,
        model: str,
        *,
        temperature: float = 0.0,
        max_output_tokens: int = 1024,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
        client: httpx.Client | None = None,
    ) -> None:
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._max_retries = max(0, max_retries)
        self._client = client or httpx.Client(
            base_url=host.rstrip("/"),
            timeout=timeout_seconds,
        )

    def complete(self, prompt: str) -> str:
        attempts = self._max_retries + 1
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                return self._complete_once(prompt)
            except httpx.TimeoutException as exc:
                last_error = exc
            except httpx.HTTPError as exc:
                last_error = exc
        if isinstance(last_error, httpx.TimeoutException):
            raise CompletionError("completion provider timed out") from last_error
        raise CompletionError("completion provider request failed") from last_error

    def _complete_once(self, prompt: str) -> str:
        try:
            response = self._client.post(
                _CHAT_PATH,
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": self._temperature,
                        "num_predict": self._max_output_tokens,
                    },
                },
            )
            response.raise_for_status()
            payload: object = response.json()
        except httpx.TimeoutException:
            raise
        except httpx.HTTPError:
            raise
        except ValueError as exc:
            raise CompletionError(
                "completion provider returned an invalid response"
            ) from exc
        return _parse_completion_content(payload)


def _parse_embeddings(payload: object) -> list[Sequence[float]]:
    if not isinstance(payload, dict):
        raise EmbeddingError("embedding provider returned an invalid response")
    raw = payload.get("embeddings")
    if not isinstance(raw, list):
        raise EmbeddingError("embedding provider returned an invalid response")
    parsed: list[Sequence[float]] = []
    for item in raw:
        if not isinstance(item, list) or len(item) != EMBEDDING_DIMENSIONS:
            raise EmbeddingError("embedding provider returned an invalid response")
        try:
            parsed.append(tuple(float(value) for value in item))
        except (TypeError, ValueError) as exc:
            raise EmbeddingError(
                "embedding provider returned an invalid response"
            ) from exc
    return parsed


def _parse_completion_content(payload: object) -> str:
    if not isinstance(payload, dict):
        raise CompletionError("completion provider returned an invalid response")
    message = payload.get("message")
    if not isinstance(message, dict):
        raise CompletionError("completion provider returned an invalid response")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise CompletionError("completion provider returned an invalid response")
    try:
        parsed: object = json.loads(content)
    except json.JSONDecodeError as exc:
        raise CompletionError(
            "completion provider returned an invalid response"
        ) from exc
    if not isinstance(parsed, dict):
        raise CompletionError("completion provider returned an invalid response")
    if not _REQUIRED_ANSWER_KEYS.issubset(parsed.keys()):
        raise CompletionError("completion provider returned an invalid response")
    if not isinstance(parsed.get("text"), str):
        raise CompletionError("completion provider returned an invalid response")
    if not isinstance(parsed.get("citations"), list):
        raise CompletionError("completion provider returned an invalid response")
    if not isinstance(parsed.get("insufficient_evidence"), bool):
        raise CompletionError("completion provider returned an invalid response")
    return content
