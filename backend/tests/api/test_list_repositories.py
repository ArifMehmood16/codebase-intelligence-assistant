"""API coverage for listing indexed repositories."""

from __future__ import annotations

import io
import zipfile

from fastapi.testclient import TestClient

from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.main import create_app


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def test_list_repositories_empty() -> None:
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.get("/api/repositories")
    assert response.status_code == 200
    assert response.json() == {"repositories": []}


def test_list_repositories_returns_uploaded_summaries() -> None:
    workspace = InMemoryWorkspace()
    client = TestClient(create_app(workspace=workspace))
    first = client.post(
        "/api/repositories",
        params={"filename": "alpha.zip"},
        content=_zip_bytes({"src/a.py": b"def a():\n    return 1\n"}),
        headers={"content-type": "application/zip"},
    )
    second = client.post(
        "/api/repositories",
        params={"filename": "beta.zip"},
        content=_zip_bytes({"src/b.py": b"def b():\n    return 2\n"}),
        headers={"content-type": "application/zip"},
    )
    assert first.status_code == 201
    assert second.status_code == 201
    listed = client.get("/api/repositories")
    assert listed.status_code == 200
    body = listed.json()
    ids = {item["repository_id"] for item in body["repositories"]}
    assert first.json()["repository_id"] in ids
    assert second.json()["repository_id"] in ids
    assert len(body["repositories"]) == 2
    for item in body["repositories"]:
        assert item["status"] in {"completed", "failed"}
        assert "indexed_file_count" in item
        assert "indexed_paths" in item
        assert item["source_filename"] in {"alpha.zip", "beta.zip"}
        assert "repository_card" in item
        assert item["repository_card"]["outline_paths"]
