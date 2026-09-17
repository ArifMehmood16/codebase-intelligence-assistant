import json
import logging
from collections.abc import Callable

import httpx
import pytest

from codebase_assistant.adapters.persistence import EMBEDDING_DIMENSIONS
from codebase_assistant.application.errors import EmbeddingError


def _vector(fill: float) -> list[float]:
    values = [0.0] * EMBEDDING_DIMENSIONS
    values[0] = fill
    return values


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    )


def test_ollama_embedder_batches_requests_and_returns_vectors() -> None:
    from codebase_assistant.adapters.ollama import OllamaEmbedder

    seen: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.read().decode())
        seen.append(len(data["input"]))
        assert request.url.path == "/api/embed"
        assert data["model"] == "nomic-embed-text"
        return httpx.Response(
            200,
            json={"embeddings": [_vector(float(len(text))) for text in data["input"]]},
        )

    embedder = OllamaEmbedder(
        host="http://ollama.test",
        model="nomic-embed-text",
        batch_size=2,
        client=_client(handler),
    )
    vectors = embedder.embed(["ab", "cde", "fghi"])
    assert seen == [2, 1]
    assert len(vectors) == 3
    assert len(vectors[0]) == EMBEDDING_DIMENSIONS
    assert vectors[0][0] == 2.0
    assert vectors[2][0] == 4.0


def test_ollama_embedder_maps_timeout_to_embedding_error() -> None:
    from codebase_assistant.adapters.ollama import OllamaEmbedder

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    embedder = OllamaEmbedder(
        host="http://ollama.test",
        model="nomic-embed-text",
        client=_client(handler),
    )
    with pytest.raises(EmbeddingError, match="timed out"):
        embedder.embed(["def greet():\n    return 1\n"])


def test_ollama_embedder_maps_malformed_response_to_embedding_error() -> None:
    from codebase_assistant.adapters.ollama import OllamaEmbedder

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"embeddings": "nope"})

    embedder = OllamaEmbedder(
        host="http://ollama.test",
        model="nomic-embed-text",
        client=_client(handler),
    )
    with pytest.raises(EmbeddingError, match="invalid"):
        embedder.embed(["x = 1"])


def test_ollama_embedder_does_not_log_source(caplog: pytest.LogCaptureFixture) -> None:
    from codebase_assistant.adapters.ollama import OllamaEmbedder

    secret = "SUPER_SECRET_SOURCE_BODY"

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"embeddings": [_vector(1.0)]})

    embedder = OllamaEmbedder(
        host="http://ollama.test",
        model="nomic-embed-text",
        client=_client(handler),
    )
    with caplog.at_level(logging.DEBUG):
        embedder.embed([secret])
    assert secret not in caplog.text
