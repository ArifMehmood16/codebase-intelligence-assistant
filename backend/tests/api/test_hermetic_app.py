"""Default API tests must stay offline even when local env selects Ollama."""

from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.main import create_app


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def test_create_app_does_not_construct_ollama_when_env_selects_ollama(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EMBEDDING_PROVIDER", "ollama")
    monkeypatch.setenv("COMPLETION_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:9")

    def boom(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Ollama adapters must not be constructed in default tests")

    monkeypatch.setattr("codebase_assistant.main.OllamaEmbedder", boom)
    monkeypatch.setattr("codebase_assistant.main.OllamaCompleter", boom)

    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.post(
        "/api/repositories",
        params={"filename": "repo.zip"},
        content=_zip_bytes({"src/app.py": b"def greet():\n    return 'hello'\n"}),
        headers={"content-type": "application/zip"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "completed"
    repository_id = response.json()["repository_id"]
    asked = client.post(
        f"/api/repositories/{repository_id}/questions",
        json={"question": "Where is greet defined?"},
    )
    assert asked.status_code == 200
